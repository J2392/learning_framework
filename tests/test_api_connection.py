"""
Kiểm tra kết nối với Perplexity API
"""
import os
import sys
import unittest
import asyncio
import json
import logging
from unittest import mock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_api_connection')

# Import configuration
try:
    from config import Config
    from dotenv import load_dotenv
except ImportError as e:
    logger.error(f"Lỗi import: {e}")
    raise

class TestAPIConnection(unittest.TestCase):
    """Kiểm tra kết nối với Perplexity API"""
    
    def setUp(self):
        """Thiết lập trước mỗi test"""
        load_dotenv()
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.dev_mode = os.getenv('DEVELOPMENT_MODE', 'False').lower() == 'true'
        self.model = os.getenv('PERPLEXITY_MODEL', 'sonar')
        self.base_url = Config.PERPLEXITY_BASE_URL
        
        # Kiểm tra API key
        if not self.api_key:
            self.skipTest("API key không tồn tại, bỏ qua test")
        
        # Tạo event loop cho async tests
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
    def tearDown(self):
        """Dọn dẹp sau mỗi test"""
        self.loop.close()
    
    def test_base_url_format(self):
        """Kiểm tra định dạng URL cơ sở"""
        logger.info(f"Kiểm tra URL cơ sở: {self.base_url}")
        self.assertTrue(self.base_url.startswith('https://'), "URL cơ sở phải bắt đầu bằng https://")
        self.assertIn('perplexity.ai', self.base_url, "URL cơ sở phải chứa domain perplexity.ai")
    
    def run_async_test(self, coro):
        """Chạy một coroutine async trong unittest"""
        return self.loop.run_until_complete(coro)
    
    def test_api_key_format(self):
        """Kiểm tra định dạng API key"""
        logger.info("Kiểm tra định dạng API key")
        self.assertTrue(self.api_key.startswith('pplx-'), 
                       f"API key phải bắt đầu bằng 'pplx-', hiện tại: {self.api_key[:8]}...")
    
    async def _send_test_request(self):
        """Gửi một request kiểm tra đến API"""
        # Note: need to install aiohttp: pip install aiohttp
        # Import temporarily to avoid dependency issues
        try:
            import aiohttp
        except ImportError:
            logger.error("Không thể import aiohttp. Hãy cài đặt: pip install aiohttp")
            raise
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, this is a test request."}
            ],
            "max_tokens": 100,
            "temperature": 0.7,
            "stream": False
        }
        
        # Log chi tiết request
        logger.info(f"Gửi request đến: {self.base_url}")
        logger.info(f"Model: {self.model}")
        logger.info(f"API key (trích): {self.api_key[:8]}...{self.api_key[-4:]}")
        
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
                        logger.info("Kết nối thành công")
                        try:
                            response_json = json.loads(response_text)
                            return {
                                "success": True,
                                "status_code": status_code,
                                "response": response_json,
                                "elapsed_time": elapsed_time
                            }
                        except json.JSONDecodeError:
                            logger.error(f"Lỗi giải mã JSON: {response_text[:200]}")
                            return {
                                "success": False,
                                "status_code": status_code,
                                "error": "Lỗi giải mã JSON",
                                "response_text": response_text[:200],
                                "elapsed_time": elapsed_time
                            }
                    else:
                        logger.error(f"Lỗi kết nối API: {status_code}")
                        error_detail = ""
                        try:
                            error_json = json.loads(response_text)
                            if isinstance(error_json, dict) and 'error' in error_json:
                                error_detail = error_json['error'].get('message', '')
                        except:
                            error_detail = response_text[:200]
                            
                        return {
                            "success": False,
                            "status_code": status_code,
                            "error": f"HTTP error {status_code}",
                            "error_detail": error_detail,
                            "elapsed_time": elapsed_time
                        }
        except Exception as e:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Lỗi kết nối: {str(e)}")
            return {
                "success": False,
                "error": f"Lỗi kết nối: {str(e)}",
                "elapsed_time": elapsed_time
            }
    
    def test_api_connection(self):
        """Kiểm tra kết nối API trong môi trường thực tế"""
        if self.dev_mode:
            logger.info("Đang ở chế độ phát triển, bỏ qua test kết nối API thực")
            self.skipTest("Đang ở chế độ phát triển")
        
        logger.info("Kiểm tra kết nối API thực")
        result = self.run_async_test(self._send_test_request())
        
        # Nếu status code là 400 và lỗi là về model không hợp lệ, ghi lại thông tin chi tiết
        if (not result['success'] and result.get('status_code') == 400 and 
            'invalid_model' in str(result.get('error_detail', '')).lower()):
            logger.error(f"Lỗi model không hợp lệ: {self.model}")
            logger.error(f"Chi tiết lỗi: {result.get('error_detail', '')}")
            self.fail(f"Model '{self.model}' không hợp lệ. Xem logs để biết thêm chi tiết.")
        
        # Check various error conditions and provide detailed logs
        if not result['success']:
            if 'status_code' in result:
                if result['status_code'] == 401:
                    logger.error("Lỗi xác thực API key (401 Unauthorized)")
                    self.fail("API key không hợp lệ hoặc đã hết hạn")
                elif result['status_code'] == 403:
                    logger.error("Lỗi quyền truy cập (403 Forbidden)")
                    self.fail("Không có quyền truy cập API")
                elif result['status_code'] == 404:
                    logger.error("Endpoint không tồn tại (404 Not Found)")
                    self.fail(f"Endpoint {self.base_url} không tồn tại")
                elif result['status_code'] == 429:
                    logger.error("Vượt quá giới hạn tốc độ (429 Too Many Requests)")
                    self.fail("Đã vượt quá giới hạn số lượng request")
                else:
                    logger.error(f"Lỗi HTTP không mong đợi: {result.get('status_code')}")
                    logger.error(f"Chi tiết: {result.get('error_detail', '')}")
                    self.fail(f"Lỗi HTTP {result.get('status_code')}: {result.get('error_detail', '')}")
            else:
                logger.error(f"Lỗi kết nối: {result.get('error', 'Unknown error')}")
                self.fail(f"Không thể kết nối: {result.get('error', 'Unknown error')}")
        
        self.assertTrue(result['success'], "Kết nối API không thành công")
        
        # Verify response format
        self.assertIn('response', result, "Phản hồi API không có dữ liệu")
        response = result['response']
        
        # Check for expected fields in the response
        required_fields = ['id', 'choices', 'model', 'object']
        for field in required_fields:
            self.assertIn(field, response, f"Phản hồi API thiếu trường '{field}'")
        
        # Check choices format
        self.assertIsInstance(response['choices'], list, "Trường 'choices' không phải là danh sách")
        self.assertTrue(len(response['choices']) > 0, "Danh sách 'choices' rỗng")
        
        # Verify response time is reasonable
        self.assertLess(result['elapsed_time'], 10, "Thời gian phản hồi quá lâu (>10s)")
        
        logger.info(f"Kết nối API thành công. Thời gian: {result['elapsed_time']:.2f}s")
    
    @mock.patch('aiohttp.ClientSession.post')
    def test_api_auth_error_handling(self, mock_post):
        """Kiểm tra xử lý lỗi xác thực API"""
        # Mock response for authentication error
        mock_response = mock.MagicMock()
        mock_response.status = 401
        mock_response.text = mock.AsyncMock(return_value=json.dumps({
            "error": {
                "message": "Invalid API key",
                "type": "invalid_request_error",
                "code": 401
            }
        }))
        mock_post.return_value.__aenter__.return_value = mock_response
        
        logger.info("Kiểm tra xử lý lỗi xác thực API")
        result = self.run_async_test(self._send_test_request())
        
        self.assertFalse(result['success'], "Không phát hiện lỗi xác thực")
        self.assertEqual(result['status_code'], 401, "Mã lỗi không phải 401")
    
    @mock.patch('aiohttp.ClientSession.post')
    def test_api_rate_limit_handling(self, mock_post):
        """Kiểm tra xử lý lỗi vượt quá giới hạn tốc độ"""
        # Mock response for rate limit error
        mock_response = mock.MagicMock()
        mock_response.status = 429
        mock_response.text = mock.AsyncMock(return_value=json.dumps({
            "error": {
                "message": "Rate limit exceeded",
                "type": "rate_limit_error",
                "code": 429
            }
        }))
        mock_post.return_value.__aenter__.return_value = mock_response
        
        logger.info("Kiểm tra xử lý lỗi vượt quá giới hạn tốc độ")
        result = self.run_async_test(self._send_test_request())
        
        self.assertFalse(result['success'], "Không phát hiện lỗi giới hạn tốc độ")
        self.assertEqual(result['status_code'], 429, "Mã lỗi không phải 429")
    
    @mock.patch('aiohttp.ClientSession.post')
    def test_api_success_response_handling(self, mock_post):
        """Kiểm tra xử lý phản hồi thành công từ API"""
        # Mock successful response
        mock_response = mock.MagicMock()
        mock_response.status = 200
        mock_response.text = mock.AsyncMock(return_value=json.dumps({
            "id": "test-id",
            "object": "chat.completion",
            "created": 1625097587,
            "model": self.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a test response."
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 5,
                "total_tokens": 25
            }
        }))
        mock_post.return_value.__aenter__.return_value = mock_response
        
        logger.info("Kiểm tra xử lý phản hồi thành công từ API")
        result = self.run_async_test(self._send_test_request())
        
        self.assertTrue(result['success'], "Phát hiện lỗi khi không có lỗi")
        self.assertEqual(result['status_code'], 200, "Mã phản hồi không phải 200")
        self.assertIn('choices', result['response'], "Phản hồi không có trường 'choices'")
        self.assertEqual(len(result['response']['choices']), 1, "Số lượng choices không phải 1")
        self.assertEqual(result['response']['choices'][0]['message']['content'], 
                        "This is a test response.", "Nội dung phản hồi không khớp")

if __name__ == '__main__':
    unittest.main(verbosity=2) 