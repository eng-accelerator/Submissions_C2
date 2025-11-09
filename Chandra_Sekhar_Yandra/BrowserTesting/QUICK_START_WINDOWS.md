# Quick Start Guide - Windows

## The Error You Had

```
File "...\llm_client.py", line 10
    def llm_chat(...) -> str | None:
                         ^
SyntaxError: invalid syntax
```

## ✅ Fixed!

The code now works with Python 3.8+ (previously required 3.10+).

## Installation (5 Steps)

### Step 1: Open Command Prompt/PowerShell

```bash
cd D:\AI\Git_hub\Sample_Project\BrowserTesting
```

### Step 2: Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

This will take a few minutes.

### Step 4: Create `.env` File

Create a file named `.env` in the BrowserTesting folder with:

```
OPENROUTER_API_KEY=your_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here
LLM_MODEL=anthropic/claude-3.5-sonnet
```

**Get OpenRouter API Key:**
- Visit: https://openrouter.ai/
- Sign up → Create API key

**Get Google API Key (for chatbot web search):**
- Go to: https://console.cloud.google.com/
- Create project → Enable Custom Search API → Create API key
- See `GOOGLE_SEARCH_SETUP.md` for detailed steps

**Get Google CSE ID:**
- Go to: https://programmablesearchengine.google.com/
- Create search engine → Copy Search Engine ID
- See `GOOGLE_SEARCH_SETUP.md` for detailed steps

**Note:** Google keys are required for the chatbot's web search feature. Without them, the chatbot will still work but won't have real-time web search.

### Step 5: Run the Application

```bash
streamlit run main.py
```

Open your browser to: http://localhost:8501

## Quick Test

Before running the full app, test that everything works:

```bash
python test_imports.py
```

Should output:
```
✓ All tests passed! Ready to run:
  streamlit run main.py
```

## Example Usage

1. Go to http://localhost:8501
2. Click on an example scenario (e.g., "SauceDemo - Verify Products Page")
3. Click "🚀 Generate & Run"
4. Watch the AI agents:
   - Discover the flow steps
   - Generate a test script
   - Execute it in a browser
   - Show results

## What Each File Does

- **`main.py`** - The Streamlit web interface
- **`requirements.txt`** - Python packages needed
- **`.env`** - Your API key (create this file)
- **`agents/`** - AI agent modules
- **`test_imports.py`** - Verify installation

## Common Issues

### "python is not recognized"

Install Python from https://python.org/ and check "Add to PATH"

### "No module named 'streamlit'"

Run: `pip install -r requirements.txt`

### "OPENROUTER_API_KEY not set"

Create `.env` file with your API key

### Port 8501 already in use

Run with different port: `streamlit run main.py --server.port 8502`

## Need Help?

Read these files:
- `WINDOWS_FIX.md` - Detailed fix information
- `Readme.md` - Full documentation
- `INSTALLATION.md` - Complete installation guide

## Summary

1. ✅ Fixed Python version compatibility (3.8+ now supported)
2. ✅ Simplified requirements.txt
3. ✅ Created test script to verify installation
4. ✅ Added Windows-specific documentation

You're all set! Run `streamlit run main.py` and enjoy! 🚀
