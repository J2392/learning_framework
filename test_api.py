"""
Test script for Perplexity API
"""
import os
import asyncio
import aiohttp
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test_api')

# Load environment variables
load_dotenv()

async def test_perplexity_api():
    """Test Perplexity API connection"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        logger.error("API key not found. Please set PERPLEXITY_API_KEY in .env file")
        return
        
    if 'xxxxxxxx' in api_key:
        logger.error("Using placeholder API key. Please update with your actual API key in .env")
        logger.error("Get a valid API key from: https://www.perplexity.ai/settings/api")
        return

    # Test both endpoints to see which one works
    endpoints = [
        "https://api.perplexity.ai/chat/completions"  # Endpoint chính xác theo tài liệu
    ]
    
    for endpoint in endpoints:
        logger.info(f"Testing endpoint: {endpoint}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        data = {
            "model": "sonar-medium-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Hello, how are you?"
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    headers=headers,
                    json=data,
                    timeout=30
                ) as response:
                    response_text = await response.text()
                    logger.info(f"Response status: {response.status}")
                    
                    if response.status == 200:
                        logger.info(f"Endpoint {endpoint} works!")
                        logger.info(f"Response: {response_text[:200]}")
                    else:
                        logger.error(f"Endpoint {endpoint} failed with status {response.status}")
                        logger.error(f"Response: {response_text}")
        except Exception as e:
            logger.error(f"Error testing {endpoint}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_perplexity_api())