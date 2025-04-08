# src/quacktokenscope/utils/tokenizers/base.py
"""
Base tokenizer interface for QuackTokenScope.

This module defines the base tokenizer interface that all concrete tokenizer
implementations must follow.
"""


from abc import ABC, abstractmethod
from collections import Counter
from logging import Logger
from typing import ClassVar

from quacktokenscope import get_logger


class BaseTokenizer(ABC):
    """
    Base class for tokenizers.

    This abstract class defines the interface that all tokenizer
    implementations must follow.
    """

    # Class variables for tokenizer metadata
    name: ClassVar[str] = "base"
    description: ClassVar[str] = "Base tokenizer interface"
    model_name: ClassVar[str] = "none"
    emoji: ClassVar[str] = "🔠"
    guild: ClassVar[str] = "Base Guild"

    def __init__(self) -> None:
        """Initialize the tokenizer."""
        self._logger = get_logger("quacktokenscope.tokenizers.{self.name}")
        self._initialized = False

    @property
    def logger(self) -> Logger:
        """Get the logger for this tokenizer."""
        return self._logger

    @property
    def is_initialized(self) -> bool:
        """Check if the tokenizer is initialized."""
        return self._initialized

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the tokenizer.

        This method should load any models or resources needed by the tokenizer.

        Returns:
            True if initialization was successful, False otherwise
        """
        pass

    @abstractmethod
    def tokenize(self, text: str) -> tuple[list[int], list[str]]:
        """
        Tokenize the input text.

        Args:
            text: The text to tokenize

        Returns:
            A tuple of (token_ids, token_strings)
        """
        pass

    @abstractmethod
    def decode(self, token_ids: list[int]) -> str:
        """
        Decode the token IDs back to text.

        Args:
            token_ids: The token IDs to decode

        Returns:
            The decoded text
        """
        pass

    @abstractmethod
    def get_vocab_size(self) -> int:
        """
        Get the size of the tokenizer's vocabulary.

        Returns:
            The size of the vocabulary
        """
        pass

    def get_token_frequency(self, token_ids: list[int], token_strs: list[str]) -> tuple[
        dict[int, int], dict[str, int]]:
        """
        Calculate the frequency of tokens in the input.

        Args:
            token_ids: List of token IDs
            token_strs: List of token strings

        Returns:
            A tuple of (id_frequencies, string_frequencies) dictionaries
        """
        id_counter = Counter(token_ids)
        str_counter = Counter(token_strs)

        return dict(id_counter), dict(str_counter)

    def __str__(self) -> str:
        """Get a string representation of the tokenizer."""
        return f"{self.emoji} {self.name} ({self.model_name})"


class MockTokenizer(BaseTokenizer):
    """
    Mock tokenizer for testing.

    This simple implementation can be used for testing or as a fallback
    when real tokenizers are not available.
    """

    name = "mock"
    description = "Mock tokenizer for testing"
    model_name = "mock-model"
    emoji = "🧪"
    guild = "Testing Guild"

    def initialize(self) -> bool:
        """Initialize the mock tokenizer."""
        self._initialized = True
        return True

    def tokenize(self, text: str) -> tuple[list[int], list[str]]:
        """
        Tokenize the input text using a simple character-based approach.

        Args:
            text: The text to tokenize

        Returns:
            A tuple of (token_ids, token_strings)
        """
        # Simple character-based tokenization for testing
        tokens = list(text)
        # Use character ASCII values as token IDs
        token_ids = [ord(c) % 1000 for c in tokens]
        return token_ids, tokens

    def decode(self, token_ids: list[int]) -> str:
        """
        Decode the token IDs back to text.

        Args:
            token_ids: The token IDs to decode

        Returns:
            The decoded text
        """
        # Simple decoding for testing - just convert back to characters
        # This will not perfectly reconstruct the original text in all cases
        return "".join(chr(tid % 128) for tid in token_ids)

    def get_vocab_size(self) -> int:
        """
        Get the size of the tokenizer's vocabulary.

        Returns:
            The size of the vocabulary
        """
        # Mock vocabulary size
        return 256