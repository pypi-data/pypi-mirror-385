from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic.json_schema import SkipJsonSchema

from shared.models.actions.base import BaseAction
from shared.models.state.screen import ActiveElement


class Tap(BaseAction):
    """Tap on a mobile element"""

    name: Literal["tap"] = "tap"
    element_number: int = Field(
        description="Number of the element to tap from the elements list", ge=1
    )
    element: SkipJsonSchema[ActiveElement | None] = Field(default=None)

    def get_action_description(self) -> str:
        """Get description of tap action"""
        return f"Tapped on element: {self.element.string_description}"
