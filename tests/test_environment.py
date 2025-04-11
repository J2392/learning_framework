"""
Kiểm tra cấu hình môi trường và các biến môi trường
"""
import os
import sys
import unittest
from unittest import mock
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_environment')

# Import configuration
try:
    from config import Config
    from dotenv import load_dotenv
except ImportError as e:
    logger.error(f"Lỗi import: {e}")
    raise

class TestEnvironment(unittest.TestCase):
    """Kiểm tra cấu hình môi trường"""
    
    def setUp(self):
        """Thiết lập trước mỗi test"""
        load_dotenv()
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.dev_mode = os.getenv('DEVELOPMENT_MODE', 'False').lower() == 'true'
        self.model = os.getenv('PERPLEXITY_MODEL', 'sonar')
        
    def test_api_key_exists(self):
        """Kiểm tra API key tồn tại"""
        logger.info("Testing API key exists")
        self.assertIsNotNone(self.api_key, "API key không được định nghĩa trong .env")
        
    def test_api_key_format(self):
        """Kiểm tra định dạng API key"""
        if self.api_key:
            logger.info("Testing API key format")
            self.assertTrue(self.api_key.startswith('pplx-'), 
                           f"API key phải bắt đầu bằng 'pplx-', hiện tại: {self.api_key[:8]}...")
    
    def test_development_mode(self):
        """Kiểm tra chế độ phát triển"""
        logger.info(f"Development mode is: {self.dev_mode}")
        # Kiểm tra chế độ phát triển trong Config
        self.assertEqual(Config.DEVELOPMENT_MODE, self.dev_mode,
                        f"Chế độ phát triển trong Config ({Config.DEVELOPMENT_MODE}) không khớp với biến môi trường ({self.dev_mode})")
    
    def test_model_exists(self):
        """Kiểm tra model đã được định nghĩa"""
        logger.info(f"Testing model name: {self.model}")
        self.assertIsNotNone(self.model, "Tên model không được định nghĩa")
        
    def test_model_is_valid(self):
        """Kiểm tra model hợp lệ"""
        valid_models = ['sonar', 'sonar-pro', 'sonar-small-online', 'sonar-medium-online',
                        'sonar-deep-research', 'sonar-reasoning', 'sonar-reasoning-pro', 'r1-1776',
                        'llama-3-70b-8192', 'claude-3-opus-20240229']
        logger.info(f"Kiểm tra model '{self.model}' có hợp lệ")
        self.assertIn(self.model, valid_models, f"Model '{self.model}' không hợp lệ. Các model hợp lệ: {valid_models}")
    
    def test_directories_exist(self):
        """Kiểm tra các thư mục cần thiết đã tồn tại"""
        logger.info("Kiểm tra các thư mục cần thiết")
        required_dirs = ['logs', 'cache', 'results', 'static', 'templates', 'analyzers', 'generators']
        root_dir = os.path.dirname(os.path.dirname(__file__))
        
        for dir_name in required_dirs:
            dir_path = os.path.join(root_dir, dir_name)
            self.assertTrue(os.path.isdir(dir_path), f"Thư mục '{dir_name}' không tồn tại")
            logger.info(f"Thư mục '{dir_name}' tồn tại: {os.path.isdir(dir_path)}")
            
    def test_mock_api_decision(self):
        """Kiểm tra quyết định sử dụng mock API"""
        logger.info("Kiểm tra quyết định sử dụng mock API")
        
        # Reload config FIRST to ensure it reflects current env vars
        from importlib import reload
        import config
        reload(config)
        
        # Now call the function with the reloaded config
        use_mock = config.Config.use_mock_api() 
        
        # Logic kỳ vọng: Mirror the logic from Config.use_mock_api directly
        expected_mock = config.Config.DEVELOPMENT_MODE or not (config.Config.PERPLEXITY_API_KEY and config.Config.PERPLEXITY_API_KEY.startswith('pplx-'))
            
        self.assertEqual(use_mock, expected_mock, 
                        f"Quyết định mock API ({use_mock}) không khớp với dự đoán ({expected_mock}) [Config DevMode: {config.Config.DEVELOPMENT_MODE}, Config API Key: {config.Config.PERPLEXITY_API_KEY[:8]}...]" )
        logger.info(f"Sử dụng mock API: {use_mock}, Dự đoán: {expected_mock}")
    
    @mock.patch.dict(os.environ, {"DEVELOPMENT_MODE": "False"})
    def test_config_without_dev_mode(self):
        """Kiểm tra cấu hình với DEVELOPMENT_MODE=False"""
        logger.info("Kiểm tra cấu hình với DEVELOPMENT_MODE=False")
        # Reload config with mocked environment
        from importlib import reload
        import config
        reload(config)
        
        self.assertFalse(config.Config.DEVELOPMENT_MODE, 
                        "Config.DEVELOPMENT_MODE không phải False khi biến môi trường DEVELOPMENT_MODE=False")

if __name__ == '__main__':
    unittest.main(verbosity=2)