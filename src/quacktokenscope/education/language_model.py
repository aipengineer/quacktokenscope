# src/quacktokenscope/education/language_model.py
"""
Simple language model simulation for educational purposes.

This module provides a simple n-gram language model implementation
to demonstrate how tokenization affects language modeling.
"""

from collections import Counter, defaultdict
from typing import Any

from quacktokenscope import get_logger
from quacktokenscope.utils.tokenizers.base import BaseTokenizer

logger = get_logger(__name__)


class SimpleLanguageModel:
    """
    Simple n-gram language model to demonstrate basic language modeling concepts.

    This model is for educational purposes only and shows how tokenization
    affects the quality of language model predictions.
    """

    def __init__(
            self,
            tokenizer: BaseTokenizer,
            n: int = 2,
            name: str = "Quack-GPT-16bit"
    ):
        """
        Initialize an n-gram model with a specific tokenizer.

        Args:
            tokenizer: A tokenizer implementing the TokenizerProtocol
            n: The n-gram size (default: 2 for bigram)
            name: Name of the model (for display purposes)
        """
        self.tokenizer = tokenizer
        self.n = n
        self.name = name
        self.ngram_counts = defaultdict(Counter)
        self.token_counts = Counter()
        self._initialized = False

    def train(self, text: str) -> None:
        """
        Train the model on input text.

        Args:
            text: The text to train on
        """
        # Tokenize the text
        token_ids, token_strs = self.tokenizer.tokenize(text)

        # Build n-gram frequencies
        for i in range(len(token_ids) - self.n + 1):
            # Create context (n-1 tokens) and target token
            context = tuple(token_ids[i:i + self.n - 1])
            target = token_ids[i + self.n - 1]

            # Count the frequency of this target given the context
            self.ngram_counts[context][target] += 1

            # Also count individual tokens for unigram fallback
            for j in range(self.n):
                if i + j < len(token_ids):
                    self.token_counts[token_ids[i + j]] += 1

        self._initialized = True
        logger.info(
            f"Trained {self.name} with {len(token_ids)} tokens, {len(self.ngram_counts)} contexts")

    def predict_next(
            self,
            context: str,
            num_predictions: int = 5,
            temperature: float = 1.0
    ) -> list[tuple[str, float]]:
        """
        Predict the next token given a context.

        Args:
            context: Text context for prediction
            num_predictions: Number of top predictions to return
            temperature: Temperature for prediction (higher = more random)

        Returns:
            list of (token_str, probability) tuples
        """
        if not self._initialized:
            raise RuntimeError("Model not trained")

        # Tokenize the context
        context_ids, _ = self.tokenizer.tokenize(context)

        # If context is shorter than n-1, pad with zeros
        while len(context_ids) < self.n - 1:
            context_ids = [0] + context_ids

        # Get the last n-1 tokens as our context
        context_ids = tuple(context_ids[-(self.n - 1):])

        # Count the frequency of each next token after this context
        next_token_counts = self.ngram_counts[context_ids]
        total_count = sum(next_token_counts.values())

        # If we have no matches, fall back to unigram probabilities
        if total_count == 0:
            next_token_counts = self.token_counts
            total_count = sum(self.token_counts.values())

            if total_count == 0:
                logger.warning("No token counts available for prediction")
                return []

        # Convert counts to probabilities with temperature
        predictions = []
        for token_id, count in next_token_counts.items():
            # Apply temperature scaling
            if temperature != 1.0:
                # Higher temperature = more uniform distribution
                # Lower temperature = more peaked distribution
                prob = (count / total_count) ** (1.0 / max(0.1, temperature))
            else:
                prob = count / total_count

            token_str = self.tokenizer.decode([token_id])
            predictions.append((token_str, prob))

        # Normalize probabilities after temperature scaling
        if temperature != 1.0 and predictions:
            total_prob = sum(p[1] for p in predictions)
            predictions = [(t, p / total_prob) for t, p in predictions]

        # Return top predictions
        return sorted(predictions, key=lambda x: x[1], reverse=True)[:num_predictions]

    def generate_text(
            self,
            prompt: str,
            max_tokens: int = 20,
            temperature: float = 1.0,
            stop_tokens: list[str] | None = None
    ) -> str:
        """
        Generate text by repeatedly predicting the next token.

        Args:
            prompt: Starting text
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for prediction randomness
            stop_tokens: Optional list of tokens that stop generation

        Returns:
            Generated text starting with the prompt
        """
        if not self._initialized:
            raise RuntimeError("Model not trained")

        # Initialize with the prompt
        context = prompt
        generated_text = prompt

        # Set default stop tokens if none provided
        if stop_tokens is None:
            stop_tokens = ["\n\n", "###", "```"]

        # Generate text token by token
        import random
        for _ in range(max_tokens):
            # Get next token predictions
            predictions = self.predict_next(context, temperature=temperature)

            # If no predictions, stop generation
            if not predictions:
                break

            # Sample next token based on probabilities
            # This is a simple implementation - real models use more sophisticated sampling
            if temperature > 0.1:
                # Weighted random selection
                weights = [p[1] for p in predictions]
                next_token = \
                random.choices([p[0] for p in predictions], weights=weights, k=1)[0]
            else:
                # Greedy selection (always pick highest probability)
                next_token = predictions[0][0]

            # Append token to generated text
            generated_text += next_token

            # Update context for next prediction (sliding window)
            context = generated_text[-100:]  # Limit context length

            # Check for stop tokens
            if any(stop_token in generated_text[-len(stop_token) * 2:] for stop_token in
                   stop_tokens):
                break

        return generated_text


