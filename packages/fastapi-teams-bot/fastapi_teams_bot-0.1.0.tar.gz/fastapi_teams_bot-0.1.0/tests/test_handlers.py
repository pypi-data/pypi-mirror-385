"""Tests for message handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fastapi_teams_bot.handlers import (
    process_message,
    send_response,
    send_typing_indicator,
)


@pytest.mark.asyncio
async def test_process_message_simple(sample_activity):
    """Test processing a simple text message."""
    mock_processor = AsyncMock(return_value={"message": "Test response"})

    result = await process_message(
        activity=sample_activity,
        auth_header="Bearer test-token",
        conversation_id="conv-123",
        message_processor=mock_processor,
    )

    assert result["message"] == "Test response"
    mock_processor.assert_called_once()

    # Check the processor was called with correct args
    call_args = mock_processor.call_args
    assert call_args[1]["user_message"] == "Hello bot"
    assert call_args[1]["user"]["id"] == "user-id-123"
    assert call_args[1]["conversation_id"] == "conv-123"


@pytest.mark.asyncio
async def test_process_message_with_button_click(sample_activity):
    """Test processing a button click."""
    activity = sample_activity.copy()
    activity["value"] = {"action": "button_clicked", "data": "test"}

    mock_processor = AsyncMock(return_value={"message": "Button handled"})

    await process_message(
        activity=activity,
        auth_header="Bearer test-token",
        conversation_id="conv-123",
        message_processor=mock_processor,
    )

    # Check metadata was passed
    call_args = mock_processor.call_args
    metadata = call_args[1]["metadata"]
    assert metadata is not None
    assert metadata["action_type"] == "button_clicked"


@pytest.mark.asyncio
async def test_process_message_error_handling(sample_activity):
    """Test error handling in message processing."""
    mock_processor = AsyncMock(side_effect=Exception("Test error"))

    result = await process_message(
        activity=sample_activity,
        auth_header="Bearer test-token",
        conversation_id="conv-123",
        message_processor=mock_processor,
    )

    # Should return error message
    assert "error" in result["message"].lower()


@pytest.mark.asyncio
async def test_send_typing_indicator():
    """Test sending typing indicator."""
    with patch("fastapi_teams_bot.handlers.ConnectorClient") as mock_connector_class:
        mock_connector = MagicMock()
        mock_connector.__aenter__ = AsyncMock(return_value=mock_connector)
        mock_connector.__aexit__ = AsyncMock(return_value=None)
        mock_connector.conversations = MagicMock()
        mock_connector.conversations.send_to_conversation = AsyncMock()

        mock_connector_class.return_value = mock_connector

        from botbuilder.schema import ChannelAccount
        from botframework.connector.auth import MicrosoftAppCredentials

        bot_account = ChannelAccount(id="bot-123", name="Test Bot")
        credentials = MagicMock(spec=MicrosoftAppCredentials)

        await send_typing_indicator(
            service_url="https://test.com",
            conversation_id="conv-123",
            bot_account=bot_account,
            credentials=credentials,
        )

        # Verify send was called
        mock_connector.conversations.send_to_conversation.assert_called_once()


@pytest.mark.asyncio
async def test_send_response_with_text(sample_activity, sample_message_response):
    """Test sending a text response."""
    with patch("fastapi_teams_bot.handlers.ConnectorClient") as mock_connector_class:
        mock_connector = MagicMock()
        mock_connector.__aenter__ = AsyncMock(return_value=mock_connector)
        mock_connector.__aexit__ = AsyncMock(return_value=None)
        mock_connector.conversations = MagicMock()
        mock_connector.conversations.send_to_conversation = AsyncMock()

        mock_connector_class.return_value = mock_connector

        from botframework.connector.auth import MicrosoftAppCredentials

        from fastapi_teams_bot.config import BotConfig

        config = BotConfig(app_id="test-id", app_password="test-password")
        credentials = MagicMock(spec=MicrosoftAppCredentials)

        await send_response(
            activity=sample_activity,
            response=sample_message_response,
            service_url="https://test.com",
            conversation_id="conv-123",
            credentials=credentials,
            config=config,
        )

        # Verify send was called
        mock_connector.conversations.send_to_conversation.assert_called_once()


@pytest.mark.asyncio
async def test_send_response_with_csv(sample_activity):
    """Test sending a response with CSV attachment."""
    response = {
        "message": "Here's your export",
        "csv": {
            "csv_content": "Name,Email\nJohn,john@example.com",
            "filename": "export.csv",
        },
    }

    with patch("fastapi_teams_bot.handlers.ConnectorClient") as mock_connector_class:
        mock_connector = MagicMock()
        mock_connector.__aenter__ = AsyncMock(return_value=mock_connector)
        mock_connector.__aexit__ = AsyncMock(return_value=None)
        mock_connector.conversations = MagicMock()
        mock_connector.conversations.send_to_conversation = AsyncMock()

        mock_connector_class.return_value = mock_connector

        from botframework.connector.auth import MicrosoftAppCredentials

        from fastapi_teams_bot.config import BotConfig

        config = BotConfig(app_id="test-id", app_password="test-password")
        credentials = MagicMock(spec=MicrosoftAppCredentials)

        await send_response(
            activity=sample_activity,
            response=response,
            service_url="https://test.com",
            conversation_id="conv-123",
            credentials=credentials,
            config=config,
        )

        # Verify send was called
        mock_connector.conversations.send_to_conversation.assert_called_once()

        # Get the activity that was sent
        call_args = mock_connector.conversations.send_to_conversation.call_args[0]
        sent_activity = call_args[1]

        # Verify CSV attachment was added
        assert sent_activity.attachments is not None
        assert len(sent_activity.attachments) > 0
