import aiohttp
import logging
import logging.handlers
import os
import re
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
            # Preprocess text first
            processed_text = self._preprocess_text(text)
            
            async with aiohttp.ClientSession() as session:
                results = {
                    'socratic_questions': await self._generate_questions(session, processed_text),
                    'multilevel_explanations': await self._generate_explanations(session, processed_text),
                    'practice_questions': await self._generate_practice_questions(session, processed_text),
                    'blooms_questions': await self._generate_blooms_questions(session, processed_text),
                    'key_terms': await self._generate_key_terms(session, processed_text),
                    'analogies': await self._generate_analogies(session, processed_text),
                    'summary': await self._generate_summary(session, processed_text)
                }
                return results
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}", exc_info=True)
            return self._get_default_result("all")

    def _preprocess_text(self, text: str) -> str:
        """Clean and optimize input text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Limit text length if needed
        max_length = 8000  # Adjust based on token limits
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        # Basic formatting
        text = text.strip()
        
        return text
    
    async def _call_api(self, session: aiohttp.ClientSession, prompt: str) -> str:
        """Make API call to Perplexity with enhanced parameters"""
        try:
            # Log the full prompt
            logger.debug(f"Full prompt being sent to API:\n{prompt}")
            
            # Log API request details
            logger.debug(f"API Request - URL: {self.base_url}/chat/completions")
            logger.debug(f"API Request - Model: {self.model}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Enhanced system prompt for more detailed analysis
            system_prompt = """
            You are an expert educator and researcher with deep domain knowledge. Follow these STRICT requirements:

            RESPONSE FORMAT:
            - Use clear hierarchical structure with numbered sections and subsections
            - Each main point must have 3-5 supporting details
            - Use bullet points and indentation for clarity
            - Include examples after each major point
            - Show your reasoning process explicitly
            
            CONTENT REQUIREMENTS:
            - Minimum 7-10 main points per section
            - Each point must be explained in 3-4 sentences
            - Include specific examples and case studies
            - Add practical applications and real-world scenarios
            - Connect ideas to broader concepts and theories
            
            DEPTH REQUIREMENTS:
            - Analyze from multiple perspectives
            - Consider implications and consequences
            - Discuss limitations and counterarguments
            - Provide evidence and justification
            - Include critical analysis
            
            EDUCATIONAL VALUE:
            - Target advanced understanding
            - Promote critical thinking
            - Encourage further exploration
            - Challenge common assumptions
            - Stimulate intellectual curiosity
            
            FORMAT YOUR RESPONSE WITH:
            1. Clear section headers in CAPS
            2. Numbered main points
            3. Bulleted supporting details
            4. Indented examples
            5. "Key Insight" boxes
            6. "Critical Analysis" sections
            7. "Practical Applications" segments
            """
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt.strip()
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 4000,
                "top_p": 0.95,
                "presence_penalty": 0.7,
                "frequency_penalty": 0.7
            }
            
            # Increase timeout for more thorough responses
            response = await session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60  # Increased timeout
            )
            if response.status == 200:
                result = await response.json()
                content = result['choices'][0]['message']['content']
                
                # Log full API response
                logger.info(f"Full API Response:\n{content}")
                
                # Log response statistics
                logger.info(f"Response length: {len(content)} chars")
                logger.info(f"Response structure: {content.count('STEP')} steps found")
                
                return content
            else:
                # Log error details
                error_text = await response.text()
                logger.error(f"API Error - Status: {response.status}")
                logger.error(f"API Error - Response: {error_text}")
                return None
        except Exception as e:
            logger.error(f"API call error: {str(e)}", exc_info=True)
            return None

    def _process_response(self, result: str, type: str) -> List[str]:
        if not result:
            return self._get_default_result(type)
        
        try:
            # Split by different section markers while preserving structure
            sections = []
            current_section = []
            
            for line in result.split('\n'):
                # Detect section headers
                if any(marker in line for marker in ['STEP', 'LEVEL', '#', '##', 'KEY INSIGHT', 'CRITICAL ANALYSIS']):
                    if current_section:
                        sections.append(current_section)
                    current_section = [line]
                # Preserve bullet points and numbering
                elif line.strip().startswith(('-', '*', '•', '1.', '2.', '3.')):
                    current_section.append(line)
                # Preserve indentation and formatting
                elif line.strip():
                    if current_section:
                        # Keep indentation for sub-points
                        if line.startswith('    '):
                            current_section.append(line)
                        else:
                            current_section.append(f"    {line}")
                    else:
                        current_section = [line]
            
            if current_section:
                sections.append(current_section)
            
            # Format sections while preserving hierarchy
            processed = []
            for section in sections:
                if section:
                    # Keep section header
                    processed.append(section[0])
                    
                    # Process content with proper indentation
                    for line in section[1:]:
                        if line.strip().startswith(('-', '*', '•')):
                            processed.append(f"  {line}")
                        elif line.strip().startswith(('1.', '2.', '3.')):
                            processed.append(line)
                        elif 'Example:' in line or 'Application:' in line:
                            processed.append(f"\n  {line}")
                        else:
                            processed.append(f"    {line}")
                    
                    processed.append("")  # Add spacing between sections
            
            return processed if processed else self._get_default_result(type)
                
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}", exc_info=True)
            return self._get_default_result(type)

    async def _generate_questions(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        prompt = """
        Act as an expert educator with deep subject matter expertise. 
        REQUIREMENTS:
        - Each step must have AT LEAST 5 detailed points
        - Each point must include examples and explanations
        - Show complete reasoning for each question developed
        - Questions must probe deep understanding, not just surface knowledge
        - Include follow-up questions and discussion points
        - Minimum 3 questions for each category
        - Each question must have:
          * Main question
          * 2-3 follow-up questions
          * Expected answer points
          * Evaluation criteria
          * Related concepts

        STEP 1: Deep Content Analysis
        - Identify main concepts and themes (minimum 5)
        - Extract core principles and methodologies
        - Analyze key arguments and their logical structure
        - Uncover implicit and explicit assumptions
        - Note potential knowledge gaps or misconceptions
        
        STEP 2: Contextual Understanding
        - Identify the domain/field of study
        - Recognize the level of complexity
        - Consider possible audience knowledge level
        - Note connections to broader themes or disciplines
        - Identify potential real-world applications
        
        STEP 3: Question Development (create at least 3 questions per category)
        - Create foundational clarifying questions that probe basic understanding
        - Design analytical questions that examine relationships between concepts
        - Develop evaluative questions that require critical judgment
        - Craft application questions that test practical usage
        - Create synthesis questions that integrate multiple concepts
        
        STEP 4: Question Refinement
        - Ensure questions are clear and unambiguous
        - Add appropriate complexity based on content
        - Structure questions to reveal thought process
        - Include sufficient context within each question
        - Ensure questions promote deep rather than surface learning
        
        Text for analysis: {text}
        
        IMPORTANT: Show your detailed thought process through each step. For the final output, organize questions by category with clear headers and provide at least 10 total questions.
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
        Create detailed questions based on all levels of Bloom's Taxonomy, showing your critical thinking process:
        
        STEP 1: Content Analysis
        - Identify the most important concepts (minimum 5)
        - List key terminology that requires understanding
        - Map relationships between main ideas
        - Determine the cognitive demands of the material
        - Identify potential challenges for learners
        
        STEP 2: Remember Level (create at least 3 questions)
        - Define essential key terms precisely
        - Create questions to recall specific facts
        - Develop questions to identify main concepts
        - Frame questions to test knowledge of definitions
        - Include questions about basic terminology
        
        STEP 3: Understand Level (create at least 3 questions)
        - Design questions requiring explanation of key relationships
        - Create questions that test interpretation of meaning
        - Develop questions requiring summarization of main points
        - Frame questions that test classification of concepts
        - Include questions about explaining processes
        
        STEP 4: Apply Level (create at least 3 questions)
        - Develop scenarios requiring application of concepts
        - Create problem-solving questions using the concepts
        - Design questions demonstrating practical methods
        - Frame questions applying theory to realistic situations
        - Include questions about implementing procedures
        
        STEP 5: Analyze Level (create at least 3 questions)
        - Create questions breaking down complex ideas
        - Design detailed compare/contrast questions
        - Develop questions examining structural relationships
        - Frame questions requiring identification of patterns
        - Include questions about differentiating between concepts
        
        STEP 6: Evaluate Level (create at least 3 questions)
        - Design questions assessing validity of claims
        - Create questions judging effectiveness of approaches
        - Develop questions requiring support for arguments
        - Frame questions critiquing methods or solutions
        - Include questions about evaluating relative importance
        
        STEP 7: Create Level (create at least 3 questions)
        - Design questions requiring innovative solutions
        - Create questions developing new ideas or hypotheses
        - Develop questions synthesizing information into cohesive wholes
        - Frame questions requiring creation of new models or frameworks
        - Include questions about transforming concepts into new contexts
        
        Text: {text}
        
        IMPORTANT: For each Bloom's level, provide:
        1. A brief explanation of how this level applies to the specific content
        2. At least 3 carefully crafted questions with clear context and specific focus
        3. Organize final output with clear category headers and numbering
        """.format(text=text)
        
        result = await self._call_api(session, prompt)
        return self._process_response(result, "blooms")

    async def _generate_key_terms(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        prompt = """
        Perform an in-depth analysis of key terms and concepts, showing your detailed thought process:
        
        STEP 1: Comprehensive Term Identification
        - Extract all important terminology (minimum 10 terms)
        - Identify domain-specific and technical vocabulary
        - Recognize core theoretical concepts and frameworks
        - Note methodological or procedural terms
        - Identify potentially ambiguous or multifaceted terms
        - Consider terminology that may be unfamiliar to novices
        
        STEP 2: Contextual Definition Development
        - Provide precise, academic definitions for each term
        - Include field-specific context and usage
        - Add multiple concrete examples for each term
        - Clarify nuances and variations in meaning where applicable
        - Note etymology or origin where relevant to understanding
        - Reference how the definition relates to the original text
        
        STEP 3: Comprehensive Relationship Analysis
        - Map hierarchical relationships between terms (superordinate/subordinate)
        - Identify causal relationships between concepts
        - Explain sequential or procedural relationships
        - Diagram conceptual networks and interconnections
        - Analyze complementary and contrasting term relationships
        - Identify foundational concepts that underpin others
        
        STEP 4: Concept Importance Evaluation
        - Rank terms by their centrality to the content
        - Explain why certain terms are foundational to understanding
        - Identify concepts that require mastery before others
        - Note which terms connect to broader disciplinary knowledge
        - Highlight terms that address common misconceptions
        
        Text: {text}
        
        IMPORTANT: In your final output:
        1. Present terms alphabetically with full definitions and contextual examples
        2. Include a visual or text-based concept map showing relationships
        3. Group related terms into meaningful categories
        4. Provide difficulty levels for each term (basic, intermediate, advanced)
        5. For each term, include "Why it matters" explanation
        """.format(text=text)
        
        result = await self._call_api(session, prompt)
        return self._process_response(result, "key_terms")

    async def _generate_analogies(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        prompt = """
        Create sophisticated analogies, metaphors, and examples to illustrate complex concepts, showing your detailed reasoning:
        
        STEP 1: Deep Concept Analysis
        - Identify at least 5 central concepts or principles
        - Break down each concept into its essential components
        - Identify the abstract relationships and patterns within each concept
        - Note the functional mechanisms and processes involved
        - Determine the conceptual challenges that make each idea difficult to grasp
        - Consider different learning styles and knowledge backgrounds
        
        STEP 2: Analogy Development (create at least 2 analogies per concept)
        - Create detailed real-world comparisons that match the concept's structure
        - Develop rich metaphors that capture abstract relationships
        - Build parallel examples from multiple domains (science, arts, everyday life)
        - Map specific elements of the concept to elements in the analogy
        - Explain why each analogy effectively represents the concept
        - Consider potential misconceptions each analogy might create
        
        STEP 3: Metaphor Refinement
        - Enhance metaphors with vivid, sensory details
        - Explain precisely how each metaphor illuminates the concept
        - Address limitations of each metaphor
        - Create extended metaphors that capture complex relationships
        - Develop complementary metaphors addressing different aspects
        
        STEP 4: Application Examples (minimum 3 per concept)
        - Provide diverse practical scenarios across different contexts
        - Create everyday applications that resonate with different audiences
        - Demonstrate usage through step-by-step examples
        - Include examples of varying complexity (beginner to advanced)
        - Show how the concept solves real problems or explains phenomena
        - Create examples showing how concepts connect to each other
        
        STEP 5: Visual Representation
        - Describe how each concept could be visualized
        - Suggest diagrams, models or illustrations that clarify relationships
        - Create verbal descriptions of visual analogies
        - Develop spatial or physical metaphors that aid understanding
        
        Text: {text}
        
        IMPORTANT: In your final output:
        1. Present each concept with its collection of analogies, metaphors and examples
        2. Explicitly state how each analogy matches the structure of the original concept
        3. Include "Why this helps" explanations for each analogy
        4. Identify which analogies work best for different types of learners
        5. Organize output by concept, with clear headers and structured formatting
        """.format(text=text)
        
        result = await self._call_api(session, prompt)
        return self._process_response(result, "analogies")

    async def _generate_summary(self, session: aiohttp.ClientSession, text: str) -> List[str]:
        prompt = """
        Create a multilevel, comprehensive summary with detailed analysis and synthesis:
        
        STEP 1: Initial Content Analysis
        - Identify the central thesis or main argument
        - Recognize at least 5 key supporting ideas
        - Map logical structure of the content
        - Note methodology or approach used
        - Identify target audience and purpose
        - Assess overall knowledge domain and complexity
        
        STEP 2: Detailed Main Points Analysis
        - Extract all significant key ideas (minimum 7)
        - Analyze the strength and validity of each argument
        - Identify the logical sequence of idea development
        - Note any paradigms or frameworks being utilized
        - Examine unstated assumptions
        - Identify potential counterarguments
        
        STEP 3: Comprehensive Supporting Evidence Examination
        - Catalog all forms of evidence presented (data, examples, citations)
        - Evaluate the quality and relevance of supporting evidence
        - Identify methodological approaches
        - Note significant examples and case studies
        - Examine the credibility of sources referenced
        - Identify evidence gaps or limitations
        
        STEP 4: Deep Synthesis and Integration
        - Create explicit connections between all major concepts
        - Develop a conceptual framework that organizes the content
        - Identify cross-cutting themes and patterns
        - Compare and contrast different viewpoints presented
        - Develop a hierarchical organization of concepts
        - Create visualizable knowledge structures
        
        STEP 5: Critical Evaluation
        - Assess overall strength of argumentation
        - Identify logical strengths and weaknesses
        - Note areas of particularly strong insight
        - Recognize limitations or gaps in reasoning
        - Suggest potential extensions or applications
        - Consider alternative interpretations
        
        Text: {text}
        
        IMPORTANT: In your final output:
        1. Provide an executive summary (150-200 words) at the beginning
        2. Create a tiered summary with progressive detail levels:
           - Level 1: Core essence (1-2 sentences)
           - Level 2: Key points outline (5-7 bullet points)
           - Level 3: Detailed analysis with all major concepts and relationships
        3. Include a visual structure representation (as text description)
        4. Organize with clear headers, logical flow, and numbered sections
        5. Conclude with 3-5 key implications or applications
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