"""Tests for type definitions."""

from fastapi_teams_bot.types import CSVData, MessageResponse, User


def test_user_type():
    """Test User TypedDict."""
    user: User = {
        "name": "Test User",
        "id": "user-123",
    }

    assert user["name"] == "Test User"
    assert user["id"] == "user-123"


def test_csv_data_type():
    """Test CSVData TypedDict."""
    csv_data: CSVData = {
        "csv_content": "Name,Email\nJohn,john@example.com",
        "filename": "data.csv",
    }

    assert csv_data["csv_content"] == "Name,Email\nJohn,john@example.com"
    assert csv_data["filename"] == "data.csv"


def test_message_response_type():
    """Test MessageResponse TypedDict."""
    response: MessageResponse = {
        "message": "Hello!",
        "csv": {
            "csv_content": "data",
            "filename": "export.csv",
        },
        "adaptive_card": {
            "type": "AdaptiveCard",
            "version": "1.4",
        },
    }

    assert response["message"] == "Hello!"
    assert response["csv"]["filename"] == "export.csv"
    assert response["adaptive_card"]["type"] == "AdaptiveCard"


def test_message_response_minimal():
    """Test minimal MessageResponse."""
    response: MessageResponse = {
        "message": "Simple response",
    }

    assert response["message"] == "Simple response"
    assert "csv" not in response
    assert "adaptive_card" not in response
