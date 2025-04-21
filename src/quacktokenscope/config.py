# src/quacktokenscope/config.py
"""
Configuration management for QuackTokenScope.

This module uses QuackCore's configuration system to manage settings
for the QuackTokenScope application.
"""

import logging
import atexit
import os
from typing import Any

from pydantic import BaseModel, Field
from quackcore.config import load_config
from quackcore.config.models import QuackConfig
from quackcore.logging import get_logger

# Import QuackCore FS service and helper functions.
from quackcore.fs.service import get_service

fs = get_service()

# Keep track of open file handlers to ensure they get closed
_file_handlers: list[logging.FileHandler] = []


@atexit.register
def _close_file_handlers() -> None:
    """
    Close all file handlers when the program exits.

    This helps avoid resource warnings during test runs.
    """
    for handler in _file_handlers:
        if handler:
            handler.close()
    _file_handlers.clear()


class QuackTokenScopeConfig(BaseModel):
    """
    QuackTokenScope-specific configuration model.

    This model defines the configuration structure specific to QuackTokenScope,
    which will be stored in the 'custom' section of the QuackCore config.
    """

    log_level: str = Field(
        default="INFO",
        description="Logging level for QuackTokenScope",
    )

    output_dir: str = Field(
        default="./output",
        description="Default directory for output files",
    )

    temp_dir: str = Field(
        default="./temp",
        description="Directory for temporary files",
    )

    default_tokenizers: list[str] = Field(
        default=["tiktoken", "huggingface", "sentencepiece"],
        description="Default tokenizers to use",
    )

    output_format: str = Field(
        default="excel",
        description="Default output format (excel, json, csv)",
    )

    max_tokens_to_display: int = Field(
        default=10,
        description="Maximum number of tokens to display in verbose mode",
        ge=1,
        le=100,
    )

    use_mock_tokenizers: bool = Field(
        default=False,
        description="Use mock tokenizers for testing",
    )


def initialize_config(config_path: str | None = None) -> QuackConfig:
    """
    Initialize configuration from a file and set up defaults.

    Args:
        config_path: Optional path to configuration file

    Returns:
        QuackConfig object with QuackTokenScope-specific configuration
    """
    global _config
    _config = None

    # Load configuration from file or defaults
    quack_config = load_config(config_path)

    # Initialize QuackTokenScope-specific configuration if not present.
    if hasattr(quack_config.custom, "get"):
        if "quacktokenscope" not in quack_config.custom:
            quack_config.custom["quacktokenscope"] = QuackTokenScopeConfig().model_dump()
        tokenscope_config = quack_config.custom.get("quacktokenscope", {})
    else:
        if not hasattr(quack_config.custom, "quacktokenscope"):
            setattr(quack_config.custom, "quacktokenscope", QuackTokenScopeConfig().model_dump())
        tokenscope_config = getattr(quack_config.custom, "quacktokenscope", {})

    # Get the log level from tokenscope_config.
    log_level_name = (
        tokenscope_config.get("log_level", "INFO")
        if isinstance(tokenscope_config, dict)
        else getattr(tokenscope_config, "log_level", "INFO")
    )
    log_level = getattr(logging, log_level_name, logging.INFO)

    # When running tests, use minimal logging configuration to avoid file handle issues.
    if "PYTEST_CURRENT_TEST" in os.environ:
        logging.basicConfig(level=log_level, force=True)
        logs_dir = "./logs"
        fs.create_directory(logs_dir, exist_ok=True)
        return quack_config

    # In normal operation, use full logging configuration.
    root_logger = get_logger("quacktokenscope")
    root_logger.setLevel(log_level)

    has_console_handler = any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        for h in root_logger.handlers
    )
    if not has_console_handler:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)

    for handler in list(root_logger.handlers):
        if isinstance(handler, logging.FileHandler):
            root_logger.removeHandler(handler)
            handler.close()

    global _file_handlers

    logs_dir = "./logs"
    if hasattr(quack_config.paths, "logs_dir"):
        logs_dir = quack_config.paths.logs_dir

    # Ensure the logs directory exists using FS API.
    fs.create_directory(logs_dir, exist_ok=True)

    try:
        log_file = fs.join_path(logs_dir, "quacktokenscope.log")
        file_handler = logging.FileHandler(str(log_file), mode="a")
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)
        _file_handlers.append(file_handler)
    except (OSError, PermissionError):
        pass

    return quack_config


_config = None


def get_config() -> QuackConfig:
    """
    Get the QuackTokenScope configuration.

    Uses lazy initialization to avoid resource issues during testing.

    Returns:
        QuackConfig instance
    """
    global _config
    if _config is None:
        _config = initialize_config()
    return _config


def get_tool_config() -> dict[str, Any]:
    """
    Get the QuackTokenScope-specific configuration.

    Returns:
        Dictionary containing QuackTokenScope configuration
    """
    config = get_config()
    if hasattr(config.custom, "get"):
        tokenscope_config = config.custom.get("quacktokenscope", {})
    else:
        tokenscope_config = getattr(config.custom, "quacktokenscope", {})
    return tokenscope_config


def update_tool_config(new_config: dict[str, Any]) -> None:
    """
    Update the QuackTokenScope-specific configuration.

    Args:
        new_config: Dictionary containing new configuration values
    """
    config = get_config()
    tool_config = get_tool_config()

    if isinstance(tool_config, dict):
        updated_config = dict(tool_config)
        updated_config.update(new_config)
    else:
        updated_config = new_config

    if hasattr(config.custom, "get"):
        config.custom["quacktokenscope"] = updated_config
    else:
        setattr(config.custom, "quacktokenscope", updated_config)

