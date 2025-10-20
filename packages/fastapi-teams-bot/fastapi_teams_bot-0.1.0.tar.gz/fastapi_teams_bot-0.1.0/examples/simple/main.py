"""Simple echo bot example."""

import os

from fastapi_teams_bot import create_teams_bot


async def echo_processor(user_message, user, conversation_id, metadata):
    """Simple echo processor that repeats the user's message."""
    return {
        "message": f"You said: {user_message}",
    }


# Create the bot
app = create_teams_bot(
    message_processor=echo_processor,
    app_id=os.environ.get("MICROSOFT_APP_ID"),
    app_password=os.environ.get("MICROSOFT_APP_PASSWORD"),
)

if __name__ == "__main__":
    import uvicorn

    print("Starting echo bot on http://0.0.0.0:3001")
    uvicorn.run(app, host="0.0.0.0", port=3001)
