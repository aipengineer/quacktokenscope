# src/quacktokenscope/education/visualization.py
"""
Interactive tokenization visualization module for QuackTokenScope.

This module provides functions for visualizing token comparisons
between different tokenizers in a rich, educational format.
"""

import re
from typing import Any

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from quackcore.logging import get_logger
from quacktokenscope.utils.tokenizers.base import BaseTokenizer

logger = get_logger(__name__)

# Tokenizer guilds information for educational context
TOKENIZER_GUILDS = {
    "tiktoken": {
        "name": "Neural Precision Guild",
        "emoji": "🧠",
        "description": "OpenAI's tokenizer optimized for modern LLMs",
    },
    "huggingface": {
        "name": "Legacy Lexicon Guild",
        "emoji": "📚",
        "description": "Widely used in research models and transformers",
    },
    "sentencepiece": {
        "name": "Statistical Fragmentation Guild",
        "emoji": "🧬",
        "description": "Language-agnostic approach with statistical methods",
    },
    "mock": {
        "name": "Testing Guild",
        "emoji": "🧪",
        "description": "Used for testing and educational demonstrations",
    },
}

# Technique explanations
TECHNIQUE_EXPLANATIONS = {
    "Greedy": "Uses a greedy algorithm that selects the longest possible token at each step",
    "Beam": "Uses beam search to explore multiple tokenization paths",
    "Default": "Uses the tokenizer's default strategy",
}

# Default mapping of tokenizers to their techniques
# This could be extended in the future as more techniques are added
TOKENIZER_TECHNIQUES = {
    "tiktoken": ["Default"],
    "huggingface": ["Default"],
    "sentencepiece": ["Default"],
    "mock": ["Default"],
}


def get_random_token_fact() -> str:
    """
    Returns a random educational fact about tokenization.

    Returns:
        A string containing a random tokenization fact
    """
    facts = [
        "Tokens often split at punctuation and whitespace boundaries.",
        "Most modern tokenizers encode frequent words as single tokens.",
        "Rare words typically get split into multiple subword tokens.",
        "Numbers are often tokenized digit by digit, increasing token count.",
        "Common prefixes and suffixes often become their own tokens.",
        "Uppercase words typically use different tokens than lowercase ones.",
        "HTML tags and code snippets often require more tokens than regular text.",
        "The tokenizer's vocabulary size directly impacts compression efficiency.",
        "Early tokenization simply split text on whitespace, treating each word as a token.",
        "Modern tokenizers use subword techniques like BPE (Byte-Pair Encoding).",
        "BPE starts with characters and merges the most frequent pairs iteratively.",
        "Unicode characters like emojis can consume multiple tokens.",
        "Some tokenizers handle whitespace explicitly with special tokens.",
        "Languages with non-Latin scripts often require specialized tokenizers.",
        "Efficient tokenization can significantly reduce API costs for LLM usage.",
    ]
    import random
    return random.choice(facts)

def display_tokenization_wisdom() -> str:
    """
    Returns a random piece of wisdom about tokenization.

    Returns:
        A string containing tokenization wisdom.
    """
    import textwrap
    wisdom = [
        textwrap.dedent("""\
            Every token costs, both in money and in context length.
            Choose them wisely.
            - The Token Master
        """).strip(),
        textwrap.dedent("""\
            The efficiency of an LLM is directly proportional to its tokenization strategy.
            - Guild of Neural Precision
        """).strip(),
        textwrap.dedent("""\
            A token saved is a token earned — and faster inference achieved.
            - Legacy Lexicon Proverb
        """).strip(),
        textwrap.dedent("""\
            Understanding tokenization is the first step to mastering prompt engineering.
            - Statistical Fragmentation Guild
        """).strip(),
        textwrap.dedent("""\
            The worst use of tokens is no use at all.
            The second worst is inefficient use.
            - The Token Economics Handbook
        """).strip(),
        textwrap.dedent("""\
            Choose your tokens as you would choose your words: with purpose and economy.
            - Wise Duck of QuackVerse
        """).strip(),
        textwrap.dedent("""\
            Behind every great language model stands an even greater tokenizer.
            - Ancient ML Wisdom
        """).strip(),
        textwrap.dedent("""\
            Know thy tokenizer, and thou shalt master the prompt.
            - The Prompt Engineer's Codex
        """).strip(),
        textwrap.dedent("""\
            What one token can do, two tokens should not.
            - Optimization Principle 101
        """).strip(),
        textwrap.dedent("""\
            In the realm of LLMs, tokens are the true currency of thought.
            - The QuackVerse Chronicles
        """).strip(),
    ]
    import random
    return random.choice(wisdom)


