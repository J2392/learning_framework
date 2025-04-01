"""
Consolidated access point for all thinking method generators.
"""

from typing import Dict, Any

# Import các generator functions từ các module riêng
from .socratic import generate_socratic_questions
from .multilevel import generate_multilevel_explanations
from .practice import generate_practice_questions
from .blooms import generate_blooms_questions
from .summarizer import generate_summary
from .keyterms import generate_keyterms
from .analogies import generate_analogies

# Available generators dictionary
AVAILABLE_GENERATORS = {
    "socratic": generate_socratic_questions,
    "multilevel": generate_multilevel_explanations,
    "practice": generate_practice_questions,
    "blooms": generate_blooms_questions,
    "summary": generate_summary,
    "keyterms": generate_keyterms,
    "analogies": generate_analogies,
}