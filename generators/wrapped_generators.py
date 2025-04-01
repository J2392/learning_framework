"""
Generator functions to transform raw analysis into structured educational content
"""

from typing import Dict, Any, List
import logging

# Setup logger
logger = logging.getLogger('generators')

def generate_socratic_questions(analysis: Dict[str, Any]) -> List[str]:
    """Generate Socratic questions based on analysis"""
    logger.info(f"Generating Socratic questions from {len(analysis.get('concepts', []))} concepts")
    questions = []
    
    concepts = analysis.get('concepts', [])
    if not concepts:
        return ["No concepts found to generate questions"]
    
    # Generate at least one question per concept
    for concept in concepts:
        questions.append(f"What is the significance of {concept} in this context?")
        questions.append(f"How does {concept} relate to other ideas in the text?")
    
    return questions

def generate_multilevels(analysis: Dict[str, Any]) -> List[str]:
    """Generate multi-level explanations based on analysis"""
    logger.info("Generating multi-level explanations")
    explanations = []
    
    complexity = analysis.get('complexity_level', 'intermediate')
    summary = analysis.get('summary', '')
    
    if not summary:
        return ["No summary found to generate explanations"]
    
    # Basic explanation
    explanations.append(f"Basic explanation: {summary}")
    
    # Add more detailed explanations based on complexity
    if complexity in ['intermediate', 'advanced', 'expert']:
        explanations.append(f"Intermediate explanation: {summary} This connects to the broader context of {analysis.get('context', 'the subject')}.")
    
    if complexity in ['advanced', 'expert']:
        keywords = ', '.join(analysis.get('keywords', [])[:3])
        explanations.append(f"Advanced explanation: The concepts of {keywords} form the theoretical foundation for understanding this topic.")
    
    if complexity == 'expert':
        explanations.append("Expert explanation: This material requires synthesizing multiple advanced concepts and applying critical analysis.")
    
    return explanations

def generate_practice_questions(analysis: Dict[str, Any]) -> List[str]:
    """Generate practice questions based on analysis"""
    logger.info("Generating practice questions")
    questions = []
    
    keywords = analysis.get('keywords', [])
    if not keywords:
        return ["No keywords found to generate practice questions"]
    
    # Generate questions based on keywords
    for keyword in keywords[:5]:
        questions.append(f"Explain the concept of {keyword} in your own words.")
    
    return questions

# Map of available generators
AVAILABLE_GENERATORS = {
    "socratic": generate_socratic_questions,
    "multilevel": generate_multilevels,
    "practice": generate_practice_questions
}