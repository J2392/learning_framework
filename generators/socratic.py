"""
Socratic questioning generator for educational content
"""

from typing import Dict, Any, List
import random
import traceback

# Safe import của logger
try:
    from utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .base_generator import BaseGenerator

class SocraticGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("Socratic")
    
    def _generate_content(self, normalized_input: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate Socratic questions based on normalized input
        
        Args:
            normalized_input: Normalized input data
            
        Returns:
            Dictionary of Socratic questions by category
        """
        concepts = normalized_input['concepts']
        context = normalized_input['context']
        
        logger.debug(f"Generating Socratic questions for: {concepts}")
        
        questions = {
            "conceptual": [],
            "clarifying": [],
            "probing": [],
            "analytical": []
        }
        
        # Always generate at least one question for each type
        main_concept = concepts[0]
        
        # Conceptual questions
        questions["conceptual"].append(
            f"What are the fundamental principles underlying {main_concept} in the context of {context}?"
        )
        
        # Clarifying questions
        questions["clarifying"].append(
            f"Could you elaborate on how {main_concept} specifically impacts {context}?"
        )
        
        # Probing questions
        questions["probing"].append(
            f"What evidence supports the relationship between {main_concept} and outcomes in {context}?"
        )
        
        # Analytical questions
        questions["analytical"].append(
            f"How might different stakeholders in {context} view the implications of {main_concept}?"
        )
        
        # Add questions for additional concepts
        for concept in concepts[1:3]:
            questions["conceptual"].append(
                f"How does {concept} relate to core principles in {context}?"
            )
            questions["clarifying"].append(
                f"What specific aspects of {concept} need further examination in {context}?"
            )
            questions["probing"].append(
                f"What assumptions underlie the relationship between {concept} and {context}?"
            )
            questions["analytical"].append(
                f"How might changes in {concept} affect different aspects of {context}?"
            )
        
        logger.info(f"Generated {sum(len(q) for q in questions.values())} Socratic questions")
        
        return questions

# Create singleton instance
generator = SocraticGenerator()

def generate_socratic_questions(analysis_result: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Wrapper function to generate Socratic questions
    
    Args:
        analysis_result: Analysis result containing text and concepts
        
    Returns:
        Dictionary of Socratic questions by category
    """
    return generator.generate(analysis_result)