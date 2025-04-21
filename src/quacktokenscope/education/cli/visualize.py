# src/quacktokenscope/education/cli/visualize.py
"""
CLI handler for the visualization command.

This module contains the handler function for the visualization CLI command.
"""

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
# Use the quackcore.fs service for file operations.
from quackcore.fs import service as fs

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

    # Check if input_text represents a file path.
    file_info = fs.get_file_info(input_text)
    if file_info.success and file_info.exists and file_info.is_file:
        read_result = fs.read_text(input_text, encoding="utf-8")
        if not read_result.success:
            print_error(f"Failed to read file: {read_result.error}", exit_code=1)
            return
        input_text = read_result.content
        print_info(f"Read input from file: {input_text}")

    # Limit very long inputs.
    if len(input_text) > 1000:
        original_length = len(input_text)
        input_text = input_text[:1000]
        print_info(f"Limited input from {original_length} to 1000 characters")

    # Create and initialize the token scope plugin to get tokenizers.
    plugin = TokenScopePlugin()
    init_result = plugin.initialize()
    if not init_result.success:
        print_error(f"Failed to initialize tokenscope plugin: {init_result.error}",
                    exit_code=1)
        return

    # Get available tokenizers.
    available_tokenizers = plugin._tokenizers
    if not available_tokenizers:
        print_error("No tokenizers available", exit_code=1)
        return

    # Filter to the requested tokenizer if specified.
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

    # Create DataFrame with tokenization results.
    df = create_tokenization_dataframe(input_text, tokenizers_to_use)

    # Show token splitting diagram if requested.
    if split_diagram and tokenizer:
        console.print(display_token_splitting_diagram(
            input_text,
            tokenizers_to_use[tokenizer],
            console
        ))

    # Display tokenization visualization.
    if tokenizer:
        # Display single tokenizer visualization using the given technique.
        console.print(display_technique(
            df,
            tokenizer,
            technique,
            console
        ))
    else:
        # Display comparison of all tokenizers.
        console.print(display_token_comparison(
            df,
            list(tokenizers_to_use.keys()),
            console
        ))

    # Suggest optimizations if requested.
    if suggest_optimizations:
        console.print(suggest_token_optimizations(input_text, console))

    # Export visualization to a file if requested.
    if export:
        try:
            # Determine the parent directory using fs.split_path and fs.join_path.
            parts = fs.split_path(export)
            parent_dir = fs.join_path(*parts[:-1])
            # Ensure the parent directory exists.
            fs.create_directory(parent_dir, exist_ok=True)
            # Export the visualization text to the file.
            write_result = fs.write_text(export, console.export_text(), encoding="utf-8", atomic=True)
            if not write_result.success:
                print_error(f"Failed to export visualization: {write_result.error}")
                return
            print_success(f"Exported visualization to: {export}")
        except Exception as e:
            print_error(f"Failed to export visualization: {e}")
