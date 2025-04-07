# src/quacktokenscope/utils/tokenizers/tiktoken_tokenizer.py
"""
Tiktoken tokenizer implementation for QuackTokenScope.

This module provides an implementation of the BaseTokenizer interface
using OpenAI's tiktoken library.
"""

import logging
from typing import ClassVar

from quacktokenscope.utils.tokenizers.base import BaseTokenizer


class TiktokenTokenizer(BaseTokenizer):
    """
    Tokenizer implementation using OpenAI's tiktoken.

    This class implements the BaseTokenizer interface using the tiktoken
    library, which is the tokenizer used by OpenAI's models.
    """

    name: ClassVar[str] = "tiktoken"
    description: ClassVar[str] = "OpenAI's tiktoken tokenizer"
    model_name: ClassVar[str] = "cl100k_base"
    emoji: ClassVar[str] = "🧠"
    guild: ClassVar[str] = "Neural Precision"

    def __init__(self) -> None:
        """Initialize the tiktoken tokenizer."""
        super().__init__()
        self._encoding = None
        self._logger = logging.getLogger(f"quacktokenscope.tokenizers.{self.name}")

    def initialize(self) -> bool:
        """
        Initialize the tiktoken tokenizer.

        This method loads the cl100k_base encoding used by GPT-4 and other
        recent OpenAI models.

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            import tiktoken
            self._encoding = tiktoken.get_encoding(self.model_name)
            self._initialized = True
            self.logger.info(
                f"Initialized {self.name} tokenizer with {self.model_name} encoding")
            return True
        except ImportError:
            self.logger.error(
                f"Failed to import tiktoken. Please install it with 'pip install tiktoken'"
            )
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize tiktoken tokenizer: {e}")
            return False

    def tokenize(self, text: str) -> tuple[list[int], list[str]]:
        """
        Tokenize the input text using tiktoken.

        Args:
            text: The text to tokenize

        Returns:
            A tuple of (token_ids, token_strings)
        """
        if not self._initialized:
            raise RuntimeError("Tokenizer not initialized")

        # Encode the text to get token IDs
        token_ids = self._encoding.encode(text)

        # Decode each token ID individually to get the string representation
        token_strs = [self._encoding.decode([token_id]) for token_id in token_ids]

        return token_ids, token_strs

    def decode(self, token_ids: list[int]) -> str:
        """
        Decode the token IDs back to text using tiktoken.

        Args:
            token_ids: The token IDs to decode

        Returns:
            The decoded text
        """
        if not self._initialized:
            raise RuntimeError("Tokenizer not initialized")

        return self._encoding.decode(token_ids)

    def get_vocab_size(self) -> int:
        """
        Get the size of the tiktoken vocabulary.

        Returns:
            The size of the vocabulary
        """
        if not self._initialized:
            raise RuntimeError("Tokenizer not initialized")

        # For tiktoken, we can get the size of the "merges" dictionary
        # This is an approximation of the vocabulary size
        return len(self._encoding._mergeable_ranks)