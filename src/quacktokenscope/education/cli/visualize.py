# src/quacktokenscope/education/cli/visualize.py
"""
CLI handler for the visualization command.

This module contains the handler function for the visualization CLI command.
"""

from pathlib import Path

import click
from quackcore.cli import print_error, print_info, print_success
from rich.console import Console

from quacktokenscope.plugins.token_scope import TokenScopePlugin
from quacktokenscope.education.visualization import (
    create_tokenization_dataframe,
    display_technique,
    display_token_comparison,
    display_token_splitting_diagram,
    suggest_token_optimizations,
)
from quackcore.logging import get_logger

logger = get_logger(__name__)


def handle_visualize_command(
        ctx: click.Context,
        input_text: str,
        technique: str = "Default",
        tokenizer: str | None = None,
        split_diagram: bool = False,
        suggest_optimizations: bool = False,
        export: str | None = None,
) -> None:
    """
    Handle the visualization command.

    Args:
        ctx: The Click context
        input_text: The text to visualize
        technique: Tokenization technique to display
        tokenizer: Specific tokenizer to use (or None for all)
        split_diagram: Whether to show token splitting diagram
        suggest_optimizations: Whether to suggest optimizations
        export: Path to export visualization to
    """
    console = Console()

    # Check if input is a file path
    input_path = Path(input_text)
    if input_path.exists() and input_path.is_file():
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                input_text = f.read()
            print_info(f"Read input from file: {input_path}")
        except Exception as e:
            print_error(f"Failed to read file: {e}", exit_code=1)
            return

    # Limit very long inputs
    if len(input_text) > 1000:
        original_length = len(input_text)
        input_text = input_text[:1000]
        print_info(f"Limited input from {original_length} to 1000 characters")

    # Create and initialize the token scope plugin to get tokenizers
    plugin = TokenScopePlugin()
    init_result = plugin.initialize()

    if not init_result.success:
        print_error(f"Failed to initialize tokenscope plugin: {init_result.error}",
                    exit_code=1)
        return

    # Get available tokenizers
    available_tokenizers = plugin._tokenizers

    if not available_tokenizers:
        print_error("No tokenizers available", exit_code=1)
        return

    # Filter to the requested tokenizer if specified
    if tokenizer:
        if tokenizer in available_tokenizers:
            tokenizers_to_use = {tokenizer: available_tokenizers[tokenizer]}
        else:
            print_error(
                f"Tokenizer '{tokenizer}' not found. Available tokenizers: {', '.join(available_tokenizers.keys())}",
                exit_code=1)
            return
    else:
        tokenizers_to_use = available_tokenizers

    # Create DataFrame with tokenization results
    df = create_tokenization_dataframe(input_text, tokenizers_to_use)

    # Show token splitting diagram if requested
    if split_diagram and tokenizer:
        console.print(display_token_splitting_diagram(
            input_text,
            tokenizers_to_use[tokenizer],
            console
        ))

    # Display tokenization visualization
    if tokenizer:
        # Display single tokenizer with technique
        console.print(display_technique(
            df,
            tokenizer,
            technique,
            console
        ))
    else:
        # Display comparison of all tokenizers
        console.print(display_token_comparison(
            df,
            list(tokenizers_to_use.keys()),
            console
        ))

    # Suggest optimizations if requested
    if suggest_optimizations:
        console.print(suggest_token_optimizations(input_text, console))

    # Export to file if requested
    if export:
        try:
            export_path = Path(export)
            # Create parent directories if they don't exist
            export_path.parent.mkdir(parents=True, exist_ok=True)

            # Export as text
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(console.export_text())

            print_success(f"Exported visualization to: {export_path}")
        except Exception as e:
            print_error(f"Failed to export visualization: {e}")