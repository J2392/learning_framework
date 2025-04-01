"""
Generator for Chain of Thought reasoning
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger('generators')

def generate_chain_of_thought(analysis: Dict[str, Any]) -> List[str]:
    """Generate step-by-step reasoning chain for complex concepts"""
    logger.info("Generating Chain of Thought reasoning")
    
    # Default chain if no analysis is available
    if not analysis:
        return ["No Chain of Thought reasoning available"]
    
    chain = []
    
    # Extract main concepts
    concepts = analysis.get('concepts', [])
    if not concepts:
        return ["No concepts found to generate Chain of Thought"]
    
    # Introduction to the chain
    chain.append("CHAIN OF THOUGHT REASONING:")
    chain.append("Let's break down the key concepts step by step:")
    
    # Generate reasoning steps for each concept
    for i, concept in enumerate(concepts[:3]):  # Limit to top 3 concepts
        chain.append(f"\nCONCEPT {i+1}: {concept.upper()}")
        steps = _generate_reasoning_steps(concept, analysis)
        chain.extend(steps)
    
    # Conclusion
    chain.append("\nINTEGRATIVE CONCLUSION:")
    chain.append("• These concepts interconnect to form a comprehensive understanding of the subject")
    chain.append("• The reasoning chain reveals both explicit connections and implicit relationships")
    chain.append("• This step-by-step approach helps identify gaps in understanding and areas for further exploration")
    
    return chain

def _generate_reasoning_steps(concept: str, analysis: Dict[str, Any]) -> List[str]:
    """Generate reasoning steps for a specific concept"""
    steps = []
    
    # Definition
    steps.append(f"• Step 1: Define {concept}")
    steps.append(f"  - {concept} refers to a key element in this domain")
    steps.append(f"  - It can be understood as a fundamental building block")
    
    # Context
    steps.append(f"• Step 2: Contextualize {concept}")
    steps.append(f"  - {concept} exists within a broader framework of related ideas")
    steps.append(f"  - Historical development provides important context")
    
    # Analysis
    steps.append(f"• Step 3: Analyze components of {concept}")
    steps.append(f"  - Breaking down {concept} reveals its constituent elements")
    steps.append(f"  - Each component serves a specific function")
    
    # Implications
    steps.append(f"• Step 4: Examine implications of {concept}")
    steps.append(f"  - Understanding {concept} leads to insights about related processes")
    steps.append(f"  - Practical applications emerge from theoretical understanding")
    
    # Integration
    steps.append(f"• Step 5: Integrate {concept} with other concepts")
    steps.append(f"  - {concept} connects with other ideas through shared principles")
    steps.append(f"  - These connections reveal a more comprehensive understanding")
    
    return steps