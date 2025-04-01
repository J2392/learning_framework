"""
Generator module initialization
"""

from .socratic import generate_socratic_questions
from .multilevel import generate_multilevel_explanations
from .practice import generate_practice_questions
from .blooms import generate_blooms_questions
from .keyterms import generate_keyterms
from .analogies import generate_analogies
from .summarizer import generate_summary

__all__ = [
    'generate_socratic_questions',
    'generate_multilevel_explanations',
    'generate_practice_questions',
    'generate_blooms_questions',
    'generate_keyterms',
    'generate_analogies',
    'generate_summary'
]

# Version
__version__ = "0.1.0"