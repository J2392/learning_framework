"""
Key terms generator for educational content
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

class KeyTermsGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("KeyTerms")
    
    def _generate_content(self, normalized_input: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate key terms and definitions based on normalized input
        
        Args:
            normalized_input: Normalized input data
            
        Returns:
            Dictionary of key terms by category
        """
        # Extract normalized data
        concepts = normalized_input['concepts']
        context = normalized_input['context']
        keywords = normalized_input.get('keywords', [])
        
        # Log để debug
        logger.debug(f"Generating key terms for concepts: {concepts}, keywords: {keywords}")
        
        # Đảm bảo có concept để xử lý
        if not concepts:
            logger.warning("No concepts found, using default")
            concepts = ["general topic"]
        
        terms = {
            "core_concepts": [],
            "related_terms": [],
            "definitions": []
        }
        
        # LUÔN thêm các khái niệm cốt lõi
        for concept in concepts[:3]:
            terms["core_concepts"].append(concept)
        
        # Đảm bảo có ít nhất một khái niệm cốt lõi
        if not terms["core_concepts"]:
            terms["core_concepts"].append("main concept")
        
        # Tạo các thuật ngữ liên quan
        related_terms_templates = [
            f"{concepts[0]} framework",
            f"{concepts[0]} methodology",
            f"{concepts[0]} in {context}",
            f"{concepts[0]} theory",
            f"{concepts[0]} application"
        ]
        
        # Thêm ít nhất 3 thuật ngữ liên quan
        for i in range(min(3, len(related_terms_templates))):
            terms["related_terms"].append(related_terms_templates[i])
        
        # Thêm từ keywords nếu có
        for keyword in keywords[:2]:
            if keyword not in terms["core_concepts"] and keyword not in terms["related_terms"]:
                terms["related_terms"].append(keyword)
        
        # Tạo định nghĩa cho tất cả các thuật ngữ
        all_terms = terms["core_concepts"] + terms["related_terms"]
        for term in all_terms:
            definition = f"{term}: A key concept in {context} that refers to the systematic approach to understanding and implementing knowledge."
            terms["definitions"].append(definition)
        
        # Log kết quả để debug
        logger.info(f"Generated {sum(len(ts) for ts in terms.values())} key terms and definitions")
        
        return terms

# Create singleton instance
generator = KeyTermsGenerator()

def generate_keyterms(analysis_result: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Wrapper function to generate key terms
    
    Args:
        analysis_result: Analysis result containing text and concepts
        
    Returns:
        Dictionary of key terms by category
    """
    return generator.generate(analysis_result)