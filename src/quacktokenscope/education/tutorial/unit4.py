# src/quacktokenscope/education/tutorial/unit4.py
"""
Unit 4: Hands-On Comparing Tokenizers tutorial.

This module implements the fourth tutorial unit, which provides
hands-on experience comparing different tokenizers.
"""

from rich.prompt import Prompt

from quacktokenscope.education.tutorial.base import TutorialUnit
from quacktokenscope.education.visualization import (
    create_tokenization_dataframe,
    display_token_comparison,
    suggest_token_optimizations,
)
from quacktokenscope.education.cost_calculator import display_cost_summary


class Unit4Tutorial(TutorialUnit):
    """Unit 4: Hands-On Comparing Tokenizers tutorial."""

    title = "Unit 4: Hands-On - Comparing Tokenizers"
    description = "Let's analyze text using different tokenizers..."

    def run(self) -> None:
        """Run Unit 4 tutorial."""
        super().run()

        # Interactive text input
        sample_text = Prompt.ask(
            "Enter a text to analyze (or press Enter for default)",
            default="The quick brown fox jumps over the lazy dog. Python 3.8 was released in 2019."
        )

        # Analyze with different tokenizers
        df = create_tokenization_dataframe(sample_text, self.tokenizers)

        # Display the comparison
        self.console.print(
            display_token_comparison(df, list(self.tokenizers.keys()), self.console))

        # Cost calculation
        if Prompt.ask("\nWould you like to see the API cost for this text?",
                      choices=["y", "n"], default="y") == "y":
            # Use tiktoken or first available tokenizer for cost calculation
            cost_tokenizer = self.get_primary_tokenizer()
            token_count = len(cost_tokenizer.tokenize(sample_text)[0])

            self.console.print(display_cost_summary(
                sample_text,
                token_count,
                0,
                "gpt-4-turbo",
                self.console
            ))

        # Token optimization
        if Prompt.ask("\nWould you like to see optimization suggestions?",
                      choices=["y", "n"], default="y") == "y":
            self.console.print(suggest_token_optimizations(sample_text, self.console))

        # Final encouragement
        self.console.print(
            "\n[bold green]Congratulations![/bold green] You've completed Unit 4 of the tokenization tutorial.")
        self.console.print(
            "Continue to Unit 5 to learn about analyzing tokenization differences.")