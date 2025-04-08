# src/quacktokenscope/commands/token_cli.py
"""
Command-line interface for the QuackTokenScope tool.

This module provides a CLI for the QuackTokenScope tool, allowing users
to analyze text files with different tokenizers and interact with Google Drive.
"""

from typing import cast

import click
from quackcore.cli import (
    handle_errors,
    init_cli_env,
    print_error,
    print_info,
    print_success,
)

from quacktokenscope.plugins.token_scope import TokenScopePlugin
from quacktokenscope.utils.frequency import format_frequency_chart, \
    classify_token_rarity
from quacktokenscope.utils.reverse_mapping import get_fidelity_emoji


@click.group(name="tokenscope")
@click.option(
    "--config",
    "-c",
    help="Path to configuration file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    help="Enable debug mode",
)
@click.pass_context
def tokenscope_cli(
        ctx: click.Context,
        config: str | None,
        verbose: bool,
        debug: bool,
) -> None:
    """
    QuackTokenScope - Compare different tokenizers on the same text.

    This tool can tokenize files using different tokenizers, compare their
    outputs, analyze frequency, and export results to various formats.
    """
    # Initialize QuackCore CLI environment
    quack_ctx = init_cli_env(
        config_path=config,
        verbose=verbose,
        debug=debug,
        app_name="quacktokenscope",
    )

    # Store the context for use in subcommands
    ctx.obj = {
        "quack_ctx": quack_ctx,
        "logger": quack_ctx.logger,
        "config": quack_ctx.config,
        "verbose": verbose
    }


# Cast the decorated function to a click.Group so that type checkers recognize it as a Command.
tokenscope_cli = cast(click.Group, tokenscope_cli)


