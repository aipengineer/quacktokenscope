# src/quacktokenscope/education/cost_calculator.py
"""
API cost calculator module for QuackTokenScope.

This module provides functions for calculating and displaying the cost
of using tokens with various language model APIs.
"""

from typing import Any

from rich.console import Console
from rich.table import Table

from quackcore.logging import get_logger

logger = get_logger(__name__)

# Default pricing models (per 1K tokens)
DEFAULT_PRICING_MODELS = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "llama-3-70b": {"input": 0.0007, "output": 0.0007},
    "llama-3-8b": {"input": 0.0002, "output": 0.0002},
}


def get_pricing_models() -> dict[str, dict[str, float]]:
    """
    Get pricing models from configuration or use defaults.

    This function attempts to load pricing from QuackCore's configuration,
    or falls back to default values if not available.

    Returns:
        dictionary of pricing models
    """
    try:
        # Try to get pricing from QuackCore config
        from quacktokenscope.config import get_config
        config = get_config()

        # Check if pricing_models exists in the configuration
        if hasattr(config.custom, "get"):
            # dictionary-like access
            pricing_models = config.custom.get("pricing_models", {})
        elif hasattr(config.custom, "pricing_models"):
            # Attribute-based access
            pricing_models = config.custom.pricing_models
        else:
            pricing_models = {}

        # If we found valid pricing models, return them
        if pricing_models and isinstance(pricing_models, dict):
            return pricing_models

    except Exception as e:
        logger.debug(f"Could not load pricing models from config: {e}")

    # Fall back to default pricing models
    return DEFAULT_PRICING_MODELS


def calculate_cost(
        input_tokens: int,
        output_tokens: int = 0,
        model: str = "gpt-4-turbo"
) -> dict[str, Any]:
    """
    Calculate the cost for processing tokens.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens (default: 0)
        model: Model name to use for pricing

    Returns:
        dictionary with cost breakdown
    """
    pricing_models = get_pricing_models()

    if model not in pricing_models:
        logger.warning(f"Unknown model: {model}, falling back to gpt-4-turbo")
        model = "gpt-4-turbo"

    pricing = pricing_models[model]

    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    total_cost = input_cost + output_cost

    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
        "pricing_info": pricing
    }


def compare_models(
        input_tokens: int,
        output_tokens: int = 0
) -> dict[str, dict[str, Any]]:
    """
    Compare costs across different models.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        dictionary mapping model names to cost info
    """
    pricing_models = get_pricing_models()
    results = {}

    for model in pricing_models:
        results[model] = calculate_cost(
            input_tokens, output_tokens, model
        )

    return results


def calculate_efficiency_metrics(
        input_text: str,
        input_tokens: int
) -> dict[str, Any]:
    """
    Calculate tokenization efficiency metrics.

    Args:
        input_text: The original text
        input_tokens: Number of tokens used

    Returns:
        dictionary of efficiency metrics
    """
    # Characters per token (higher is more efficient)
    chars_per_token = len(input_text) / input_tokens if input_tokens > 0 else 0

    # English benchmarks (approximate)
    avg_benchmark = 4.0  # Average English text
    good_benchmark = 5.0  # Efficient tokenization

    # Determine efficiency rating
    if chars_per_token >= good_benchmark:
        rating = "Excellent"
        emoji = "🌟"
    elif chars_per_token >= avg_benchmark:
        rating = "Good"
        emoji = "✓"
    else:
        rating = "Could be improved"
        emoji = "💡"

    return {
        "chars_per_token": chars_per_token,
        "efficiency_rating": rating,
        "emoji": emoji,
        "benchmark_avg": avg_benchmark,
        "benchmark_good": good_benchmark
    }


def display_cost_context(
        cost: float,
        console: Console | None = None
) -> str:
    """
    Add real-world context to the calculated API cost.

    Args:
        cost: The calculated cost
        console: Optional Rich console to use

    Returns:
        Text output of the displayed context
    """
    if console is None:
        console = Console(record=True)

    # Define some reference points
    references = [
        (0.00001, "less than a grain of sand"),
        (0.0001, "less than a sip of water"),
        (0.001, "less than sending a text message"),
        (0.01, "about the cost of a sheet of paper"),
        (0.05, "roughly the cost of an email"),
        (0.10, "about the cost of a sticky note"),
        (0.25, "the cost of a short phone call"),
        (1.00, "approximately the cost of a cup of coffee"),
        (5.00, "about the cost of a fast food meal"),
        (10.00, "the cost of a movie ticket")
    ]

    # Find the closest reference point
    closest = min(references, key=lambda x: abs(x[0] - cost))

    if cost <= closest[0]:
        console.print(f"\n[italic]This costs {closest[1]}.[/italic]")
    else:
        console.print(f"\n[italic]This costs more than {closest[1]}.[/italic]")

    # Add practical usage context
    if cost < 0.001:
        console.print(
            "[green]💰 This is extremely economical for production use.[/green]")
    elif cost < 0.01:
        console.print("[green]💰 This is very economical for production use.[/green]")
    elif cost < 0.10:
        console.print(
            "[cyan]💰 This is suitable for regular API calls in production.[/cyan]")
    elif cost < 1.00:
        console.print(
            "[yellow]💰 Consider optimizing for high-volume production use.[/yellow]")
    else:
        console.print("[red]💰 This would be expensive for frequent API calls.[/red]")

    # Return the console output if recorded
    if hasattr(console, "export_text"):
        return console.export_text()
    return ""


