# src/quacktokenscope/education/cli/__init__.py
"""
CLI handlers for education commands.

This module contains the handler functions for the educational CLI commands.
"""

from quacktokenscope.education.cli.visualize import handle_visualize_command
from quacktokenscope.education.cli.calculate_cost import handle_calculate_cost_command
from quacktokenscope.education.cli.challenge import handle_challenge_command
from quacktokenscope.education.cli.language_model import handle_language_model_command
from quacktokenscope.education.cli.tutorial import handle_tutorial_command

__all__ = [
    "handle_visualize_command",
    "handle_calculate_cost_command",
    "handle_challenge_command",
    "handle_language_model_command",
    "handle_tutorial_command",
]