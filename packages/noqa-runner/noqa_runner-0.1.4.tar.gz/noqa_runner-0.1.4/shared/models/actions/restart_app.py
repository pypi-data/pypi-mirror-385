from __future__ import annotations

from typing import Literal

from shared.models.actions.base import BaseAction


class RestartApp(BaseAction):
    """Restart the application"""

    name: Literal["restart_app"] = "restart_app"
    bundle_id: str

    def get_action_description(self) -> str:
        return f"Restart app {self.bundle_id}"
