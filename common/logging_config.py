"""Shared logging setup, used by every agent's tools.py and llm_client.py.

Attaches our own console handler to a dedicated logger instead of using
logging.basicConfig() on the root logger — basicConfig() is a no-op once
something else (e.g. the `adk` CLI) has already added handlers to the root
logger, which would otherwise silently swallow our log output.
"""

import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s - %(message)s"
_BASE_LOGGER_NAME = "agent_discovery"
_configured = False


def setup_logging() -> None:
    """Configure the app's base logger once, level taken from LOG_LEVEL (default INFO)."""
    global _configured
    if _configured:
        return
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    base_logger = logging.getLogger(_BASE_LOGGER_NAME)
    base_logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    base_logger.addHandler(handler)
    # Also let messages reach the root logger's handlers (e.g. adk's own
    # per-run log file) instead of only our console handler.
    base_logger.propagate = True

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a logger under the app's base logger, ensuring setup runs first."""
    setup_logging()
    return logging.getLogger(f"{_BASE_LOGGER_NAME}.{name}")
