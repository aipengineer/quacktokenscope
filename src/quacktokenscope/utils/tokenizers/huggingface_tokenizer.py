# src/quacktokenscope/utils/tokenizers/huggingface_tokenizer.py
"""
HuggingFace tokenizer implementation for QuackTokenScope.

This module provides an implementation of the BaseTokenizer interface
using HuggingFace's transformers library.
"""

import logging
from typing import ClassVar

from quacktokenscope.utils.tokenizers.base import BaseTokenizer


class HuggingFaceTokenizer(BaseTokenizer):
    """
    Tokenizer implementation using HuggingFace's transformers.

    This class implements the BaseTokenizer interface using the transformers
    library from HuggingFace, specifically using the AutoTokenizer.
    """

    name: ClassVar[str] = "huggingface"
    description: ClassVar[str] = "HuggingFace's transformers tokenizer"
    model_name: ClassVar[str] = "bert-base-uncased"
    emoji: ClassVar[str] = "📚"
    guild: ClassVar[str] = "Legacy Lexicon"

    def __init__(self) -> None:
        """Initialize the HuggingFace tokenizer."""
        super().__init__()
        self._tokenizer = None
        self._logger = logging.getLogger(f"quacktokenscope.tokenizers.{self.name}")

    def initialize(self) -> bool:
        """
        Initialize the HuggingFace tokenizer.

        This method loads the bert-base-uncased tokenizer from HuggingFace.

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            from transformers import AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._initialized = True
            self.logger.info(
                f"Initialized {self.name} tokenizer with {self.model_name} model")
            return True
        except ImportError:
            self.logger.error(
                f"Failed to import transformers. Please install it with 'pip install transformers'"
            )
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize HuggingFace tokenizer: {e}")
            return False

    def tokenize(self, text: str) -> tuple[list[int], list[str]]:
        """
        Tokenize the input text using HuggingFace's tokenizer.

        Args:
            text: The text to tokenize

        Returns:
            A tuple of (token_ids, token_strings)
        """
        if not self._initialized:
            raise RuntimeError("Tokenizer not initialized")

        # Encode the text to get token IDs
        encoded = self._tokenizer.encode(text, add_special_tokens=False)
        token_ids = encoded

        # Convert token IDs to token strings
        tokens = self._tokenizer.convert_ids_to_tokens(token_ids)

        return token_ids, tokens

    def decode(self, token_ids: list[int]) -> str:
        """
        Decode the token IDs back to text using HuggingFace's tokenizer.

        Args:
            token_ids: The token IDs to decode

        Returns:
            The decoded text
        """
        if not self._initialized:
            raise RuntimeError("Tokenizer not initialized")

        # Decode the token IDs back to text
        return self._tokenizer.decode(token_ids, skip_special_tokens=True)

    def get_vocab_size(self) -> int:
        """
        Get the size of the HuggingFace tokenizer's vocabulary.

        Returns:
            The size of the vocabulary
        """
        if not self._initialized:
            raise RuntimeError("Tokenizer not initialized")

        return len(self._tokenizer.vocab)