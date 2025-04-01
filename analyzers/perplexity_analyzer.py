import aiohttp
import logging
import logging.handlers
import os
from typing import Dict, Any, List
from config import Config
from utils.logger import setup_logger

# Khởi tạo logger
logger = setup_logger('perplexity_analyzer')
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

file_handler = logging.handlers.RotatingFileHandler(
    os.path.join(log_dir, 'analyzer.log'),
    maxBytes=1024*1024,
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

class PerplexityAnalyzer:
    def __init__(self):
        self.api_key = Config.PERPLEXITY_API_KEY
        self.base_url = Config.PERPLEXITY_BASE_URL
        self.model = Config.PERPLEXITY_MODEL

    async def analyze(self, text: str) -> Dict[str, Any]:
        """Main analysis method"""
        try:
            async with aiohttp.ClientSession() as session:
                results = {
                    'socratic_questions': await self._generate_questions(session, text),
                    'multilevel_explanations': await self._generate_explanations(session, text),
                    'practice_questions': await self._generate_practice_questions(session, text),
                    'blooms_questions': await self._generate_blooms_questions(session, text),
                    'key_terms': await self._generate_key_terms(session, text),
                    'analogies': await self._generate_analogies(session, text),
                    'summary': await self._generate_summary(session, text)
                }
                return results
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}", exc_info=True)
            return self._get_default_result("all")

    async def _call_api(self, session: aiohttp.ClientSession, prompt: str) -> str:
        """Make API call to Perplexity"""
        try:
            logger.debug(f"Sending prompt to API: {prompt[:200]}...")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert educator. You MUST follow the structured analysis steps EXACTLY as provided and show your detailed thought process for EACH step. Format your response to match the requested structure precisely."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
                "presence_penalty": 0.6,
                "frequency_penalty": 0.3
            }
            
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=45
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result['choices'][0]['message']['content']
                    logger.info(f"API Response received: {content[:500]}...")
                    return content
                else:
                    error_text = await response.text()
                    logger.error(f"API error status {response.status}: {error_text}")
                    return None
        except Exception as e:
            logger.error(f"API call error: {str(e)}", exc_info=True)
            return None

    def _process_response(self, result: str, type: str) -> List[str]:
        """Process and structure API response"""
        if not result:
            logger.warning(f"Empty result for type {type}, using default")
            return self._get_default_result(type)
        
        try:
            logger.debug(f"Processing response for type {type}: {result[:200]}...")
            
            # Split by STEP markers
            steps = []
            current_step = []
            lines = result.split('\n')
            
            for line in lines:
                if line.startswith('STEP '):
                    logger.debug(f"Found step marker: {line}")
                    if current_step:
                        steps.append(current_step)
                    current_step = [line]
                elif line.strip():
                    current_step.append(line)
            
            if current_step:
                steps.append(current_step)
            
            # Format each step
            processed = []
            for i, step in enumerate(steps):
                if step:
                    logger.debug(f"Processing step {i+1}: {step[0]}")
                    processed.append(step[0])
                    processed.extend([f"  {line.strip('- ').strip()}" for line in step[1:] if line.strip()])
                    processed.append("")
            
            # Add final output section if exists
            if "Output:" in result or "FINAL OUTPUT:" in result:
                logger.debug("Processing final output section")
                output_marker = "Output:" if "Output:" in result else "FINAL OUTPUT:"
                output_section = result.split(output_marker)[1].strip()
                processed.extend([
                    "FINAL OUTPUT:",
                    *[f"  {line.strip('- ').strip()}" for line in output_section.split('\n') if line.strip()]
                ])
            
            logger.info(f"Successfully processed response for {type} with {len(processed)} lines")
            return processed if processed else self._get_default_result(type)
                
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}", exc_info=True)
            return self._get_default_result(type)

    async def _generate_questions(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        prompt = """
        Act as an expert educator. Follow this step-by-step thought process:
        
        STEP 1: Initial Analysis
        - Identify main concepts
        - Note key arguments
        - List assumptions
        
        STEP 2: Question Development
        - Create foundational questions
        - Design analytical questions
        - Develop evaluative questions
        
        Text for analysis: {text}
        
        Show your work through each step, then provide final questions.
        """.format(text=text)
        
        result = await self._call_api(session, prompt)
        return self._process_response(result, "questions")

    async def _generate_explanations(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        prompt = """
        Analyze this text in multiple levels:
        
        STEP 1: Basic Level
        - Core concepts
        - Main principles
        - Key definitions
        
        STEP 2: Intermediate Level
        - Relationships between concepts
        - Practical applications
        - Supporting evidence
        
        STEP 3: Advanced Level
        - Complex implications
        - Critical analysis
        - Broader context
        
        Text: {text}
        """.format(text=text)
        
        result = await self._call_api(session, prompt)
        return self._process_response(result, "explanations")

    async def _generate_practice_questions(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        prompt = """
        Create practice questions:
        
        STEP 1: Multiple Choice
        - Core concept questions
        - Application scenarios
        - Analysis problems
        
        STEP 2: Short Answer
        - Explanation prompts
        - Compare/contrast questions
        - Evidence-based responses
        
        STEP 3: Discussion
        - Critical thinking prompts
        - Case studies
        - Integration challenges
        
        Text: {text}
        """.format(text=text)
        
        result = await self._call_api(session, prompt)
        return self._process_response(result, "practice")

    async def _generate_blooms_questions(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        prompt = """
        Create questions based on Bloom's Taxonomy levels:
        
        STEP 1: Remember
        - Define key terms
        - Recall basic facts
        - Identify main concepts
        
        STEP 2: Understand
        - Explain relationships
        - Interpret meaning
        - Summarize main points
        
        STEP 3: Apply
        - Use concepts in new situations
        - Solve related problems
        - Demonstrate methods
        
        STEP 4: Analyze
        - Break down complex ideas
        - Compare and contrast
        - Examine relationships
        
        STEP 5: Evaluate
        - Assess validity
        - Judge effectiveness
        - Support arguments
        
        STEP 6: Create
        - Design solutions
        - Develop new ideas
        - Synthesize information
        
        Text: {text}
        """.format(text=text)
        
        result = await self._call_api(session, prompt)
        return self._process_response(result, "blooms")

    async def _generate_key_terms(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        prompt = """
        Analyze key terms and concepts:
        
        STEP 1: Term Identification
        - List important terms
        - Note technical vocabulary
        - Identify core concepts
        
        STEP 2: Definition Development
        - Provide clear definitions
        - Include context
        - Add examples
        
        STEP 3: Relationship Analysis
        - Show connections between terms
        - Explain hierarchies
        - Map concept relationships
        
        Text: {text}
        """.format(text=text)
        
        result = await self._call_api(session, prompt)
        return self._process_response(result, "key_terms")

    async def _generate_analogies(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        prompt = """
        Create analogies and examples:
        
        STEP 1: Core Concept Analysis
        - Identify main ideas
        - List key features
        - Note relationships
        
        STEP 2: Analogy Development
        - Create real-world comparisons
        - Develop metaphors
        - Build parallel examples
        
        STEP 3: Application Examples
        - Provide practical scenarios
        - Show everyday applications
        - Demonstrate usage
        
        Text: {text}
        """.format(text=text)
        
        result = await self._call_api(session, prompt)
        return self._process_response(result, "analogies")

    async def _generate_summary(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        prompt = """
        Create a comprehensive summary:
        
        STEP 1: Main Points
        - Identify key ideas
        - List major arguments
        - Note conclusions
        
        STEP 2: Supporting Details
        - Find evidence
        - Note examples
        - List explanations
        
        STEP 3: Synthesis
        - Connect ideas
        - Show relationships
        - Build framework
        
        Text: {text}
        """.format(text=text)
        
        result = await self._call_api(session, prompt)
        return self._process_response(result, "summary")

    def _get_default_result(self, type: str) -> List[str]:
        """Return default results when API fails"""
        defaults = {
            "questions": [
                "What are the main concepts presented?",
                "How do these ideas connect to existing knowledge?",
                "What evidence supports these claims?"
            ],
            "explanations": [
                "Basic: Core concepts and principles",
                "Intermediate: Relationships between ideas",
                "Advanced: Complex implications"
            ],
            "practice": [
                "Multiple Choice: Select the best answer...",
                "Short Answer: Explain briefly...",
                "Discussion: Analyze in detail..."
            ],
            "blooms": [
                "Remember: Define key terms",
                "Understand: Explain concepts",
                "Apply: Use in new situations",
                "Analyze: Break down components",
                "Evaluate: Assess validity",
                "Create: Develop new ideas"
            ],
            "key_terms": [
                "Term 1: Basic definition",
                "Term 2: Technical meaning",
                "Term 3: Contextual usage"
            ],
            "analogies": [
                "Real-world comparison 1",
                "Metaphor example",
                "Practical application"
            ],
            "summary": [
                "Main point 1",
                "Supporting detail",
                "Conclusion"
            ],
            "all": {
                "socratic_questions": ["What are the main concepts presented?"],
                "multilevel_explanations": ["Basic: Core concepts and principles"],
                "practice_questions": ["Multiple Choice: Select the best answer..."],
                "blooms_questions": ["Remember: Define key terms"],
                "key_terms": ["Term 1: Basic definition"],
                "analogies": ["Similar to everyday example..."],
                "summary": ["Key Points: Main ideas and concepts"]
            }
        }
        return defaults.get(type, ["No results available"])