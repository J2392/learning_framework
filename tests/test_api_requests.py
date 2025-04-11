"""
Kiểm tra các API request đến Perplexity API
"""
import os
import sys
import unittest
import asyncio
import json
import logging
# Cần cài đặt: pip install aiohttp
import aiohttp
from unittest import mock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_api_requests')

# Try to import modules
try:
    from config import Config
    from dotenv import load_dotenv
except ImportError as e:
    logger.error(f"Lỗi import module: {e}")
    raise

# Run async function in tests
def run_async(coro):
    """Run coroutine in event loop"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

class TestAPIRequests(unittest.TestCase):
    """Kiểm tra các API request"""
    
    @classmethod
    def setUpClass(cls):
        """Thiết lập trước tất cả tests"""
        load_dotenv()
        cls.api_key = os.getenv('PERPLEXITY_API_KEY')
        cls.dev_mode = os.getenv('DEVELOPMENT_MODE', 'True').lower() == 'true'
        cls.model = os.getenv('PERPLEXITY_MODEL', 'sonar')
        cls.base_url = Config.PERPLEXITY_BASE_URL
        
        # Kiểm tra API key
        if not cls.api_key:
            logger.warning("API key không tồn tại, một số test sẽ bị bỏ qua")
    
    def setUp(self):
        """Thiết lập trước mỗi test"""
        # Tạo event loop cho async tests
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Dọn dẹp sau mỗi test"""
        self.loop.close()
    
    async def make_api_request(self, prompt, model=None, max_tokens=100, temperature=0.7, stream=False):
        """Thực hiện API request đến Perplexity API"""
        if not self.api_key:
            raise ValueError("API key không tồn tại")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        data = {
            "model": model or self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        # Chi tiết request
        logger.info(f"Gửi request đến: {self.base_url}")
        logger.info(f"Model: {model or self.model}")
        logger.info(f"Prompt: {prompt[:50]}...")
        logger.info(f"Tham số: max_tokens={max_tokens}, temperature={temperature}, stream={stream}")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=30
                ) as response:
                    elapsed_time = asyncio.get_event_loop().time() - start_time
                    status_code = response.status
                    response_text = await response.text()
                    
                    logger.info(f"Thời gian phản hồi: {elapsed_time:.2f}s")
                    logger.info(f"Status code: {status_code}")
                    
                    if status_code == 200:
                        response_json = json.loads(response_text)
                        return {
                            "success": True,
                            "status_code": status_code,
                            "response": response_json,
                            "elapsed_time": elapsed_time
                        }
                    else:
                        error_details = "Unknown error"
                        try:
                            error_json = json.loads(response_text)
                            if 'error' in error_json:
                                error_details = error_json['error']
                        except json.JSONDecodeError:
                            error_details = response_text[:200]
                            
                        logger.error(f"API error: {status_code} - {error_details}")
                        return {
                            "success": False,
                            "status_code": status_code,
                            "error": error_details,
                            "elapsed_time": elapsed_time
                        }
        except Exception as e:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Request exception: {type(e).__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"{type(e).__name__}: {str(e)}",
                "elapsed_time": elapsed_time
            }
    
    def test_api_url(self):
        """Kiểm tra URL của API hợp lệ"""
        logger.info(f"Kiểm tra URL API: {self.base_url}")
        self.assertTrue(self.base_url.startswith('https://'), "URL API phải bắt đầu bằng https://")
        self.assertIn('perplexity.ai', self.base_url, "URL API phải chứa domain perplexity.ai")
        self.assertTrue(self.base_url.endswith('/chat/completions'), "URL API phải kết thúc bằng /chat/completions")
    
    @unittest.skipIf(os.getenv('DEVELOPMENT_MODE', 'False').lower() == 'true' or \
                     os.getenv('PERPLEXITY_API_KEY') is None or \
                     not os.getenv('PERPLEXITY_API_KEY', '').startswith('pplx-'), 
                     "API key không tồn tại/không hợp lệ hoặc đang ở chế độ dev")
    def test_simple_request(self):
        """Kiểm tra yêu cầu API đơn giản"""
        logger.info("Kiểm tra yêu cầu API đơn giản")
        
        prompt = "What is machine learning?"
        result = run_async(self.make_api_request(prompt))
        
        # Kiểm tra request thành công
        self.assertTrue(result["success"], f"Request thất bại: {result.get('error', 'Unknown error')}")
        self.assertEqual(result["status_code"], 200, f"Status code không phải 200: {result.get('status_code')}")
        
        # Kiểm tra cấu trúc phản hồi
        response = result["response"]
        self.assertIn("choices", response, "Phản hồi thiếu trường 'choices'")
        self.assertTrue(len(response["choices"]) > 0, "Danh sách 'choices' rỗng")
        self.assertIn("message", response["choices"][0], "Phản hồi thiếu trường 'message' trong choice đầu tiên")
        self.assertIn("content", response["choices"][0]["message"], "Phản hồi thiếu trường 'content' trong message")
        
        # Log kết quả
        content = response["choices"][0]["message"]["content"]
        logger.info(f"Phản hồi: {content[:100]}...")
    
    @unittest.skipIf(os.getenv('DEVELOPMENT_MODE', 'False').lower() == 'true' or \
                     os.getenv('PERPLEXITY_API_KEY') is None or \
                     not os.getenv('PERPLEXITY_API_KEY', '').startswith('pplx-'), 
                     "API key không tồn tại/không hợp lệ hoặc đang ở chế độ dev")
    def test_different_temperatures(self):
        """Kiểm tra API với các giá trị temperature khác nhau"""
        logger.info("Kiểm tra các giá trị temperature khác nhau")
        
        prompt = "Write a short poem about artificial intelligence"
        temperatures = [0.0, 0.5, 1.0]
        results = {}
        
        for temp in temperatures:
            logger.info(f"Kiểm tra với temperature = {temp}")
            result = run_async(self.make_api_request(prompt, temperature=temp))
            self.assertTrue(result["success"], f"Request thất bại với temperature={temp}")
            results[temp] = result["response"]["choices"][0]["message"]["content"]
        
        # Log kết quả để so sánh thủ công
        for temp, content in results.items():
            logger.info(f"Temperature {temp}:\n{content[:100]}...\n")
        
        # Kiểm tra output có sự khác biệt với temperature khác nhau
        # Temperature 0.0 thường tạo ra output ổn định nhất, 1.0 tạo ra nhiều sự khác biệt nhất
        if results[0.0] == results[1.0]:
            logger.warning("Phản hồi giống nhau giữa temperature=0.0 và temperature=1.0, có thể là trùng hợp")
    
    @unittest.skipIf(os.getenv('DEVELOPMENT_MODE', 'False').lower() == 'true' or \
                     os.getenv('PERPLEXITY_API_KEY') is None or \
                     not os.getenv('PERPLEXITY_API_KEY', '').startswith('pplx-'), 
                     "API key không tồn tại/không hợp lệ hoặc đang ở chế độ dev")
    def test_max_tokens_limit(self):
        """Kiểm tra giới hạn max_tokens"""
        logger.info("Kiểm tra giới hạn max_tokens")
        
        prompt = "Write a detailed explanation of how neural networks work"
        max_tokens_values = [10, 50, 100]
        results = {}
        
        for max_tokens in max_tokens_values:
            logger.info(f"Kiểm tra với max_tokens = {max_tokens}")
            result = run_async(self.make_api_request(prompt, max_tokens=max_tokens))
            self.assertTrue(result["success"], f"Request thất bại với max_tokens={max_tokens}")
            
            content = result["response"]["choices"][0]["message"]["content"]
            results[max_tokens] = content
            
            # Đếm số từ gần đúng
            word_count = len(content.split())
            logger.info(f"max_tokens={max_tokens}, word count ~{word_count}")
            
            # max_tokens không phải là số từ chính xác, nhưng phải có mối tương quan
            self.assertLessEqual(word_count, max_tokens * 2, f"Số từ ({word_count}) vượt quá giới hạn max_tokens*2")
    
    @unittest.skipIf(True, "Stream mode test cần xử lý đặc biệt, tạm bỏ qua")
    def test_stream_mode(self):
        """Kiểm tra chế độ stream"""
        logger.info("Kiểm tra chế độ stream")
        
        prompt = "Explain the concept of relativity"
        result = run_async(self.make_api_request(prompt, stream=True))
        
        # Streaming response needs special handling, just check if the request succeeds
        self.assertTrue(result["success"], "Stream request thất bại")
    
    @unittest.skipIf(os.getenv('DEVELOPMENT_MODE', 'False').lower() == 'true' or \
                     os.getenv('PERPLEXITY_API_KEY') is None or \
                     not os.getenv('PERPLEXITY_API_KEY', '').startswith('pplx-'), 
                     "API key không tồn tại/không hợp lệ hoặc đang ở chế độ dev")
    def test_long_prompt(self):
        """Kiểm tra prompt dài"""
        logger.info("Kiểm tra prompt dài")
        
        # Tạo prompt dài
        prompt = "Summarize the following text:\n\n" + ("This is a test text. " * 50)
        result = run_async(self.make_api_request(prompt))
        
        self.assertTrue(result["success"], "Request với prompt dài thất bại")
        self.assertEqual(result["status_code"], 200, f"Status code không phải 200: {result.get('status_code')}")
        
        # Kiểm tra phản hồi
        response = result["response"]
        self.assertIn("choices", response, "Phản hồi thiếu trường 'choices'")
        content = response["choices"][0]["message"]["content"]
        logger.info(f"Phản hồi với prompt dài: {content[:100]}...")
    
    def test_format_prompt(self):
        """Kiểm tra format prompt chính xác"""
        logger.info("Kiểm tra format prompt")
        
        # Test với mock để tránh gọi API thực
        with mock.patch('aiohttp.ClientSession.post') as mock_post:
            # Mock response
            mock_response = mock.MagicMock()
            mock_response.status = 200
            mock_response.text = mock.AsyncMock(return_value=json.dumps({
                "choices": [{"message": {"content": "Mock response"}}]
            }))
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # Gọi hàm make_api_request để capture request body
            prompt = "Test prompt"
            run_async(self.make_api_request(prompt))
            
            # Kiểm tra format của request
            call_args = mock_post.call_args
            self.assertIsNotNone(call_args, "Không có request nào được gọi")
            
            # Kiểm tra JSON body
            json_data = call_args[1]['json']
            self.assertEqual(json_data["model"], self.model, f"Model không khớp: {json_data['model']} != {self.model}")
            self.assertEqual(len(json_data["messages"]), 2, "Phải có đúng 2 messages (system + user)")
            self.assertEqual(json_data["messages"][0]["role"], "system", "Message đầu tiên phải có role='system'")
            self.assertEqual(json_data["messages"][1]["role"], "user", "Message thứ hai phải có role='user'")
            self.assertEqual(json_data["messages"][1]["content"], prompt, f"Prompt không khớp: {json_data['messages'][1]['content']} != {prompt}")
    
    @mock.patch('aiohttp.ClientSession.post')
    def test_error_handling_invalid_api_key(self, mock_post):
        """Kiểm tra xử lý lỗi API key không hợp lệ"""
        logger.info("Kiểm tra xử lý lỗi API key không hợp lệ")
        
        # Mock response for unauthorized error
        mock_response = mock.MagicMock()
        mock_response.status = 401
        mock_response.text = mock.AsyncMock(return_value=json.dumps({
            "error": {
                "message": "Invalid API key",
                "type": "invalid_request_error",
                "param": None,
                "code": None
            }
        }))
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Test request
        prompt = "Test prompt"
        result = run_async(self.make_api_request(prompt))
        
        # Kiểm tra xử lý lỗi
        self.assertFalse(result["success"], "Request không nên thành công với API key không hợp lệ")
        self.assertEqual(result["status_code"], 401, "Status code phải là 401 Unauthorized")
        self.assertIn("error", result, "Kết quả phải chứa thông tin lỗi")
    
    @mock.patch('aiohttp.ClientSession.post')
    def test_error_handling_invalid_model(self, mock_post):
        """Kiểm tra xử lý lỗi model không hợp lệ"""
        logger.info("Kiểm tra xử lý lỗi model không hợp lệ")
        
        # Mock response for invalid model error
        mock_response = mock.MagicMock()
        mock_response.status = 400
        mock_response.text = mock.AsyncMock(return_value=json.dumps({
            "error": {
                "message": "Model 'invalid-model' not found",
                "type": "invalid_request_error",
                "param": "model",
                "code": None
            }
        }))
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Test request with invalid model
        prompt = "Test prompt"
        result = run_async(self.make_api_request(prompt, model="invalid-model"))
        
        # Kiểm tra xử lý lỗi
        self.assertFalse(result["success"], "Request không nên thành công với model không hợp lệ")
        self.assertEqual(result["status_code"], 400, "Status code phải là 400 Bad Request")
        self.assertIn("error", result, "Kết quả phải chứa thông tin lỗi")
    
    @mock.patch('aiohttp.ClientSession.post')
    def test_error_handling_rate_limit(self, mock_post):
        """Kiểm tra xử lý lỗi vượt quá giới hạn tốc độ"""
        logger.info("Kiểm tra xử lý lỗi vượt quá giới hạn tốc độ")
        
        # Mock response for rate limit error
        mock_response = mock.MagicMock()
        mock_response.status = 429
        mock_response.text = mock.AsyncMock(return_value=json.dumps({
            "error": {
                "message": "Rate limit exceeded. Please try again later.",
                "type": "rate_limit_error",
                "param": None,
                "code": None
            }
        }))
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Test request
        prompt = "Test prompt"
        result = run_async(self.make_api_request(prompt))
        
        # Kiểm tra xử lý lỗi
        self.assertFalse(result["success"], "Request không nên thành công khi vượt quá giới hạn tốc độ")
        self.assertEqual(result["status_code"], 429, "Status code phải là 429 Too Many Requests")
        self.assertIn("error", result, "Kết quả phải chứa thông tin lỗi")
    
    @mock.patch('aiohttp.ClientSession.post')
    def test_error_handling_timeout(self, mock_post):
        """Kiểm tra xử lý lỗi timeout"""
        logger.info("Kiểm tra xử lý lỗi timeout")
        
        # Mock timeout by raising exception
        mock_post.side_effect = asyncio.TimeoutError("Request timed out")
        
        # Test request
        prompt = "Test prompt"
        result = run_async(self.make_api_request(prompt))
        
        # Kiểm tra xử lý lỗi
        self.assertFalse(result["success"], "Request không nên thành công khi bị timeout")
        self.assertIn("error", result, "Kết quả phải chứa thông tin lỗi")
        self.assertIn("TimeoutError", str(result["error"]), "Lỗi phải là TimeoutError")
    
    def test_model_list(self):
        """Kiểm tra danh sách model hợp lệ"""
        logger.info("Kiểm tra danh sách model hợp lệ")
        
        # Danh sách model hợp lệ của Perplexity API
        valid_models = [
            "sonar",
            "sonar-pro",
            "sonar-small-chat", 
            "sonar-medium-chat",
            "sonar-small-online", 
            "sonar-medium-online",
            "sonar-deep-research", 
            "sonar-reasoning", 
            "sonar-reasoning-pro", 
            "r1-1776",
            "llama-3-70b-8192", 
            "claude-3-opus-20240229"
        ]
        
        self.assertIn(self.model, valid_models, f"Model mặc định '{self.model}' không nằm trong danh sách model hợp lệ")

if __name__ == '__main__':
    unittest.main(verbosity=2) 