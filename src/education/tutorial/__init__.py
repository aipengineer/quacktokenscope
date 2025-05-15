# src/quacktokenscope/education/tutorial/__init__.py
"""
Tutorial modules for QuackTokenScope education.

This package contains tutorial units for learning about tokenization
concepts in a structured way.
"""

from quacktokenscope.education.tutorial.base import TutorialUnit
from quacktokenscope.education.tutorial.unit1 import Unit1Tutorial
from quacktokenscope.education.tutorial.unit2 import Unit2Tutorial
from quacktokenscope.education.tutorial.unit3 import Unit3Tutorial
from quacktokenscope.education.tutorial.unit4 import Unit4Tutorial
from quacktokenscope.education.tutorial.unit5 import Unit5Tutorial
from quacktokenscope.education.tutorial.unit6 import Unit6Tutorial
from quacktokenscope.education.tutorial.unit7 import Unit7Tutorial
from quacktokenscope.education.tutorial.unit8 import Unit8Tutorial

# Map unit numbers to tutorial classes
TUTORIAL_UNITS = {
    1: Unit1Tutorial,
    2: Unit2Tutorial,
    3: Unit3Tutorial,
    4: Unit4Tutorial,
    5: Unit5Tutorial,
    6: Unit6Tutorial,
    7: Unit7Tutorial,
    8: Unit8Tutorial,
}

__all__ = [
    "TutorialUnit",
    "Unit1Tutorial",
    "Unit2Tutorial",
    "Unit3Tutorial",
    "Unit4Tutorial",
    "Unit5Tutorial",
    "Unit6Tutorial",
    "Unit7Tutorial",
    "Unit8Tutorial",
    "TUTORIAL_UNITS",
]