def highlight_token_patterns(token_segment: str) -> str:
    """
    Adds highlighting for interesting token patterns.

    Args:
        token_segment: The token segment to highlight

    Returns:
        Rich-formatted string with appropriate highlighting
    """
    # Convert to string to handle non-string values
    segment = str(token_segment)

    # Add pattern-based styling
    if segment.startswith(' '):
        return f"[cyan]{segment}[/cyan]"  # Leading space tokens
    elif len(segment) == 1 and not segment.isalnum():
        return f"[yellow]{segment}[/yellow]"  # Single punctuation
    elif segment.isupper():
        return f"[magenta]{segment}[/magenta]"  # ALL CAPS
    elif segment.isdigit():
        return f"[blue]{segment}[/blue]"  # Numbers
    return segment


def create_tokenization_dataframe(text: str,
                                  tokenizers: dict[str, BaseTokenizer]) -> pd.DataFrame:
    """
    Create a DataFrame containing tokenization results from multiple tokenizers.

    Args:
        text: The text to tokenize
        tokenizers: Dictionary mapping tokenizer names to instances

    Returns:
        Pandas DataFrame with tokenization results
    """
    # Maximum token count across all tokenizers
    max_tokens = 0
    tokenization_data = {}

    # Tokenize the text with each tokenizer
    for name, tokenizer in tokenizers.items():
        try:
            token_ids, token_strs = tokenizer.tokenize(text)
            max_tokens = max(max_tokens, len(token_ids))

            # Store results
            tokenization_data[name] = {
                "ids": token_ids,
                "segments": token_strs,
            }
        except Exception as e:
            logger.error(f"Error tokenizing with {name}: {e}")
            tokenization_data[name] = {
                "ids": [],
                "segments": [],
            }

    # Create a DataFrame with token indices as rows
    df = pd.DataFrame(index=range(max_tokens))

    # Add data for each tokenizer
    for name, data in tokenization_data.items():
        # Add token IDs
        id_col = f"{name}_ID"
        df[id_col] = pd.Series(data["ids"]).reindex(df.index)

        # Add token segments
        segment_col = f"{name}_Segment"
        df[segment_col] = pd.Series(data["segments"]).reindex(df.index)

    # Add token index column
    df.insert(0, "Token_Index", df.index)

    return df


def display_technique(
        df: pd.DataFrame,
        tokenizer: str,
        technique: str = "Default",
        console: Console | None = None
) -> str:
    """
    Display a formatted table for a specific tokenizer technique.

    Args:
        df: DataFrame containing tokenization data
        tokenizer: Name of the tokenizer to display
        technique: Tokenization technique (Default, Greedy, Beam, etc.)
        console: Optional Rich console to use for display

    Returns:
        Text representation of the displayed table
    """
    if console is None:
        console = Console(record=True)

    # Get tokenizer guild info
    guild_info = TOKENIZER_GUILDS.get(tokenizer, {
        "name": "Unknown Guild",
        "emoji": "❓",
        "description": "Unknown tokenization method",
    })

    # Get technique explanation
    technique_info = TECHNIQUE_EXPLANATIONS.get(technique,
                                                "Uses an unspecified tokenization strategy")

    # Show educational panel before the table
    info_text = f"{guild_info['name']} ({guild_info['emoji']})\n{guild_info['description']}\n\n[italic]{technique_info}[/italic]"
    console.print(
        Panel(info_text, title=f"About {tokenizer.capitalize()} ({technique})",
              border_style="green"))

    # Create the table
    table = Table(
        title=f"{guild_info['emoji']} {tokenizer.capitalize()} - {technique} Tokenization")
    table.add_column("Index", justify="right", style="bold cyan")
    table.add_column("Token ID", style="magenta")
    table.add_column("Segment", style="green")

    # Determine the column names based on tokenizer and technique
    id_col = f"{tokenizer}_ID"
    seg_col = f"{tokenizer}_Segment"

    # Use technique-specific columns if they exist
    if technique != "Default":
        tech_id_col = f"{tokenizer}_{technique}_ID"
        tech_seg_col = f"{tokenizer}_{technique}_Segment"

        if tech_id_col in df.columns:
            id_col = tech_id_col
        if tech_seg_col in df.columns:
            seg_col = tech_seg_col

    # Populate the table
    for idx, row in df.iterrows():
        token_id = str(row.get(id_col, "—"))
        token_seg = str(row.get(seg_col, "—"))

        # Skip rows with missing values
        if token_id == "—" and token_seg == "—":
            continue

        # Apply highlighting
        token_seg = highlight_token_patterns(token_seg)

        table.add_row(str(idx), token_id, token_seg)

    # Display the table
    console.print(table)

    # Add a random educational fact
    console.print(f"\n💡 [italic]Did you know? {get_random_token_fact()}[/italic]")

    # Return the console output if recorded
    if hasattr(console, "export_text"):
        return console.export_text()
    return ""


