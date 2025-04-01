"""
Perplexity API Analyzer
"""
import os
import logging
import aiohttp
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
import asyncio
from mocks.mock_api import MockPerplexityAPI

# Sửa import từ relative thành absolute
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config  # Thay đổi từ relative thành absolute import

# Load environment variables
load_dotenv()

# Setup logger
logger = logging.getLogger('perplexity_analyzer')

class PerplexityAnalyzer:
    def __init__(self):
        # Load config
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = os.getenv('PERPLEXITY_MODEL', 'sonar-medium-online')
        
        # Check for development mode override
        if hasattr(Config, 'DEVELOPMENT_MODE') and Config.DEVELOPMENT_MODE:
            logger.info("Development mode enabled: using mock API")
            self.use_api = False
        # Validate API key format
        elif not self.api_key or not self.api_key.startswith('pplx-'):
            logger.warning("Invalid API key format, falling back to mock API")
            self.use_api = False
        else:
            # Use real API with valid key
            logger.info("Using Perplexity Pro API with model: " + self.model)
            self.use_api = True
        
        logger.debug(f"Initialized with model: {self.model}")

    async def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text using Perplexity API
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dict containing analysis results
        """
        logger.info(f"Analyzing text (length: {len(text)})")
        
        if not text:
            raise ValueError("Empty text provided")
        
        # Check if using API or default responses
        if not self.use_api:
            logger.warning("Using default responses instead of API")
            return {
                "questions": self._get_default_result("questions"),
                "explanations": self._get_default_result("explanations"),
                "practice": self._get_default_result("practice"),
                "key_terms": self._get_default_result("key_terms"),
                "summary": self._get_default_result("summary"),
                "blooms": self._get_default_result("blooms"),
                "analogies": self._get_default_result("analogies")
            }
        
        if not self.api_key:
            raise ValueError("API key is required")
        
        # Preprocess text if needed
        processed_text = self._preprocess_text(text) if hasattr(self, '_preprocess_text') else text
        
        try:
            # Create a session for API calls
            async with aiohttp.ClientSession() as session:
                # Generate different types of content
                results = {
                    "questions": await self._generate_questions(session, processed_text),
                    "explanations": await self._generate_explanations(session, processed_text),
                    "practice": await self._generate_practice_questions(session, processed_text),
                    "key_terms": await self._generate_key_terms(session, processed_text),
                    "summary": await self._generate_summary(session, processed_text)
                }
                
                # Try to generate additional content if methods exist
                try:
                    results["blooms"] = await self._generate_blooms_questions(session, processed_text)
                except AttributeError:
                    results["blooms"] = []
                    
                try:
                    results["analogies"] = await self._generate_analogies(session, processed_text)
                except AttributeError:
                    results["analogies"] = []
                    
                logger.info("Analysis completed successfully")
                return results
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text before analysis"""
        # Remove excessive whitespace
        processed = ' '.join(text.split())
        return processed

    async def _generate_questions(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        """Generate Socratic questions based on the text"""
        prompt = f"Generate 5 Socratic questions about the following text:\n\n{text}"
        result = await self._call_api_with_retry(session, prompt)
        return self._process_response(result, "questions")
    
    async def _generate_explanations(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        """Generate multi-level explanations about the text"""
        prompt = f"Generate multi-level explanations for the following text. Include basic, intermediate, and advanced explanations:\n\n{text}"
        result = await self._call_api_with_retry(session, prompt)
        return self._process_response(result, "explanations")
    
    async def _generate_practice_questions(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        """Generate practice questions based on the text"""
        prompt = f"Create 5 practice questions with varying difficulty levels based on this text:\n\n{text}"
        result = await self._call_api_with_retry(session, prompt)
        return self._process_response(result, "practice")

    async def _generate_key_terms(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        """Generate key terms and definitions from the text"""
        prompt = f"Extract important terms and provide definitions from this text:\n\n{text}"
        result = await self._call_api_with_retry(session, prompt)
        return self._process_response(result, "key_terms")
    
    async def _generate_summary(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        """Generate a summary of the text"""
        prompt = f"Provide a comprehensive summary of this text:\n\n{text}"
        result = await self._call_api_with_retry(session, prompt)
        return self._process_response(result, "summary")

    async def _generate_blooms_questions(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        """Generate questions using Bloom's taxonomy levels"""
        prompt = f"Create questions for each level of Bloom's taxonomy (remember, understand, apply, analyze, evaluate, create) based on this text:\n\n{text}"
        result = await self._call_api_with_retry(session, prompt)
        return self._process_response(result, "blooms")
    
    async def _generate_analogies(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        """Generate analogies to explain concepts in the text"""
        prompt = f"Create 3-5 analogies to explain the concepts in this text:\n\n{text}"
        result = await self._call_api_with_retry(session, prompt)
        return self._process_response(result, "analogies")

    def _process_response(self, result: str, type: str) -> List[str]:
        """Process API response into structured list"""
        if not result:
            logger.warning(f"Empty result for {type}, using default")
            return self._get_default_result(type)
        
        try:
            # Split by newlines and remove empty lines
            lines = [line.strip() for line in result.split('\n') if line.strip()]
            
            # If no lines, use default
            if not lines:
                return self._get_default_result(type)
            
            return lines
        except Exception as e:
            logger.error(f"Error processing {type} response: {str(e)}")
            return self._get_default_result(type)

    def _get_default_result(self, type: str) -> List[str]:
        """Get default result for a specific type"""
        defaults = {
            "questions": ["No Socratic questions available"],
            "explanations": ["No multi-level explanations available"],
            "practice": ["No practice questions available"],
            "blooms": ["No Bloom's taxonomy questions available"],
            "key_terms": [
                "Term 1: Basic definition", 
                "Term 2: Technical meaning", 
                "Term 3: Contextual usage"
            ],
            "analogies": ["No analogies available"],
            "summary": ["No summary available"]
        }
        
        return defaults.get(type, ["No results available"])

    async def _call_api(self, session: aiohttp.ClientSession, prompt: str) -> str:
        """Call Perplexity API with given prompt"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert educator helping analyze content. Provide detailed, structured responses."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            # Log request details
            masked_prompt = prompt[:50] + "..." if len(prompt) > 50 else prompt
            logger.debug(f"Making API call to: {self.base_url}")
            logger.debug(f"API Key: {self.api_key[:8]}...{self.api_key[-4:]}")
            logger.debug(f"Model: {self.model}")
            logger.debug(f"Prompt: {masked_prompt}")
            
            async with session.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=60
            ) as response:
                response_text = await response.text()
                logger.debug(f"Response status: {response.status}")
                
                if response.status == 200:
                    try:
                        result = await response.json()
                        logger.debug("API call successful")
                        content = result['choices'][0]['message']['content']
                        logger.debug(f"Response content (first 100 chars): {content[:100]}...")
                        return content
                    except (KeyError, json.JSONDecodeError) as e:
                        logger.error(f"Error parsing API response: {str(e)}")
                        logger.error(f"Response text: {response_text}")
                        return None
                elif response.status == 401:
                    logger.error("API error 401 - Unauthorized. Check your API key.")
                    logger.error("Verify your Pro subscription is active.")
                    return None
                elif response.status == 404:
                    logger.error(f"API error 404 - Endpoint not found: {self.base_url}")
                    return None
                elif response.status == 400:
                    logger.error(f"API error 400 - Bad Request")
                    logger.error(f"Response details: {response_text}")
                    # Check for specific error messages in response
                    try:
                        error_json = json.loads(response_text)
                        if 'error' in error_json and 'message' in error_json['error']:
                            logger.error(f"Error message: {error_json['error']['message']}")
                    except:
                        pass
                    return None
                else:
                    logger.error(f"API error: {response.status}")
                    logger.error(f"Response: {response_text}")
                    return None
                
        except Exception as e:
            logger.error(f"API call error: {str(e)}")
            return None

    async def _call_api_with_retry(self, session: aiohttp.ClientSession, prompt: str, max_retries=3) -> str:
        """Call Perplexity API with retry logic"""
        retries = 0
        while retries < max_retries:
            try:
                result = await self._call_api(session, prompt)
                if result:
                    return result
                
                # If we get here, the API call failed
                retries += 1
                logger.warning(f"API call failed. Retrying ({retries}/{max_retries})...")
                await asyncio.sleep(1 * retries)  # Exponential backoff
            except Exception as e:
                logger.error(f"API call attempt {retries+1} failed: {str(e)}")
                retries += 1
                if retries >= max_retries:
                    logger.error(f"Maximum retry attempts ({max_retries}) reached")
                    return None
                await asyncio.sleep(1 * retries)  # Exponential backoff
        
        return None
