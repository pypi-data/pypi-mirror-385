"""FastAPI Teams Bot - FastAPI-based Microsoft Teams bot library.

This library provides a simple way to create Microsoft Teams bots using FastAPI
with pluggable message processing logic. Perfect for integrating with LangGraph,
LangChain, or any custom async message processor.

Example:
    >>> from fastapi_teams_bot import create_teams_bot
    >>>
    >>> async def my_processor(user_message, user, conversation_id, metadata):
    ...     # Your custom logic here (LangGraph, LangChain, etc.)
    ...     return {
    ...         "message": f"You said: {user_message}",
    ...         "adaptive_card": {},  # Optional
    ...         "csv": {},  # Optional
    ...     }
    >>>
    >>> app = create_teams_bot(my_processor)
    >>>
    >>> # Run with: uvicorn main:app --host 0.0.0.0 --port 3001
"""

from .bot import TeamsBot, create_teams_bot
from .config import BotConfig
from .types import CSVData, MessageProcessor, MessageResponse, User

__version__ = "0.1.0"

__all__ = [
    "TeamsBot",
    "create_teams_bot",
    "BotConfig",
    "User",
    "MessageResponse",
    "CSVData",
    "MessageProcessor",
]
