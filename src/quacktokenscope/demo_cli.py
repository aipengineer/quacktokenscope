# src/quacktokenscope/demo_cli.py
"""
Demo command-line interface for QuackTokenScope.

This module provides a CLI for demonstration and testing purposes only.
In production environments, QuackBuddy should be used as the user-facing CLI.
"""

import click
from quackcore.cli import (
    handle_errors,
    init_cli_env,
    print_error,
    print_info,
    print_success,
)

from quacktokenscope.plugins.token_scope import TokenScopePlugin
from quacktokenscope.version import display_version_info, __version__
from quacktokenscope.commands.token_cli import tokenscope_cli
from quacktokenscope.config import get_config

# Get project name from config or use default
try:
    config = get_config()
    PROJECT_NAME = getattr(config.general, "project_name", "QuackTokenScope")
except:
    PROJECT_NAME = "QuackTokenScope"  # Fallback to default

# Create an actual Click group object (not a decorated function)
# This creates an instance of click.Group that can be used in tests
cli = click.Group(name=PROJECT_NAME.lower())


# Main command decorator
@cli.command("main")
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
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress non-error output",
)
@click.version_option(
    version=__version__,
    prog_name=PROJECT_NAME,
    callback=display_version_info,
    message=f"{PROJECT_NAME} version %(version)s"
)
@click.pass_context
def main_command(
        ctx: click.Context,
        config: str | None,
        verbose: bool,
        debug: bool,
        quiet: bool,
) -> None:
    """
    Demo CLI - For development/testing purposes only.

    In production, use QuackBuddy as the user-facing CLI instead.
    This CLI is included only as a reference implementation and for teaching.
    """
    # Initialize QuackCore CLI environment
    quack_ctx = init_cli_env(
        config_path=config,
        verbose=verbose,
        debug=debug,
        quiet=quiet,
        app_name=PROJECT_NAME.lower(),
    )

    # Store the context for use in subcommands
    ctx.obj = {
        "quack_ctx": quack_ctx,
        "logger": quack_ctx.logger,
        "config": quack_ctx.config,
    }


@cli.command("tokenize")
@click.argument(
    "input_file",
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
        input_file: str,
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

    INPUT_FILE can be a local file path or a Google Drive file ID.

    Examples:
        tokenize myfile.txt
        tokenize myfile.txt --same-dir
        tokenize 1abc2defg3hij --dry-run
    """
    logger = ctx.obj["logger"]
    logger.info(f"Tokenizing file: {input_file}")

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
        print_error(
            f"Failed to initialize {PROJECT_NAME.lower()} plugin: {init_result.error}",
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
        file_path=input_file,
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
            print(f"  • {file_type}: https://drive.google.com/file/d/{file_id}/view")

    # Wrap up
    print("\n📦 QuackTokenScope Mission Report:")
    print(f"• File analyzed: {file_name}")
    total_token_sum = sum(total_tokens.values())
    print(f"• Tokens compared: {total_token_sum:,}")
    print(f"• Best reconstruction: {best_match}")


# Add a dedicated version command that calls display_version_info directly
@cli.command("version")
def version_command():
    """Display version information."""
    # Call the version function directly, don't rely on callback
    # This ensures the mock can track the call
    return display_version_info(None, None, True)


# Add the tokenscope_cli command group
cli.add_command(tokenscope_cli)


def main() -> None:
    """
    Entry point for the demo CLI (for development/testing only).

    NOTE: This main function is for testing/development only.
    In production, QuackBuddy should be used instead.
    """
    print(f"🔎 {PROJECT_NAME} - Compare how different tokenizers 'see' the same text")
    print("NOTE: This CLI is for development/teaching purposes only.")
    print("")
    cli(obj={})


if __name__ == "__main__":
    main()