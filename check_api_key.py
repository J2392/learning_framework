"""
Script to verify the Perplexity API key
"""
import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def main():
    # Get API key
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("❌ ERROR: No API key found in .env file")
        return
    
    if 'YOUR_ACTUAL_API_KEY_HERE' in api_key:
        print("❌ ERROR: You're using a placeholder API key")
        print("Please update your .env file with a real API key from https://www.perplexity.ai/settings/api")
        return
    
    # Check if API key starts with pplx-
    if not api_key.startswith('pplx-'):
        print("❌ ERROR: Invalid API key format")
        print("Perplexity API keys should start with 'pplx-'")
        return
    
    # Simple test request to Perplexity API
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Hello, are you working?"
            }
        ]
    }
    
    print("\n📡 Testing Perplexity API connection...")
    print(f"🔑 Using API key: {api_key[:8]}...{api_key[-4:]}")
    print(f"🌐 URL: {url}")
    print(f"📦 Request data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"\n🔄 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! API key is valid and working.")
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"\n💬 Response from API:\n{message}")
        elif response.status_code == 401:
            print("❌ ERROR: Unauthorized (401)")
            print("Your API key is invalid or has expired.")
            print("Please check or regenerate your API key at: https://www.perplexity.ai/settings/api")
        elif response.status_code == 404:
            print("❌ ERROR: Not Found (404)")
            print("The API endpoint URL may be incorrect.")
            print("Please check the current Perplexity API documentation.")
        else:
            print(f"❌ ERROR: Unexpected status code {response.status_code}")
            print(f"Response content: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

    # Thêm logging chi tiết hơn
    print(f"Current working directory: {os.getcwd()}")
    print(f"Loaded API key: {api_key}")
    print(f"Length of API key: {len(api_key) if api_key else 0}")

if __name__ == "__main__":
    main() 