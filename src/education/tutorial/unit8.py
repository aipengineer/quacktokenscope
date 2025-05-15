# src/quacktokenscope/education/tutorial/unit8.py
"""
Unit 8: Wrapping Up & Next Steps tutorial.

This module implements the eighth tutorial unit, which summarizes
the key concepts and presents next steps.
"""

from rich.prompt import Prompt
from rich.panel import Panel

from quacktokenscope.education.tutorial.base import TutorialUnit


class Unit8Tutorial(TutorialUnit):
    """Unit 8: Wrapping Up & Next Steps tutorial."""

    title = "Unit 8: Wrapping Up & Next Steps"
    description = "Congratulations on completing the tokenization tutorial!"

    def run(self) -> None:
        """Run Unit 8 tutorial."""
        super().run()

        # Summary of key concepts
        self.console.print("\n[bold]Key Concepts Reviewed:[/bold]")
        self.console.print("• Tokens are the basic units that LLMs process text")
        self.console.print(
            "• Different tokenizers use different strategies (BPE, WordPiece, etc.)")
        self.console.print("• Token count affects API costs and context limits")
        self.console.print("• Efficient tokenization leads to better model performance")
        self.console.print("• Prompt engineering can optimize token usage")

        # Best practices
        self.console.print(Panel(
            "• Be concise and direct in your prompts\n"
            "• Remove unnecessary formatting and pleasantries\n"
            "• Test different prompt phrasings to optimize token usage\n"
            "• Consider token limitations when designing applications\n"
            "• Choose the appropriate model for your task and budget",
            title="Best Practices",
            border_style="green"
        ))

        # Advanced concepts to explore
        self.console.print("\n[bold]Advanced Topics to Explore:[/bold]")
        self.console.print("• Custom tokenizer training")
        self.console.print("• Multilingual tokenization challenges")
        self.console.print("• Tokenization's impact on model biases")
        self.console.print("• Token merging techniques for efficiency")
        self.console.print("• Token pruning and context compression")

        # Final challenge
        self.console.print(
            "\n[bold yellow]Final Challenge: The Ultimate Token Optimizer[/bold yellow]")
        self.console.print(
            "Take this prompt and optimize it for token efficiency while preserving meaning:")

        challenge_prompt = """
        I would like to kindly request, if it's not too much trouble, for you to provide me with a comprehensive and detailed explanation regarding the historical development of artificial intelligence throughout the 20th and 21st centuries, including all of the key milestones, important researchers, and significant breakthroughs that have contributed to the field as we know it today. Thank you very much for your assistance with this matter.
        """

        self.console.print(Panel(challenge_prompt, title="Verbose Prompt"))

        if Prompt.ask("\nWould you like to see a token-optimized version?",
                      choices=["y", "n"], default="y") == "y":
            optimized_prompt = "Explain AI's historical development in the 20th-21st centuries, including key milestones, researchers, and breakthroughs."

            tokenizer_instance = self.get_primary_tokenizer()

            original_count = len(tokenizer_instance.tokenize(challenge_prompt)[0])
            optimized_count = len(tokenizer_instance.tokenize(optimized_prompt)[0])

            savings = original_count - optimized_count
            savings_percent = (savings / original_count) * 100

            self.console.print(Panel(optimized_prompt, title="Optimized Prompt"))

            self.console.print(f"\nOriginal prompt: {original_count} tokens")
            self.console.print(f"Optimized prompt: {optimized_count} tokens")
            self.console.print(
                f"[green]Savings: {savings} tokens ({savings_percent:.1f}%)[/green]")

            # Cost comparison
            original_cost = (
                                        original_count / 1000) * 0.01  # Assuming $0.01 per 1K tokens
            optimized_cost = (optimized_count / 1000) * 0.01

            self.console.print(f"\nOriginal cost: ${original_cost:.4f}")
            self.console.print(f"Optimized cost: ${optimized_cost:.4f}")
            self.console.print(
                f"[green]Cost savings: ${original_cost - optimized_cost:.4f}[/green]")

        # Final thoughts and next steps
        self.console.print(Panel(
            "You've completed the QuackTokenScope tutorial on tokenization!\n\n"
            "Continue exploring with the other commands:\n"
            "• quacktool tokenscope edu visualize\n"
            "• quacktool tokenscope edu calculate-cost\n"
            "• quacktool tokenscope edu challenge\n"
            "• quacktool tokenscope edu language-model\n\n"
            "Remember: Understanding tokenization is key to effective prompt engineering and cost optimization!",
            title="🎓 Congratulations!",
            border_style="green"
        ))