"""Runner settings"""

from __future__ import annotations

from pydantic import Field, HttpUrl

from shared.config import SharedSettings


class RunnerSettings(SharedSettings):
    """Settings for remote runner"""

    # Agent API configuration
    AGENT_API_URL: HttpUrl = Field(
        default="https://agent.noqa.ai", description="Base URL for the agent API"
    )
    DEFAULT_APPIUM_URL: str = Field(
        default="http://localhost:4723",
        description="Default Appium URL for the agent API",
    )


settings = RunnerSettings()
