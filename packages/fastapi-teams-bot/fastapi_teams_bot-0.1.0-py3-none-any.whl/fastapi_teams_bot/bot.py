"""Main Teams Bot class."""

import asyncio
import json
import logging
from typing import Optional

from botframework.connector.auth import (
    AuthenticationConfiguration,
    JwtTokenValidation,
    MicrosoftAppCredentials,
    SimpleCredentialProvider,
)
from fastapi import FastAPI, HTTPException, Request, Response

from .config import BotConfig
from .handlers import handle_file_consent, process_and_respond_to_message
from .types import MessageProcessor

logger = logging.getLogger(__name__)


class TeamsBot:
    """Microsoft Teams bot with FastAPI integration.

    This class manages the Teams bot configuration and provides a FastAPI
    application with a message endpoint that handles Teams activities.

    Example:
        >>> from fastapi_teams_bot import TeamsBot, BotConfig
        >>>
        >>> async def my_processor(user_message, user, conversation_id, metadata):
        ...     return {"message": f"You said: {user_message}"}
        >>>
        >>> config = BotConfig.from_env()
        >>> bot = TeamsBot(config)
        >>> app = bot.create_app(my_processor)
    """

    def __init__(self, config: BotConfig):
        """Initialize Teams bot.

        Args:
            config: Bot configuration
        """
        self.config = config
        self._app: Optional[FastAPI] = None

        # Set up authentication
        self.credentials = MicrosoftAppCredentials(
            config.app_id,
            config.app_password,
            config.app_tenant_id,
        )
        self.credential_provider = SimpleCredentialProvider(
            config.app_id,
            config.app_password,
        )
        self.auth_config = AuthenticationConfiguration()

    def create_app(self, message_processor: MessageProcessor) -> FastAPI:
        """Create FastAPI application with Teams bot endpoint.

        Args:
            message_processor: Async function to process messages

        Returns:
            Configured FastAPI application
        """
        app = FastAPI(title="Teams Bot", version="1.0.0")

        @app.post(self.config.endpoint_path)
        async def messages(request: Request) -> Response:
            return await self._handle_activity(request, message_processor)

        self._app = app
        return app

    async def _handle_activity(
        self, request: Request, message_processor: MessageProcessor
    ) -> Response:
        """Handle incoming Teams activity."""
        # Parse activity
        try:
            activity = await request.json()
        except Exception as e:
            logger.error("Failed to parse JSON: %s", e)
            raise HTTPException(status_code=400, detail="Invalid JSON")

        logger.info("Received activity: %s", json.dumps(activity))

        # Validate authentication
        auth_header: str = str(request.headers.get("Authorization") or "")
        channel_id: str = str(activity.get("channelId") or "")
        service_url: str = str(activity.get("serviceUrl") or "")

        try:
            await JwtTokenValidation.validate_auth_header(
                auth_header,
                self.credential_provider,
                "",
                channel_id,
                service_url,
                self.auth_config,
            )
        except Exception as e:
            logger.exception("Auth validation failed: %s", e)
            raise HTTPException(status_code=401, detail="Invalid auth token")

        # Handle different activity types
        activity_type = activity.get("type")

        if activity_type == "invoke" and activity.get("name") == "fileConsent/invoke":
            asyncio.create_task(
                handle_file_consent(
                    activity, service_url, self.credentials, self.config
                )
            )
            return Response(status_code=200)

        if activity_type != "message":
            return Response(status_code=200)

        # Process message asynchronously
        conversation_id = str(activity.get("conversation", {}).get("id") or "")
        asyncio.create_task(
            process_and_respond_to_message(
                activity,
                auth_header,
                conversation_id,
                service_url,
                message_processor,
                self.credentials,
                self.config,
            )
        )

        return Response(status_code=200)


def create_teams_bot(
    message_processor: MessageProcessor,
    app_id: Optional[str] = None,
    app_password: Optional[str] = None,
    app_tenant_id: Optional[str] = None,
    **config_kwargs,
) -> FastAPI:
    """Convenience function to create a Teams bot with minimal setup.

    Args:
        message_processor: Async function to process messages
        app_id: Microsoft App ID (or from MICROSOFT_APP_ID env var)
        app_password: Microsoft App Password (or from MICROSOFT_APP_PASSWORD env var)
        app_tenant_id: Optional Microsoft Tenant ID
        **config_kwargs: Additional BotConfig parameters

    Returns:
        Configured FastAPI application

    Example:
        >>> from fastapi_teams_bot import create_teams_bot
        >>>
        >>> async def my_processor(user_message, user, conversation_id, metadata):
        ...     return {"message": f"Echo: {user_message}"}
        >>>
        >>> app = create_teams_bot(my_processor)
    """
    if app_id and app_password:
        config = BotConfig(
            app_id=app_id,
            app_password=app_password,
            app_tenant_id=app_tenant_id,
            **config_kwargs,
        )
    else:
        config = BotConfig.from_env()
        # Override with any provided kwargs
        for key, value in config_kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

    bot = TeamsBot(config)
    return bot.create_app(message_processor)
