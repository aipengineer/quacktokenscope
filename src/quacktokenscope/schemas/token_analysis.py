# src/quacktokenscope/schemas/token_analysis.py
"""
Token analysis schema definitions for QuackTokenScope.

This module contains Pydantic models that define the structure of token analysis
data extracted from documents by the QuackTokenScope tool.
"""

from pydantic import BaseModel, Field
from typing import Any


class TokenFrequency(BaseModel):
    """Model for token frequency analysis."""

    tokenizer: str = Field(description="Name of the tokenizer")
    file: str = Field(description="Name of the analyzed file")
    frequencies: dict[str, int] = Field(
        description="Mapping of token string to frequency count"
    )
    id_frequencies: dict[str, int] = Field(
        description="Mapping of token ID to frequency count"
    )


class TokenizerStats(BaseModel):
    """Statistics for a single tokenizer's analysis."""

    name: str = Field(description="Name of the tokenizer")
    total_tokens: int = Field(description="Total number of tokens")
    unique_tokens: int = Field(description="Number of unique tokens")
    vocab_size: int = Field(description="Size of tokenizer's vocabulary")
    avg_token_length: float = Field(description="Average token length in characters")
    reconstruction_score: float = Field(
        description="Text reconstruction fidelity score (0-1)"
    )
    reconstruction_status: str = Field(
        description="Fidelity status: Flawless, Imperfect, or Botched"
    )


class TokenRow(BaseModel):
    """A row in the token comparison table."""

    token_index: int = Field(description="Index of the token in the sequence")
    # Each tokenizer will have its own columns in this model
    # We use Any because different tokenizers have different token types
    tokenizer_data: dict[str, dict[str, Any]] = Field(
        description="Per-tokenizer token data (id and string)"
    )


class TokenAnalysis(BaseModel):
    """Complete token analysis results."""

    filename: str = Field(description="Name of the analyzed file")
    tokenizers_used: list[str] = Field(description="List of tokenizers used")
    stats: dict[str, TokenizerStats] = Field(
        description="Statistics per tokenizer"
    )
    token_table: list[TokenRow] = Field(
        description="Table of token comparisons"
    )
    best_match: str = Field(
        description="Tokenizer with the best reconstruction score"
    )


class TokenSummary(BaseModel):
    """Summary of token analysis for display or export."""

    filename: str = Field(description="Name of the analyzed file")
    tokenizers_used: list[str] = Field(description="List of tokenizers used")
    total_tokens: dict[str, int] = Field(
        description="Total tokens per tokenizer"
    )
    best_match: str = Field(
        description="Tokenizer with the best reconstruction score"
    )
    most_common_token: dict[str, tuple[str, int]] = Field(
        description="Most common token per tokenizer (token, count)"
    )
    rarest_token: dict[str, tuple[str, int]] = Field(
        description="Rarest token per tokenizer (token, count)"
    )