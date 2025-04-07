# src/quacktokenscope/cli.py
"""
CLI compatibility module.

This module provides backward compatibility for imports from quacktokenscope.cli
which now points to demo_cli.py
"""

# Re-export everything from demo_cli.py
from quacktokenscope.demo_cli import *

# Export the main entry point
__all__ = ["main", "cli"]