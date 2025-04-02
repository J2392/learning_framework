"""
Generator for Socratic questions
"""
import logging

logger = logging.getLogger(__name__)

def generate_socratic_questions(analysis_data):
    """Generate Socratic questions based on analyzed text"""
    try:
        text = analysis_data.get('text', '')
        if not text:
            logger.warning("No text provided for Socratic questions generation")
            return []
            
        # Get key concepts from analysis data or generate from text
        key_concepts = analysis_data.get('key_concepts', [])
        themes = analysis_data.get('themes', [])
        entities = analysis_data.get('entities', [])
        
        # Use these to form better questions
        questions = []
        
        # Add some default questions if we have key concepts
        if key_concepts:
            for concept in key_concepts[:3]:  # Use top 3 concepts
                questions.append(f"What is the significance of {concept} in this context?")
                questions.append(f"How does {concept} relate to other ideas presented?")
                
        # Add theme-based questions
        if themes:
            for theme in themes[:2]:  # Use top 2 themes
                questions.append(f"How does the theme of {theme} develop throughout the text?")
                questions.append(f"What evidence supports the theme of {theme}?")
        
        # Add general Socratic questions if we don't have enough
        if len(questions) < 5:
            general_questions = [
                "What are the key assumptions in this text?",
                "What evidence is presented to support the main claims?",
                "How might someone with a different perspective view this topic?",
                "What are the implications if these ideas are correct?",
                "How do these concepts connect to broader contexts?",
                "What contradictions or tensions exist within these arguments?"
            ]
            questions.extend(general_questions)
            
        # Return a reasonable number of questions
        return questions[:8]  # Limit to 8 questions
            
    except Exception as e:
        logger.error(f"Error generating Socratic questions: {str(e)}")
        return []