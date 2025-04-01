"""
Test different Perplexity API models to find supported ones
"""
import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def test_model(model_name):
    """Test if a specific model is supported by Perplexity API"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("❌ ERROR: No API key found in .env file")
        return False
    
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model_name,
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
    
    print(f"\n🧪 Testing model: {model_name}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"🔄 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ SUCCESS! Model '{model_name}' is supported.")
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"💬 Response: {message[:100]}...")
            return True
        else:
            print(f"❌ ERROR: Model '{model_name}' is not supported.")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    # List of models to test
    models_to_test = [
        "sonar-pro",
        "sonar",
        "sonar-deep-research",
        "sonar-reasoning-pro",
        "sonar-reasoning",
        "r1-1776"
    ]
    
    supported_models = []
    
    for model in models_to_test:
        if test_model(model):
            supported_models.append(model)
    
    print("\n=== Summary ===")
    print(f"Total models tested: {len(models_to_test)}")
    print(f"Supported models: {len(supported_models)}")
    
    if supported_models:
        print("\nSupported models:")
        for model in supported_models:
            print(f"- {model}")
        
        # Suggest the first working model
        recommend = supported_models[0]
        print(f"\n👉 Recommended model to use: {recommend}")
        print(f"Update your .env file with: PERPLEXITY_MODEL={recommend}")
    else:
        print("\n❌ No supported models found. Check if your API key is valid and you have credits.") 