@tokenscope_cli.command("tokenize")
@click.argument(
    "input",
    type=str,
)
@click.option(
    "--output",
    "-o",
    help="Output path for results",
    type=click.Path(file_okay=False),
)
@click.option(
    "--same-dir",
    is_flag=True,
    help="Output results in the same directory as the input file",
)
@click.option(
    "--tokenizers",
    help="Comma-separated list of tokenizers to use (tiktoken, huggingface, sentencepiece)",
    type=str,
)
@click.option(
    "--output-format",
    type=click.Choice(["excel", "json", "csv", "all"]),
    default="excel",
    help="Output format for results",
)
@click.option(
    "--limit",
    type=int,
    help="Limit number of characters processed",
)
@click.option(
    "--upload/--no-upload",
    default=True,
    help="Upload results to Google Drive if input is from Drive",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Don't upload results to Google Drive",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Print detailed tokenization information",
)
@click.pass_context
@handle_errors(exit_code=1)
def tokenize_command(
        ctx: click.Context,
        input: str,
        output: str | None,
        same_dir: bool,
        tokenizers: str | None,
        output_format: str,
        limit: int | None,
        upload: bool,
        dry_run: bool,
        verbose: bool,
) -> None:
    """
    Tokenize a text file using different tokenizers.

    INPUT can be a local file path or a Google Drive file ID.

    Examples:
        quacktool tokenscope tokenize myfile.txt
        quacktool tokenscope tokenize myfile.txt --same-dir
        quacktool tokenscope tokenize 1abc2defg3hij --dry-run
    """
    logger = ctx.obj["logger"]
    logger.info(f"Tokenizing file: {input}")

    # Start with a welcoming ASCII art header
    print(
        "\n"
        "🔮 Summoning tokens from the three Great Tokenizer Guilds...\n"
        "• 🧠 OpenAI's Neural Precision\n"
        "• 📚 HuggingFace's Legacy Lexicon\n"
        "• 🧬 SentencePiece of Statistical Fragmentation\n"
    )

    # Create and initialize the token scope plugin
    plugin = TokenScopePlugin()
    init_result = plugin.initialize()

    if not init_result.success:
        print_error(f"Failed to initialize tokenscope plugin: {init_result.error}",
                    exit_code=1)

    # Process options
    options = {
        "tokenizers": tokenizers,
        "output_format": output_format,
        "upload": upload,
        "dry_run": dry_run,
        "verbose": verbose,
        "same_dir": same_dir
    }

    if limit:
        options["limit"] = limit

    # Process the file
    print_info("🔍 Analyzing tokens...")
    result = plugin.process_file(
        file_path=input,
        output_path=output,
        options=options
    )

    if not result.success:
        print_error(f"Failed to tokenize file: {result.error}", exit_code=1)

    # Display results
    content = result.content
    summary = content.get("summary", {})
    exported_files = content.get("exported_files", {})

    print_success("✨ Tokenization complete!")

    # Print summary information
    file_name = content.get("original_file_name", summary.get("filename", "unknown"))
    tokenizers_used = summary.get("tokenizers_used", [])
    total_tokens = summary.get("total_tokens", {})
    best_match = summary.get("best_match", "unknown")

    print("\n📊 Token Count Comparison:")
    for tokenizer in tokenizers_used:
        count = total_tokens.get(tokenizer, 0)
        print(f"  • {tokenizer}: {count:,} tokens")

    # Show reverse mapping results if available
    if "analysis" in content:
        analysis = content["analysis"]
        stats = analysis.get("stats", {})

        print("\n🔁 Reverse Mapping (Fidelity Check):")
        for tokenizer in tokenizers_used:
            if tokenizer in stats:
                tokenizer_stats = stats[tokenizer]
                status = tokenizer_stats.get("reconstruction_status", "Unknown")
                score = tokenizer_stats.get("reconstruction_score", 0.0)
                emoji = get_fidelity_emoji(status)
                print(f"  • {tokenizer} → {emoji} {status} ({score:.1%})")

    # Show most common tokens if available
    most_common = summary.get("most_common_token", {})
    rarest = summary.get("rarest_token", {})

    if most_common and tokenizers_used:
        print("\n📈 Token Popularity:")
        for tokenizer in tokenizers_used:
            if tokenizer in most_common and most_common[tokenizer]:
                token, count = most_common[tokenizer]
                print(
                    f"  • {tokenizer} most common: \"{token}\" {format_frequency_chart(token, count, 10)}")

            if tokenizer in rarest and rarest[tokenizer]:
                token, count = rarest[tokenizer]
                rarity_class = classify_token_rarity(token, count,
                                                     total_tokens.get(tokenizer, 0))
                print(f"  • {tokenizer} rarest: \"{token}\" ({count}x) {rarity_class}")

    # Show export summary
    if exported_files:
        print("\n📁 Results exported to:")
        for file_type, file_path in exported_files.items():
            print(f"  • {file_type}: {file_path}")

    # Show Google Drive upload information if applicable
    drive_files = content.get("drive_files", {})
    if drive_files:
        print("\n☁️ Files uploaded to Google Drive:")
        for file_type, file_id in drive_files.items():
            print(f"  • {file_type}: https://drive.google.com/file/d/{file_id}")

    # Wrap up
    print("\n📦 QuackTokenScope Mission Report:")
    print(f"• File analyzed: {file_name}")
    total_token_sum = sum(total_tokens.values())
    print(f"• Tokens compared: {total_token_sum:,}")
    print(f"• Best reconstruction: {best_match}")

    # If there was a legendary token, mention it
    legendary_found = False
    for tokenizer in tokenizers_used:
        if tokenizer in rarest and rarest[tokenizer]:
            token, count = rarest[tokenizer]
            rarity_class = classify_token_rarity(token, count,
                                                 total_tokens.get(tokenizer, 0))
            if "Legendary" in rarity_class:
                print(f"• Rarest token: \"{token}\" {rarity_class}")
                legendary_found = True
                break

    if not legendary_found and tokenizers_used and rarest:
        # Just pick the first tokenizer's rarest token
        tokenizer = tokenizers_used[0]
        if tokenizer in rarest and rarest[tokenizer]:
            token, count = rarest[tokenizer]
            rarity_class = classify_token_rarity(token, count,
                                                 total_tokens.get(tokenizer, 0))
            print(f"• Rarest token: \"{token}\" {rarity_class}")


def main() -> None:
    """Entry point for the tokenscope CLI."""
    tokenscope_cli(obj={})


if __name__ == "__main__":
    main()