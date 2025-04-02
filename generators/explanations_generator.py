"""
Generator for multi-level explanations
"""
import logging

logger = logging.getLogger(__name__)

def generate_explanations(analysis_data):
    """Generate multi-level explanations based on analyzed text"""
    try:
        text = analysis_data.get('text', '')
        if not text:
            logger.warning("No text provided for explanations generation")
            return []
            
        # Get key concepts and other analysis data
        key_concepts = analysis_data.get('key_concepts', [])
        summary = analysis_data.get('summary', [])
        
        # Generate explanations at different levels
        explanations = []
        
        # Basic explanation - for beginners
        basic = "Basic explanation: "
        if summary:
            basic += summary[0] if isinstance(summary, list) else summary
        else:
            basic += "This text covers fundamental concepts related to the main topic."
        explanations.append(basic)
        
        # Intermediate explanation - more detail
        intermediate = "Intermediate explanation: "
        if key_concepts and len(key_concepts) >= 2:
            intermediate += f"The text explores the relationship between {key_concepts[0]} and {key_concepts[1]}, "
            intermediate += "showing how these concepts interact and influence each other."
        else:
            intermediate += "The text presents a more nuanced view of the subject, considering various perspectives and applications."
        explanations.append(intermediate)
        
        # Advanced explanation - complex analysis
        advanced = "Advanced explanation: "
        advanced += "At a deeper level, this content examines the theoretical foundations and implications of these ideas, "
        advanced += "challenging readers to consider complex interconnections and systemic factors."
        explanations.append(advanced)
        
        return explanations
            
    except Exception as e:
        logger.error(f"Error generating explanations: {str(e)}")
        return []