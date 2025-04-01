"""
Multi-level explanation generator for educational content
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

class MultilevelGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("Multilevel")
    
    def _generate_content(self, normalized_input: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate multi-level explanations based on normalized input
        
        Args:
            normalized_input: Normalized input data
            
        Returns:
            Dictionary of explanations by complexity level
        """
        # Extract normalized data
        concepts = normalized_input['concepts']
        context = normalized_input['context']
        
        # Log để debug
        logger.debug(f"Generating multi-level explanations for: {concepts}")
        
        # Đảm bảo có concept để xử lý
        if not concepts:
            logger.warning("No concepts found, using default")
            concepts = ["general topic"]
        
        # Lấy concept đầu tiên để đảm bảo luôn có kết quả
        main_concept = concepts[0]
        
        # Khởi tạo kết quả với giá trị mặc định
        explanations = {
            "basic": [],
            "intermediate": [],
            "advanced": [],
            "expert": []
        }
        
        # Basic level
        explanations["basic"].append(
            f"At its most basic level, {main_concept} in {context} involves understanding fundamental principles and their direct applications."
        )
        
        # Intermediate level
        explanations["intermediate"].append(
            f"At an intermediate level, {main_concept} demonstrates how different components in {context} interact and influence each other."
        )
        
        # Advanced level
        explanations["advanced"].append(
            f"At an advanced level, {main_concept} reveals complex relationships and systemic effects within {context}, including feedback loops and emergent properties."
        )
        
        # Expert level
        explanations["expert"].append(
            f"At an expert level, {main_concept} encompasses theoretical frameworks, practical implementations, and critical analysis of limitations and future directions in {context}."
        )
        
        # Thêm giải thích cho các concepts khác nếu có
        for concept in concepts[1:3]:
            explanations["basic"].append(
                f"{concept} provides a foundation for understanding basic principles in {context}."
            )
            explanations["intermediate"].append(
                f"{concept} demonstrates interconnected relationships within {context}."
            )
            explanations["advanced"].append(
                f"{concept} reveals complex dynamics and systemic effects in {context}."
            )
            explanations["expert"].append(
                f"{concept} contributes to theoretical and practical advancements in {context}."
            )
        
        # Log kết quả để debug
        logger.info(f"Generated {sum(len(e) for e in explanations.values())} multi-level explanations")
        
        return explanations

# Create singleton instance
generator = MultilevelGenerator()

def generate_multilevel_explanations(analysis_result: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Wrapper function to generate multi-level explanations
    
    Args:
        analysis_result: Analysis result containing text and concepts
        
    Returns:
        Dictionary of explanations by complexity level
    """
    return generator.generate(analysis_result)