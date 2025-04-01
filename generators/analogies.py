"""
Analogies and examples generator for educational content
"""

from typing import Dict, Any, List
import random
import traceback

# Safe import của logger
try:
    from learning_framework.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .base_generator import BaseGenerator

class AnalogiesGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("Analogies")
    
    def _generate_content(self, normalized_input: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate analogies and examples based on normalized input
        
        Args:
            normalized_input: Normalized input data
            
        Returns:
            Dictionary of analogies and examples by category
        """
        # Extract normalized data
        concepts = normalized_input['concepts']
        context = normalized_input['context']
        
        # Log để debug
        logger.debug(f"Generating analogies for concepts: {concepts}")
        
        # Đảm bảo có concept để xử lý
        if not concepts:
            logger.warning("No concepts found, using default")
            concepts = ["general topic"]
        
        # Lấy concept đầu tiên để đảm bảo luôn có kết quả
        main_concept = concepts[0]
        
        result = {
            "analogies": [],
            "examples": [],
            "comparisons": [],
            "metaphors": []
        }
        
        # LUÔN thêm ít nhất một mục cho mỗi loại
        
        # Analogies
        result["analogies"].append(
            f"{main_concept} is like a bridge, connecting different ideas within {context}."
        )
        
        # Examples
        result["examples"].append(
            f"A practical example of {main_concept} is its application in solving real-world problems in {context}."
        )
        
        # Comparisons
        result["comparisons"].append(
            f"When comparing {main_concept} to traditional approaches in {context}, we see significant differences in methodology and outcomes."
        )
        
        # Metaphors
        result["metaphors"].append(
            f"{main_concept} is the foundation upon which understanding in {context} is built."
        )
        
        # Thêm nội dung cho các concepts khác nếu có
        for concept in concepts[1:3]:
            # Analogies
            analogy_templates = [
                f"{concept} functions similar to a map, guiding understanding through the complex terrain of {context}.",
                f"Just as a conductor orchestrates a symphony, {concept} organizes various elements within {context}."
            ]
            result["analogies"].append(random.choice(analogy_templates))
            
            # Examples
            example_templates = [
                f"One can observe {concept} in action when examining how experts approach challenges in {context}.",
                f"An illustration of {concept} can be seen in how it transforms theoretical knowledge into practical solutions in {context}."
            ]
            result["examples"].append(random.choice(example_templates))
            
            # Comparisons
            comparison_templates = [
                f"{concept} differs from conventional thinking in {context} by emphasizing innovative problem-solving strategies.",
                f"The distinction between {concept} and standard practices in {context} highlights the evolution of thought in this field."
            ]
            result["comparisons"].append(random.choice(comparison_templates))
            
            # Metaphors
            metaphor_templates = [
                f"In the garden of knowledge, {concept} is a perennial plant that continues to grow and evolve within {context}.",
                f"{concept} serves as the compass that guides exploration through the uncharted territories of {context}."
            ]
            result["metaphors"].append(random.choice(metaphor_templates))
        
        # Log kết quả để debug
        logger.info(f"Generated {sum(len(items) for items in result.values())} analogies and examples")
        
        return result

# Create singleton instance
generator = AnalogiesGenerator()

def generate_analogies(analysis_result: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Wrapper function to generate analogies and examples
    
    Args:
        analysis_result: Analysis result containing text and concepts
        
    Returns:
        Dictionary of analogies and examples by category
    """
    return generator.generate(analysis_result)