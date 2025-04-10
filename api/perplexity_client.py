"""
Perplexity API client for text analysis
"""
import os
import json
import requests
import asyncio
from config import Config

class PerplexityAnalyzer:
    """Analyzer class using Perplexity API"""
    
    def __init__(self, model=None):
        self.api_key = Config.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = model or "sonar-pro"
        
    async def analyze(self, text, generators=None):
        """
        Analyze text using Perplexity API
        """
        if not text:
            return {"error": "No text provided"}
            
        # If no specific generators are requested, use all available
        from generators import AVAILABLE_GENERATORS
        if not generators:
            generators = list(AVAILABLE_GENERATORS.keys())
            
        result = {}
        
        # Run each generator
        for generator_key in generators:
            if generator_key in AVAILABLE_GENERATORS:
                generator_func = AVAILABLE_GENERATORS[generator_key]
                try:
                    # Call API with prompt generated by the generator function
                    prompt = generator_func(text)
                    api_result = self._call_api(prompt)
                    result[generator_key] = api_result
                except Exception as e:
                    result[generator_key] = {"error": str(e)}
                    
        return result
        
    def _call_api(self, prompt):
        """
        Call Perplexity API
        """
        # MOCK implementation for testing
        if Config.is_development_mode():
            # Return mock data for development mode
            return self._get_mock_response(prompt)
            
        # Real API call implementation
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            return self._parse_response(response.json())
        except requests.exceptions.RequestException as e:
            # Handle API errors
            return {"error": f"API error: {str(e)}"}
    
    def _parse_response(self, response_data):
        """Parse API response"""
        try:
            content = response_data["choices"][0]["message"]["content"]
            # Try to parse as JSON if possible
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Return as raw text if not valid JSON
                return {"text": content}
        except (KeyError, IndexError):
            return {"error": "Invalid API response format"}
            
    def _get_mock_response(self, prompt):
        """Return mock data for testing"""
        if "questions" in prompt.lower():
            return [
                "1. **What are the ethical implications of AI in healthcare diagnostics?**",
                "2. **How can diverse and representative datasets be effectively integrated?**",
                "3. **What collaborative measures should regulatory bodies adopt?**",
                "4. **How can transparency and accountability help address fairness concerns?**",
                "5. **What role does informed consent play in ethical AI use?**"
            ]
        elif "explain" in prompt.lower():
            return {
                "basic": "AI in healthcare offers benefits but raises ethical concerns about bias and inequality.",
                "intermediate": "AI can revolutionize diagnostics but may introduce bias that worsens health disparities.",
                "advanced": "The integration of sophisticated AI systems presents complex ethical challenges..."
            }
        else:
            return {"text": "Mock response for: " + prompt[:50] + "..."}
