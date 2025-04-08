# src/quacktokenscope/education/cli/calculate_cost.py
"""
CLI handler for the cost calculator command.

This module contains the handler function for the cost calculator CLI command.
"""

import click
from quackcore.cli import print_error, print_info
from rich.console import Console
from rich.table import Table

from quacktokenscope import get_logger
from quacktokenscope.plugins.token_scope import TokenScopePlugin
from quacktokenscope.education.cost_calculator import (
    display_cost_summary,
    compare_models,
)
from quacktokenscope.education.challenges.what_if import (
    run_what_if_analysis,
    display_what_if_results,
)
# Use the quackcore.fs service for filesystem operations.
from quackcore.fs import service as fs

logger = get_logger(__name__)


def handle_calculate_cost_command(
    ctx: click.Context,
    input_text: str,
    model: str = "gpt-4-turbo",
    output_tokens: int = 0,
    tokenizer: str = "tiktoken",
    what_if: bool = False,
    compare_models_flag: bool = False,
) -> None:
    """
    Handle the cost calculator command.

    Args:
        ctx: The Click context
        input_text: The text to calculate costs for
        model: The model to use for cost calculation
        output_tokens: Number of output tokens to include
        tokenizer: Tokenizer to use for counting tokens
        what_if: Whether to show what-if scenarios
        compare_models_flag: Whether to compare costs across models
    """
    console = Console()

    # Check if the provided input_text represents a file path.
    # We preserve the original input as file_path.
    file_path = input_text
    file_info = fs.get_file_info(file_path)
    if file_info.success and file_info.exists and file_info.is_file:
        read_result = fs.read_text(file_path, encoding="utf-8")
        if not read_result.success:
            print_error(f"Failed to read file: {read_result.error}", exit_code=1)
            return
        input_text = read_result.content
        print_info(f"Read input from file: {file_path}")

    # Create and initialize the token scope plugin to get tokenizers.
    plugin = TokenScopePlugin()
    init_result = plugin.initialize()
    if not init_result.success:
        print_error(
            f"Failed to initialize tokenscope plugin: {init_result.error}",
            exit_code=1
        )
        return

    # Get available tokenizers.
    available_tokenizers = plugin._tokenizers
    if tokenizer not in available_tokenizers:
        print_error(
            f"Tokenizer '{tokenizer}' not found. Available tokenizers: "
            f"{', '.join(available_tokenizers.keys())}",
            exit_code=1
        )
        return

    # Get token count.
    tokenizer_instance = available_tokenizers[tokenizer]
    input_tokens = len(tokenizer_instance.tokenize(input_text)[0])

    # Show basic cost calculation.
    console.print(
        display_cost_summary(
            input_text,
            input_tokens,
            output_tokens,
            model,
            console
        )
    )

    # Show what-if scenarios if requested.
    if what_if:
        analysis = run_what_if_analysis(
            input_text,
            tokenizer_instance,
            model,
        )
        console.print(display_what_if_results(analysis, console))

    # Compare models if requested.
    if compare_models_flag:
        results = compare_models(input_tokens, output_tokens)

        table = Table(title="Model Cost Comparison")
        table.add_column("Model", style="cyan")
        table.add_column("Total Cost", style="green")
        table.add_column("Input Cost", style="yellow")
        table.add_column("Output Cost", style="yellow")

        for model_name, cost_info in sorted(
            results.items(), key=lambda x: x[1]["total_cost"]
        ):
            table.add_row(
                model_name,
                f"${cost_info['total_cost']:.6f}",
                f"${cost_info['input_cost']:.6f}",
                f"${cost_info['output_cost']:.6f}"
            )

        console.print(table)
