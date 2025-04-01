"""
Generator for key terms and definitions
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger('generators')

def generate_key_terms(analysis: Dict[str, Any]) -> List[str]:
    """Generate key terms and definitions from analysis"""
    logger.info("Generating key terms and definitions")
    
    # Default terms if no analysis is available
    if not analysis:
        return [
            "Term 1: Basic definition",
            "Term 2: Technical meaning",
            "Term 3: Contextual usage"
        ]
    
    # Extract keywords from analysis
    keywords = analysis.get('keywords', [])
    if not keywords:
        return ["No key terms available"]
    
    terms = []
    for i, keyword in enumerate(keywords[:10]):  # Limit to top 10 keywords
        term_def = f"Term {i+1}: {keyword} - "
        
        # Add definition context if available
        if 'definitions' in analysis and keyword in analysis['definitions']:
            term_def += analysis['definitions'][keyword]
        else:
            term_def += "Definition not available"
            
        terms.append(term_def)
    
    return terms