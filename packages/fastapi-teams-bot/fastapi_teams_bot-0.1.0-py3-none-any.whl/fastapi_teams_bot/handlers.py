"""Message and activity handlers for Teams bot."""

import base64
import logging
from typing import Any, Dict, cast

import aiohttp
from botbuilder.schema import Activity, ActivityTypes, Attachment, ChannelAccount
from botframework.connector.aio import ConnectorClient
from botframework.connector.auth import MicrosoftAppCredentials

from .config import BotConfig
from .types import MessageProcessor, User

logger = logging.getLogger(__name__)


async def process_message(
    activity: dict,
    auth_header: str,
    conversation_id: str,
    message_processor: MessageProcessor,
) -> Dict[str, Any]:
    """Process incoming message activity and extract metadata.

    Args:
        activity: The Teams activity dictionary
        auth_header: Authorization header for downloading files
        conversation_id: Teams conversation ID
        message_processor: Function to process the message

    Returns:
        Response dictionary with message, csv, and adaptive_card
    """
    fr = activity.get("from") or {}
    user: User = {
        "name": fr.get("name") or "User",
        "id": fr.get("id") or "unknown",
    }
    user_text = activity.get("text") or ""
    activity_value = activity.get("value")

    csv_content = None
    for att in activity.get("attachments", []):
        content_type = att.get("contentType")
        if content_type == "text/csv":
            csv_url = att.get("contentUrl")
        elif content_type == "application/vnd.microsoft.teams.file.download.info":
            download_info = att.get("content") or {}
            csv_url = download_info.get("downloadUrl")
        else:
            csv_url = None

        if csv_url and csv_url.startswith("http"):
            try:
                async with aiohttp.ClientSession() as session:
                    headers = (
                        {"Authorization": auth_header}
                        if content_type == "text/csv"
                        else {}
                    )
                    async with session.get(csv_url, headers=headers) as resp:
                        if resp.status == 200:
                            csv_content = await resp.text()
                            logger.info("Successfully extracted CSV content")
                        else:
                            logger.warning(
                                f"Failed to download CSV: status {resp.status}"
                            )
            except Exception as e:
                logger.exception(f"Error downloading CSV: {e}")

    metadata = None
    if csv_content:
        metadata = {
            "action_type": "csv_upload",
            "csv_data": csv_content,
        }
        user_text = "User uploaded CSV file"
    elif activity_value and isinstance(activity_value, dict):
        action = activity_value.get("action")
        if action:
            metadata = {
                "action_type": action,
                "action_data": activity_value,
            }
            user_text = f"User clicked: {metadata['action_type']}"

    try:
        return await message_processor(
            user_message=user_text,
            user=cast(User, user),
            conversation_id=conversation_id,
            metadata=metadata,
        )
    except Exception as e:
        logger.exception("Workflow error: %s", e)
        return {
            "message": "I encountered an error processing your request.",
            "csv": {},
            "adaptive_card": {},
        }


async def send_typing_indicator(
    service_url: str,
    conversation_id: str,
    bot_account: ChannelAccount,
    credentials: MicrosoftAppCredentials,
):
    """Send a typing indicator to Teams to show the bot is working.

    Args:
        service_url: Teams service URL
        conversation_id: Teams conversation ID
        bot_account: Bot's channel account
        credentials: Microsoft app credentials
    """
    if not service_url or not conversation_id:
        logger.warning("Missing service URL or conversation ID for typing indicator")
        return

    try:
        async with ConnectorClient(credentials, base_url=service_url) as connector:
            typing_activity = Activity(
                type=ActivityTypes.typing,
                from_property=bot_account,
            )

            await connector.conversations.send_to_conversation(
                conversation_id, typing_activity
            )
            logger.debug("Sent typing indicator")
    except Exception as e:
        logger.warning(f"Failed to send typing indicator: {e}")


