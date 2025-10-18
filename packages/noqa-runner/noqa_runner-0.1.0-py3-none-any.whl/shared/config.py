"""Base settings shared between server and runner"""

from __future__ import annotations

import logging

import sentry_sdk
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class SharedSettings(BaseSettings):
    """Base settings used by server, runner, and test_handler"""

    # Environment
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")

    # Monitoring
    SENTRY_DSN: str | None = Field(default=None)

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields from .env
    )


logger = logging.getLogger(__name__)


def sentry_init(dsn: str | None = None, environment: str = "development"):
    """Initialize Sentry for error tracking"""
    if not dsn:
        return

    sentry_sdk.init(dsn=dsn, environment=environment, traces_sample_rate=0.1)
