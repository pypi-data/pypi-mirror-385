from __future__ import annotations

from typing import Union

from pydantic import BaseModel, Field

from shared.models.actions.activate_app import ActivateApp
from shared.models.actions.background_app import BackgroundApp
from shared.models.actions.input_text import InputText
from shared.models.actions.open_url import OpenUrl
from shared.models.actions.restart_app import RestartApp
from shared.models.actions.scroll import Scroll
from shared.models.actions.stop import Stop
from shared.models.actions.tap import Tap
from shared.models.actions.terminate_app import TerminateApp
from shared.models.actions.wait import Wait
from shared.models.state.condition import Condition


class ActionData(BaseModel):
    """Response schema for mobile actions"""

    action: Union[
        Tap,
        InputText,
        # Swipe,
        Scroll,
        Wait,
        Stop,
        ActivateApp,
        BackgroundApp,
        TerminateApp,
        RestartApp,
        OpenUrl,
    ] = Field(discriminator="name")
    reasoning: str = Field(
        description="Explanation of your decision and reasoning for this action"
    )
    conditions_updates: list[Condition] = Field(
        default=[], description="List of test condition updates"
    )
