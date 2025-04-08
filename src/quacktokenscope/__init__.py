# src/quacktokenscope/__init__.py
"""
Initialization module for QuackTokenScope.

This module handles environment setup and other initialization tasks
that should be performed when the application starts.
"""


from pathlib import Path

from quackcore.logging import get_logger

logger = get_logger(__name__)

# Import version directly - this is a simple import that won't cause circular dependencies
from quacktokenscope.version import __version__

# Import lazily-loaded modules directly
from quacktokenscope.config import get_config, get_logger
from quacktokenscope.plugins.token_scope import TokenScopePlugin
from quacktokenscope.schemas.token_analysis import TokenAnalysis, TokenFrequency, TokenSummary

# Define what this package exposes
__all__ = [
    # Version
    "__version__",
    # Config
    "get_config",
    "get_logger",
    # Tokenscope functionality
    "TokenScopePlugin",
    "TokenAnalysis",
    "TokenFrequency",
    "TokenSummary",
    "initialize"
]


def ensure_directories() -> None:
    """Ensure necessary directories exist."""
    try:
        Path("./output").mkdir(exist_ok=True, parents=True)
        Path("./temp").mkdir(exist_ok=True, parents=True)
        Path("./logs").mkdir(exist_ok=True, parents=True)
        Path("./models").mkdir(exist_ok=True, parents=True)
        logger.debug("Directory structure initialized")
    except Exception as e:
        logger.warning(f"Error creating directories: {e}")


def initialize() -> None:
    """Initialize QuackTokenScope application."""
    ensure_directories()

    # Let QuackCore handle environment variables when its APIs are called
    logger.debug("QuackTokenScope initialized")