async def send_response(
    activity: dict,
    response: Dict[str, Any],
    service_url: str,
    conversation_id: str,
    credentials: MicrosoftAppCredentials,
    config: BotConfig,
):
    """Send response message to Teams with optional attachments.

    Args:
        activity: Original activity that triggered this response
        response: Response dictionary with message, csv, and adaptive_card
        service_url: Teams service URL
        conversation_id: Teams conversation ID
        credentials: Microsoft app credentials
        config: Bot configuration
    """
    incoming_recipient = activity.get("recipient") or {}
    bot_id = str(incoming_recipient.get("id") or config.app_id)
    bot_name = incoming_recipient.get("name") or "Teams Bot"
    bot_account = ChannelAccount(id=bot_id, name=bot_name)

    message = response.get("message", "")
    csv_data = response.get("csv", {})
    adaptive_card = response.get("adaptive_card", {})

    if not service_url or not conversation_id:
        logger.warning(
            "Missing service URL or conversation ID; unable to deliver response"
        )
        return

    try:
        async with ConnectorClient(credentials, base_url=service_url) as connector:
            attachments: list[Attachment] = []

            if csv_data:
                csv_bytes = csv_data.get("csv_content", "").encode("utf-8")
                csv_base64 = base64.b64encode(csv_bytes).decode("utf-8")
                csv_filename = csv_data.get("filename", "export.csv")
                attachments.append(
                    Attachment(
                        name=csv_filename,
                        content_type="application/vnd.microsoft.teams.card.file.consent",
                        content={
                            "description": "CSV export ready for download.",
                            "sizeInBytes": len(csv_bytes),
                            "acceptContext": {
                                "csv_base64": csv_base64,
                                "filename": csv_filename,
                            },
                            "declineContext": {
                                "filename": csv_filename,
                            },
                        },
                    )
                )
                logger.info("Added file consent card for CSV export")

            if adaptive_card:
                attachments.append(
                    Attachment(
                        content_type="application/vnd.microsoft.card.adaptive",
                        content=adaptive_card,
                    )
                )
                logger.info("Added Adaptive Card attachment to response")

            out_activity = Activity(
                type=ActivityTypes.message,
                text=message,
                from_property=bot_account,
                attachments=attachments or None,
            )

            resp = await connector.conversations.send_to_conversation(
                conversation_id, out_activity
            )
            logger.info("Sent activity, response: %s", getattr(resp, "id", repr(resp)))
    except Exception as e:
        logger.exception("Failed to send outgoing activity: %s", e)


