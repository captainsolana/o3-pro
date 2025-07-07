import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_azure_openai_config():
    """Test Azure OpenAI O3-Pro configuration"""
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
    model = os.getenv("AZURE_OPENAI_MODEL")
    
    print("=== Azure OpenAI O3-Pro Configuration Test ===")
    print(f"Endpoint: {endpoint}")
    print(f"API Key: {'*' * len(api_key[:8]) + api_key[-8:] if api_key else 'Not found'}")
    print(f"API Version: {api_version}")
    print(f"Model: {model}")
    print()
    
    if not endpoint or not api_key or not model:
        print("❌ Missing required configuration!")
        return False
    
    try:
        # Build the correct URL for O3-Pro
        if endpoint and not endpoint.endswith('/'):
            endpoint = endpoint + '/'
        
        api_url = f"{endpoint}openai/responses?api-version={api_version}"
        print(f"Testing URL: {api_url}")
        
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key
        }
        
        payload = {
            "model": model,
            "input": "User: Hello! Can you respond with just 'Test successful'?"
        }
        
        print("Testing connection to Azure OpenAI O3-Pro...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'output' in result and len(result['output']) > 0:
                # Find the message content in O3-Pro response format
                for output_item in result['output']:
                    if output_item.get('type') == 'message' and 'content' in output_item:
                        for content_item in output_item['content']:
                            if content_item.get('type') == 'output_text':
                                print("✅ Configuration test successful!")
                                print(f"Response: {content_item['text']}")
                                return True
                print("❌ No message content found in response")
                return False
            else:
                print("❌ Unexpected response format")
                print(f"Response: {result}")
                return False
        else:
            print(f"❌ Configuration test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_azure_openai_config()
