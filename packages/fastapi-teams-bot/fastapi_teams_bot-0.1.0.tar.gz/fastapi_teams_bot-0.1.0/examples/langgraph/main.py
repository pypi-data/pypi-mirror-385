"""LangGraph integration example."""

import os
from typing import Optional

from fastapi_teams_bot import create_teams_bot


# Simulated LangGraph workflow
async def process_user_message(
    user_message: str,
    user: dict,
    conversation_id: str,
    metadata: Optional[dict] = None,
) -> dict:
    """
    This simulates a LangGraph workflow.
    Replace this with your actual LangGraph implementation.
    """

    # Handle special commands
    if user_message.strip().lower() == "/help":
        return {
            "message": "**Available Commands**\n\n- `/help` - Show this message\n- `/new` - Start new conversation\n\nJust type your question naturally!",
        }

    if user_message.strip().lower() == "/new":
        return {
            "message": f"✨ Hello {user['name']}! New conversation started!",
        }

    # Handle CSV upload
    if metadata and metadata.get("action_type") == "csv_upload":
        csv_data = metadata.get("csv_data", "")
        lines = csv_data.split("\n")
        return {
            "message": f"Processed CSV with {len(lines)} lines!",
        }

    # Regular message processing
    # In a real implementation, this would call your LangGraph workflow
    return {
        "message": f"Processed: {user_message}\n\n(This is a simulated LangGraph response. Replace with your actual workflow.)",
        "adaptive_card": {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": f"Hello {user['name']}!",
                    "size": "Large",
                    "weight": "Bolder",
                },
                {
                    "type": "TextBlock",
                    "text": f"You said: {user_message}",
                    "wrap": True,
                },
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "👍 Helpful",
                    "data": {"action": "feedback_positive"},
                },
                {
                    "type": "Action.Submit",
                    "title": "👎 Not helpful",
                    "data": {"action": "feedback_negative"},
                },
            ],
        },
    }


# Create the bot
app = create_teams_bot(
    message_processor=process_user_message,
    app_id=os.environ.get("MICROSOFT_APP_ID"),
    app_password=os.environ.get("MICROSOFT_APP_PASSWORD"),
)

if __name__ == "__main__":
    import uvicorn

    print("Starting LangGraph bot on http://0.0.0.0:3001")
    uvicorn.run(app, host="0.0.0.0", port=3001)
