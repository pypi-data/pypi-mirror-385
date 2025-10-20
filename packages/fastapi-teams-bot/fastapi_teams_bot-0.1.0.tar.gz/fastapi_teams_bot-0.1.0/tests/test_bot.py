"""Tests for bot creation and configuration."""

from unittest.mock import AsyncMock, patch

import pytest

from fastapi_teams_bot import TeamsBot, create_teams_bot
from fastapi_teams_bot.config import BotConfig


@pytest.fixture
def mock_processor():
    """Mock message processor."""

    async def processor(user_message, user, conversation_id, metadata=None):
        return {"message": f"Echo: {user_message}"}

    return processor


def test_create_teams_bot_with_credentials(mock_processor):
    """Test creating bot with explicit credentials."""
    app = create_teams_bot(
        mock_processor,
        app_id="test-id",
        app_password="test-password",
        app_tenant_id="test-tenant",
    )

    assert app is not None
    assert hasattr(app, "routes")


def test_create_teams_bot_from_env(mock_processor, monkeypatch):
    """Test creating bot from environment variables."""
    monkeypatch.setenv("MICROSOFT_APP_ID", "test-id")
    monkeypatch.setenv("MICROSOFT_APP_PASSWORD", "test-password")

    app = create_teams_bot(mock_processor)

    assert app is not None


def test_teams_bot_class(mock_processor):
    """Test TeamsBot class."""
    config = BotConfig(
        app_id="test-id",
        app_password="test-password",
    )

    bot = TeamsBot(config)
    assert bot.config == config

    app = bot.create_app(mock_processor)
    assert app is not None


def test_teams_bot_custom_endpoint(mock_processor):
    """Test bot with custom endpoint."""
    config = BotConfig(
        app_id="test-id",
        app_password="test-password",
        endpoint_path="/custom/messages",
    )

    bot = TeamsBot(config)
    app = bot.create_app(mock_processor)

    # Check that route exists
    routes = [route.path for route in app.routes]
    assert "/custom/messages" in routes


def test_create_teams_bot_with_config_kwargs(mock_processor, monkeypatch):
    """Test creating bot with additional config kwargs."""
    monkeypatch.setenv("MICROSOFT_APP_ID", "test-id")
    monkeypatch.setenv("MICROSOFT_APP_PASSWORD", "test-password")

    app = create_teams_bot(
        mock_processor,
        enable_typing_indicator=False,
        max_file_size_mb=20,
    )

    assert app is not None


@pytest.mark.asyncio
async def test_bot_handles_invalid_json(mock_processor):
    """Test bot handles invalid JSON."""
    from fastapi.testclient import TestClient

    config = BotConfig(
        app_id="test-id",
        app_password="test-password",
    )

    bot = TeamsBot(config)
    app = bot.create_app(mock_processor)

    client = TestClient(app)

    with patch(
        "fastapi_teams_bot.bot.JwtTokenValidation.validate_auth_header",
        new_callable=AsyncMock,
    ):
        response = client.post(
            "/api/messages",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
