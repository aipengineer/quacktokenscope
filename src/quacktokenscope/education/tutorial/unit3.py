# src/quacktokenscope/education/tutorial/unit3.py
"""
Unit 3: Tokenization Techniques tutorial.

This module implements the third tutorial unit, which introduces
different tokenization techniques like BPE.
"""

from rich.prompt import Prompt
from rich.panel import Panel

from quacktokenscope.education.tutorial.base import TutorialUnit
from quacktokenscope.education.visualization import (
    create_tokenization_dataframe,
    display_token_comparison,
    display_token_splitting_diagram,
)


class Unit3Tutorial(TutorialUnit):
    """Unit 3: Tokenization Techniques tutorial."""

    title = "Unit 3: Tokenization Techniques"
    description = "Exploring how different tokenizers work..."

    def run(self) -> None:
        """Run Unit 3 tutorial."""
        super().run()

        # Show comparison of tokenizers on the same text
        example_text = "The quick brown fox jumps over the lazy dog."

        df = create_tokenization_dataframe(example_text, self.tokenizers)
        self.console.print(
            display_token_comparison(df, list(self.tokenizers.keys()), self.console))

        # Educational content about BPE
        self.console.print("\n[bold]Byte Pair Encoding (BPE):[/bold]")
        self.console.print(
            "BPE is one of the most common subword tokenization algorithms. Here's how it works:")
        self.console.print("1. Start with individual characters as tokens")
        self.console.print("2. Count the frequency of adjacent pairs of tokens")
        self.console.print("3. Merge the most frequent pair into a new token")
        self.console.print("4. Repeat until desired vocabulary size is reached")

        # Visual example
        self.console.print("\n[bold]BPE Example:[/bold]")
        self.console.print("Starting with: 'l o w e r'")
        self.console.print("Most common pair: 'e r' → Merge to 'er'")
        self.console.print("Result: 'l o w er'")
        self.console.print("Most common pair: 'l o' → Merge to 'lo'")
        self.console.print("Result: 'lo w er'")
        self.console.print("And so on...")

        # Explain different tokenization approaches
        self.console.print(Panel(
            "Modern tokenization techniques include:\n\n"
            "• Byte Pair Encoding (BPE): Merges frequent character pairs iteratively\n"
            "• WordPiece: Similar to BPE but with likelihood-based decisions\n"
            "• SentencePiece: Language-agnostic approach that handles whitespace\n"
            "• Unigram: Probabilistic approach that optimizes likelihood",
            title="Tokenization Approaches",
            border_style="green"
        ))

        # Interactive element
        if Prompt.ask("\nWould you like to see token splitting for a custom phrase?",
                      choices=["y", "n"], default="y") == "y":
            custom_text = Prompt.ask("Enter your phrase")
            tokenizer_name = Prompt.ask(
                "Which tokenizer?",
                choices=list(self.tokenizers.keys()),
                default=next(iter(self.tokenizers.keys()))
            )

            self.console.print(display_token_splitting_diagram(
                custom_text,
                self.tokenizers[tokenizer_name],
                self.console
            ))

        # Compare tokenization efficiency
        self.console.print("\n[bold]Tokenization Efficiency Comparison:[/bold]")
        self.console.print("Different tokenization strategies have trade-offs:")
        self.console.print("• Vocabulary size (smaller is more memory-efficient)")
        self.console.print(
            "• Compression ratio (higher characters per token is better)")
        self.console.print("• Handling of out-of-vocabulary words")
        self.console.print("• Language-specific vs. multilingual capabilities")

        # Final encouragement
        self.console.print(
            "\n[bold green]Congratulations![/bold green] You've completed Unit 3 of the tokenization tutorial.")
        self.console.print(
            "Continue to Unit 4 to get hands-on with comparing tokenizers in Python.")