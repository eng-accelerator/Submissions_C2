#!/usr/bin/env python3
"""
Complete verification script for new features
Tests Python compatibility, imports, and basic functionality
"""

import sys
import os
import platform

print("=" * 70)
print("Browser Automation AI Agent - Complete Verification")
print("=" * 70)

# Step 1: Python version check
print("\n1. Python Version Check")
print("-" * 70)
py_version = sys.version_info
print(f"   Python {py_version.major}.{py_version.minor}.{py_version.micro}")
print(f"   Path: {sys.executable}")

if py_version.major >= 3 and py_version.minor >= 8:
    print(f"   ✅ Compatible (requires Python 3.8+)")
else:
    print(f"   ❌ Incompatible (requires Python 3.8+)")
    print(f"   Please upgrade Python from https://python.org/")
    sys.exit(1)

# Step 2: File structure check
print("\n2. File Structure Check")
print("-" * 70)
required_files = [
    "main.py",
    "chatbot.py",
    "price_comparison.py",
    "feature_chatbot_ui.py",
    "feature_price_comparison_ui.py",
    "requirements.txt"
]

for filename in required_files:
    if os.path.exists(filename):
        print(f"   ✅ {filename}")
    else:
        print(f"   ❌ {filename} - MISSING!")

# Step 3: Syntax check
print("\n3. Python Syntax Check")
print("-" * 70)
import py_compile

syntax_files = [
    "chatbot.py",
    "price_comparison.py",
    "feature_chatbot_ui.py",
    "feature_price_comparison_ui.py",
    "main.py"
]

syntax_ok = True
for filename in syntax_files:
    if os.path.exists(filename):
        try:
            py_compile.compile(filename, doraise=True)
            print(f"   ✅ {filename} syntax OK")
        except py_compile.PyCompileError as e:
            print(f"   ❌ {filename} syntax error:")
            print(f"      {e}")
            syntax_ok = False
    else:
        print(f"   ⚠️  {filename} not found")

if not syntax_ok:
    print("\n❌ Syntax errors found! Please fix before continuing.")
    sys.exit(1)

# Step 4: Core dependencies check
print("\n4. Core Dependencies Check")
print("-" * 70)

dependencies = {
    "streamlit": "Streamlit web framework",
    "playwright": "Browser automation",
    "requests": "HTTP library",
    "dotenv": "Environment variables",
}

missing_deps = []
for module_name, description in dependencies.items():
    try:
        if module_name == "dotenv":
            import importlib
            importlib.import_module("dotenv")
        else:
            __import__(module_name)
        print(f"   ✅ {module_name:15} - {description}")
    except ImportError:
        print(f"   ❌ {module_name:15} - MISSING!")
        missing_deps.append(module_name)

if missing_deps:
    print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
    print(f"   Install with: pip install -r requirements.txt")
else:
    print(f"\n   All core dependencies installed!")

# Step 5: New feature imports
print("\n5. New Feature Imports")
print("-" * 70)

try:
    from chatbot import chat_with_llm, get_available_models
    print("   ✅ chatbot module")
except SyntaxError as e:
    print(f"   ❌ chatbot syntax error: {e}")
    print(f"      Check PYTHON_COMPATIBILITY_FIXES.md")
    sys.exit(1)
except ImportError as e:
    print(f"   ⚠️  chatbot import error: {e}")
    print(f"      Install missing dependencies")

try:
    from price_comparison import compare_prices
    print("   ✅ price_comparison module")
except SyntaxError as e:
    print(f"   ❌ price_comparison syntax error: {e}")
    sys.exit(1)
except ImportError as e:
    print(f"   ⚠️  price_comparison import error: {e}")

try:
    from feature_chatbot_ui import render_chatbot_tab
    print("   ✅ feature_chatbot_ui module")
except ImportError as e:
    print(f"   ⚠️  feature_chatbot_ui import error: {e}")

try:
    from feature_price_comparison_ui import render_price_comparison_tab
    print("   ✅ feature_price_comparison_ui module")
except ImportError as e:
    print(f"   ⚠️  feature_price_comparison_ui import error: {e}")

# Step 6: Optional dependencies
print("\n6. Optional Dependencies")
print("-" * 70)

try:
    from duckduckgo_search import DDGS
    print("   ✅ duckduckgo-search (web search for chatbot)")
except ImportError:
    print("   ⚠️  duckduckgo-search not installed")
    print("      Install with: pip install duckduckgo-search")
    print("      Chatbot will work but without web search")

# Step 7: Environment check
print("\n7. Environment Configuration")
print("-" * 70)

if os.path.exists(".env"):
    print("   ✅ .env file exists")
    try:
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv('OPENROUTER_API_KEY')
        if api_key:
            print(f"   ✅ OPENROUTER_API_KEY is set ({len(api_key)} characters)")
        else:
            print("   ⚠️  OPENROUTER_API_KEY not set in .env")
            print("      Get your key from: https://openrouter.ai/")
            print("      Add to .env: OPENROUTER_API_KEY=your_key_here")
    except ImportError:
        print("   ⚠️  python-dotenv not installed")
        print("      Install with: pip install python-dotenv")
        print("      Or install all: pip install -r requirements.txt")
else:
    print("   ⚠️  .env file not found")
    print("      Create .env with: OPENROUTER_API_KEY=your_key_here")

# Step 8: Basic functionality test
print("\n8. Basic Functionality Test")
print("-" * 70)

try:
    # Test model list
    models = get_available_models()
    print(f"   ✅ Available AI models: {len(models)}")
    for name in models.keys():
        print(f"      - {name}")
except NameError:
    print(f"   ⚠️  Chatbot not imported (dependencies missing)")
    print(f"      Install dependencies first: pip install -r requirements.txt")
except Exception as e:
    print(f"   ⚠️  Model list error: {e}")

# Final summary
print("\n" + "=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)

if syntax_ok and not missing_deps:
    print("✅ All checks passed!")
    print("\nYou can now run the application:")
    print("  streamlit run main.py")
    print("\nThen open: http://localhost:8501")
    print("\nFeatures available:")
    print("  - 🤖 Browser Testing (original)")
    print("  - 💬 AI Chatbot (new)")
    print("  - 💰 Price Comparison (new)")
else:
    print("⚠️  Some issues found")
    if missing_deps:
        print(f"\nInstall missing dependencies:")
        print(f"  pip install -r requirements.txt")
    print("\nAfter fixing issues, run this script again.")

print("\n" + "=" * 70)
