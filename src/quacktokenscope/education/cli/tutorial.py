# src/quacktokenscope/education/cli/tutorial.py
"""
CLI handler for the tutorial command.

This module contains the handler function for the tutorial CLI command.
"""


import click
from quackcore.cli import print_error, print_info
from rich.console import Console

from quacktokenscope.plugins.token_scope import TokenScopePlugin
from quacktokenscope.education.tutorial import TUTORIAL_UNITS
from quackcore.logging import get_logger

logger = get_logger(__name__)


def handle_tutorial_command(ctx: click.Context, unit: int) -> None:
    """
    Handle the tutorial command.

    Args:
        ctx: The Click context
        unit: The tutorial unit number to run
    """
    console = Console()

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

    console.print("\n[bold]🎓 Welcome to the QuackTokenScope Tutorial![/bold]")

    # Check if the requested unit exists
    if unit in TUTORIAL_UNITS:
        # Create and run the tutorial unit
        tutorial_class = TUTORIAL_UNITS[unit]
        tutorial = tutorial_class(available_tokenizers, console)

        logger.info(f"Running tutorial unit {unit}: {tutorial.title}")
        tutorial.run()
    else:
        # List available units
        console.print(
            f"\n[yellow]Tutorial unit {unit} not found. Available units: 1-{len(TUTORIAL_UNITS)}[/yellow]")
        console.print("Please choose a unit number from the following:")

        for unit_num, tutorial_class in TUTORIAL_UNITS.items():
            console.print(f"{unit_num}. {tutorial_class.title}")