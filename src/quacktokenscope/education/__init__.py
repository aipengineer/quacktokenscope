# src/quacktokenscope/education/__init__.py
"""
Education modules for QuackTokenScope.

This package contains educational tools to help users understand
tokenization concepts in a fun and interactive way.
"""

from quacktokenscope.education.visualization import (
    create_tokenization_dataframe,
    display_technique,
    display_token_comparison,
    display_token_splitting_diagram,
    guild_challenge,
    suggest_token_optimizations,
    get_random_token_fact,
    display_tokenization_wisdom,
    export_visualization_to_text,
)

from quacktokenscope.education.cost_calculator import (
    calculate_cost,
    compare_models,
    display_cost_summary,
    display_what_if_scenarios,
    calculate_efficiency_metrics,
)

from quacktokenscope.education.language_model import (
    SimpleLanguageModel,
    compare_tokenizer_predictions,
    display_tokenizer_predictions,
    display_text_generation,
)

__all__ = [
    # Visualization
    "create_tokenization_dataframe",
    "display_technique",
    "display_token_comparison",
    "display_token_splitting_diagram",
    "guild_challenge",
    "suggest_token_optimizations",
    "get_random_token_fact",
    "display_tokenization_wisdom",
    "export_visualization_to_text",

    # Cost calculator
    "calculate_cost",
    "compare_models",
    "display_cost_summary",
    "display_what_if_scenarios",
    "calculate_efficiency_metrics",

    # Language model
    "SimpleLanguageModel",
    "compare_tokenizer_predictions",
    "display_tokenizer_predictions",
    "display_text_generation",
]