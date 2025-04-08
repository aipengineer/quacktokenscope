# src/quacktokenscope/education/cli/language_model.py
"""
CLI handler for the language model command.

This module contains the handler function for the language model CLI command.
"""

from pathlib import Path

import click
from quackcore.cli import print_error, print_info
from rich.console import Console

from quacktokenscope import get_logger
from quacktokenscope.plugins.token_scope import TokenScopePlugin
from quacktokenscope.education.language_model import (
    SimpleLanguageModel,
    compare_tokenizer_predictions,
    display_tokenizer_predictions,
    display_text_generation,
)

logger = get_logger(__name__)


def handle_language_model_command(
        ctx: click.Context,
        input_text: str,
        train: str | None = None,
        tokenizer: str = "tiktoken",
        ngram: int = 2,
        predict_only: bool = False,
        compare_tokenizers: bool = False,
) -> None:
    """
    Handle the language model command.

    Args:
        ctx: The Click context
        input_text: The input text (prompt) for the model
        train: Text corpus to train the model on
        tokenizer: Tokenizer to use
        ngram: N-gram size (2 for bigram, etc.)
        predict_only: Only show predictions, not text generation
        compare_tokenizers: Compare predictions with different tokenizers
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

    # Check if training corpus is a file path
    training_text = ""
    if train:
        train_path = Path(train)
        if train_path.exists() and train_path.is_file():
            try:
                with open(train_path, "r", encoding="utf-8") as f:
                    training_text = f.read()
                print_info(f"Read training corpus from file: {train_path}")
            except Exception as e:
                print_error(f"Failed to read training file: {e}", exit_code=1)
                return
        else:
            training_text = train
    else:
        # Default training corpus
        training_text = """
        The quick brown fox jumps over the lazy dog. The dog sleeps peacefully under the tree.
        Tokenization is the process of splitting text into tokens. Tokens are the building blocks of language models.
        Different tokenizers use different strategies to split text. Some use whitespace, others use subword units.
        Understanding tokenization helps optimize prompts and reduce API costs for large language models.
        """
        print_info("Using default training corpus")

    # Create and initialize the token scope plugin to get tokenizers
    plugin = TokenScopePlugin()
    init_result = plugin.initialize()

    if not init_result.success:
        print_error(f"Failed to initialize tokenscope plugin: {init_result.error}",
                    exit_code=1)
        return

    # Get available tokenizers
    available_tokenizers = plugin._tokenizers

    if tokenizer not in available_tokenizers:
        print_error(
            f"Tokenizer '{tokenizer}' not found. Available tokenizers: {', '.join(available_tokenizers.keys())}",
            exit_code=1)
        return

    # Compare different tokenizers if requested
    if compare_tokenizers:
        predictions = compare_tokenizer_predictions(
            input_text,
            training_text,
            available_tokenizers,
            n=ngram
        )

        console.print(display_tokenizer_predictions(
            input_text,
            predictions,
            console
        ))
    else:
        # Use a single tokenizer
        tokenizer_instance = available_tokenizers[tokenizer]

        # Create and train the model
        model = SimpleLanguageModel(
            tokenizer_instance,
            n=ngram,
            name=f"Quack-{tokenizer.capitalize()}-{ngram}gram"
        )

        model.train(training_text)

        # Show next token predictions
        predictions = model.predict_next(input_text, num_predictions=5)

        console.print(f"[bold]Input:[/bold] {input_text}")
        console.print(
            f"[bold]Model:[/bold] {model.name} ({ngram}-gram using {tokenizer})")

        console.print("\n[bold]Top 5 next token predictions:[/bold]")
        for i, (token, prob) in enumerate(predictions):
            console.print(f"{i + 1}. '{token}' ({prob:.2%})")

        # Show text generation unless predict-only flag is set
        if not predict_only:
            console.print(display_text_generation(
                input_text,
                model,
                console
            ))