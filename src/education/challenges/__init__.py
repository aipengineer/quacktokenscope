# src/quacktokenscope/education/challenges/__init__.py
"""
Challenge modules for QuackTokenScope education.

This package contains challenge-based educational features
for learning about tokenization concepts.
"""

from quacktokenscope.education.challenges.token_challenge import (
    run_challenge,
    CHALLENGE_TEXTS,
    EDUCATIONAL_INSIGHTS,
)

from quacktokenscope.education.challenges.what_if import (
    run_what_if_analysis,
)

__all__ = [
    "run_challenge",
    "CHALLENGE_TEXTS",
    "EDUCATIONAL_INSIGHTS",
    "run_what_if_analysis",
]