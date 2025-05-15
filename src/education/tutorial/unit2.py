# src/quacktokenscope/education/tutorial/unit2.py
"""
Unit 2: Foundations of Language Modeling tutorial.

This module implements the second tutorial unit, which introduces
basic language modeling concepts and how they relate to tokenization.
"""

from rich.prompt import Prompt
from rich.panel import Panel

from quacktokenscope.education.tutorial.base import TutorialUnit
from quacktokenscope.education.language_model import SimpleLanguageModel


class Unit2Tutorial(TutorialUnit):
    """Unit 2: Foundations of Language Modeling tutorial."""

    title = "Unit 2: Foundations of Language Modeling"
    description = "Exploring bigram and n-gram models..."

    def run(self) -> None:
        """Run Unit 2 tutorial."""
        super().run()

        # Training corpus
        training_text = """
        The quick brown fox jumps over the lazy dog. The dog sleeps peacefully under the tree.
        The fox runs away. The quick rabbit also jumps. The tree provides shade.
        """

        self.console.print(Panel(
            training_text.strip(),
            title="Training Corpus",
            border_style="blue"
        ))

        # Explain n-gram models
        self.console.print(Panel(
            "N-gram models predict the next token based on the previous N-1 tokens:\n\n"
            "• Unigram (N=1): Individual token probabilities, no context\n"
            "• Bigram (N=2): Predicts based on the previous token only\n"
            "• Trigram (N=3): Uses the previous two tokens for context\n"
            "• Higher N: More context, but requires more training data",
            title="N-gram Language Models",
            border_style="green"
        ))

        # Create a bigram model
        primary_tokenizer = self.get_primary_tokenizer()
        model = SimpleLanguageModel(primary_tokenizer, n=2, name="Quack-Bigram")
        model.train(training_text)

        # Show prediction examples
        prompts = ["The", "The quick", "The dog"]

        for prompt in prompts:
            self.console.print(f"\n[bold]Prompt:[/bold] '{prompt}'")
            predictions = model.predict_next(prompt, num_predictions=3)

            self.console.print("[bold]Top predictions (bigram model):[/bold]")
            for i, (token, prob) in enumerate(predictions):
                self.console.print(f"{i + 1}. '{token}' ({prob:.2%})")

        # Educational explanation
        self.console.print("\n[bold]How it works:[/bold]")
        self.console.print("1. The bigram model looks at the last token in your prompt")
        self.console.print(
            "2. It finds all instances of that token in the training data")
        self.console.print("3. It counts which tokens follow it and their frequencies")
        self.console.print(
            "4. It returns the most likely next tokens based on those counts")

        self.console.print("\n[bold]Limitations:[/bold]")
        self.console.print("• Bigram models only look at the previous token")
        self.console.print("• They can't capture long-range dependencies")
        self.console.print(
            "• Modern language models use transformers that can handle much more context")

        # Interactive challenge
        if Prompt.ask(
                "\nWould you like to try with a trigram model to see the difference?",
                choices=["y", "n"], default="y") == "y":
            # Create a trigram model
            model = SimpleLanguageModel(primary_tokenizer, n=3, name="Quack-Trigram")
            model.train(training_text)

            # Show prediction examples
            for prompt in prompts:
                self.console.print(f"\n[bold]Prompt:[/bold] '{prompt}'")
                predictions = model.predict_next(prompt, num_predictions=3)

                self.console.print("[bold]Top predictions (trigram model):[/bold]")
                for i, (token, prob) in enumerate(predictions):
                    self.console.print(f"{i + 1}. '{token}' ({prob:.2%})")

            self.console.print("\n[bold]Trigram vs. Bigram:[/bold]")
            self.console.print(
                "• Trigram models consider the last two tokens, not just one")
            self.console.print("• This gives them more context for making predictions")
            self.console.print(
                "• But they still have limited context compared to modern LLMs")

        # Explain relation to tokenization
        self.console.print(Panel(
            "Tokenization is fundamental to language modeling because:\n\n"
            "• The quality of tokenization affects prediction quality\n"
            "• Efficient tokenizers reduce vocabulary size\n"
            "• Better tokenization leads to better context understanding\n"
            "• Modern LLMs inherit these foundations but use neural networks",
            title="Connection to Tokenization",
            border_style="yellow"
        ))

        # Final encouragement
        self.console.print(
            "\n[bold green]Congratulations![/bold green] You've completed Unit 2 of the tokenization tutorial.")
        self.console.print(
            "Continue to Unit 3 to learn about different tokenization techniques.")