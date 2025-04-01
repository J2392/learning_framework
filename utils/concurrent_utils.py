# utils/concurrent_utils.py
"""
Utilities for concurrent processing of generators
"""

from typing import Dict, Any, List, Callable
import asyncio
from concurrent.futures import ThreadPoolExecutor
import traceback
import importlib

try:
    from utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class GeneratorExecutor:
    """
    Handles concurrent execution of content generators
    """
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    async def execute_generators(
        self,
        generators: Dict[str, Callable],
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute multiple generators concurrently
        
        Args:
            generators: Dictionary of generator functions
            analysis_result: Analysis result to pass to generators
            
        Returns:
            Combined results from all generators
        """
        try:
            loop = asyncio.get_event_loop()
            tasks = []
            
            for name, generator in generators.items():
                # Create task for each generator
                task = loop.run_in_executor(
                    self.executor,
                    self._safe_execute,
                    name,
                    generator,
                    analysis_result
                )
                tasks.append((name, task))
            
            # Wait for all tasks to complete
            results = {}
            for name, task in tasks:
                try:
                    result = await task
                    results[name] = result
                except Exception as e:
                    logger.error(f"Error executing generator {name}: {str(e)}")
                    results[name] = self._get_error_result(name)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in execute_generators: {str(e)}")
            logger.error(traceback.format_exc())
            return {}

    def _safe_execute(
        self,
        name: str,
        generator: Callable,
        analysis_result: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Safely execute a single generator with error handling
        """
        try:
            logger.debug(f"Executing generator: {name}")
            result = generator(analysis_result)
            logger.debug(f"Generator {name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error in generator {name}: {str(e)}")
            logger.error(traceback.format_exc())
            return self._get_error_result(name)

    def _get_error_result(self, name: str) -> Dict[str, List[str]]:
        """
        Return a default error result for failed generators
        """
        return {
            "error": [f"Error generating content for {name}. Please try again."]
        }

    def shutdown(self):
        """
        Cleanup executor resources
        """
        self.executor.shutdown(wait=True)

# Create singleton instance
executor = GeneratorExecutor()

def _import_generators() -> Dict[str, Callable]:
    """
    Dynamically import generator functions
    """
    generators = {}
    generator_modules = [
        ('socratic', 'generate_socratic_questions'),
        ('multilevel', 'generate_multilevel_explanations'),
        ('practice', 'generate_practice_questions'),
        ('blooms', 'generate_blooms_questions'),
        ('keyterms', 'generate_keyterms'),
        ('analogies', 'generate_analogies'),
        ('summary', 'generate_summary')
    ]
    
    for name, func_name in generator_modules:
        try:
            module = importlib.import_module(f'generators.{name}')
            generators[name] = getattr(module, func_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Error importing generator {name}: {str(e)}")
    
    return generators

async def execute_concurrent_analysis(
    analysis_result: Dict[str, Any],
    selected_methods: List[str]
) -> Dict[str, Any]:
    """
    Execute selected generators concurrently
    
    Args:
        analysis_result: Analysis result to pass to generators
        selected_methods: List of selected generator methods
        
    Returns:
        Combined results from selected generators
    """
    try:
        # Import generators dynamically
        generators = _import_generators()

        # Filter generators based on selected methods
        if 'all' in selected_methods:
            selected_generators = generators
        else:
            selected_generators = {
                name: func 
                for name, func in generators.items()
                if name in selected_methods
            }

        # Execute selected generators concurrently
        results = await executor.execute_generators(
            selected_generators,
            analysis_result
        )

        return results

    except Exception as e:
        logger.error(f"Error in execute_concurrent_analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return {}

def cleanup():
    """
    Cleanup concurrent processing resources
    """
    executor.shutdown()