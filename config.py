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
    if PERPLEXITY_API_KEY:
        if not PERPLEXITY_API_KEY.startswith('pplx-'):
            raise ValueError("Invalid API key format - must start with 'pplx-'")
    
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
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '60'))
    API_MAX_RETRIES = int(os.getenv('API_MAX_RETRIES', '3'))
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB
    
    # Text Analysis
    MAX_TEXT_SIZE = 50000  # Maximum text size in characters
    DEFAULT_LANGUAGE = 'en'  # Default language for analysis
    
    # Perplexity API - API endpoint URL
    PERPLEXITY_BASE_URL = "https://api.perplexity.ai/chat/completions"
    PERPLEXITY_MODEL = os.getenv('PERPLEXITY_MODEL', 'sonar-pro')
    
    # Results Storage
    RESULTS_DIR = 'results'

    # Add a development mode flag
    DEVELOPMENT_MODE = False
    
    @staticmethod
    def init_app(app):
        """Initialize application configuration"""
        # Validate required config
        if not Config.PERPLEXITY_API_KEY:
            app.logger.warning("PERPLEXITY_API_KEY not set - API features will be disabled")
        
        # Create necessary directories
        os.makedirs(Config.CACHE_DIR, exist_ok=True)
        os.makedirs(Config.RESULTS_DIR, exist_ok=True)

    @staticmethod
    def validate_config():
        """Validate all required configuration"""
        if not Config.PERPLEXITY_API_KEY:
            raise ValueError("Missing PERPLEXITY_API_KEY in .env file")

    @staticmethod
    def use_mock_api():
        """Check if we should use mock API instead of real API"""
        return Config.DEVELOPMENT_MODE or not Config.PERPLEXITY_API_KEY.startswith('pplx-')