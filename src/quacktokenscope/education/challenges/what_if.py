# src/quacktokenscope/education/challenges/what_if.py
"""
What-if analysis for text tokenization.

This module provides functionality to analyze how text modifications
affect tokenization and API costs.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple

from rich.console import Console
from rich.table import Table

from quacktokenscope.education.cost_calculator import calculate_cost

logger = logging.getLogger(__name__)

# Standard text modifications for what-if analysis
STANDARD_MODIFICATIONS = [
    ("Original", lambda text: text),
    ("Lowercase", lambda text: text.lower()),
    ("Remove punctuation", lambda text: re.sub(r'[^\w\s]', '', text)),
    ("Replace newlines with spaces", lambda text: text.replace("\n", " ")),
    ("Remove extra spaces", lambda text: re.sub(r'\s+', ' ', text).strip())
]


def run_what_if_analysis(
        text: str,
        tokenizer: Any,
        model: str = "gpt-4-turbo",
        console: Optional[Console] = None,
        custom_modifications: Optional[List[Tuple[str, callable]]] = None
) -> Dict[str, Any]:
    """
    Run a what-if analysis on text modifications.

    Args:
        text: The original text to analyze
        tokenizer: Tokenizer to use for analysis
        model: The model to use for cost calculation
        console: Optional console for display
        custom_modifications: Optional custom text modifications to analyze

    Returns:
        Analysis results including token counts and costs
    """
    if console is None:
        console = Console()

    # Use custom modifications if provided, otherwise use defaults
    modifications = custom_modifications if custom_modifications else STANDARD_MODIFICATIONS

    # Get original token count and cost
    original_tokens = len(tokenizer.tokenize(text)[0])
    original_cost = calculate_cost(original_tokens, model=model)["total_cost"]

    # Prepare results
    results = []

    # Analyze each modification
    for name, modifier in modifications:
        # Apply the modification
        modified_text = modifier(text)

        # Get token count and cost
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

        # Store result
        results.append({
            "name": name,
            "modified_text": modified_text,
            "tokens": tokens,
            "savings": savings,
            "savings_raw": token_diff,
            "savings_percent": token_percent,
            "cost": cost,
            "cost_diff": cost_diff
        })

    # Add a summary to the results
    has_savings = any(r["savings_raw"] > 0 for r in results if r["name"] != "Original")
    max_savings = max((r for r in results if r["name"] != "Original"),
                      key=lambda x: x["savings_raw"],
                      default={"name": "None", "savings_raw": 0})

    # Return the full analysis
    return {
        "original_text": text,
        "original_tokens": original_tokens,
        "original_cost": original_cost,
        "modifications": results,
        "has_savings": has_savings,
        "best_modification": max_savings["name"] if max_savings[
                                                        "savings_raw"] > 0 else "None",
        "max_token_savings": max_savings["savings_raw"],
        "max_cost_savings": max_savings["cost_diff"] if max_savings[
                                                            "savings_raw"] > 0 else 0
    }


def display_what_if_results(analysis: Dict[str, Any],
                            console: Optional[Console] = None) -> str:
    """
    Display what-if analysis results in a formatted table.

    Args:
        analysis: The analysis results from run_what_if_analysis
        console: Optional console for display

    Returns:
        Text representation of the displayed table
    """
    if console is None:
        console = Console(record=True)

    # Create the table
    table = Table(title="What If? Tokenization Scenarios")
    table.add_column("Scenario", style="cyan")
    table.add_column("Tokens", style="magenta")
    table.add_column("Savings", style="green")
    table.add_column("Cost", style="yellow")

    # Add rows for each modification
    for mod in analysis["modifications"]:
        table.add_row(
            mod["name"],
            str(mod["tokens"]),
            mod["savings"],
            f"${mod['cost']:.4f}"
        )

    # Display the table
    console.print(table)

    # Add some tips based on the analysis
    if analysis["has_savings"]:
        console.print(
            f"\n[green]💡 Tip:[/green] The '{analysis['best_modification']}' modification saves the most tokens!")
        console.print(
            f"     Maximum savings: {analysis['max_token_savings']} tokens (${analysis['max_cost_savings']:.6f})")
    else:
        console.print(
            "\n[yellow]Note:[/yellow] None of these simple modifications reduced the token count.")
        console.print(
            "     Try more complex optimizations like rewording or restructuring the content.")

    # Return the console output if recorded
    if hasattr(console, "export_text"):
        return console.export_text()
    return ""