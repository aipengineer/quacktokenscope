# src/quacktokenscope/utils/reverse_mapping.py
"""
Reverse mapping utilities for QuackTokenScope.

This module provides functions for evaluating the fidelity of tokenization
by reconstructing text from tokens and comparing it to the original.
"""


from quacktokenscope.utils.tokenizers.base import BaseTokenizer
from quackcore.logging import get_logger

logger = get_logger(__name__)

try:
    # Try to import Levenshtein for better distance calculation
    import Levenshtein

    USE_LEVENSHTEIN = True
except ImportError:
    # Fall back to a simpler approach if Levenshtein is not available
    USE_LEVENSHTEIN = False
    logger.warning(
        "Levenshtein package not found. Using simple string comparison for reverse mapping. "
        "Install with 'pip install Levenshtein' for more accurate results."
    )


def calculate_similarity(original: str, reconstructed: str) -> float:
    """
    Calculate the similarity between original and reconstructed text.

    Args:
        original: The original text
        reconstructed: The reconstructed text

    Returns:
        A similarity score between 0 and 1
    """
    if not original:
        return 1.0 if not reconstructed else 0.0

    if USE_LEVENSHTEIN:
        # Use Levenshtein ratio for a more nuanced similarity score
        return Levenshtein.ratio(original, reconstructed)
    else:
        # Simple character-by-character comparison
        # Normalize lengths to get a ratio between 0 and 1
        max_len = max(len(original), len(reconstructed))
        if max_len == 0:
            return 1.0

        # Count matching characters
        matches = sum(1 for a, b in zip(original, reconstructed) if a == b)
        return matches / max_len


def evaluate_reconstruction(
        tokenizer: BaseTokenizer, text: str
) -> tuple[str, float, str]:
    """
    Evaluate how well a tokenizer can reconstruct the original text.

    Args:
        tokenizer: The tokenizer to evaluate
        text: The original text

    Returns:
        A tuple containing:
        - The reconstructed text
        - A similarity score between 0 and 1
        - A status string: "Flawless", "Imperfect", or "Botched"
    """
    logger.info(f"Evaluating reconstruction fidelity for {tokenizer.name}")

    # Tokenize the text
    token_ids, _ = tokenizer.tokenize(text)

    # Reconstruct the text
    reconstructed = tokenizer.decode(token_ids)

    # Calculate the similarity
    similarity = calculate_similarity(text, reconstructed)

    # Determine the status based on the similarity
    if similarity == 1.0:
        status = "Flawless"
    elif similarity >= 0.9:
        status = "Imperfect"
    else:
        status = "Botched"

    return reconstructed, similarity, status


def get_fidelity_emoji(status: str) -> str:
    """
    Get an emoji representation of the fidelity status.

    Args:
        status: The fidelity status string

    Returns:
        An emoji representing the status
    """
    if status == "Flawless":
        return "💯"
    elif status == "Imperfect":
        return "⚠️"
    else:
        return "❌"