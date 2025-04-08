# src/quacktokenscope/education/challenges/token_challenge.py
"""
Token guessing challenge game logic.

This module contains the logic for the token guessing challenge game,
where users guess which tokenizer will use the fewest tokens for a given text.
"""

import logging
from typing import Dict, List, Any, Optional

from rich.console import Console

from quacktokenscope.education.visualization import guild_challenge

logger = logging.getLogger(__name__)

# Challenge texts of increasing difficulty
CHALLENGE_TEXTS = [
    "Hello, world!",
    "The quick brown fox jumps over the lazy dog.",
    "To be, or not to be: that is the question.",
    "COVID-19 has affected many people worldwide since 2020.",
    "https://www.example.com is a domain used in documentation. Check it out!"
]

# Educational insights for each challenge
EDUCATIONAL_INSIGHTS = [
    "Simple greetings often tokenize efficiently across different tokenizers.",
    "Common phrases like 'the quick brown fox' might be handled differently by tokenizers trained on different corpora.",
    "Punctuation and special characters increase the token count in most tokenizers.",
    "Numbers, dates, and newer terms like 'COVID-19' can challenge tokenizers differently.",
    "URLs and special formatting typically require more tokens than regular text."
]


def run_challenge(
        tokenizers: Dict[str, Any],
        console: Optional[Console] = None,
        custom_texts: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Run the token challenge game.

    Args:
        tokenizers: Dictionary of available tokenizers
        console: Optional console for display
        custom_texts: Optional list of custom challenge texts

    Returns:
        Challenge results including score and stats
    """
    if console is None:
        console = Console()

    # Use custom texts if provided, otherwise use defaults
    texts = custom_texts if custom_texts else CHALLENGE_TEXTS

    # If custom texts are provided, ensure we have matching insights
    insights = EDUCATIONAL_INSIGHTS
    if custom_texts and len(custom_texts) != len(EDUCATIONAL_INSIGHTS):
        # Generate generic insights if needed
        insights = ["Different tokenizers handle text patterns differently."] * len(
            custom_texts)

    # Prepare results structure
    challenge_results = []

    # Run each challenge
    for i, text in enumerate(texts):
        # Run the guild challenge for this text
        challenge_data = guild_challenge(text, tokenizers, console)

        # Store challenge data
        challenge_results.append({
            "challenge_number": i + 1,
            "text": text,
            "insight": insights[i] if i < len(
                insights) else "Understanding tokenization helps optimize prompts.",
            "guild_data": challenge_data
        })

    # Return all results
    return {
        "total": len(texts),
        "challenges": challenge_results
    }