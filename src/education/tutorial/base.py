# src/quacktokenscope/education/tutorial/base.py
"""
Base class for tutorial units.

This module provides the base class that tutorial units inherit from.
"""

from typing import Any
from rich.console import Console
from quackcore.logging import get_logger

logger = get_logger(__name__)


class TutorialUnit:
    """Base class for tutorial units."""

    title = "Generic Tutorial Unit"
    description = "A tutorial unit"

    def __init__(self, tokenizers: dict[str, Any], console: Console = None):
        """
        Initialize the tutorial unit.

        Args:
            tokenizers: Dictionary of available tokenizers
            console: Optional console for display
        """
        self.tokenizers = tokenizers
        self.console = console or Console()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def run(self) -> None:
        """
        Run the tutorial unit.

        This method should be overridden by subclasses to implement
        the specific tutorial content.
        """
        self.console.print(f"\n[bold yellow]===== {self.title} =====[/bold yellow]")
        self.console.print(self.description)

        # Subclasses should implement specific tutorial content
        self.logger.debug(f"Running tutorial unit: {self.title}")

    def get_primary_tokenizer(self):
        """
        Get a primary tokenizer for examples.

        Returns:
            A tokenizer instance to use for examples
        """
        # Prefer tiktoken if available, otherwise use the first available tokenizer
        return self.tokenizers.get("tiktoken", next(iter(self.tokenizers.values())))