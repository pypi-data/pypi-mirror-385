"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_activity():
    """Sample Teams activity for testing."""
    return {
        "type": "message",
        "id": "1234567890",
        "timestamp": "2025-10-19T12:00:00.000Z",
        "channelId": "msteams",
        "serviceUrl": "https://smba.trafficmanager.net/amer/",
        "from": {
            "id": "user-id-123",
            "name": "Test User",
        },
        "conversation": {
            "id": "conv-id-456",
            "conversationType": "personal",
        },
        "recipient": {
            "id": "bot-id-789",
            "name": "Test Bot",
        },
        "text": "Hello bot",
        "channelData": {
            "tenant": {"id": "tenant-id"},
        },
    }


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return {
        "name": "Test User",
        "id": "user-id-123",
    }


@pytest.fixture
def sample_message_response():
    """Sample message response for testing."""
    return {
        "message": "Test response",
        "csv": {},
        "adaptive_card": {},
    }
