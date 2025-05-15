# src/quacktokenscope/education/tutorial/unit6.py
"""
Unit 6: API Costs & Optimizing Prompts tutorial.

This module implements the sixth tutorial unit, which explores
how tokenization affects API costs and prompt optimization.
"""

from rich.prompt import Prompt
from rich.panel import Panel

from quacktokenscope.education.tutorial.base import TutorialUnit
from quacktokenscope.education.cost_calculator import display_cost_summary
from quacktokenscope.education.challenges.what_if import (
    run_what_if_analysis,
    display_what_if_results
)


class Unit6Tutorial(TutorialUnit):
    """Unit 6: API Costs & Optimizing Prompts tutorial."""

    title = "Unit 6: API Costs & Optimizing Prompts"
    description = "Let's explore how tokenization affects API costs..."

    def run(self) -> None:
        """Run Unit 6 tutorial."""
        super().run()

        # Sample text
        sample_text = """
        Dear AI Assistant,

        I hope this message finds you well. I am writing to inquire about the process of photosynthesis in plants. 

        Could you please provide me with a detailed explanation of how photosynthesis works, including all the key stages, 
        chemical reactions, and the importance of this process for life on Earth?

        Thank you very much for your assistance.

        Best regards,
        User
        """

        # Tokenize the sample text
        cost_tokenizer = self.get_primary_tokenizer()
        token_count = len(cost_tokenizer.tokenize(sample_text)[0])

        # Calculate and display cost
        self.console.print("\n[bold]Original Prompt:[/bold]")
        self.console.print(Panel(sample_text, title="Sample Prompt"))

        self.console.print(f"\n[bold]Token count:[/bold] {token_count}")

        # Cost calculation
        self.console.print(display_cost_summary(
            sample_text,
            token_count,
            0,
            "gpt-4-turbo",
            self.console
        ))

        # Optimized version
        optimized_text = """
        Explain photosynthesis in plants, including stages, chemical reactions, and its importance for life on Earth.
        """

        optimized_count = len(cost_tokenizer.tokenize(optimized_text)[0])

        self.console.print("\n[bold]Optimized Prompt:[/bold]")
        self.console.print(Panel(optimized_text, title="Optimized Prompt"))

        self.console.print(f"\n[bold]Token count:[/bold] {optimized_count}")

        # Cost calculation for optimized
        self.console.print(display_cost_summary(
            optimized_text,
            optimized_count,
            0,
            "gpt-4-turbo",
            self.console
        ))

        # Optimization principles
        self.console.print("\n[bold]Prompt Optimization Principles:[/bold]")
        self.console.print("• Remove unnecessary formalities and fluff")
        self.console.print("• Use direct, concise language")
        self.console.print("• Eliminate redundant information")
        self.console.print("• Be specific about what you need")
        self.console.print("• Consider the tradeoff between clarity and brevity")

        # Interactive element
        if Prompt.ask(
                "\nWould you like to see 'What If' scenarios for token optimization?",
                choices=["y", "n"], default="y") == "y":
            analysis = run_what_if_analysis(
                sample_text,
                cost_tokenizer,
                "gpt-4-turbo",
            )
            self.console.print(display_what_if_results(analysis, self.console))

        # Final encouragement
        self.console.print(
            "\n[bold green]Congratulations![/bold green] You've completed Unit 6 of the tokenization tutorial.")
        self.console.print(
            "Continue to Unit 7 to learn about tokenizing diverse texts.")