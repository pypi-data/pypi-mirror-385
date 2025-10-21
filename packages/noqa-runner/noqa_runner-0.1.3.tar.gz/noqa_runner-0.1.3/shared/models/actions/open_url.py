from __future__ import annotations

from typing import Literal

from pydantic import AnyUrl, Field

from shared.models.actions.base import BaseAction


class OpenUrl(BaseAction):
    """Navigate to specific URL within the app"""

    name: Literal["open_url"] = "open_url"
    url: AnyUrl = Field(
        description="URL to navigate to (must contain protocol like https:// or myapp://)",
        min_length=1,
    )

    def get_action_description(self) -> str:
        """Get description of open URL action"""
        return f"Opened URL: {self.url}"
