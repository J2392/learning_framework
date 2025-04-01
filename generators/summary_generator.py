"""
Generator for text summaries
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger('generators')

def generate_summary(analysis: Dict[str, Any]) -> List[str]:
    """Generate concise summaries at different levels of detail"""
    logger.info("Generating text summaries")
    
    # Default summary if no analysis is available
    if not analysis:
        return ["No summary available"]
    
    summaries = []
    
    # One-sentence summary
    summaries.append("One-sentence summary: " + _generate_one_sentence_summary(analysis))
    
    # Short paragraph summary
    summaries.append("Short summary: " + _generate_short_summary(analysis))
    
    # Detailed summary with key points
    detailed_summary = _generate_detailed_summary(analysis)
    summaries.append("Detailed summary:")
    summaries.extend(detailed_summary)
    
    # Key takeaways
    takeaways = _generate_key_takeaways(analysis)
    summaries.append("Key takeaways:")
    summaries.extend(takeaways)
    
    return summaries

def _generate_one_sentence_summary(analysis: Dict[str, Any]) -> str:
    """Generate a one-sentence summary"""
    if 'main_idea' in analysis:
        return analysis['main_idea']
    
    if 'concepts' in analysis and analysis['concepts']:
        concepts = ', '.join(analysis['concepts'][:3])
        return f"This text explores the concepts of {concepts} and their implications."
    
    return "This text discusses important concepts and their relationships."

def _generate_short_summary(analysis: Dict[str, Any]) -> str:
    """Generate a short paragraph summary"""
    if 'summary' in analysis and analysis['summary']:
        return analysis['summary']
    
    return "This material explores several interconnected concepts and their practical applications. It presents evidence and arguments that build toward a coherent understanding of the subject matter."

def _generate_detailed_summary(analysis: Dict[str, Any]) -> List[str]:
    """Generate a detailed summary with bullet points"""
    detailed = []
    
    # Use sections if available
    if 'sections' in analysis and analysis['sections']:
        for section in analysis['sections']:
            if 'title' in section and 'content' in section:
                detailed.append(f"• {section['title']}: {section['content']}")
    else:
        # Create generic summary points
        detailed.append("• Introduction to the main concepts and their significance")
        detailed.append("• Exploration of key relationships and dependencies")
        detailed.append("• Analysis of implications and potential applications")
        detailed.append("• Consideration of limitations and future directions")
    
    return detailed

def _generate_key_takeaways(analysis: Dict[str, Any]) -> List[str]:
    """Generate key takeaways from the analysis"""
    takeaways = []
    
    # Use key points if available
    if 'key_points' in analysis and analysis['key_points']:
        for i, point in enumerate(analysis['key_points'][:5]):
            takeaways.append(f"• Takeaway {i+1}: {point}")
    else:
        # Create generic takeaways
        takeaways.append("• Takeaway 1: Understanding the core concepts is essential")
        takeaways.append("• Takeaway 2: The relationships between concepts reveal deeper insights")
        takeaways.append("• Takeaway 3: Practical applications depend on context and constraints")
    
    return takeaways 