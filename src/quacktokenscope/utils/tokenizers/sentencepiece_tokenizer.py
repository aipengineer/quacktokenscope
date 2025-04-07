# src/quacktokenscope/utils/tokenizers/sentencepiece_tokenizer.py
"""
SentencePiece tokenizer implementation for QuackTokenScope.

This module provides an implementation of the BaseTokenizer interface
using Google's SentencePiece library.
"""

import logging
from pathlib import Path
from typing import ClassVar

from quacktokenscope.utils.tokenizers.base import BaseTokenizer


class SentencePieceTokenizer(BaseTokenizer):
    """
    Tokenizer implementation using Google's SentencePiece.

    This class implements the BaseTokenizer interface using the SentencePiece
    library from Google, which implements subword units like BPE and unigram.
    """

    name: ClassVar[str] = "sentencepiece"
    description: ClassVar[str] = "Google's SentencePiece tokenizer"
    model_name: ClassVar[str] = "t5-base"  # Using T5's SentencePiece model
    emoji: ClassVar[str] = "🧬"
    guild: ClassVar[str] = "Statistical Fragmentation"

    def __init__(self) -> None:
        """Initialize the SentencePiece tokenizer."""
        super().__init__()
        self._tokenizer = None
        self._temp_dir = None
        self._logger = logging.getLogger(f"quacktokenscope.tokenizers.{self.name}")

    def initialize(self) -> bool:
        """
        Initialize the SentencePiece tokenizer.

        This method attempts to use a pre-trained SentencePiece model from T5,
        or falls back to a simpler model if necessary.

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # First try to use transformers with T5 model (has SentencePiece built-in)
            try:
                from transformers import T5Tokenizer
                self._tokenizer = T5Tokenizer.from_pretrained(self.model_name)
                self._initialized = True
                self.logger.info(f"Initialized {self.name} tokenizer using T5Tokenizer")
                return True
            except (ImportError, Exception) as e:
                self.logger.warning(f"Failed to initialize T5Tokenizer: {e}")
                self.logger.info("Falling back to direct SentencePiece implementation")

                # Fall back to direct SentencePiece implementation
                import sentencepiece as spm

                # Try to find an existing model or download a small pre-trained one
                # For simplicity in this example, we'll use a model that might be
                # cached by HuggingFace or create a very basic one

                # Check if we have a models directory
                models_dir = Path("./models")
                models_dir.mkdir(exist_ok=True, parents=True)

                model_path = models_dir / "sentencepiece.model"

                if not model_path.exists():
                    # If no model exists, try to create a very simple one from sample text
                    self.logger.info(
                        "No SentencePiece model found, creating a simple one...")

                    # Create a temporary directory for training
                    import tempfile
                    self._temp_dir = tempfile.mkdtemp(prefix="quacktokenscope_spm_")

                    # Create a simple text file for training
                    train_path = Path(self._temp_dir) / "train.txt"
                    with open(train_path, "w", encoding="utf-8") as f:
                        f.write("This is a sample text for SentencePiece training.\n")
                        f.write(
                            "It contains some words and sentences to build a small model.\n")
                        f.write(
                            "The model will be very limited but sufficient for demonstration.\n")

                    # Train a tiny model
                    spm.SentencePieceTrainer.train(
                        f"--input={train_path} "
                        f"--model_prefix={models_dir}/sentencepiece "
                        "--vocab_size=100 "
                        "--character_coverage=1.0 "
                        "--model_type=unigram"
                    )

                # Load the model
                self._tokenizer = spm.SentencePieceProcessor()
                self._tokenizer.load(str(model_path))
                self._initialized = True
                self.logger.info(
                    f"Initialized {self.name} tokenizer using direct SentencePiece")
                return True

        except ImportError:
            self.logger.error(
                "Failed to import sentencepiece. Please install it with 'pip install sentencepiece'"
            )
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize SentencePiece tokenizer: {e}")
            return False

    def tokenize(self, text: str) -> tuple[list[int], list[str]]:
        """
        Tokenize the input text using SentencePiece.

        Args:
            text: The text to tokenize

        Returns:
            A tuple of (token_ids, token_strings)
        """
        if not self._initialized:
            raise RuntimeError("Tokenizer not initialized")

        # Check if we're using the T5Tokenizer or direct SentencePiece
        if hasattr(self._tokenizer, "encode"):
            # T5Tokenizer
            token_ids = self._tokenizer.encode(text, add_special_tokens=False)
            token_strs = self._tokenizer.convert_ids_to_tokens(token_ids)
        else:
            # Direct SentencePiece
            token_ids = self._tokenizer.encode(text, out_type=int)
            token_strs = self._tokenizer.encode(text, out_type=str)

        return token_ids, token_strs

    def decode(self, token_ids: list[int]) -> str:
        """
        Decode the token IDs back to text using SentencePiece.

        Args:
            token_ids: The token IDs to decode

        Returns:
            The decoded text
        """
        if not self._initialized:
            raise RuntimeError("Tokenizer not initialized")

        # Check if we're using the T5Tokenizer or direct SentencePiece
        if hasattr(self._tokenizer, "decode"):
            # T5Tokenizer
            return self._tokenizer.decode(token_ids, skip_special_tokens=True)
        else:
            # Direct SentencePiece
            return self._tokenizer.decode(token_ids)

    def get_vocab_size(self) -> int:
        """
        Get the size of the SentencePiece vocabulary.

        Returns:
            The size of the vocabulary
        """
        if not self._initialized:
            raise RuntimeError("Tokenizer not initialized")

        # Check if we're using the T5Tokenizer or direct SentencePiece
        if hasattr(self._tokenizer, "vocab_size"):
            # T5Tokenizer
            return self._tokenizer.vocab_size
        else:
            # Direct SentencePiece
            return self._tokenizer.get_piece_size()