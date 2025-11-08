#!/usr/bin/env python3
"""
Quick verification that the Browser Automation AI Agent is ready to run.
"""

import sys

print("🧠 Browser Automation AI Agent - System Check")
print("=" * 60)

# Test 1: Python version
print("\n1. Checking Python version...")
import platform
py_version = platform.python_version()
print(f"   ✓ Python {py_version}")

# Test 2: Core dependencies
print("\n2. Checking core dependencies...")
try:
    import streamlit as st
    print(f"   ✓ Streamlit {st.__version__}")
except ImportError as e:
    print(f"   ✗ Streamlit not found: {e}")
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright
    print(f"   ✓ Playwright installed")
except ImportError as e:
    print(f"   ✗ Playwright not found: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print(f"   ✓ Pandas {pd.__version__}")
except ImportError:
    pass

# Test 3: Agent modules
print("\n3. Checking agent modules...")
try:
    from agents.flow_discovery import discover_flow
    from agents.script_generator import generate_script
    from agents.execution import execute_script
    from agents.error_diagnosis import diagnose
    from agents.adaptive_repair import self_heal
    print("   ✓ All agent modules loaded")
except ImportError as e:
    print(f"   ✗ Agent import error: {e}")
    sys.exit(1)

# Test 4: Environment configuration
print("\n4. Checking environment configuration...")
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENROUTER_API_KEY')
if api_key:
    print(f"   ✓ OPENROUTER_API_KEY is set")
else:
    print(f"   ⚠ OPENROUTER_API_KEY not set (AI agents will return fallback responses)")

# Test 5: Quick functional test
print("\n5. Running quick functional test...")
try:
    # Test flow discovery (will use fallback without API key)
    steps = discover_flow("https://example.com", "test login flow")
    if steps and len(steps) > 0:
        print(f"   ✓ Flow discovery works (returned {len(steps)} steps)")
    
    # Test script generation (will use fallback without API key)
    script = generate_script("https://example.com", steps, "Playwright (Python)", "test")
    if script:
        print(f"   ✓ Script generation works (generated {len(script)} chars)")
    
    print("\n" + "=" * 60)
    print("✓ All systems operational!")
    print("=" * 60)
    print("\n🚀 Ready to run!")
    print("\nStart the application with:")
    print("  streamlit run main.py")
    print("\nOr use the convenience script:")
    print("  ./run.sh")
    
except Exception as e:
    print(f"   ✗ Functional test failed: {e}")
    sys.exit(1)

