"""Integration tests."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from fastapi_teams_bot import create_teams_bot
from fastapi_teams_bot.config import BotConfig


@pytest.fixture
def echo_processor():
    """Simple echo processor for testing."""

    async def processor(user_message, user, conversation_id, metadata=None):
        return {"message": f"Echo: {user_message}"}

    return processor


def test_create_bot_integration(echo_processor):
    """Test creating a bot end-to-end."""
    config = BotConfig(
        app_id="test-id",
        app_password="test-password",
    )

    from fastapi_teams_bot import TeamsBot

    bot = TeamsBot(config)
    app = bot.create_app(echo_processor)

    # Verify app is created successfully
    assert app is not None


@pytest.mark.asyncio
async def test_message_flow_integration(echo_processor, sample_activity):
    """Test the full message flow."""
    app = create_teams_bot(
        echo_processor,
        app_id="test-id",
        app_password="test-password",
    )

    client = TestClient(app)

    # Mock authentication
    with patch(
        "fastapi_teams_bot.bot.JwtTokenValidation.validate_auth_header",
        new_callable=AsyncMock,
    ):
        # Mock connector for responses
        with patch("fastapi_teams_bot.handlers.ConnectorClient"):
            response = client.post(
                "/api/messages",
                json=sample_activity,
                headers={"Authorization": "Bearer test-token"},
            )

            # Should accept the message
            assert response.status_code == 200


def test_bot_with_custom_endpoint(echo_processor):
    """Test bot with custom endpoint path."""
    app = create_teams_bot(
        echo_processor,
        app_id="test-id",
        app_password="test-password",
        endpoint_path="/custom/messages",
    )

    routes = [route.path for route in app.routes]
    assert "/custom/messages" in routes


def test_bot_health_check():
    """Test adding custom routes to bot."""

    async def simple_processor(user_message, user, conversation_id, metadata=None):
        return {"message": "OK"}

    from fastapi_teams_bot import TeamsBot

    config = BotConfig(app_id="test-id", app_password="test-password")
    bot = TeamsBot(config)
    app = bot.create_app(simple_processor)

    # Add health check
    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
