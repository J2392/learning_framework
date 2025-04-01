"""
Generator for Bloom's Taxonomy questions
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger('generators')

def generate_blooms_questions(analysis: Dict[str, Any]) -> List[str]:
    """Generate questions using Bloom's Taxonomy"""
    logger.info("Generating Bloom's Taxonomy questions")
    
    # Default questions if no analysis is available
    if not analysis:
        return ["No Bloom's taxonomy questions available"]
    
    questions = []
    
    # Knowledge level
    questions.append("Define the key concepts presented in this text.")
    questions.append("List the main points discussed in the material.")
    
    # Comprehension level
    questions.append("Explain the relationship between the main ideas.")
    questions.append("Summarize the core argument of this text.")
    
    # Application level
    questions.append("How would you apply these concepts in a real-world situation?")
    questions.append("Give an example of how these ideas might be implemented.")
    
    # Analysis level
    questions.append("Compare and contrast the different perspectives presented.")
    questions.append("What evidence supports the main claims in this text?")
    
    # Synthesis level
    questions.append("How would you design a system that incorporates these principles?")
    questions.append("What might be an alternative approach to these problems?")
    
    # Evaluation level
    questions.append("Evaluate the effectiveness of the proposed solutions.")
    questions.append("Which arguments are most compelling, and why?")
    
    return questions