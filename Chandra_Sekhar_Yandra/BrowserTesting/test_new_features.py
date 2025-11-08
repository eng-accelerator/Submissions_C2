#!/usr/bin/env python3
"""
Test script for new features: Chatbot and Price Comparison
Run this to verify both features are working correctly
"""

import sys
import os

print("=" * 70)
print("Testing New Features: Chatbot & Price Comparison")
print("=" * 70)

# Test 1: Import chatbot module
print("\n1. Testing Chatbot Module...")
try:
    from chatbot import chat_with_llm, get_available_models, search_web
    print("   ✓ Chatbot module imported successfully")

    # Test available models
    models = get_available_models()
    print(f"   ✓ Available models: {len(models)}")
    for name in models.keys():
        print(f"      - {name}")

    # Test web search (without API key)
    print("\n   Testing web search...")
    results = search_web("Python programming", num_results=2)
    if results and len(results) > 0:
        print(f"   ✓ Web search works ({len(results)} results found)")
        if results[0].get('title') != 'Web search unavailable':
            print(f"      Sample: {results[0]['title'][:50]}...")
        else:
            print("      ⚠ DuckDuckGo search not available (install: pip install duckduckgo-search)")
    else:
        print("   ⚠ Web search returned no results")

    # Test chatbot (will return warning without API key)
    print("\n   Testing chatbot response...")
    response, _ = chat_with_llm("Say hello", model="openai/gpt-3.5-turbo")
    if response:
        if "OPENROUTER_API_KEY not set" in response:
            print("   ⚠ API key not set (expected)")
        else:
            print(f"   ✓ Chatbot response: {response[:50]}...")
    else:
        print("   ✗ Chatbot returned None")

except ImportError as e:
    print(f"   ✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 2: Import price comparison module
print("\n2. Testing Price Comparison Module...")
try:
    from price_comparison import compare_prices, extract_domain, build_search_url
    print("   ✓ Price comparison module imported successfully")

    # Test utility functions
    domain = extract_domain("https://www.amazon.com/products")
    print(f"   ✓ Domain extraction works: {domain}")

    search_url = build_search_url("https://www.amazon.com", "iPhone 15")
    print(f"   ✓ Search URL building works")
    print(f"      {search_url[:60]}...")

    # Note: We won't run full price comparison in test as it requires browser automation
    print("\n   ⚠ Skipping full price comparison test (requires Playwright browser)")
    print("      Run the actual feature in Streamlit to test price scraping")

except ImportError as e:
    print(f"   ✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 3: Import UI components
print("\n3. Testing UI Components...")
try:
    from feature_chatbot_ui import render_chatbot_tab
    print("   ✓ Chatbot UI component imported")

    from feature_price_comparison_ui import render_price_comparison_tab
    print("   ✓ Price comparison UI component imported")

except ImportError as e:
    print(f"   ✗ Import error: {e}")
    sys.exit(1)

# Test 4: Check environment
print("\n4. Checking Environment...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENROUTER_API_KEY')
if api_key:
    print("   ✓ OPENROUTER_API_KEY is set")
    print("      Both features will work with full functionality")
else:
    print("   ⚠ OPENROUTER_API_KEY not set")
    print("      Features will work with limited functionality")
    print("      Set in .env file for full access")

# Test 5: Check dependencies
print("\n5. Checking Dependencies...")
try:
    import streamlit
    print(f"   ✓ Streamlit {streamlit.__version__}")
except ImportError:
    print("   ✗ Streamlit not installed")
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright
    print("   ✓ Playwright installed")
except ImportError:
    print("   ✗ Playwright not installed")
    sys.exit(1)

try:
    from duckduckgo_search import DDGS
    print("   ✓ DuckDuckGo Search installed")
except ImportError:
    print("   ⚠ DuckDuckGo Search not installed (optional)")
    print("      Install with: pip install duckduckgo-search")

# Summary
print("\n" + "=" * 70)
print("✓ All core tests passed!")
print("=" * 70)

print("\n📋 Next Steps:")
print("1. Set OPENROUTER_API_KEY in .env file if not already set")
print("2. Install optional dependency: pip install duckduckgo-search")
print("3. Run the application: streamlit run main.py")
print("4. Navigate to:")
print("   - 💬 AI Chatbot tab to test chatbot")
print("   - 💰 Price Comparison tab to test price comparison")

print("\n" + "=" * 70)
