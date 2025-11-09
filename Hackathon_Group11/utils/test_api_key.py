"""
Test OpenRouter API Key
Quick utility to verify API key is working
"""

import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def test_openrouter_key():
    """Test if OpenRouter API key is valid."""
    api_key = os.getenv("OPEN_ROUTER_KEY")
    
    print("=" * 60)
    print("Testing OpenRouter API Key")
    print("=" * 60)
    print()
    
    # Check if key exists
    if not api_key:
        print("❌ ERROR: OPEN_ROUTER_KEY not found in environment")
        print()
        print("Please:")
        print("1. Create a .env file in the project root")
        print("2. Add: OPEN_ROUTER_KEY=your_key_here")
        print("3. Get your key from: https://openrouter.ai/keys")
        return False
    
    if api_key == "your_openrouter_key_here":
        print("❌ ERROR: OPEN_ROUTER_KEY is still set to placeholder value")
        print()
        print("Please update your .env file with your actual API key")
        print("Get your key from: https://openrouter.ai/keys")
        return False
    
    # Clean key
    api_key = api_key.strip().strip('"').strip("'")
    
    # Check format
    if not api_key.startswith('sk-or-'):
        print(f"⚠️  WARNING: API key format may be invalid")
        print(f"   Expected to start with 'sk-or-'")
        print(f"   Your key starts with: {api_key[:10]}...")
        print()
    
    print(f"✅ API key found: {api_key[:15]}...")
    print()
    
    # Test API call
    print("Testing API connection...")
    try:
        llm = ChatOpenAI(
            model="openai/gpt-3.5-turbo",  # Use cheaper model for testing
            temperature=0.3,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/yourusername/multi-agent-researcher",
                "X-Title": "Multi-Agent AI Deep Researcher"
            }
        )
        
        # Make a simple test call
        response = llm.invoke("Say 'API key is working' if you can read this.")
        result = response.content if hasattr(response, 'content') else str(response)
        
        print("✅ API key is valid and working!")
        print(f"   Response: {result}")
        print()
        print("You can now use the system with OpenRouter.")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print("❌ API key test failed!")
        print()
        
        if "401" in error_msg or "Unauthorized" in error_msg or "User not found" in error_msg:
            print("ERROR: Authentication failed")
            print()
            print("Possible issues:")
            print("1. API key is invalid or expired")
            print("2. API key has been revoked")
            print("3. API key format is incorrect")
            print()
            print("Please:")
            print("1. Verify your key at: https://openrouter.ai/keys")
            print("2. Check that the key is active")
            print("3. Ensure the key has sufficient credits")
            print("4. Update your .env file with the correct key")
        else:
            print(f"Error: {error_msg}")
            print()
            print("Please check:")
            print("1. Your internet connection")
            print("2. OpenRouter service status")
            print("3. API key is correct")
        
        return False

if __name__ == "__main__":
    success = test_openrouter_key()
    print()
    print("=" * 60)
    sys.exit(0 if success else 1)

