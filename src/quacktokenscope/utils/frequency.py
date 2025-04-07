# src/quacktokenscope/utils/frequency.py
"""
Frequency analysis utilities for QuackTokenScope.

This module provides functions for analyzing token frequency
in tokenized text.
"""

import logging
from collections import Counter

from quacktokenscope.schemas.token_analysis import TokenFrequency
from quacktokenscope.utils.tokenizers.base import BaseTokenizer

logger = logging.getLogger(__name__)


def analyze_token_frequency(
        tokenizer: BaseTokenizer, text: str, filename: str
) -> tuple[TokenFrequency, tuple[str, int], tuple[str, int]]:
    """
    Analyze the frequency of tokens in a text.

    Args:
        tokenizer: The tokenizer to use
        text: The text to analyze
        filename: The name of the file being analyzed

    Returns:
        A tuple containing:
        - TokenFrequency object with the frequency analysis
        - Tuple of (most_common_token, count)
        - Tuple of (rarest_token, count)
    """
    logger.info(f"Analyzing token frequency using {tokenizer.name}")

    # Tokenize the text
    token_ids, token_strs = tokenizer.tokenize(text)

    # Get the frequency counts
    id_counter = Counter(token_ids)
    str_counter = Counter(token_strs)

    # Convert to dictionaries for the schema
    id_frequencies = {str(token_id): count for token_id, count in id_counter.items()}
    str_frequencies = dict(str_counter)

    # Create the TokenFrequency object
    frequency = TokenFrequency(
        tokenizer=tokenizer.name,
        file=filename,
        frequencies=str_frequencies,
        id_frequencies=id_frequencies
    )

    # Find the most common and rarest tokens
    # Only consider tokens that appear at least once
    if str_frequencies:
        most_common = str_counter.most_common(1)[0]
        # Get the rarest token (least frequent but still present)
        rarest = str_counter.most_common()[-1]
    else:
        most_common = ("", 0)
        rarest = ("", 0)

    return frequency, most_common, rarest


def format_frequency_chart(token: str, count: int, max_width: int = 20) -> str:
    """
    Format a frequency chart for display in the CLI.

    Args:
        token: The token string
        count: The token count
        max_width: Maximum width of the chart

    Returns:
        A string representation of the frequency chart
    """
    # Calculate the width of the bar
    width = min(count, max_width)

    # Create the bar using block characters
    bar = "█" * width

    return f"{bar} ({count}x)"


def classify_token_rarity(token: str, count: int, total_tokens: int) -> str:
    """
    Classify a token's rarity for display.

    Args:
        token: The token string
        count: The token count
        total_tokens: The total number of tokens

    Returns:
        A rarity classification string (🟢 Common, 🔴 Rare, 🟣 Legendary)
    """
    # Calculate the frequency as a percentage
    frequency = (count / total_tokens) * 100 if total_tokens > 0 else 0

    # Classify based on frequency
    if frequency < 0.1:
        return "🟣 Legendary"
    elif frequency < 1.0:
        return "🔴 Rare"
    else:
        return "🟢 Common"