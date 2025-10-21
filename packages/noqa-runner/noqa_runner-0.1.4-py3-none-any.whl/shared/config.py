"""Base settings shared between server and runner"""

from __future__ import annotations

import logging

import sentry_sdk
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class SharedSettings(BaseSettings):
    """Base settings used by server, runner, and test_handler"""

    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    SENTRY_DSN: str | None = Field(default=None)

    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


logger = logging.getLogger(__name__)


def sentry_init(dsn: str | None = None, environment: str = "development"):
    """Initialize Sentry. Logging is automatically captured via stdlib logging."""
    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=0.1,
        enable_logs=True,  # Automatically capture stdlib logging as Sentry logs
    )
