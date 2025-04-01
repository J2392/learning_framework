# analyzers/__init__.py

"""
Analyzer module initialization
"""

# Expose main classes
from .text_analyzer import TextAnalyzer
from .perplexity_analyzer import PerplexityAnalyzer

# Version
__version__ = "0.1.0"

__all__ = [
    'TextAnalyzer',
    'PerplexityAnalyzer'
]