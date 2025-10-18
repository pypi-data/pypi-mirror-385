from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic.json_schema import SkipJsonSchema

from shared.models.actions.base import BaseAction
from shared.models.state.screen import ActiveElement


class Scroll(BaseAction):
    """Scroll on a mobile element"""

    name: Literal["scroll"] = "scroll"
    element_number: int = Field(
        description="Number of the element to scroll, from the elements list", ge=1
    )
    direction: Literal["up", "down", "left", "right"] = Field(
        description="Direction to scroll"
    )
    element: SkipJsonSchema[ActiveElement | None] = None

    def get_action_description(self) -> str:
        """Get description of scroll action"""
        return (
            f"Scrolled {self.direction} on element: {self.element.string_description}"
        )
