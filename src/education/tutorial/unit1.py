# src/quacktokenscope/education/tutorial/unit1.py
"""
Unit 1: The Token Puzzle tutorial.

This module implements the first tutorial unit, which introduces
the concept of tokenization and how it differs from words.
"""

from rich.prompt import Prompt
from rich.panel import Panel

from quacktokenscope.education.tutorial.base import TutorialUnit
from quacktokenscope.education.visualization import display_token_splitting_diagram


class Unit1Tutorial(TutorialUnit):
    """Unit 1: The Token Puzzle tutorial."""

    title = "Unit 1: The Token Puzzle"
    description = "Let's explore how LLMs see text through tokens..."

    def run(self) -> None:
        """Run Unit 1 tutorial."""
        super().run()

        # Interactive challenge
        challenge_text = "The quick brown fox jumps over the lazy dog"
        self.console.print(
            f"\n[bold]Challenge:[/bold] How many tokens do you think are in the sentence:")
        self.console.print(f"[cyan]'{challenge_text}'[/cyan]")

        options = ["5", "9", "10", "13"]
        self.console.print("\nOptions:")
        for i, opt in enumerate(options):
            self.console.print(f"{i + 1}. {opt} tokens")

        # Get user guess
        guess = Prompt.ask("Your answer (1-4)", choices=["1", "2", "3", "4"])

        # Calculate actual token count
        primary_tokenizer = self.get_primary_tokenizer()
        token_ids, _ = primary_tokenizer.tokenize(challenge_text)
        actual_count = len(token_ids)

        # Respond to the guess
        self.console.print(
            f"\nThe actual token count is: [bold]{actual_count}[/bold] tokens")

        # Show the tokens
        self.console.print(display_token_splitting_diagram(
            challenge_text,
            primary_tokenizer,
            self.console
        ))

        # Explanation of why tokens matter
        self.console.print(Panel(
            "Tokens are the basic units that LLMs process text. They're not the same as words! "
            "Understanding how text gets split into tokens is crucial for several reasons:\n\n"
            "• API costs are calculated per token\n"
            "• Context windows are limited by token count\n"
            "• Prompt engineering requires token awareness\n"
            "• Different models use different tokenization strategies",
            title="Why Tokens Matter",
            border_style="green"
        ))

        # Educational wrap-up
        self.console.print("\n[bold]Key takeaways:[/bold]")
        self.console.print("• Tokens are not the same as words")
        self.console.print("• Tokenizers use different strategies to split text")
        self.console.print("• Understanding tokenization helps optimize prompts")
        self.console.print("• Common words often become single tokens")
        self.console.print(
            "• Special characters and rare words may be split into multiple tokens")

        # Try some more examples if the user wants
        if Prompt.ask("\nWould you like to try more examples?", choices=["y", "n"],
                      default="y") == "y":
            examples = [
                "Hello, world!",
                "https://www.example.com",
                "COVID-19 pandemic",
                "Python programming is fun! 🐍"
            ]

            for example in examples:
                token_ids, _ = primary_tokenizer.tokenize(example)
                count = len(token_ids)

                self.console.print(f"\n[bold]Example:[/bold] '{example}'")
                self.console.print(f"Token count: [bold]{count}[/bold]")

                self.console.print(display_token_splitting_diagram(
                    example,
                    primary_tokenizer,
                    self.console
                ))

        # Final encouragement
        self.console.print(
            "\n[bold green]Congratulations![/bold green] You've completed Unit 1 of the tokenization tutorial.")
        self.console.print(
            "Continue to Unit 2 to learn about language modeling fundamentals.")