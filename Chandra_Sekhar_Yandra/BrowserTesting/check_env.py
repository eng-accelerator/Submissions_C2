#!/usr/bin/env python3
"""
Quick diagnostic script to check .env file setup
"""

import os
from pathlib import Path

print("=" * 70)
print("Environment Configuration Checker")
print("=" * 70)

# Check 1: Current directory
print("\n1. Current Directory")
print("-" * 70)
current_dir = Path.cwd()
print(f"   Working directory: {current_dir}")

# Check 2: .env file exists
print("\n2. .env File Check")
print("-" * 70)
env_file = Path("BrowserTesting") / ".env" if "BrowserTesting" not in str(current_dir) else Path(".env")
if not env_file.exists():
    env_file = Path(".env")

if env_file.exists():
    print(f"   ✅ .env file found at: {env_file.absolute()}")

    # Read file size
    file_size = env_file.stat().st_size
    print(f"   File size: {file_size} bytes")

    if file_size == 0:
        print("   ⚠️  WARNING: .env file is empty!")
    else:
        print("   ✅ .env file has content")
else:
    print(f"   ❌ .env file NOT found")
    print(f"   Expected location: {env_file.absolute()}")
    print("\n   Create it with:")
    print("   echo OPENROUTER_API_KEY=your_key_here > .env")

# Check 3: Load dotenv
print("\n3. Python-dotenv Module")
print("-" * 70)
try:
    from dotenv import load_dotenv
    print("   ✅ python-dotenv is installed")

    # Try to load
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
        print("   ✅ .env file loaded")
    else:
        load_dotenv()
        print("   ⚠️  Attempted to load .env (file not found)")

except ImportError:
    print("   ❌ python-dotenv is NOT installed")
    print("   Install with: pip install python-dotenv")
    exit(1)

# Check 4: Environment variables
print("\n4. Environment Variables")
print("-" * 70)

api_key = os.getenv("OPENROUTER_API_KEY")
if api_key:
    # Mask most of the key for security
    if len(api_key) > 20:
        masked_key = api_key[:10] + "..." + api_key[-10:]
    else:
        masked_key = api_key[:5] + "..." if len(api_key) > 5 else "***"

    print(f"   ✅ OPENROUTER_API_KEY is set")
    print(f"   Value: {masked_key}")
    print(f"   Length: {len(api_key)} characters")

    # Check if it looks valid
    if api_key.startswith("sk-or-v1-"):
        print("   ✅ Key format looks correct (starts with sk-or-v1-)")
    elif api_key == "your_key_here" or api_key == "your_openrouter_api_key_here":
        print("   ⚠️  WARNING: Still using placeholder value!")
        print("   Replace with your actual API key from https://openrouter.ai/")
    else:
        print("   ⚠️  Key format unusual (should start with sk-or-v1-)")
else:
    print("   ❌ OPENROUTER_API_KEY is NOT set")
    print("\n   Solutions:")
    print("   1. Create .env file with: OPENROUTER_API_KEY=your_key_here")
    print("   2. Get your key from: https://openrouter.ai/")
    print("   3. Make sure .env file is in the same directory as this script")

llm_model = os.getenv("LLM_MODEL")
if llm_model:
    print(f"   ✅ LLM_MODEL is set: {llm_model}")
else:
    print(f"   ⚠️  LLM_MODEL not set (optional)")

google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    if len(google_api_key) > 20:
        masked = google_api_key[:10] + "..." + google_api_key[-5:]
    else:
        masked = google_api_key[:5] + "..." if len(google_api_key) > 5 else "***"
    print(f"   ✅ GOOGLE_API_KEY is set ({len(google_api_key)} characters)")
    print(f"   Value: {masked}")
else:
    print(f"   ⚠️  GOOGLE_API_KEY not set (required for web search)")
    print(f"      Get from: https://console.cloud.google.com/apis/credentials")

google_cse_id = os.getenv("GOOGLE_CSE_ID")
if google_cse_id:
    print(f"   ✅ GOOGLE_CSE_ID is set: {google_cse_id[:10]}...{google_cse_id[-5:] if len(google_cse_id) > 15 else ''}")
else:
    print(f"   ⚠️  GOOGLE_CSE_ID not set (required for web search)")
    print(f"      Create at: https://programmablesearchengine.google.com/")

# Check 5: .env file contents (if exists)
print("\n5. .env File Contents")
print("-" * 70)
if env_file.exists():
    try:
        with open(env_file, 'r') as f:
            lines = f.readlines()

        print(f"   File has {len(lines)} line(s)")

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Mask the value
            if '=' in line:
                key, value = line.split('=', 1)
                if 'KEY' in key.upper():
                    if len(value) > 20:
                        masked = value[:10] + "..." + value[-10:]
                    else:
                        masked = value[:5] + "..." if len(value) > 5 else "***"
                    print(f"   Line {i}: {key}={masked}")
                else:
                    print(f"   Line {i}: {line}")
            else:
                print(f"   Line {i}: {line}")

    except Exception as e:
        print(f"   ⚠️  Error reading file: {e}")
else:
    print("   ❌ .env file doesn't exist - cannot display contents")

# Check 6: Test API connection (if key is set)
print("\n6. API Connection Test")
print("-" * 70)
if api_key and api_key not in ["your_key_here", "your_openrouter_api_key_here"]:
    print("   Testing connection to OpenRouter API...")
    try:
        import requests

        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )

        if response.status_code == 200:
            print("   ✅ API connection successful!")
            print("   ✅ API key is valid")
        elif response.status_code == 401:
            print("   ❌ API key is invalid or expired")
            print("   Get a new key from: https://openrouter.ai/")
        elif response.status_code == 402:
            print("   ⚠️  API key valid but insufficient credits")
            print("   Add credits at: https://openrouter.ai/")
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")

    except ImportError:
        print("   ⚠️  'requests' module not installed")
        print("   Install with: pip install requests")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
else:
    print("   ⚠️  Skipped (no valid API key set)")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

issues = []

if not env_file.exists():
    issues.append("Create .env file")
if not api_key:
    issues.append("Set OPENROUTER_API_KEY in .env")
elif api_key in ["your_key_here", "your_openrouter_api_key_here"]:
    issues.append("Replace placeholder API key with real key")

if issues:
    print("❌ Issues found:")
    for issue in issues:
        print(f"   - {issue}")
    print("\n📚 See ENV_SETUP.md for detailed instructions")
else:
    print("✅ Environment is configured correctly!")
    print("🚀 Ready to run: streamlit run main.py")

print("=" * 70)
