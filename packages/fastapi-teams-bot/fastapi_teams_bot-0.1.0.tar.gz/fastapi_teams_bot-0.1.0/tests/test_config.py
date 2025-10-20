"""Tests for BotConfig."""

import pytest

from fastapi_teams_bot.config import BotConfig


def test_config_creation():
    """Test creating config with explicit values."""
    config = BotConfig(
        app_id="test-id",
        app_password="test-password",
        app_tenant_id="test-tenant",
    )

    assert config.app_id == "test-id"
    assert config.app_password == "test-password"
    assert config.app_tenant_id == "test-tenant"
    assert config.endpoint_path == "/api/messages"
    assert config.enable_typing_indicator is True
    assert config.max_file_size_mb == 10


def test_config_from_env(monkeypatch):
    """Test creating config from environment variables."""
    monkeypatch.setenv("MICROSOFT_APP_ID", "test-id")
    monkeypatch.setenv("MICROSOFT_APP_PASSWORD", "test-password")
    monkeypatch.setenv("MICROSOFT_APP_TENANT_ID", "test-tenant")

    config = BotConfig.from_env()

    assert config.app_id == "test-id"
    assert config.app_password == "test-password"
    assert config.app_tenant_id == "test-tenant"


def test_config_from_env_no_tenant(monkeypatch):
    """Test creating config without tenant ID."""
    monkeypatch.setenv("MICROSOFT_APP_ID", "test-id")
    monkeypatch.setenv("MICROSOFT_APP_PASSWORD", "test-password")
    monkeypatch.delenv("MICROSOFT_APP_TENANT_ID", raising=False)

    config = BotConfig.from_env()

    assert config.app_id == "test-id"
    assert config.app_password == "test-password"
    assert config.app_tenant_id is None


def test_config_from_env_missing_credentials(monkeypatch):
    """Test that missing credentials raise error."""
    monkeypatch.delenv("MICROSOFT_APP_ID", raising=False)
    monkeypatch.delenv("MICROSOFT_APP_PASSWORD", raising=False)

    with pytest.raises(ValueError, match="must be set"):
        BotConfig.from_env()


def test_config_custom_endpoint():
    """Test custom endpoint configuration."""
    config = BotConfig(
        app_id="test-id",
        app_password="test-password",
        endpoint_path="/custom/endpoint",
    )

    assert config.endpoint_path == "/custom/endpoint"


def test_config_custom_file_settings():
    """Test custom file settings."""
    config = BotConfig(
        app_id="test-id",
        app_password="test-password",
        max_file_size_mb=20,
        supported_file_types=["text/csv", "application/pdf"],
    )

    assert config.max_file_size_mb == 20
    assert "application/pdf" in config.supported_file_types
