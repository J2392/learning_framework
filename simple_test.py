import requests
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Lấy API key từ .env
api_key = os.getenv("PERPLEXITY_API_KEY")

if "xxxxxxxx" in api_key:
    print("ERROR: Using placeholder API key. Update your .env file with a real API key.")
    exit(1)

# Endpoint API
url = "https://api.perplexity.ai/chat/completions"

# Headers
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Dữ liệu gửi đi
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

# Gửi request và in kết quả
print("Sending request to Perplexity API...")
print(f"API key: {api_key[:8]}...{api_key[-4:]}")
print(f"URL: {url}")

try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("Success! Response:")
        print(response.json()["choices"][0]["message"]["content"])
    else:
        print("Failed. Response:")
        print(response.text)
except Exception as e:
    print(f"Error: {str(e)}")