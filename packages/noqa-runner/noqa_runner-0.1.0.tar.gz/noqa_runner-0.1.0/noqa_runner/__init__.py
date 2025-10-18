"""
noqa runner package.

AI-powered mobile test execution runner for iOS applications.
"""

from __future__ import annotations

from noqa_runner.logging_config import configure_logging

# Configure default logging on module import
# CLI will reconfigure with custom log level if needed
configure_logging()