def compare_tokenizer_predictions(
        prompt: str,
        text_corpus: str,
        tokenizers: dict[str, BaseTokenizer],
        n: int = 2,
        num_predictions: int = 3
) -> dict[str, list[tuple[str, float]]]:
    """
    Compare next-token predictions using different tokenizers.

    Args:
        prompt: The prompt to predict from
        text_corpus: The training text
        tokenizers: Dictionary of tokenizers to compare
        n: n-gram size
        num_predictions: Number of predictions to return for each tokenizer

    Returns:
        Dictionary mapping tokenizer names to prediction lists
    """
    results = {}

    for name, tokenizer in tokenizers.items():
        try:
            # Train a simple model with this tokenizer
            model = SimpleLanguageModel(tokenizer, n=n, name=f"Quack-{name}")
            model.train(text_corpus)

            # Get predictions
            predictions = model.predict_next(prompt, num_predictions=num_predictions)
            results[name] = predictions

        except Exception as e:
            logger.error(f"Error with tokenizer {name}: {e}")
            results[name] = []

    return results


def display_tokenizer_predictions(
        prompt: str,
        predictions: dict[str, list[tuple[str, float]]],
        console: Any | None = None
) -> str:
    """
    Display predictions from multiple tokenizers in a formatted table.

    Args:
        prompt: The prompt that was used
        predictions: Dictionary mapping tokenizer names to prediction lists
        console: Optional Rich console to use

    Returns:
        Text representation of the displayed predictions
    """
    from rich.console import Console
    from rich.table import Table

    if console is None:
        console = Console(record=True)

    console.print(f"[bold]Prompt:[/bold] {prompt}")

    table = Table(title="Next Token Predictions by Tokenizer")
    table.add_column("Tokenizer", style="cyan")

    # Find the maximum number of predictions
    max_preds = max(len(preds) for preds in predictions.values()) if predictions else 0

    # Add columns for each prediction rank
    for i in range(max_preds):
        table.add_column(f"Prediction {i + 1}", style="green")
        table.add_column(f"Probability {i + 1}", style="yellow")

    # Add rows for each tokenizer
    for tokenizer_name, preds in predictions.items():
        row = [tokenizer_name]

        for i in range(max_preds):
            if i < len(preds):
                token, prob = preds[i]
                row.extend([f"'{token}'", f"{prob:.2%}"])
            else:
                row.extend(["—", "—"])

        table.add_row(*row)

    console.print(table)

    # Add some educational context
    console.print("\n[bold]Why predictions differ:[/bold]")
    console.print(
        "Different tokenizers split text in different ways, affecting what the model learns.")
    console.print(
        "A tokenizer that produces fewer, more meaningful tokens often leads to better predictions.")

    # Return the console output if recorded
    if hasattr(console, "export_text"):
        return console.export_text()
    return ""


def display_text_generation(
        prompt: str,
        model: SimpleLanguageModel,
        console: Any | None = None
) -> str:
    """
    Display text generation from a simple language model.

    Args:
        prompt: The starting text
        model: The language model to use
        console: Optional Rich console to use

    Returns:
        Text representation of the generation process
    """
    from rich.console import Console
    from rich.panel import Panel

    if console is None:
        console = Console(record=True)

    console.print(f"[bold]Text Generation with {model.name}[/bold]")
    console.print(f"Using {model.tokenizer.name} tokenizer, {model.n}-gram model")

    # Generate with different temperatures
    temps = [0.5, 1.0, 1.5]

    for temp in temps:
        generated = model.generate_text(prompt, temperature=temp, max_tokens=20)

        # Highlight the prompt vs generated text
        formatted_text = prompt + generated[len(prompt):]
        prompt_end = len(prompt)

        displayed_text = f"[bold cyan]{formatted_text[:prompt_end]}[/bold cyan][green]{formatted_text[prompt_end:]}[/green]"

        console.print(Panel(
            displayed_text,
            title=f"Temperature: {temp}",
            subtitle="Bold = prompt, Green = generated"
        ))

    # Educational explanation
    console.print("\n[bold]About Temperature:[/bold]")
    console.print(
        "• [cyan]Lower temperature[/cyan] (0.5): More focused, deterministic text")
    console.print(
        "• [cyan]Medium temperature[/cyan] (1.0): Balanced creativity and coherence")
    console.print(
        "• [cyan]Higher temperature[/cyan] (1.5): More random, creative, and diverse")

    # Limitations of n-gram models
    console.print("\n[bold yellow]Educational Note:[/bold yellow]")
    console.print(
        "This is a simple n-gram language model for educational purposes only.")
    console.print(
        "Real LLMs use neural networks and transformers that capture much more context.")
    console.print(
        "But the fundamental concept remains: a LLM predicts the next token based on previous tokens.")

    # Return the console output if recorded
    if hasattr(console, "export_text"):
        return console.export_text()
    return ""