"""Configuration for Teams Bot."""

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BotConfig:
    """Configuration for Microsoft Teams bot.

    Attributes:
        app_id: Microsoft App ID (from Azure Bot Registration)
        app_password: Microsoft App Password (from Azure Bot Registration)
        app_tenant_id: Optional Microsoft App Tenant ID
        endpoint_path: FastAPI endpoint path for bot messages
        enable_typing_indicator: Whether to send typing indicators
        max_file_size_mb: Maximum file size for uploads in MB
        supported_file_types: List of supported MIME types for file uploads
    """

    app_id: str
    app_password: str
    app_tenant_id: Optional[str] = None
    endpoint_path: str = "/api/messages"
    enable_typing_indicator: bool = True
    max_file_size_mb: int = 10
    supported_file_types: List[str] = field(
        default_factory=lambda: [
            "text/csv",
            "application/vnd.microsoft.teams.file.download.info",
        ]
    )

    @classmethod
    def from_env(cls) -> "BotConfig":
        """Create configuration from environment variables.

        Expected environment variables:
            - MICROSOFT_APP_ID
            - MICROSOFT_APP_PASSWORD
            - MICROSOFT_APP_TENANT_ID (optional)

        Returns:
            BotConfig instance

        Raises:
            ValueError: If required environment variables are not set
        """
        app_id = os.environ.get("MICROSOFT_APP_ID", "")
        app_password = os.environ.get("MICROSOFT_APP_PASSWORD", "")

        if not app_id or not app_password:
            raise ValueError(
                "MICROSOFT_APP_ID and MICROSOFT_APP_PASSWORD must be set in environment"
            )

        return cls(
            app_id=app_id,
            app_password=app_password,
            app_tenant_id=os.environ.get("MICROSOFT_APP_TENANT_ID"),
        )
