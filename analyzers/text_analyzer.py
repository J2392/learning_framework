# analyzers/text_analyzer.py
import spacy
import re
from collections import Counter
from functools import lru_cache
from typing import List, Dict, Any, Union
import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

class TextAnalyzer:
    """
    NLP analyzer for extracting meaningful information from text
    """
    
    def __init__(self):
        self.max_text_size = Config.MAX_TEXT_SIZE
        self.default_language = Config.DEFAULT_LANGUAGE
        try:
            # Load appropriate language model
            if self.default_language == "en":
                self._load_spacy_model("en_core_web_sm")
            else:
                logger.warning(f"Language {self.default_language} not supported, using English...")
                self._load_spacy_model("en_core_web_sm")
        except Exception as e:
            logger.error(f"Error initializing TextAnalyzer: {str(e)}")
            raise
        
        # Additional stopwords
        self.additional_stopwords = ["actually", "basically", "generally", "literally", "really"]
        
        # Add stopwords to spaCy's list
        for word in self.additional_stopwords:
            self.nlp.Defaults.stop_words.add(word)
    
    def _load_spacy_model(self, model_name: str):
        """Load spaCy model with error handling and download if needed"""
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            logger.warning(f"Model {model_name} not found, trying to download...")
            import subprocess
            subprocess.run([sys.executable, "-m", "spacy", "download", model_name], check=True)
            self.nlp = spacy.load(model_name)
    
    def sanitize_text(self, text: str) -> str:
        """
        Sanitize input text
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove dangerous special characters
        text = re.sub(r'[<>]', '', text)
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32)
        return text.strip()
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze input text
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis results
        """
        # Validate input
        if not text:
            return self._get_error_result("No text provided")
            
        if len(text) > self.max_text_size:
            return self._get_error_result(f"Text exceeds maximum size of {self.max_text_size} characters")

        try:
            # Perform basic analysis
            words = self._tokenize(text)
            
            return {
                'text': text,
                'language': self.default_language,
                'word_count': len(words),
                'complexity': self._calculate_complexity(words),
                'error': None
            }

        except Exception as e:
            return self._get_error_result(str(e))

    def _tokenize(self, text: str) -> List[str]:
        """Split text into words"""
        return re.findall(r'\w+', text.lower())

    def _calculate_complexity(self, words: List[str]) -> int:
        """Calculate text complexity score"""
        if not words:
            return 0
        avg_word_length = sum(len(word) for word in words) / len(words)
        return min(5, int(avg_word_length / 2))

    def _get_error_result(self, error_message: str) -> Dict[str, Any]:
        """Return error result structure"""
        return {
            'text': '',
            'language': self.default_language,
            'word_count': 0,
            'complexity': 0,
            'error': error_message
        }

    def extract_key_concepts(self, doc) -> List[str]:
        """Extract key concepts from text"""
        concepts = []
        for sent in doc.sents:
            for token in sent:
                if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop:
                    concepts.append(token.text)
        return list(set(concepts))
    
    def extract_keywords(self, doc) -> List[str]:
        """Extract important keywords"""
        keywords = []
        for token in doc:
            if not token.is_stop and token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB']:
                keywords.append(token.text)
        return list(set(keywords))
    
    def extract_entities(self, doc) -> List[Dict[str, str]]:
        """Extract named entities"""
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        return entities
    
    def extract_sentences(self, doc) -> List[str]:
        """Extract sentences from text"""
        return [sent.text.strip() for sent in doc.sents]
    
    def extract_noun_chunks(self, doc) -> List[str]:
        """Extract noun phrases"""
        return [chunk.text for chunk in doc.noun_chunks]
    
    def extract_related_concepts(self, doc) -> Dict[str, List[str]]:
        """Extract related concepts for each key concept"""
        # Extract key concepts first
        key_concepts = self.extract_key_concepts(doc)
        
        # Find related concepts based on co-occurrence in sentences
        related = {}
        for concept in key_concepts:
            related[concept] = []
            
            # Find words/phrases appearing in the same sentence as the concept
            for sent in doc.sents:
                if concept.lower() in sent.text.lower():
                    # Extract other noun chunks from this sentence
                    for chunk in sent.noun_chunks:
                        if (chunk.text.lower() != concept.lower() and 
                            not any(chunk.text.lower() in rc.lower() for rc in related[concept]) and
                            len(chunk.text) > 3):
                            related[concept].append(chunk.text)
            
            # Limit the number of related concepts
            related[concept] = related[concept][:5]
            
        return related
    
    def extract_context(self, doc) -> str:
        """Determine the general context of the text"""
        # Extract and analyze frequency of meaningful words
        content_words = [token.text.lower() for token in doc 
                        if not token.is_stop and not token.is_punct and token.pos_ in ('NOUN', 'PROPN')]
        
        # Count frequency
        word_freq = Counter(content_words)
        common_words = [word for word, freq in word_freq.most_common(10)]
        
        # Domain keywords
        domain_keywords = {
            "education": ["learning", "education", "teaching", "knowledge", "understanding", "method"],
            "business": ["business", "market", "customer", "sales", "marketing", "strategy"],
            "technology": ["software", "data", "technology", "system", "network", "internet"],
            "science": ["research", "method", "experiment", "theory", "analysis"],
            "health": ["health", "disease", "treatment", "doctor", "medicine", "patient"]
        }
        
        # Determine the domain with the most matches
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for word in common_words if any(kw in word for kw in keywords))
            domain_scores[domain] = score
        
        # Choose the domain with the highest score
        if domain_scores:
            best_domain = max(domain_scores.items(), key=lambda x: x[1])
            if best_domain[1] > 0:
                return best_domain[0]
        
        # If no specific domain is identified
        return "general topic"
    
    def extract_problems(self, doc) -> List[str]:
        """Extract problems mentioned in the text"""
        problems = []
        for sent in doc.sents:
            if any(word in sent.text.lower() for word in ['problem', 'issue', 'challenge', 'difficulty']):
                problems.append(sent.text)
        return problems
    
    def identify_themes(self, doc) -> List[str]:
        """Identify main themes"""
        themes = []
        for sent in doc.sents:
            if len(sent) > 5:  # Only consider sentences of reasonable length
                themes.append(sent.text)
        return themes[:5]  # Return top 5 themes
    
    def assess_complexity(self, doc) -> Dict[str, float]:
        """Assess text complexity"""
        return {
            "avg_sentence_length": sum(len(sent) for sent in doc.sents) / len(list(doc.sents)) if doc.sents else 0,
            "unique_words": len(set(token.text for token in doc)),
            "total_words": len(doc)
        }

# Create a singleton instance
text_analyzer = TextAnalyzer()