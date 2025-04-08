# src/quacktokenscope/plugin.py
"""
Plugin implementation for QuackCore integration.

This module provides the main entry point for QuackCore's plugin discovery system.
"""

import inspect
import os
import tempfile
from logging import Logger
from typing import Any, cast

from quackcore.integrations.core.results import IntegrationResult
from quackcore.logging import get_logger
from quacktokenscope.plugins.token_scope import TokenScopePlugin
from quacktokenscope.protocols import QuackToolPluginProtocol

# Import QuackCore FS service and helper functions.
from quackcore.fs import service as fs, join_path

# Module-level dictionary to track registrations
_PLUGIN_REGISTRY: dict[str, QuackToolPluginProtocol] = {}
_LOGGER = get_logger(__name__)

# Define lock directory and lock file using QuackCore FS helpers.
_LOCK_DIR = join_path(tempfile.gettempdir(), "quacktokenscope")
_LOCK_FILE = join_path(_LOCK_DIR, "instance.lock")


def _check_other_instances() -> tuple[bool, str]:
    """
    Check if there are other instances of the plugin running.

    Returns:
        Tuple of (is_another_instance_running, message)
    """
    try:
        # Ensure the lock directory exists.
        fs.create_directory(_LOCK_DIR, exist_ok=True)

        # Check if lock file exists using fs.get_file_info.
        lock_info = fs.get_file_info(_LOCK_FILE)
        if lock_info.success and lock_info.exists:
            # Try to read the PID from the lock file.
            read_result = fs.read_text(_LOCK_FILE, encoding="utf-8")
            if read_result.success:
                pid = read_result.content.strip()
                return True, f"Another instance appears to be running (PID: {pid})"
            else:
                return True, "Another instance appears to be running"
            # If the lock file is old, we can overwrite it (this is not explicitly checked here).

        # Write the current PID into the lock file.
        write_result = fs.write_text(_LOCK_FILE, str(os.getpid()), encoding="utf-8",
                                     atomic=True)
        if not write_result.success:
            _LOGGER.warning(f"Failed to write lock file: {write_result.error}")
        return False, "No other instances detected"

    except Exception as e:
        _LOGGER.warning(f"Error checking for other instances: {e}")
        # Continue even if we can't check for other instances.
        return False, f"Could not check for other instances: {e}"


class QuackTokenScopePlugin(QuackToolPluginProtocol):
    """Plugin implementation for QuackTokenScope."""

    _instance = None  # Class-level instance tracking
    _logger = None  # Class-level logger instance
    _token_scope_plugin = None  # TokenScope plugin instance
    _project_name = "QuackTokenScope"  # Default name if config can't be loaded

    def __new__(cls):
        """Implement singleton pattern at the class level."""
        if cls._instance is None:
            cls._instance = super(QuackTokenScopePlugin, cls).__new__(cls)
            cls._instance._initialized = False  # Initialize the instance attributes
            cls._logger = get_logger(__name__)  # Initialize the logger at class level

            # Try to load the project name from config.
            try:
                from quackcore.config import load_config
                config = load_config()
                if hasattr(config, "general") and hasattr(config.general,
                                                          "project_name"):
                    cls._project_name = config.general.project_name
            except Exception as e:
                cls._logger.debug(f"Could not load project name from config: {e}")
                # Keep using the default name.
        return cls._instance

    def __init__(self) -> None:
        """Initialize the plugin if not already initialized."""
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = False
        self._token_scope_plugin = None

    @property
    def logger(self) -> Logger:
        """Get the logger for the plugin."""
        return self.__class__._logger

    @property
    def name(self) -> str:
        """Return the plugin name."""
        return self.__class__._project_name

    @property
    def version(self) -> str:
        """Return the plugin version."""
        return "0.1.0"

    def initialize(self) -> IntegrationResult:
        """
        Initialize the plugin.

        Returns:
            IntegrationResult indicating success or failure.
        """
        try:
            # Check for other instances.
            other_instance_running, message = _check_other_instances()
            if other_instance_running:
                return IntegrationResult.error_result(
                    f"Cannot initialize QuackTokenScope: {message}. "
                    f"Please close other CLI sessions using QuackTokenScope and try again."
                )

            # Initialize the token scope plugin.
            self._token_scope_plugin = TokenScopePlugin()
            init_result = self._token_scope_plugin.initialize()
            if not init_result.success:
                return init_result

            self._initialized = True
            return IntegrationResult.success_result(
                message=f"{self.__class__._project_name} plugin initialized successfully"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize QuackTokenScope plugin: {e}")
            return IntegrationResult.error_result(
                f"Failed to initialize {self.__class__._project_name} plugin: {str(e)}"
            )

    def is_available(self) -> bool:
        """
        Check if the plugin is available.

        Returns:
            True if the plugin is available.
        """
        return self._initialized

    def process_file(
            self,
            file_path: str,
            output_path: str | None = None,
            options: dict[str, Any] | None = None,
    ) -> IntegrationResult:
        """
        Process a file using QuackTokenScope.

        Args:
            file_path: Path to the file to process.
            output_path: Optional path for the output file.
            options: Optional processing options.

        Returns:
            IntegrationResult containing the result of the operation.
        """
        if not self._initialized:
            init_result = self.initialize()
            if not init_result.success:
                return init_result

        try:
            self.logger.info(f"Processing file: {file_path}")
            # Delegate to the token scope plugin.
            if self._token_scope_plugin:
                return self._token_scope_plugin.process_file(
                    file_path=file_path,
                    output_path=output_path,
                    options=options
                )
            else:
                return IntegrationResult.error_result(
                    "Token scope plugin not initialized")
        except Exception as e:
            self.logger.error(f"Error processing file: {e}")
            return IntegrationResult.error_result(f"Error processing file: {str(e)}")

    def __del__(self):
        """Clean up resources when the plugin is garbage collected."""
        try:
            lock_info = fs.get_file_info(_LOCK_FILE)
            if lock_info.success and lock_info.exists:
                read_result = fs.read_text(_LOCK_FILE, encoding="utf-8")
                if read_result.success and read_result.content.strip() == str(
                        os.getpid()):
                    fs.delete(_LOCK_FILE)
        except Exception:
            pass


def create_plugin() -> QuackToolPluginProtocol:
    """
    Create and return a singleton QuackTokenScope plugin instance.

    This function ensures that the plugin is instantiated and registered only once
    across the entire application lifetime, even if imported multiple times.

    Returns:
        The singleton QuackTokenScope plugin instance.
    """
    # Get the caller's module using inspect.
    caller_frame = inspect.currentframe()
    caller_frame = caller_frame.f_back if caller_frame else None
    caller_module = caller_frame.f_globals.get('__name__',
                                               'unknown') if caller_frame else 'unknown'

    plugin_key = "quacktokenscope_plugin"
    if plugin_key in _PLUGIN_REGISTRY:
        plugin = cast(QuackTokenScopePlugin, _PLUGIN_REGISTRY[plugin_key])
        plugin._initialized = False
        return plugin

    instance = QuackTokenScopePlugin()
    instance._initialized = False
    _PLUGIN_REGISTRY[plugin_key] = instance

    _LOGGER.debug(f"Plugin instance created by {caller_module}")
    return instance
