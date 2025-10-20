"""Type definitions for FastAPI Teams Bot."""

from typing import Any, Dict, Optional, Protocol

from typing_extensions import TypedDict


class User(TypedDict):
    """User information from Teams message.

    Attributes:
        name: Display name of the user
        id: Unique identifier for the user
    """

    name: str
    id: str


class CSVData(TypedDict, total=False):
    """CSV file data for download.

    Attributes:
        csv_content: CSV content as string
        filename: Name of the CSV file
    """

    csv_content: str
    filename: str


class MessageResponse(TypedDict, total=False):
    """Expected response format from message processor.

    Attributes:
        message: Text message to send to user
        csv: Optional CSV file data for download
        adaptive_card: Optional Adaptive Card JSON
    """

    message: str
    csv: Optional[CSVData]
    adaptive_card: Optional[Dict[str, Any]]


class MessageProcessor(Protocol):
    """Protocol for custom message processing logic.

    Implementations should process user messages and return formatted responses.
    This can integrate with any backend: LangGraph, LangChain, custom logic, etc.
    """

    async def __call__(
        self,
        user_message: str,
        user: User,
        conversation_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MessageResponse:
        """Process a user message and return a response.

        Args:
            user_message: The text message from the user
            user: User information (name and id)
            conversation_id: Teams conversation identifier
            metadata: Optional metadata about the message:
                - For CSV uploads: {"action_type": "csv_upload", "csv_data": str}
                - For button clicks: {"action_type": str, "action_data": dict}

        Returns:
            MessageResponse with message, optional CSV, and optional Adaptive Card
        """
        ...