def display_cost_summary(
        input_text: str,
        input_tokens: int,
        output_tokens: int = 0,
        model: str = "gpt-4-turbo",
        console: Console | None = None
) -> str:
    """
    Display a formatted API cost summary.

    Args:
        input_text: The original input text
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name to use for pricing
        console: Optional Rich console to use

    Returns:
        Text output of the displayed summary
    """
    if console is None:
        console = Console(record=True)

    # Calculate cost
    cost_info = calculate_cost(input_tokens, output_tokens, model)

    # Create a panel for the cost summary
    console.print("\n")

    # Main cost table
    table = Table(title="API Cost Summary")
    table.add_column("Item", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Model", cost_info["model"])
    table.add_row("Input Tokens", f"{cost_info['input_tokens']:,}")
    table.add_row("Output Tokens", f"{cost_info['output_tokens']:,}")
    table.add_row("Input Cost", f"${cost_info['input_cost']:.4f}")
    table.add_row("Output Cost", f"${cost_info['output_cost']:.4f}")
    table.add_row("Total Cost", f"${cost_info['total_cost']:.4f}")

    console.print(table)

    # Add efficiency metrics
    efficiency = calculate_efficiency_metrics(input_text, input_tokens)

    # Efficiency table
    efficiency_table = Table(title="Tokenization Efficiency")
    efficiency_table.add_column("Metric", style="cyan")
    efficiency_table.add_column("Value", style="green")

    efficiency_table.add_row("Characters per token",
                             f"{efficiency['chars_per_token']:.2f}")
    efficiency_table.add_row("Efficiency rating",
                             f"{efficiency['emoji']} {efficiency['efficiency_rating']}")
    efficiency_table.add_row("Average benchmark",
                             f"{efficiency['benchmark_avg']} chars/token")
    efficiency_table.add_row("Good benchmark",
                             f"{efficiency['benchmark_good']} chars/token")

    console.print(efficiency_table)

    # If efficiency could be improved, offer a tip
    if efficiency['efficiency_rating'] == "Could be improved":
        console.print(
            "\n[yellow]Efficiency Tip:[/yellow] Try reducing special characters and formatting to lower token count.")

    # Add real-world cost context
    display_cost_context(cost_info['total_cost'], console)

    # Add a fun message
    console.print(
        f"\n[bold green]Your tokens cost: ${cost_info['total_cost']:.4f}[/bold green] - every token counts! 🦆")

    # Return the console output if recorded
    if hasattr(console, "export_text"):
        return console.export_text()
    return ""


def display_what_if_scenarios(
        text: str,
        tokenizer: Any,
        model: str = "gpt-4-turbo",
        console: Console | None = None
) -> str:
    """
    Show how text modifications affect token count and cost.

    Args:
        text: The original text
        tokenizer: Tokenizer to use for analysis
        model: The model to use for cost calculation
        console: Optional Rich console to use

    Returns:
        Text output of the displayed scenarios
    """
    import re

    if console is None:
        console = Console(record=True)

    scenarios = [
        ("Original", text),
        ("Lowercase", text.lower()),
        ("Remove punctuation", re.sub(r'[^\w\s]', '', text)),
        ("Replace newlines with spaces", text.replace("\n", " ")),
        ("Remove extra spaces", re.sub(r'\s+', ' ', text).strip())
    ]

    table = Table(title="What If? Tokenization Scenarios")
    table.add_column("Scenario", style="cyan")
    table.add_column("Tokens", style="magenta")
    table.add_column("Savings", style="green")
    table.add_column("Cost", style="yellow")

    # Get original token count
    original_tokens = len(tokenizer.tokenize(text)[0])
    original_cost = calculate_cost(original_tokens, model=model)["total_cost"]

    for name, modified_text in scenarios:
        tokens = len(tokenizer.tokenize(modified_text)[0])
        cost = calculate_cost(tokens, model=model)["total_cost"]

        # Calculate savings
        token_diff = original_tokens - tokens
        token_percent = (
                    token_diff / original_tokens * 100) if original_tokens > 0 else 0
        cost_diff = original_cost - cost

        # Format savings
        if name == "Original":
            savings = "—"
        elif token_diff > 0:
            savings = f"-{token_diff} tokens ({token_percent:.1f}%)"
        elif token_diff < 0:
            savings = f"+{abs(token_diff)} tokens ({abs(token_percent):.1f}%)"
        else:
            savings = "No change"

        table.add_row(name, str(tokens), savings, f"${cost:.4f}")

    console.print(table)

    # Additional tips
    if any(len(tokenizer.tokenize(s[1])[0]) < original_tokens for s in scenarios[1:]):
        console.print(
            "\n[green]💡 Tip:[/green] Some of these modifications reduce token count and cost!")
    else:
        console.print(
            "\n[yellow]Note:[/yellow] None of these simple modifications reduced the token count.")

    # Return the console output if recorded
    if hasattr(console, "export_text"):
        return console.export_text()
    return ""