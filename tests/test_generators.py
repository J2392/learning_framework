"""
Tests for individual generators in the application
"""
import os
import sys
import unittest
import asyncio
import json
import logging
from unittest import mock
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_generators')

# Create results directory
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_results')
os.makedirs(RESULTS_DIR, exist_ok=True)

# Import modules to test
try:
    from analyzers.perplexity_analyzer import PerplexityAnalyzer
    from mocks.mock_api import MockPerplexityAPI
    from config import Config
    from dotenv import load_dotenv
    
    # Try to import the individual generators
    from generators.sentiment_generator import SentimentGenerator
    USE_DIRECT_GENERATORS = True
except ImportError as e:
    logger.warning(f"Không thể import các generator riêng lẻ: {e}")
    USE_DIRECT_GENERATORS = False

# Sample text for testing
SAMPLE_TEXT_SHORT = """
Artificial intelligence (AI) is revolutionizing education. It enables personalized learning
experiences and provides immediate feedback to students. Teachers can use AI to automate
routine tasks and focus more on individual student needs.
"""

SAMPLE_TEXT_MEDIUM = """
Climate change poses significant challenges to global ecosystems and human societies.
Rising temperatures lead to more extreme weather events, including droughts, floods, and
storms. These changes affect agriculture, water resources, and public health worldwide.
Scientists agree that reducing greenhouse gas emissions is essential to mitigate the worst
effects of climate change. Renewable energy adoption, improved energy efficiency, and
sustainable land management practices are key strategies for addressing this global crisis.
"""

# Run async function in tests
def run_async(loop, coro):
    """Run coroutine in a specific event loop"""
    if loop.is_closed():
        logger.warning("Attempted to run on a closed loop. Returning None.")
        return None
    return loop.run_until_complete(coro)

