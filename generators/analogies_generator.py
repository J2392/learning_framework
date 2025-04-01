"""
Generator for analogies and metaphors
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger('generators')

def generate_analogies(analysis: Dict[str, Any]) -> List[str]:
    """Generate analogies and metaphors to explain complex concepts"""
    logger.info("Generating analogies and metaphors")
    
    # Default analogies if no analysis is available
    if not analysis:
        return ["No analogies available"]
    
    analogies = []
    
    # Extract concepts from analysis
    concepts = analysis.get('concepts', [])
    if not concepts:
        return ["No concepts found to generate analogies"]
    
    # Simple analogies
    analogies.append("Understanding this concept is like building a house: you need a strong foundation before adding complex structures.")
    analogies.append("This process can be compared to a river flowing: it follows the path of least resistance while gradually reshaping its environment.")
    
    # Domain-specific analogies
    if 'domain' in analysis:
        domain = analysis['domain']
        if domain == 'technology':
            analogies.append("This system architecture works like a city's transportation network: different components must communicate efficiently to function as a whole.")
        elif domain == 'science':
            analogies.append("These molecules interact like dancers in a choreographed performance: each movement precisely timed and coordinated.")
        elif domain == 'business':
            analogies.append("Market dynamics resemble an ecosystem: each species (company) adapts to changes or risks extinction.")
            
    # Concept-specific analogies
    for concept in concepts[:3]:  # Limit to top 3 concepts
        analogies.append(f"The concept of {concept} is similar to {_get_analogy_for_concept(concept)}")
    
    return analogies

def _get_analogy_for_concept(concept: str) -> str:
    """Helper function to generate an analogy for a specific concept"""
    # Dictionary of common concept analogies
    analogies = {
        "algorithms": "recipes in a cookbook: they provide step-by-step instructions to achieve specific outcomes",
        "data": "raw materials in a factory: valuable only when processed and transformed",
        "learning": "growing a garden: it requires regular attention, proper conditions, and patience",
        "development": "a journey: the path matters as much as the destination",
        "analysis": "using a microscope: examining details reveals patterns invisible to the naked eye"
    }
    
    # Default analogy if concept not in dictionary
    return analogies.get(concept.lower(), "exploring unknown territory: challenging but potentially rewarding")