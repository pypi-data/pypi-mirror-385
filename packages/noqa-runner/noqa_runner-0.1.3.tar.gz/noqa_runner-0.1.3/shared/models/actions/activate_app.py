from __future__ import annotations

from typing import Literal

from shared.models.actions.base import BaseAction


class ActivateApp(BaseAction):
    """Activate the application"""

    name: Literal["activate_app"] = "activate_app"
    bundle_id: str

    def get_action_description(self) -> str:
        return "Activate app {self.bundle_id}"