class TestGenerators(unittest.TestCase):
    """Tests for individual generators"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        load_dotenv()
        # Force development mode for testing
        os.environ['DEVELOPMENT_MODE'] = 'True'
        Config.DEVELOPMENT_MODE = True # Ensure config reflects env var
        cls.analyzer = PerplexityAnalyzer()
        
        # Set up session for testing
        cls.test_session = mock.MagicMock()
        cls.generator_names = [
            "summary", "key_terms", "questions", 
            "explanations", "practice", "blooms", "analogies"
        ]
        
    def setUp(self):
        """Set up before each test, create a new event loop"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.text = SAMPLE_TEXT_SHORT
        
    def tearDown(self):
        """Clean up after each test, close the event loop"""
        self.loop.close()
        asyncio.set_event_loop(None) # Reset the event loop policy
        
    def save_result(self, generator_name, result):
        """Save test result to file"""
        filename = f"test_{generator_name}_{time.time():.0f}.json"
        filepath = os.path.join(RESULTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if isinstance(result, list) or isinstance(result, dict):
                json.dump(result, f, indent=2, ensure_ascii=False)
            else:
                json.dump({"result": str(result)}, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Kết quả được lưu vào {filepath}")
    
    def _get_generator_function(self, generator_name):
        """Get generator function by name"""
        generator_functions = {
            # "sentiment": self.analyzer._generate_sentiment, # Removed
            "summary": self.analyzer._generate_summary,
            "key_terms": self.analyzer._generate_key_terms,
            "questions": self.analyzer._generate_questions,
            "explanations": self.analyzer._generate_explanations,
            "practice": self.analyzer._generate_practice_questions,
            "blooms": self.analyzer._generate_blooms_questions,
            "analogies": self.analyzer._generate_analogies
        }
        
        if generator_name not in generator_functions:
            raise ValueError(f"Generator không hợp lệ: {generator_name}")
        
        return generator_functions[generator_name]
    
    def test_all_generators_exist(self):
        """Kiểm tra tất cả các generator tồn tại"""
        logger.info("Kiểm tra tất cả các generator tồn tại")
        
        for generator_name in self.generator_names:
            with self.subTest(generator=generator_name):
                generator_func = self._get_generator_function(generator_name)
                self.assertIsNotNone(generator_func, f"Generator {generator_name} không tồn tại")
                logger.info(f"Generator {generator_name} tồn tại: {generator_func.__name__}")
    
    async def _test_generator(self, generator_name, text):
        """Test a single generator by calling the main analyze method in dev mode"""
        logger.info(f"Testing generator: {generator_name} via analyze() in dev mode")
        
        # Ensure we are in dev mode for this test approach
        self.assertTrue(Config.DEVELOPMENT_MODE, "Generator tests should run in DEVELOPMENT_MODE=True")
        
        start_time = time.time()
        # Call the main analyze method which should return mock results
        full_result = await self.analyzer.analyze(text)
        execution_time = time.time() - start_time
        
        self.assertIsInstance(full_result, dict, "Analyze result is not a dictionary")
        self.assertIn(generator_name, full_result, f"Generator {generator_name} key missing in analyze result")
        
        result = full_result[generator_name]
        
        # Log results
        logger.info(f"analyze() execution time for {generator_name}: {execution_time:.2f}s")
        logger.info(f"Result type: {type(result).__name__}")
        
        if isinstance(result, list):
            logger.info(f"Result length: {len(result)} items")
        elif isinstance(result, dict):
            logger.info(f"Result keys: {', '.join(result.keys())}")
        
        # Save result
        self.save_result(generator_name, result)
        
        return {
            "generator": generator_name,
            "result": result,
            "execution_time": execution_time
        }
    
    # def test_sentiment_generator(self):
    #     """Test sentiment generator - Removed as sentiment generator doesn't exist"""
    #     logger.info("Testing sentiment generator")
    #     result = run_async(self.loop, self._test_generator("sentiment", self.text))
        
    #     self.assertIsNotNone(result["result"], "Sentiment generator returned None")
    #     if isinstance(result["result"], list):
    #         self.assertTrue(len(result["result"]) > 0, "Sentiment result list is empty")
    
    def test_summary_generator(self):
        """Test summary generator"""
        logger.info("Testing summary generator")
        result = run_async(self.loop, self._test_generator("summary", self.text))
        
        self.assertIsNotNone(result["result"], "Summary generator returned None")
        if isinstance(result["result"], str):
            self.assertTrue(len(result["result"]) > 0, "Summary result is empty")
        elif isinstance(result["result"], list):
            self.assertTrue(len(result["result"]) > 0, "Summary result list is empty")
    
    def test_key_terms_generator(self):
        """Test key terms generator"""
        logger.info("Testing key terms generator")
        result = run_async(self.loop, self._test_generator("key_terms", self.text))
        
        self.assertIsNotNone(result["result"], "Key terms generator returned None")
        if isinstance(result["result"], list):
            self.assertTrue(len(result["result"]) > 0, "Key terms result list is empty")
    
    def test_questions_generator(self):
        """Test questions generator"""
        logger.info("Testing questions generator")
        result = run_async(self.loop, self._test_generator("questions", self.text))
        
        self.assertIsNotNone(result["result"], "Questions generator returned None")
        if isinstance(result["result"], list):
            self.assertTrue(len(result["result"]) > 0, "Questions result list is empty")
    
    def test_practice_generator(self):
        """Test practice questions generator"""
        logger.info("Testing practice questions generator")
        result = run_async(self.loop, self._test_generator("practice", self.text))
        
        self.assertIsNotNone(result["result"], "Practice questions generator returned None")
        if isinstance(result["result"], list):
            self.assertTrue(len(result["result"]) > 0, "Practice questions result list is empty")
    
    def test_all_generators_with_longer_text(self):
        """Test all generators with longer text"""
        logger.info("Testing all generators with longer text")
        
        # Use medium text
        self.text = SAMPLE_TEXT_MEDIUM
        
        results = {}
        for generator_name in ["summary", "key_terms"]:  # Limit to 2 generators to save time
            with self.subTest(generator=generator_name):
                result = run_async(self.loop, self._test_generator(generator_name, self.text))
                results[generator_name] = result
                self.assertIsNotNone(result["result"], f"{generator_name} generator returned None")
        
        # Log comparison
        logger.info("Execution time comparison:")
        for generator_name, result in results.items():
            logger.info(f"  {generator_name}: {result['execution_time']:.2f}s")
    
    async def _test_analyze_method(self):
        """Test the main analyze method"""
        logger.info("Testing main analyze method")
        
        # Call the analyze method
        start_time = asyncio.get_event_loop().time()
        result = await self.analyzer.analyze(self.text)
        execution_time = asyncio.get_event_loop().time() - start_time
        
        # Log results
        logger.info(f"analyze() execution time: {execution_time:.2f}s")
        logger.info(f"Result type: {type(result).__name__}")
        logger.info(f"Result has {len(result)} fields")
        
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, list):
                    logger.info(f"  {key}: {len(value)} items")
                else:
                    logger.info(f"  {key}: {type(value).__name__}")
        
        # Save result
        self.save_result("full_analyze", result)
        
        return {
            "result": result,
            "execution_time": execution_time
        }
    
    def test_analyze_method(self):
        """Test the main analyze method"""
        logger.info("Testing analyze method")
        result = run_async(self.loop, self._test_analyze_method())
        
        self.assertIsNotNone(result["result"], "Analyze method returned None")
        self.assertIsInstance(result["result"], dict, "Analyze result is not a dictionary")
        
        # Check for expected keys
        expected_keys = ["summary", "key_terms"]
        for key in expected_keys:
            self.assertIn(key, result["result"], f"Analyze result missing expected key: {key}")
    
    def test_mock_api(self):
        """Test the MockPerplexityAPI directly"""
        logger.info("Testing MockPerplexityAPI directly")
        
        mock_api = MockPerplexityAPI()
        prompt = "Generate a summary for the following text:\n\n" + self.text
        category = "summary" # Define a category for the mock
        
        # Use the get_response method
        result = mock_api.get_response(prompt, category)
        
        self.assertIsNotNone(result, "MockPerplexityAPI returned None")
        # Mock returns a list of strings now
        self.assertIsInstance(result, list, "MockPerplexityAPI result is not a list")
        self.assertTrue(len(result) > 0, "MockPerplexityAPI result is empty")
        
        logger.info(f"MockPerplexityAPI result items: {len(result)}")
        logger.info(f"Result excerpt: {result[0][:100]}...")
    
    @unittest.skipIf(not USE_DIRECT_GENERATORS, "Không thể import generators riêng lẻ")
    def test_direct_sentiment_generator(self):
        """Test SentimentGenerator class directly, if available"""
        logger.info("Testing SentimentGenerator class directly")
        
        generator = SentimentGenerator()
        
        # Test the generate method directly
        prompt = generator.generate_prompt(self.text)
        self.assertIsInstance(prompt, str, "Generated prompt is not a string")
        self.assertIn(self.text, prompt, "Generated prompt doesn't include the input text")
        
        # Test the process_response method with a mock response
        mock_response = """
        Sentiment Analysis:
        Overall Sentiment: Positive
        Sentiment Score: 4/5
        Main emotional tones: Optimistic, enthusiastic
        Key emotion-bearing words/phrases: "revolutionizing", "enables", "immediate feedback"
        """
        
        result = generator.process_response(mock_response)
        
        self.assertIsNotNone(result, "SentimentGenerator.process_response returned None")
        
        # Log result
        logger.info(f"Direct SentimentGenerator result: {result}")
        self.save_result("direct_sentiment", result)
    
    def test_analyzer_cache(self):
        """Test that analyzer caches results correctly"""
        logger.info("Testing analyzer cache functionality")
        
        # First call to analyze
        first_result = run_async(self.loop, self.analyzer.analyze(self.text))
        
        # Second call with same text should be faster due to caching
        start_time = time.time()
        second_result = run_async(self.loop, self.analyzer.analyze(self.text))
        second_execution_time = time.time() - start_time
        
        # Check that results are the same
        self.assertEqual(first_result, second_result, "Cached result doesn't match original result")
        
        logger.info(f"Second call execution time: {second_execution_time:.2f}s")
        self.assertLess(second_execution_time, 0.1, "Cache lookup took too long (>0.1s)")
        
        # Check with different text
        different_text = "This is a completely different text for testing cache."
        different_result = run_async(self.loop, self.analyzer.analyze(different_text))
        
        self.assertNotEqual(first_result, different_result, "Different text produced same result")

if __name__ == '__main__':
    unittest.main(verbosity=2) 