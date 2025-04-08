# src/quacktokenscope/education/tutorial/unit5.py
"""
Unit 5: Analyzing Tokenization Differences tutorial.

This module implements the fifth tutorial unit, which explores
why tokenization strategies matter for different text types.
"""

from rich.prompt import Prompt
from rich.panel import Panel

from quacktokenscope.education.tutorial.base import TutorialUnit
from quacktokenscope.education.visualization import (
    create_tokenization_dataframe,
    display_token_comparison,
    display_token_splitting_diagram,
)


class Unit5Tutorial(TutorialUnit):
    """Unit 5: Analyzing Tokenization Differences tutorial."""

    title = "Unit 5: Analyzing Tokenization Differences"
    description = "Let's explore why tokenization strategies matter..."

    def run(self) -> None:
        """Run Unit 5 tutorial."""
        super().run()

        # Examples of different text types
        examples = {
            "English": "The quick brown fox jumps over the lazy dog.",
            "Code": "def hello_world():\n    print('Hello, world!')",
            "URL": "https://www.example.com/path/to/resource?query=value",
            "Numbers": "The price is $1,234.56 for 42 items.",
            "Emojis": "I ❤️ tokenization! 🚀 It's so interesting! 🧠"
        }

        # Let user select an example
        self.console.print("\n[bold]Choose a text type to analyze:[/bold]")
        for i, (name, text) in enumerate(examples.items(), 1):
            self.console.print(f"{i}. {name}")

        choice = Prompt.ask("Your choice",
                            choices=[str(i) for i in range(1, len(examples) + 1)])
        selected_type = list(examples.keys())[int(choice) - 1]
        selected_text = examples[selected_type]

        # Analyze the selected text
        df = create_tokenization_dataframe(selected_text, self.tokenizers)
        self.console.print(
            display_token_comparison(df, list(self.tokenizers.keys()), self.console))

        # Educational insights based on the selection
        self.console.print(f"\n[bold]Insights for {selected_type} text:[/bold]")

        insights = {
            "English": [
                "• Common English words are often single tokens",
                "• Punctuation typically gets its own token or merges with the preceding word",
                "• Articles like 'the' are frequent enough to be their own tokens"
            ],
            "Code": [
                "• Code often uses more tokens due to special characters and formatting",
                "• Indentation and whitespace create separate tokens",
                "• Function names and syntax elements may be split differently"
            ],
            "URL": [
                "• URLs are often tokenized inefficiently",
                "• Special characters like '/', ':', and '?' create separate tokens",
                "• Domain names may be split in unexpected ways"
            ],
            "Numbers": [
                "• Numbers are often split into individual digits",
                "• Currency symbols and commas create additional tokens",
                "• Round numbers might be more efficiently tokenized"
            ],
            "Emojis": [
                "• Emojis typically use multiple tokens",
                "• They're represented as Unicode sequences internally",
                "• More recent tokenizers handle emojis better than older ones"
            ]
        }

        for insight in insights.get(selected_type, []):
            self.console.print(insight)

        # Final encouragement
        self.console.print(
            "\n[bold green]Congratulations![/bold green] You've completed Unit 5 of the tokenization tutorial.")
        self.console.print(
            "Continue to Unit 6 to learn about API costs and optimizing prompts.")