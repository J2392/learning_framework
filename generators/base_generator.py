"""
Base generator class for standardized input processing and error handling
"""

from typing import Dict, Any, List, Optional
import traceback

# Safe import của logger
try:
    from learning_framework.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class BaseGenerator:
    def __init__(self, name: str):
        self.name = name
        logger.debug(f"Initializing {self.name} generator")
    
    def generate(self, analysis_result: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Main generate method that handles input normalization and error handling
        """
        try:
            # Normalize input
            normalized_input = self._normalize_input(analysis_result)
            
            # Generate content
            result = self._generate_content(normalized_input)
            
            # Validate result
            return self._ensure_valid_result(result)
            
        except Exception as e:
            logger.error(f"Error in {self.name} generator: {str(e)}")
            logger.error(traceback.format_exc())
            # Return empty but valid structure
            return self._get_default_result()
    
    def _normalize_input(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize input data to ensure required fields exist
        """
        normalized = {
            'text': analysis_result.get('text', ''),
            'concepts': [],
            'context': 'general',
            'keywords': []
        }

        # Extract concepts from different possible locations
        if 'concepts' in analysis_result:
            normalized['concepts'] = analysis_result['concepts']
        elif 'entities' in analysis_result:
            normalized['concepts'] = analysis_result['entities']
        
        # Extract context
        if 'context' in analysis_result:
            normalized['context'] = analysis_result['context']
            
        # Extract keywords
        if 'keywords' in analysis_result:
            normalized['keywords'] = analysis_result['keywords']

        # Ensure we always have at least one concept
        if not normalized['concepts']:
            normalized['concepts'] = ['general topic']

        return normalized
    
    def _generate_content(self, normalized_input: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Abstract method to be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _generate_content")
    
    def _ensure_valid_result(self, result: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Ensure result has valid structure and content
        """
        if not result:
            return self._get_default_result()
            
        # Ensure all lists exist and have at least one item
        for key in result:
            if not result[key]:
                result[key] = [f"Default {key} content for {self.name}"]
                
        return result
    
    def _get_default_result(self) -> Dict[str, List[str]]:
        """
        Return default result structure
        """
        return {
            'questions': [f"Default question for {self.name}"],
            'explanations': [f"Default explanation for {self.name}"],
            'examples': [f"Default example for {self.name}"]
        }
    
    def _handle_error(self, e: Exception) -> Dict[str, List[str]]:
        """
        Standardized error handling
        
        Args:
            e: Exception that occurred
            
        Returns:
            Error dictionary with message
        """
        logger.error(f"Error in {self.name} generator: {e}")
        logger.error(traceback.format_exc())
        return self._get_default_result()