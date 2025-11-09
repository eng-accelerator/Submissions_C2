# Windows Installation - Step by Step

## Current Issue

You're seeing: `ModuleNotFoundError: No module named 'dotenv'`

This means dependencies need to be installed.

---

## Solution (3 Simple Steps)

### Step 1: Install Dependencies

Open Command Prompt or PowerShell in the BrowserTesting directory:

```bash
cd D:\AI\Git_hub\Sample_Project\BrowserTesting
pip install -r requirements.txt
```

**Wait 2-5 minutes** for all packages to download and install.

### Step 2: Install Playwright Browser

```bash
playwright install chromium
```

**Wait 1-2 minutes** for the browser to download.

### Step 3: Verify Installation

```bash
python verify_setup.py
```

You should see: `✅ All checks passed!`

---

## What Gets Installed

When you run `pip install -r requirements.txt`, these packages are installed:

- **streamlit** - Web interface framework
- **playwright** - Browser automation
- **python-dotenv** - Reads .env file (this is what's missing!)
- **requests** - HTTP requests
- **pandas** - Data processing
- **numpy** - Numerical operations
- **duckduckgo-search** - Web search for chatbot
- And their dependencies

---

## After Installation

### Configure API Key

Create a file named `.env` in the BrowserTesting directory:

```
OPENROUTER_API_KEY=your_key_here
```

Get your key from: https://openrouter.ai/

### Run the Application

```bash
streamlit run main.py
```

Open: http://localhost:8501

---

## If Installation Fails

### Problem: "pip is not recognized"

**Solution**: Python is not in PATH. Reinstall Python and check "Add to PATH".

### Problem: "Permission denied"

**Solution**: Run Command Prompt as Administrator.

### Problem: Timeout errors

**Solution**: Increase timeout:
```bash
pip install --timeout=120 -r requirements.txt
```

### Problem: Specific package fails

**Solution**: Install manually:
```bash
pip install python-dotenv
pip install streamlit
pip install playwright
pip install requests
pip install duckduckgo-search
```

---

## Virtual Environment (Recommended)

To avoid conflicts with other Python projects:

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install browser
playwright install chromium

# Run application
streamlit run main.py
```

---

## Verification Checklist

After running `pip install -r requirements.txt`:

- [ ] No error messages
- [ ] Sees "Successfully installed..." messages
- [ ] `python verify_setup.py` runs without errors
- [ ] Shows "✅ All checks passed!"

---

## Expected Output

### During Installation:
```
Collecting streamlit>=1.28.0
  Downloading streamlit-1.xx.x-py2.py3-none-any.whl
Collecting playwright>=1.40.0
  Downloading playwright-1.xx.x-py3-none-win_amd64.whl
Collecting python-dotenv>=1.0.0
  Downloading python_dotenv-1.x.x-py3-none-any.whl
...
Successfully installed streamlit-x.x.x playwright-x.x.x python-dotenv-x.x.x ...
```

### After Verification:
```
======================================================================
Browser Automation AI Agent - Complete Verification
======================================================================

1. Python Version Check
   ✅ Compatible (requires Python 3.8+)

2. File Structure Check
   ✅ main.py
   ✅ chatbot.py
   ✅ price_comparison.py

3. Python Syntax Check
   ✅ chatbot.py syntax OK
   ✅ main.py syntax OK

4. Core Dependencies Check
   ✅ streamlit       - Streamlit web framework
   ✅ playwright      - Browser automation
   ✅ requests        - HTTP library
   ✅ dotenv          - Environment variables

======================================================================
✅ All checks passed!
======================================================================
```

---

## Next Steps

1. ✅ Run: `pip install -r requirements.txt`
2. ✅ Run: `playwright install chromium`
3. ✅ Run: `python verify_setup.py`
4. ✅ Create `.env` file with API key
5. ✅ Run: `streamlit run main.py`
6. ✅ Open: http://localhost:8501

---

## Quick Commands

```bash
# Full installation sequence
cd D:\AI\Git_hub\Sample_Project\BrowserTesting
pip install -r requirements.txt
playwright install chromium
python verify_setup.py
streamlit run main.py
```

---

**Do this now**: Run `pip install -r requirements.txt` 🚀
