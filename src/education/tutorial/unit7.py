# src/quacktokenscope/education/tutorial/unit7.py
"""
Unit 7: Tokenizing Diverse Texts tutorial.

This module implements the seventh tutorial unit, which compares
how different types of text tokenize.
"""

from rich.prompt import Prompt
from rich.panel import Panel

from quacktokenscope.education.tutorial.base import TutorialUnit
from quacktokenscope.education.visualization import display_token_splitting_diagram


class Unit7Tutorial(TutorialUnit):
    """Unit 7: Tokenizing Diverse Texts tutorial."""

    title = "Unit 7: Tokenizing Diverse Texts"
    description = "Let's compare how different types of text tokenize..."

    def run(self) -> None:
        """Run Unit 7 tutorial."""
        super().run()

        # Sample texts of different genres
        genre_samples = {
            "Literary": "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness.",
            "Technical": "The function takes an array of integers and returns the sum of all elements that satisfy the predicate x => x % 2 == 0.",
            "Conversational": "Hey there! How's it going? I haven't seen you in forever! What's new?",
            "Code": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
            "Social Media": "#ThrowbackThursday to that amazing trip! 😍 Can't wait to go back! @travel_buddy"
        }

        # Let user select genres to compare
        self.console.print("\n[bold]Select two text genres to compare:[/bold]")
        for i, genre in enumerate(genre_samples.keys(), 1):
            self.console.print(f"{i}. {genre}")

        first_choice = Prompt.ask("First choice", choices=[str(i) for i in range(1,
                                                                                 len(genre_samples) + 1)])
        second_choice = Prompt.ask("Second choice", choices=[str(i) for i in range(1,
                                                                                   len(genre_samples) + 1)])

        first_genre = list(genre_samples.keys())[int(first_choice) - 1]
        second_genre = list(genre_samples.keys())[int(second_choice) - 1]

        first_text = genre_samples[first_genre]
        second_text = genre_samples[second_genre]

        # Choose a tokenizer
        tokenizer_name = Prompt.ask(
            "Select a tokenizer to use",
            choices=list(self.tokenizers.keys()),
            default=next(iter(self.tokenizers.keys()))
        )

        tokenizer_instance = self.tokenizers[tokenizer_name]

        # Analyze both texts
        first_tokens = tokenizer_instance.tokenize(first_text)
        second_tokens = tokenizer_instance.tokenize(second_text)

        first_count = len(first_tokens[0])
        second_count = len(second_tokens[0])

        # Display results
        self.console.print(f"\n[bold]{first_genre} text:[/bold]")
        self.console.print(Panel(first_text))
        self.console.print(f"Token count: {first_count}")

        self.console.print(f"\n[bold]{second_genre} text:[/bold]")
        self.console.print(Panel(second_text))
        self.console.print(f"Token count: {second_count}")

        # Comparison
        self.console.print("\n[bold]Comparison:[/bold]")

        chars_per_token1 = len(first_text) / first_count
        chars_per_token2 = len(second_text) / second_count

        self.console.print(
            f"{first_genre}: {chars_per_token1:.2f} characters per token")
        self.console.print(
            f"{second_genre}: {chars_per_token2:.2f} characters per token")

        # Who wins?
        if chars_per_token1 > chars_per_token2:
            self.console.print(
                f"\n[green]{first_genre} text is more token-efficient![/green]")
        elif chars_per_token2 > chars_per_token1:
            self.console.print(
                f"\n[green]{second_genre} text is more token-efficient![/green]")
        else:
            self.console.print(
                "\n[yellow]Both texts have similar token efficiency.[/yellow]")

        # Show token breakdown for one of them
        if Prompt.ask(
                "\nWould you like to see the token breakdown for one of these texts?",
                choices=["y", "n"], default="y") == "y":
            genre_choice = Prompt.ask(
                "Which one?",
                choices=["1", "2"],
                default="1"
            )

            if genre_choice == "1":
                self.console.print(
                    display_token_splitting_diagram(first_text, tokenizer_instance,
                                                    self.console))
            else:
                self.console.print(
                    display_token_splitting_diagram(second_text, tokenizer_instance,
                                                    self.console))

        # Final encouragement
        self.console.print(
            "\n[bold green]Congratulations![/bold green] You've completed Unit 7 of the tokenization tutorial.")
        self.console.print("Continue to Unit 8 for the final wrap-up and next steps.")