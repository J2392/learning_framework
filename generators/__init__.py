"""
Available generators for the learning framework
"""

from generators.questions_generator import generate_socratic_questions
from generators.explanations_generator import generate_explanations
from generators.practice_generator import generate_practice_questions
from generators.blooms_generator import generate_blooms_questions
from generators.key_terms_generator import generate_key_terms
from generators.analogies_generator import generate_analogies
from generators.summary_generator import generate_summary

# Exported generators dictionary
AVAILABLE_GENERATORS = {
    "questions": generate_socratic_questions,
    "explanations": generate_explanations,
    "practice": generate_practice_questions,
    "blooms": generate_blooms_questions,
    "key_terms": generate_key_terms,
    "analogies": generate_analogies,
    "summary": generate_summary
}

__all__ = ['AVAILABLE_GENERATORS']