def display_token_comparison(
        df: pd.DataFrame,
        tokenizers: list[str],
        console: Console | None = None
) -> str:
    """
    Display a side-by-side comparison of multiple tokenizers.

    Args:
        df: DataFrame containing tokenization data
        tokenizers: list of tokenizer names to include in the comparison
        console: Optional Rich console to use for display

    Returns:
        Text representation of the displayed table
    """
    if console is None:
        console = Console(record=True)

    # Create the table
    table = Table(title="Tokenization Comparison")
    table.add_column("Index", justify="right", style="bold cyan")

    # Add columns for each tokenizer
    for tokenizer in tokenizers:
        guild_info = TOKENIZER_GUILDS.get(tokenizer, {"emoji": "❓"})
        table.add_column(f"{guild_info['emoji']} {tokenizer.capitalize()} ID",
                         style="magenta")
        table.add_column(f"{guild_info['emoji']} {tokenizer.capitalize()} Segment",
                         style="green")

    # Determine the max number of tokens
    max_tokens = 0
    for tokenizer in tokenizers:
        id_col = f"{tokenizer}_ID"
        if id_col in df.columns:
            # Count non-NaN values
            token_count = df[id_col].count()
            max_tokens = max(max_tokens, token_count)

    # Populate the table
    for idx in range(max_tokens):
        row_values = [str(idx)]

        for tokenizer in tokenizers:
            id_col = f"{tokenizer}_ID"
            seg_col = f"{tokenizer}_Segment"

            # Get values or placeholders
            token_id = str(df.loc[idx, id_col] if idx < len(df) and pd.notna(
                df.loc[idx, id_col]) else "—")
            token_seg = str(df.loc[idx, seg_col] if idx < len(df) and pd.notna(
                df.loc[idx, seg_col]) else "—")

            # Apply highlighting
            token_seg = highlight_token_patterns(token_seg)

            row_values.extend([token_id, token_seg])

        table.add_row(*row_values)

    # Display the table
    console.print(table)

    # Show token counts
    console.print("\n[bold]Token Count Summary:[/bold]")
    for tokenizer in tokenizers:
        id_col = f"{tokenizer}_ID"
        if id_col in df.columns:
            token_count = df[id_col].count()
            guild_info = TOKENIZER_GUILDS.get(tokenizer, {"emoji": "❓"})
            console.print(
                f"{guild_info['emoji']} {tokenizer.capitalize()}: {token_count} tokens")

    # Add a random piece of wisdom
    console.print(f"\n🔮 [italic]{display_tokenization_wisdom()}[/italic]")

    # Return the console output if recorded
    if hasattr(console, "export_text"):
        return console.export_text()
    return ""


def display_token_splitting_diagram(
        text: str,
        tokenizer: BaseTokenizer,
        console: Console | None = None
) -> str:
    """
    Display a visual ASCII diagram of how text is split into tokens.

    Args:
        text: The text to tokenize
        tokenizer: The tokenizer to use
        console: Optional Rich console to use for display

    Returns:
        Text representation of the diagram
    """
    if console is None:
        console = Console(record=True)

    # Only show diagram for reasonably short text
    if len(text) > 80:
        text = text[:77] + "..."

    # Get tokenization
    token_ids, token_strs = tokenizer.tokenize(text)

    # Create the diagram header
    console.print(f"[bold]Token Splitting Diagram - {tokenizer.name}[/bold]")
    console.print(f"[cyan]Original text:[/cyan] {text}")
    console.print("\n[cyan]Tokens:[/cyan]")

    # Display token boundaries and indices
    current_pos = 0
    for i, token in enumerate(token_strs):
        # Get the token position in the original text
        token_start = current_pos
        token_end = current_pos + len(token)
        current_pos = token_end

        # Create a visual representation with background color
        if i % 2 == 0:
            styled_token = f"[black on cyan]{token}[/]"
        else:
            styled_token = f"[black on green]{token}[/]"

        # Display token with its index and ID
        console.print(f"Token {i}: {styled_token} (ID: {token_ids[i]})")

    # Return the console output if recorded
    if hasattr(console, "export_text"):
        return console.export_text()
    return ""


