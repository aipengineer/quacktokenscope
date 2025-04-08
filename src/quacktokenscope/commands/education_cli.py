# src/quacktokenscope/commands/education_cli.py
"""
CLI commands for educational features in QuackTokenScope.

This module provides CLI commands for the educational tools in QuackTokenScope,
including visualization, cost calculation, and language model simulation.
"""

import click
from quackcore.cli import handle_errors

from quacktokenscope.education.cli.visualize import handle_visualize_command
from quacktokenscope.education.cli.calculate_cost import handle_calculate_cost_command
from quacktokenscope.education.cli.challenge import handle_challenge_command
from quacktokenscope.education.cli.language_model import handle_language_model_command
from quacktokenscope.education.cli.tutorial import handle_tutorial_command


@click.group(name="edu")
def education_cli():
    """
    Educational tools for learning about tokenization.

    This command group provides interactive tools for exploring
    tokenization concepts, API costs, and language model basics.
    """
    pass


@education_cli.command("visualize")
@click.argument("input_text", type=str)
@click.option(
    "--technique",
    type=str,
    default="Default",
    help="Tokenization technique to display (Default, Greedy, etc.)",
)
@click.option(
    "--tokenizer",
    type=str,
    default=None,
    help="Tokenizer to use (tiktoken, huggingface, etc.). Shows all if not specified.",
)
@click.option(
    "--split-diagram",
    is_flag=True,
    help="Show token splitting diagram",
)
@click.option(
    "--suggest-optimizations",
    is_flag=True,
    help="Suggest ways to optimize token usage",
)
@click.option(
    "--export",
    type=str,
    default=None,
    help="Export visualization to a text file",
)
@click.pass_context
@handle_errors(exit_code=1)
def visualize_command(ctx, **kwargs):
    """
    Visualize how text is tokenized by different tokenizers.

    Examples:
        quacktool tokenscope edu visualize "Hello, world!"
        quacktool tokenscope edu visualize "Hello, world!" --tokenizer tiktoken
        quacktool tokenscope edu visualize "Hello, world!" --split-diagram
    """
    handle_visualize_command(ctx, **kwargs)


@education_cli.command("calculate-cost")
@click.argument("input_text", type=str)
@click.option(
    "--model",
    type=str,
    default="gpt-4-turbo",
    help="Model to calculate costs for",
)
@click.option(
    "--output-tokens",
    type=int,
    default=0,
    help="Number of output tokens to include in calculation",
)
@click.option(
    "--tokenizer",
    type=str,
    default="tiktoken",
    help="Tokenizer to use for counting input tokens",
)
@click.option(
    "--what-if",
    is_flag=True,
    help="Show 'What If' scenarios for token optimization",
)
@click.option(
    "--compare-models",
    is_flag=True,
    help="Compare costs across different models",
)
@click.pass_context
@handle_errors(exit_code=1)
def calculate_cost_command(ctx, **kwargs):
    """
    Calculate API costs for text based on token count.

    Examples:
        quacktool tokenscope edu calculate-cost "Hello, world!"
        quacktool tokenscope edu calculate-cost "Hello, world!" --model gpt-3.5-turbo
        quacktool tokenscope edu calculate-cost "Hello, world!" --what-if
    """
    handle_calculate_cost_command(ctx, **kwargs)


@education_cli.command("challenge")
@click.pass_context
@handle_errors(exit_code=1)
def token_challenge_command(ctx):
    """
    Interactive token guessing challenge game.

    This command presents challenges to test your understanding of tokenization.

    Examples:
        quacktool tokenscope edu challenge
    """
    handle_challenge_command(ctx)


@education_cli.command("language-model")
@click.argument("input_text", type=str)
@click.option(
    "--train",
    type=str,
    help="Text corpus to train the model on",
)
@click.option(
    "--tokenizer",
    type=str,
    default="tiktoken",
    help="Tokenizer to use",
)
@click.option(
    "--ngram",
    type=int,
    default=2,
    help="N-gram size (2 for bigram, 3 for trigram, etc.)",
)
@click.option(
    "--predict-only",
    is_flag=True,
    help="Only show next token predictions, not text generation",
)
@click.option(
    "--compare-tokenizers",
    is_flag=True,
    help="Compare predictions using different tokenizers",
)
@click.pass_context
@handle_errors(exit_code=1)
def language_model_command(ctx, **kwargs):
    """
    Simulate a simple language model to demonstrate tokenization effects.

    Examples:
        quacktool tokenscope edu language-model "Hello" --train "Hello world. Hello there."
        quacktool tokenscope edu language-model "To be" --train hamlet.txt
        quacktool tokenscope edu language-model "Once upon" --train fairytales.txt --compare-tokenizers
    """
    handle_language_model_command(ctx, **kwargs)


@education_cli.command("tutorial")
@click.option(
    "--unit",
    type=int,
    default=1,
    help="Tutorial unit number (1-8)",
)
@click.pass_context
@handle_errors(exit_code=1)
def tutorial_command(ctx, unit):
    """
    Start an interactive tutorial session.

    This command launches guided tutorials that correspond to
    the units in the tokenization learning path.

    Examples:
        quacktool tokenscope edu tutorial --unit 1
    """
    handle_tutorial_command(ctx, unit)