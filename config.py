"""
Application configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global cache setting
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change')
    
    # API Keys
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'logs/app.log'
    
    # Cache
    CACHE_TYPE = 'filesystem'
    CACHE_DIR = 'cache'
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_ENABLED = CACHE_ENABLED
    
    # API
    API_TIMEOUT = 30
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB
    
    # Text Analysis
    MAX_TEXT_SIZE = 50000  # Maximum text size in characters
    DEFAULT_LANGUAGE = 'en'  # Default language for analysis
    
    # Perplexity API
    PERPLEXITY_BASE_URL = "https://api.perplexity.ai/v1"
    PERPLEXITY_MODEL = "mixtral-8x7b-instruct"
    
    # Results Storage
    RESULTS_DIR = 'results'

    @staticmethod
    def init_app(app):
        """Initialize application configuration"""
        # Validate required config
        if not Config.PERPLEXITY_API_KEY:
            app.logger.warning("PERPLEXITY_API_KEY not set - API features will be disabled")
        
        # Create necessary directories
        os.makedirs(Config.CACHE_DIR, exist_ok=True)
        os.makedirs(Config.RESULTS_DIR, exist_ok=True)