"""
Summary generator for educational content
"""

from typing import Dict, Any, List
import traceback

# Safe import của logger
try:
    from utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .base_generator import BaseGenerator

class SummaryGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("Summary")
    
    def _generate_content(self, normalized_input: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate summary based on normalized input
        
        Args:
            normalized_input: Normalized input data
            
        Returns:
            Dictionary of summary content
        """
        # Extract normalized data
        text = normalized_input['text']
        concepts = normalized_input['concepts']
        context = normalized_input['context']
        
        # Log để debug
        logger.debug(f"Generating summary for text of length {len(text)}, concepts: {concepts}")
        
        # Đảm bảo có concept để xử lý
        if not concepts:
            logger.warning("No concepts found, using default")
            concepts = ["general topic"]
        
        summary = {
            "brief": [],
            "detailed": [],
            "key_points": []
        }
        
        # LUÔN thêm ít nhất một mục cho mỗi loại
        
        # Brief summary
        concepts_str = ", ".join(concepts[:3])
        summary["brief"].append(f"This text discusses {concepts_str} in the context of {context}.")
        
        # Detailed summary
        detailed_summary = f"The content examines {concepts[0]} and its relationship to {context}. "
        if len(concepts) > 1:
            detailed_summary += f"It explores key aspects including {', '.join(concepts[1:3])}."
        else:
            detailed_summary += f"It explores key aspects related to this concept."
        summary["detailed"].append(detailed_summary)
        
        # Key points - luôn có ít nhất 3 điểm chính
        summary["key_points"].append(f"{concepts[0]} is an important element in understanding {context}.")
        summary["key_points"].append(f"The relationship between {concepts[0]} and {context} highlights significant patterns and trends.")
        summary["key_points"].append(f"Understanding {concepts[0]} requires consideration of multiple perspectives and approaches.")
        
        # Thêm key points cho các concepts khác nếu có
        for concept in concepts[1:3]:
            key_point = f"{concept} contributes to the broader understanding of {context} through its unique characteristics and applications."
            summary["key_points"].append(key_point)
        
        # Log kết quả để debug
        logger.info(f"Generated summary with {sum(len(points) for points in summary.values())} components")
        
        return summary

# Create singleton instance
generator = SummaryGenerator()

def generate_summary(analysis_result: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Wrapper function to generate summary
    
    Args:
        analysis_result: Analysis result containing text and concepts
        
    Returns:
        Dictionary of summary content
    """
    return generator.generate(analysis_result)