# src/quacktokenscope/utils/tokenizers/__init__.py
"""
Tokenizer implementations package for QuackTokenScope.
"""

from quacktokenscope.utils.tokenizers.base import BaseTokenizer, MockTokenizer
from quacktokenscope.utils.tokenizers.tiktoken_tokenizer import TiktokenTokenizer
from quacktokenscope.utils.tokenizers.huggingface_tokenizer import HuggingFaceTokenizer
from quacktokenscope.utils.tokenizers.sentencepiece_tokenizer import SentencePieceTokenizer

# Dictionary mapping tokenizer names to their classes
TOKENIZER_REGISTRY = {
    "tiktoken": TiktokenTokenizer,
    "huggingface": HuggingFaceTokenizer,
    #"sentencepiece": SentencePieceTokenizer,
    "mock": MockTokenizer,
}

__all__ = [
    "BaseTokenizer",
    "MockTokenizer",
    "TiktokenTokenizer",
    "HuggingFaceTokenizer",
    #"SentencePieceTokenizer",
    "TOKENIZER_REGISTRY",
]