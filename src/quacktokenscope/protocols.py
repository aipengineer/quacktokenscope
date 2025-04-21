# src/quacktokenscope/protocols.py
"""
Protocol definitions for QuackTokenScope.

This module defines protocols that plugins must implement to be
compatible with QuackCore and QuackTokenScope.
"""

from logging import Logger
from typing import Any, Protocol, runtime_checkable

from quackcore.integrations.core.results import IntegrationResult
from quackcore.plugins.protocols import QuackPluginProtocol, QuackPluginMetadata


@runtime_checkable
class TokenizerProtocol(Protocol):
    """Protocol for tokenizers."""

    @property
    def name(self) -> str:
        """Get the name of the tokenizer."""
        ...

    def initialize(self) -> bool:
        """Initialize the tokenizer."""
        ...

    def tokenize(self, text: str) -> tuple[list[int], list[str]]:
        """
        Tokenize the input text.

        Args:
            text: The text to tokenize

        Returns:
            A tuple of (token_ids, token_strings)
        """
        ...

    def decode(self, token_ids: list[int]) -> str:
        """
        Decode the token IDs back to text.

        Args:
            token_ids: The token IDs to decode

        Returns:
            The decoded text
        """
        ...

    def get_vocab_size(self) -> int:
        """
        Get the size of the tokenizer's vocabulary.

        Returns:
            The size of the vocabulary
        """
        ...


@runtime_checkable
class QuackToolPluginProtocol(QuackPluginProtocol, Protocol):
    """Protocol for QuackTool plugins."""

    # Add initialization state attribute to the protocol
    _initialized: bool

    @property
    def logger(self) -> Logger:
        """Get the logger for the plugin."""
        ...

    @property
    def version(self) -> str:
        """Get the version of the plugin."""
        ...

    def get_metadata(self) -> QuackPluginMetadata:
        """
        Get metadata for the plugin.

        Returns:
            QuackPluginMetadata: Plugin metadata
        """
        ...

    def initialize(self) -> IntegrationResult:
        """Initialize the plugin."""
        ...

    def is_available(self) -> bool:
        """Check if the plugin is available."""
        ...

    def process_file(
        self,
        file_path: str,
        output_path: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> IntegrationResult:
        """Process a file using the plugin."""
        ...