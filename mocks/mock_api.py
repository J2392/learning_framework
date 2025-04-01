"""
Mock Perplexity API for development without API key
"""
import random
import time

class MockPerplexityAPI:
    def __init__(self):
        self.questions = [
            "What are the key principles discussed in this text?",
            "How do these concepts relate to each other?",
            "What evidence supports the main argument?",
            "What are potential counterarguments to these ideas?",
            "How could these concepts be applied in a different context?"
        ]
        
        self.explanations = [
            "Basic explanation: This text explores fundamental concepts in the field.",
            "Intermediate explanation: The ideas presented connect theory with practice.",
            "Advanced explanation: The nuanced relationships between concepts reveal deeper patterns."
        ]
        
        # Add more mock responses as needed
        
    def get_response(self, prompt, category):
        """Simulate API response with a delay"""
        # Add random delay to simulate network latency
        time.sleep(random.uniform(0.5, 1.5))
        
        if "question" in category:
            return random.sample(self.questions, min(3, len(self.questions)))
        elif "explanation" in category:
            return self.explanations
        elif "key_term" in category:
            return [
                "Term 1: First important concept in the text",
                "Term 2: Second key term with detailed explanation",
                "Term 3: Another critical concept from the material"
            ]
        # Add more categories as needed
        
        return ["Generated content for " + category] 