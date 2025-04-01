"""
Practice questions generator for educational content
"""

from typing import Dict, Any, List
import random
import traceback

# Safe import của logger
try:
    from utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .base_generator import BaseGenerator

class PracticeGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("Practice")
    
    def _generate_content(self, normalized_input: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate practice questions based on normalized input
        
        Args:
            normalized_input: Normalized input data
            
        Returns:
            Dictionary of practice questions by type
        """
        # Extract normalized data
        concepts = normalized_input['concepts']
        context = normalized_input['context']
        
        # Log để debug
        logger.debug(f"Generating practice questions for concepts: {concepts}")
        
        # Đảm bảo có concept để xử lý
        if not concepts:
            logger.warning("No concepts found, using default")
            concepts = ["general topic"]
        
        # Lấy concept đầu tiên để đảm bảo luôn có kết quả
        main_concept = concepts[0]
        
        questions = {
            "multiple_choice": [],
            "short_answer": [],
            "discussion": []
        }
        
        # LUÔN thêm ít nhất một câu hỏi cho mỗi loại
        questions["multiple_choice"].append(
            f"Which of the following best describes {main_concept}?\n"
            "a) A systematic approach to understanding knowledge\n"
            "b) A framework for organizing information\n"
            "c) A method for analyzing complex ideas\n"
            "d) All of the above"
        )
        
        questions["short_answer"].append(
            f"Briefly explain how {main_concept} relates to {context}."
        )
        
        questions["discussion"].append(
            f"Analyze the importance of {main_concept} in the broader context of {context}."
        )
        
        # Thêm câu hỏi cho các concepts khác nếu có
        for concept in concepts[1:3]:
            # Multiple choice questions
            mc_templates = [
                f"What is the primary purpose of {concept} in {context}?\n"
                "a) To organize information\n"
                "b) To facilitate understanding\n"
                "c) To analyze complex ideas\n"
                "d) To synthesize knowledge",
                
                f"Which aspect of {concept} is most relevant to {context}?\n"
                "a) Its theoretical framework\n"
                "b) Its practical applications\n"
                "c) Its historical development\n"
                "d) Its future implications"
            ]
            questions["multiple_choice"].append(random.choice(mc_templates))
            
            # Short answer questions
            sa_templates = [
                f"Describe two key features of {concept}.",
                f"Explain the significance of {concept} in relation to {context}."
            ]
            questions["short_answer"].append(random.choice(sa_templates))
            
            # Discussion questions
            disc_templates = [
                f"Evaluate the effectiveness of {concept} in addressing challenges within {context}.",
                f"Discuss how different perspectives might approach {concept} differently."
            ]
            questions["discussion"].append(random.choice(disc_templates))
        
        # Log kết quả để debug
        logger.info(f"Generated {sum(len(qs) for qs in questions.values())} practice questions")
        
        return questions

# Create singleton instance
generator = PracticeGenerator()

def generate_practice_questions(analysis_result: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Wrapper function to generate practice questions
    
    Args:
        analysis_result: Analysis result containing text and concepts
        
    Returns:
        Dictionary of practice questions by type
    """
    return generator.generate(analysis_result)