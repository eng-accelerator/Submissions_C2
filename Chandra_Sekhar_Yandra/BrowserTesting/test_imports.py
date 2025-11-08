#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
Run this before starting the application to check for compatibility issues.
"""

import sys
import platform

print("=" * 60)
print("Browser Automation AI Agent - Import Test")
print("=" * 60)
print(f"\nPython Version: {platform.python_version()}")
print(f"Python Path: {sys.executable}")
print()

# Test 1: Check Python version
py_version = sys.version_info
print(f"1. Checking Python version...")
if py_version.major >= 3 and py_version.minor >= 8:
    print(f"   ✓ Python {py_version.major}.{py_version.minor}.{py_version.micro} (compatible)")
else:
    print(f"   ✗ Python {py_version.major}.{py_version.minor} (requires 3.8+)")
    sys.exit(1)

# Test 2: Import core dependencies
print("\n2. Testing core dependencies...")
try:
    import streamlit
    print(f"   ✓ streamlit {streamlit.__version__}")
except ImportError as e:
    print(f"   ✗ streamlit import failed: {e}")
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright
    print(f"   ✓ playwright")
except ImportError as e:
    print(f"   ✗ playwright import failed: {e}")
    sys.exit(1)

try:
    import requests
    print(f"   ✓ requests")
except ImportError as e:
    print(f"   ✗ requests import failed: {e}")
    sys.exit(1)

# Test 3: Import agent modules
print("\n3. Testing agent modules...")
try:
    from agents.llm.llm_client import llm_chat
    print(f"   ✓ llm_client (fixed type hints)")
except ImportError as e:
    print(f"   ✗ llm_client import failed: {e}")
    sys.exit(1)
except SyntaxError as e:
    print(f"   ✗ llm_client syntax error: {e}")
    print(f"   This usually means Python version incompatibility")
    sys.exit(1)

try:
    from agents.flow_discovery import discover_flow
    from agents.script_generator import generate_script
    from agents.execution import execute_script
    from agents.error_diagnosis import diagnose
    from agents.adaptive_repair import self_heal
    print(f"   ✓ All agent modules loaded")
except ImportError as e:
    print(f"   ✗ Agent import failed: {e}")
    sys.exit(1)

# Test 4: Quick functional test
print("\n4. Testing basic functionality...")
try:
    # Test with fallback (no API key needed)
    steps = discover_flow("https://example.com", "test")
    if steps:
        print(f"   ✓ Flow discovery works")
    else:
        print(f"   ⚠ Flow discovery returned None (expected without API key)")
except Exception as e:
    print(f"   ✗ Flow discovery error: {e}")
    sys.exit(1)

# Test 5: Check environment
print("\n5. Checking environment...")
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENROUTER_API_KEY')
if api_key:
    print(f"   ✓ OPENROUTER_API_KEY is set")
else:
    print(f"   ⚠ OPENROUTER_API_KEY not set (AI features disabled)")

print("\n" + "=" * 60)
print("✓ All tests passed! Ready to run:")
print("  streamlit run main.py")
print("=" * 60)