def suggest_token_optimizations(text: str, console: Console | None = None) -> str:
    """
    Analyze text and suggest ways to optimize token usage.

    Args:
        text: The text to analyze
        console: Optional Rich console to use for display

    Returns:
        Text representation of the suggestions
    """
    if console is None:
        console = Console(record=True)

    suggestions = []

    # Check for patterns that typically increase token count
    if text.count("\n\n") > 3:
        suggestions.append("Reduce multiple blank lines to minimize whitespace tokens")

    if len(re.findall(r'\s{2,}', text)) > 5:
        suggestions.append("Reduce multiple spaces to single spaces")

    if text.isupper() and len(text) > 20:
        suggestions.append("Convert ALL CAPS text to normal case to reduce token count")

    if text.count("```") > 1:
        suggestions.append(
            "Code blocks often use more tokens - consider if they're necessary")

    if len(re.findall(r'https?://\S+', text)) > 0:
        suggestions.append(
            "URLs typically use many tokens - consider removing if not needed")

    if len(text) > 100 and ":" in text:
        bullets = text.count(":") / (text.count(".") + 1)
        if bullets > 0.3:  # If there are many colon-separated items
            suggestions.append("list items with many colons can increase token count")

    # Add general suggestions if we don't have specific ones
    if not suggestions:
        suggestions = [
            "Remove unnecessary punctuation",
            "Use contractions (e.g., 'don't' instead of 'do not')",
            "Remove redundant words and phrases",
            "Use simpler vocabulary where possible"
        ]

    # Display suggestions
    console.print(Panel("\n".join([f"• {s}" for s in suggestions]),
                        title="Token Optimization Suggestions",
                        border_style="yellow"))

    # Return the console output if recorded
    if hasattr(console, "export_text"):
        return console.export_text()
    return ""


def guild_challenge(
        text: str,
        tokenizers: dict[str, BaseTokenizer],
        console: Console | None = None
) -> dict[str, Any]:
    """
    Present a tokenization challenge to estimate token counts.

    Args:
        text: The text for the challenge
        tokenizers: Dictionary mapping tokenizer names to instances
        console: Optional Rich console to use for display

    Returns:
        Challenge results dictionary
    """
    if console is None:
        console = Console(record=True)

    # Get guild information for available tokenizers
    guilds = {}
    for i, (name, tokenizer) in enumerate(tokenizers.items(), 1):
        guild_info = TOKENIZER_GUILDS.get(name, {
            "name": f"{name.capitalize()} Guild",
            "emoji": "❓"
        })

        guild_name = f"{guild_info['emoji']} {guild_info['name']}"
        guilds[str(i)] = {
            "name": guild_name,
            "tokenizer_name": name,
            "tokenizer": tokenizer
        }

    # Display challenge introduction
    console.print("\n[bold yellow]🏆 GUILD CHALLENGE![/bold yellow]")
    console.print(
        "Which guild's tokenizer will use the [bold]FEWEST[/bold] tokens for this text?")
    console.print(f"\n[cyan]Challenge text:[/cyan] {text}")

    # Calculate actual token counts
    token_counts = {}
    for key, guild in guilds.items():
        tokenizer = guild["tokenizer"]
        token_ids, _ = tokenizer.tokenize(text)
        token_counts[key] = len(token_ids)

    # Find the winner (lowest token count)
    winner_key = min(token_counts.items(), key=lambda x: x[1])[0]

    # Return results dictionary for interactive use
    results = {
        "challenge_text": text,
        "guilds": guilds,
        "token_counts": token_counts,
        "winner_key": winner_key,
        "winner_name": guilds[winner_key]["name"],
        "winner_tokenizer": guilds[winner_key]["tokenizer_name"],
        "winning_count": token_counts[winner_key]
    }

    # For CLI display, show all token counts
    console.print("\n[bold]Guild Token Counts:[/bold]")
    for key, count in token_counts.items():
        guild_name = guilds[key]["name"]
        if key == winner_key:
            console.print(f"[green]{guild_name}: {count} tokens ⭐ WINNER![/green]")
        else:
            console.print(f"{guild_name}: {count} tokens")

    # Return the results
    return results


def export_visualization_to_text(
        console_output: str,
        output_path: str
) -> bool:
    """
    Export visualization to a text file.

    Args:
        console_output: Rich console output text
        output_path: Path to save the output

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(console_output)
        logger.info(f"Exported visualization to text file: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to export visualization: {e}")
        return False