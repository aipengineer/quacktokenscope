# src/quacktokenscope/education/cli/challenge.py
"""
CLI handler for the token challenge command.

This module contains the handler function for the token challenge CLI command.
"""

import logging

import click
from quackcore.cli import print_error, print_info
from rich.console import Console
from rich.prompt import Prompt

from quacktokenscope.plugins.token_scope import TokenScopePlugin
from quacktokenscope.education.challenges.token_challenge import (
    run_challenge, EDUCATIONAL_INSIGHTS
)

logger = logging.getLogger(__name__)


def handle_challenge_command(ctx: click.Context) -> None:
    """
    Handle the token challenge command.

    Args:
        ctx: The Click context
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

    # Introduction message
    print_info("🏆 Welcome to the TokenScope Challenge! 🏆")
    print_info("Test your knowledge of how different tokenizers handle text.")

    # Game state
    score = 0

    # Run the challenges
    challenge_data = run_challenge(available_tokenizers, console)

    # Process each challenge with user interaction
    for i, challenge in enumerate(challenge_data["challenges"]):
        results = challenge["guild_data"]

        console.print(
            f"\n[bold cyan]Challenge {i + 1}/{len(challenge_data['challenges'])}:[/bold cyan]")

        # Display the text to tokenize
        console.print(f"\n[bold]Text to tokenize:[/bold] {challenge['text']}")

        # Ask for user's guess
        available_options = list(results["guilds"].keys())
        options_text = "\n".join(
            [f"{key}: {guild['name']}" for key, guild in results["guilds"].items()])

        console.print(
            f"\n[bold yellow]Which guild's tokenizer will use the FEWEST tokens?[/bold yellow]")
        console.print(f"\n{options_text}")

        user_guess = Prompt.ask("Your prediction", choices=available_options)

        # Check if the user was correct
        correct = (user_guess == results["winner_key"])

        if correct:
            score += 1
            console.print(f"\n[bold green]🎉 Correct! +1 point[/bold green]")
        else:
            console.print(
                f"\n[bold red]Not quite! The winner was {results['winner_name']}[/bold red]")

        # Show token counts
        console.print(f"\n[bold]Token counts:[/bold]")
        for key, count in results["token_counts"].items():
            guild_name = results["guilds"][key]["name"]
            if key == results["winner_key"]:
                console.print(f"[green]{guild_name}: {count} tokens ⭐[/green]")
            else:
                console.print(f"{guild_name}: {count} tokens")

        # Educational insight
        console.print(f"\n[italic]{challenge['insight']}[/italic]")

        # Continue prompt between challenges
        if i < len(challenge_data["challenges"]) - 1:
            Prompt.ask("\nPress Enter for next challenge", default="")

    # Final score
    console.print(
        f"\n[bold]🏆 Final Score: {score}/{len(challenge_data['challenges'])}[/bold]")

    if score == len(challenge_data["challenges"]):
        console.print("[bold green]Perfect score! You're a TokenMaster! 👑[/bold green]")
    elif score >= len(challenge_data["challenges"]) * 0.7:
        console.print(
            "[bold green]Great job! You have a solid understanding of tokenization! 🌟[/bold green]")
    elif score >= len(challenge_data["challenges"]) * 0.4:
        console.print(
            "[bold yellow]Good effort! Keep learning about tokenization! 📚[/bold yellow]")
    else:
        console.print(
            "[bold yellow]Tokenization can be tricky! Try again after learning more! 🔍[/bold yellow]")

    # Educational summary
    console.print("\n[bold]Key Tokenization Takeaways:[/bold]")
    console.print(
        "• Different tokenizers split text differently based on their training")
    console.print(
        "• Special characters, URLs, and rare terms often increase token count")
    console.print("• Modern tokenizers like tiktoken are optimized for efficiency")
    console.print(
        "• Understanding tokenization helps optimize prompts and reduce costs")