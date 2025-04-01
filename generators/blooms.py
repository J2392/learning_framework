"""
Bloom's Taxonomy question generator for educational content
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

class BloomsGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("Blooms")
    
    def _generate_content(self, normalized_input: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate Bloom's Taxonomy questions based on normalized input
        
        Args:
            normalized_input: Normalized input data
            
        Returns:
            Dictionary of questions by Bloom's level
        """
        # Extract normalized data
        concepts = normalized_input['concepts']
        context = normalized_input['context']
        
        # Log để debug
        logger.debug(f"Generating Bloom's questions for concepts: {concepts}")
        
        # Đảm bảo có concept để xử lý
        if not concepts:
            logger.warning("No concepts found, using default")
            concepts = ["general topic"]
        
        # Lấy concept đầu tiên để đảm bảo luôn có kết quả
        main_concept = concepts[0]
        
        questions = {
            "remember": [],
            "understand": [],
            "apply": [],
            "analyze": [],
            "evaluate": [],
            "create": []
        }
        
        # LUÔN thêm ít nhất một câu hỏi cho mỗi cấp độ Bloom
        
        # Remember level (Knowledge)
        questions["remember"].append(f"Define {main_concept} in your own words.")
        
        # Understand level (Comprehension)
        questions["understand"].append(f"Explain how {main_concept} works within {context}.")
        
        # Apply level (Application)
        questions["apply"].append(f"How would you use {main_concept} to solve a problem in {context}?")
        
        # Analyze level (Analysis)
        questions["analyze"].append(f"Compare and contrast different approaches to {main_concept}.")
        
        # Evaluate level (Evaluation)
        questions["evaluate"].append(f"Assess the effectiveness of {main_concept} in addressing challenges in {context}.")
        
        # Create level (Synthesis)
        questions["create"].append(f"Design a new approach that integrates {main_concept} with other aspects of {context}.")
        
        # Thêm câu hỏi cho các concepts khác nếu có
        for concept in concepts[1:3]:
            # Remember level
            remember_templates = [
                f"List the key components of {concept}.",
                f"Recall the main characteristics of {concept}."
            ]
            questions["remember"].append(random.choice(remember_templates))
            
            # Understand level
            understand_templates = [
                f"Describe the relationship between {concept} and {context}.",
                f"Summarize the main ideas behind {concept}."
            ]
            questions["understand"].append(random.choice(understand_templates))
            
            # Apply level
            apply_templates = [
                f"Demonstrate how {concept} could be implemented in a real-world situation.",
                f"Apply the principles of {concept} to address a specific challenge."
            ]
            questions["apply"].append(random.choice(apply_templates))
            
            # Analyze level
            analyze_templates = [
                f"Analyze the relationship between {concept} and other elements of {context}.",
                f"Examine the underlying assumptions of {concept}."
            ]
            questions["analyze"].append(random.choice(analyze_templates))
            
            # Evaluate level
            evaluate_templates = [
                f"Critique the current understanding of {concept}.",
                f"Justify the importance of {concept} in {context}."
            ]
            questions["evaluate"].append(random.choice(evaluate_templates))
            
            # Create level
            create_templates = [
                f"Develop a framework for implementing {concept} in a novel context.",
                f"Create a model that demonstrates the relationship between {concept} and related ideas."
            ]
            questions["create"].append(random.choice(create_templates))
        
        # Log kết quả để debug
        logger.info(f"Generated {sum(len(q) for q in questions.values())} Bloom's Taxonomy questions")
        
        return questions

# Create singleton instance
generator = BloomsGenerator()

def generate_blooms_questions(analysis_result: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Wrapper function to generate Bloom's Taxonomy questions
    
    Args:
        analysis_result: Analysis result containing text and concepts
        
    Returns:
        Dictionary of questions by Bloom's level
    """
    return generator.generate(analysis_result)