async def handle_file_consent(
    activity: dict,
    service_url: str,
    credentials: MicrosoftAppCredentials,
    config: BotConfig,
):
    """Handle file consent response from user.

    Args:
        activity: File consent activity
        service_url: Teams service URL
        credentials: Microsoft app credentials
        config: Bot configuration
    """
    value = activity.get("value") or {}
    action = value.get("action")
    context = value.get("context") or {}
    upload_info = value.get("uploadInfo") or {}
    conversation_id = str(activity.get("conversation", {}).get("id") or "")

    if not service_url or not conversation_id:
        logger.warning(
            "Missing service URL or conversation ID for file consent handling"
        )
        return

    bot_recipient = activity.get("recipient") or {}
    bot_account = ChannelAccount(
        id=str(bot_recipient.get("id") or config.app_id),
        name=bot_recipient.get("name") or "Teams Bot",
    )

    try:
        async with ConnectorClient(credentials, base_url=service_url) as connector:
            if action == "accept":
                csv_base64 = context.get("csv_base64")
                filename = (
                    context.get("filename") or upload_info.get("name") or "export.csv"
                )
                upload_url = upload_info.get("uploadUrl")

                if not csv_base64 or not upload_url:
                    logger.error("File consent accept missing payload or upload URL")
                    await connector.conversations.send_to_conversation(
                        conversation_id,
                        Activity(
                            type=ActivityTypes.message,
                            from_property=bot_account,
                            text="Unable to upload the CSV file.",
                        ),
                    )
                    return

                try:
                    csv_bytes = base64.b64decode(csv_base64)
                except Exception as e:
                    logger.exception(
                        "Failed to decode CSV contents from context: %s", e
                    )
                    await connector.conversations.send_to_conversation(
                        conversation_id,
                        Activity(
                            type=ActivityTypes.message,
                            from_property=bot_account,
                            text="Unable to decode the CSV file for upload.",
                        ),
                    )
                    return

                try:
                    async with aiohttp.ClientSession() as session:
                        total_bytes = len(csv_bytes)
                        headers = {
                            "Content-Type": "application/octet-stream",
                            "Content-Length": str(total_bytes),
                            "Content-Range": f"bytes 0-{total_bytes - 1}/{total_bytes}",
                        }
                        async with session.put(
                            upload_url, data=csv_bytes, headers=headers
                        ) as upload_resp:
                            if upload_resp.status not in {200, 201, 202}:
                                body = await upload_resp.text()
                                logger.error(
                                    "Teams upload URL returned %s: %s",
                                    upload_resp.status,
                                    body,
                                )
                                await connector.conversations.send_to_conversation(
                                    conversation_id,
                                    Activity(
                                        type=ActivityTypes.message,
                                        from_property=bot_account,
                                        text="Failed to deliver the CSV file to Teams.",
                                    ),
                                )
                                return
                except Exception as e:
                    logger.exception("Error uploading CSV to Teams storage: %s", e)
                    await connector.conversations.send_to_conversation(
                        conversation_id,
                        Activity(
                            type=ActivityTypes.message,
                            from_property=bot_account,
                            text="An error occurred while uploading the CSV file.",
                        ),
                    )
                    return

                file_attachment = Attachment(
                    name=filename,
                    content_type="application/vnd.microsoft.teams.card.file.info",
                    content={
                        "uniqueId": upload_info.get("uniqueId")
                        or upload_info.get("id")
                        or "",
                        "fileType": "csv",
                    },
                    content_url=upload_info.get("contentUrl") or upload_url or "",
                )

                await connector.conversations.send_to_conversation(
                    conversation_id,
                    Activity(
                        type=ActivityTypes.message,
                        from_property=bot_account,
                        text="Your CSV export is ready.",
                        attachments=[file_attachment],
                    ),
                )
                logger.info("Completed file consent upload for %s", filename)

            elif action == "decline":
                filename = (
                    context.get("filename") or upload_info.get("name") or "export.csv"
                )
                await connector.conversations.send_to_conversation(
                    conversation_id,
                    Activity(
                        type=ActivityTypes.message,
                        from_property=bot_account,
                        text=f"Upload cancelled for {filename}.",
                    ),
                )
                logger.info("User declined file upload for %s", filename)
            else:
                logger.warning("Received unsupported file consent action: %s", action)
    except Exception as e:
        logger.exception("Failed to process file consent event: %s", e)


async def process_and_respond_to_message(
    activity: dict,
    auth_header: str,
    conversation_id: str,
    service_url: str,
    message_processor: MessageProcessor,
    credentials: MicrosoftAppCredentials,
    config: BotConfig,
):
    """Process message and send response with typing indicator.

    Args:
        activity: Teams activity
        auth_header: Authorization header
        conversation_id: Teams conversation ID
        service_url: Teams service URL
        message_processor: Function to process messages
        credentials: Microsoft app credentials
        config: Bot configuration
    """
    incoming_recipient = activity.get("recipient") or {}
    bot_account = ChannelAccount(
        id=str(incoming_recipient.get("id") or config.app_id),
        name=incoming_recipient.get("name") or "Teams Bot",
    )

    if config.enable_typing_indicator:
        await send_typing_indicator(
            service_url, conversation_id, bot_account, credentials
        )

    response = await process_message(
        activity, auth_header, conversation_id, message_processor
    )
    await send_response(
        activity, response, service_url, conversation_id, credentials, config
    )
