"""Structured logging configuration for all packages (shared, runner, server)"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog


def configure_logging(
    log_level: str = "INFO",
    service_name: str | None = None,
    include_timestamp: bool = True,
) -> None:
    """
    Configure structured JSON logging with context support.

    Structlog logs to stdlib logging, which Sentry automatically captures.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR)
        service_name: Service name to include in logs
        include_timestamp: Whether to include ISO timestamp in logs
    """
    # Validate log_level
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if log_level.upper() not in valid_levels:
        raise ValueError(
            f"Invalid log_level: {log_level}. Must be one of {valid_levels}"
        )

    # Disable verbose logs from external libraries
    _disable_external_logs()

    # Build processors
    processors: list[Any] = [structlog.stdlib.add_log_level]

    if include_timestamp:
        processors.append(structlog.processors.TimeStamper(fmt="iso"))

    if service_name:
        processors.append(_add_service_name(service_name))

    processors.extend(
        [
            structlog.contextvars.merge_contextvars,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging (structlog writes here, Sentry reads from here)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )


def _disable_external_logs() -> None:
    """Disable verbose logs from external libraries"""
    external_loggers = {
        "appium": logging.WARNING,
        "urllib3": logging.ERROR,
        "urllib3.connectionpool": logging.ERROR,
        "httpx": logging.WARNING,
        "httpcore": logging.WARNING,
        "selenium": logging.WARNING,
        "aiohttp": logging.WARNING,
        "asyncio": logging.WARNING,
    }
    for logger_name, level in external_loggers.items():
        logging.getLogger(logger_name).setLevel(level)


def _add_service_name(service_name: str):
    """Add service_name to all log events"""

    def add_service(logger, method_name, event_dict):
        event_dict["service"] = service_name
        return event_dict

    return add_service


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structlog logger"""
    return structlog.get_logger(name)
