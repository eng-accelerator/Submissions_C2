# Environment Setup Guide (.env file)

## Your Current Error

```
Error connecting to OpenRouter API: Expecting value: line 1 column 1 (char 0)
```

This error means one of two things:
1. The `.env` file doesn't exist
2. The `OPENROUTER_API_KEY` is missing or invalid

---

## Solution: Create .env File

### Step 1: Create the .env File

In the `BrowserTesting` directory, create a file named `.env`:

**Windows (Command Prompt):**
```bash
cd D:\AI\Git_hub\Sample_Project\BrowserTesting
echo OPENROUTER_API_KEY=your_key_here > .env
```

**Windows (PowerShell):**
```bash
cd D:\AI\Git_hub\Sample_Project\BrowserTesting
"OPENROUTER_API_KEY=your_key_here" | Out-File -FilePath .env -Encoding ASCII
```

**Or manually create it:**
1. Open Notepad
2. Type: `OPENROUTER_API_KEY=your_key_here`
3. Save as `.env` (NOT .env.txt) in the BrowserTesting folder
4. Make sure "Save as type" is set to "All Files"

### Step 2: Get Your API Key

1. Go to https://openrouter.ai/
2. Sign up or log in
3. Go to Keys section
4. Create a new API key
5. Copy the key

### Step 3: Add Your Key to .env

Edit the `.env` file and replace `your_key_here` with your actual API key:

```
OPENROUTER_API_KEY=sk-or-v1-1234567890abcdef...
```

**Important:**
- No spaces around the `=` sign
- No quotes around the key
- The key starts with `sk-or-v1-`

### Step 4: Verify

Your `.env` file should look like this:

```
OPENROUTER_API_KEY=sk-or-v1-1234567890abcdefghijklmnopqrstuvwxyz1234567890
GOOGLE_API_KEY=AIzaSyC-your_google_api_key_here
GOOGLE_CSE_ID=your_search_engine_id_here
LLM_MODEL=anthropic/claude-3.5-sonnet
```

---

## Complete .env Template

Copy this template and replace with your actual keys:

```bash
# OpenRouter API Configuration
# Get your API key from: https://openrouter.ai/
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Google Custom Search API Configuration (for web search in chatbot)
# Get API key from: https://console.cloud.google.com/apis/credentials
# Create Custom Search Engine at: https://programmablesearchengine.google.com/
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here

# LLM Model (used by original browser testing features)
LLM_MODEL=anthropic/claude-3.5-sonnet

# Optional: Set specific model defaults
# CHATBOT_DEFAULT_MODEL=openai/gpt-3.5-turbo
```

---

## Testing Your Setup

### Test 1: Check if .env file exists

**Windows:**
```bash
cd D:\AI\Git_hub\Sample_Project\BrowserTesting
dir .env
```

You should see the `.env` file listed.

### Test 2: Check file contents

**Windows:**
```bash
type .env
```

You should see your API key.

### Test 3: Run verification script

```bash
python verify_setup.py
```

Should show: `✅ OPENROUTER_API_KEY is set`

### Test 4: Test chatbot

```bash
python -c "from chatbot import chat_with_llm; print(chat_with_llm('Hello')[0])"
```

Should get a response from the AI (not an error).

---

## Common Issues

### Issue 1: "File not found" when checking .env

**Problem:** The `.env` file wasn't created properly.

**Solution:**
1. Make sure you're in the BrowserTesting directory
2. Create the file again
3. Use Notepad and save as "All Files" type, not "Text Documents"

### Issue 2: "OPENROUTER_API_KEY not set"

**Problem:** The `.env` file exists but the key isn't being read.

**Solutions:**
1. Check for typos: It must be exactly `OPENROUTER_API_KEY`
2. No spaces: Should be `KEY=value` not `KEY = value`
3. No quotes: Should be `KEY=sk-or-v1-...` not `KEY="sk-or-v1-..."`
4. Save the file after editing

### Issue 3: "Invalid API key"

**Problem:** The API key is incorrect or expired.

**Solutions:**
1. Copy the key again from https://openrouter.ai/
2. Make sure you copied the entire key
3. Check that the key starts with `sk-or-v1-`
4. Try generating a new key

### Issue 4: "Expecting value: line 1 column 1"

**Problem:** The API endpoint is receiving an empty response.

**This is now fixed!** The chatbot.py has been updated with:
- Correct API endpoint: `/api/v1/chat/completions`
- Better error handling
- Explicit .env file loading

**Solutions:**
1. Make sure `.env` file exists with valid API key
2. Check internet connection
3. Verify API key is active at https://openrouter.ai/

### Issue 5: "Insufficient credits"

**Problem:** Your OpenRouter account has no credits.

**Solutions:**
1. Go to https://openrouter.ai/
2. Add credits to your account
3. Or use free tier models if available

---

## .env File Location

The `.env` file MUST be in the same directory as the Python files:

```
D:\AI\Git_hub\Sample_Project\BrowserTesting\
├── .env                    ← HERE (same level as main.py)
├── main.py
├── chatbot.py
├── price_comparison.py
└── ...
```

**Not here:**
```
D:\AI\Git_hub\Sample_Project\.env  ← WRONG
```

---

## Security Note

**Important:** The `.env` file contains your API key, which is like a password.

- ✅ Keep it private
- ✅ Don't share it
- ✅ Don't commit it to Git (it's in .gitignore)
- ✅ Don't post it online

If you accidentally expose your key:
1. Go to https://openrouter.ai/
2. Revoke the old key
3. Create a new key
4. Update your `.env` file

---

## Quick Setup Commands

```bash
# Navigate to directory
cd D:\AI\Git_hub\Sample_Project\BrowserTesting

# Create .env file (replace YOUR_ACTUAL_KEY)
echo OPENROUTER_API_KEY=YOUR_ACTUAL_KEY > .env

# Verify it was created
dir .env

# Check contents
type .env

# Test setup
python verify_setup.py

# Run application
streamlit run main.py
```

---

## After Setting Up .env

Once your `.env` file is created with a valid API key:

1. ✅ The chatbot will work
2. ✅ Price comparison will get smart website suggestions
3. ✅ No more "API key not set" warnings
4. ✅ All features fully functional

---

## Need an API Key?

### OpenRouter (Recommended)

**Free tier available** with limited usage.

1. Visit: https://openrouter.ai/
2. Sign up with email or Google
3. Go to "Keys" section
4. Click "Create Key"
5. Copy the key (starts with `sk-or-v1-`)
6. Paste into `.env` file

### Cost Information

- **Free tier:** Usually includes some free credits
- **Paid tier:** Pay only for what you use
- **GPT-3.5 Turbo:** ~$0.001-0.002 per message
- **GPT-4:** ~$0.03-0.06 per message

---

## Summary

**What you need:**
1. Create `.env` file in BrowserTesting directory
2. Add `OPENROUTER_API_KEY=your_actual_key`
3. Get key from https://openrouter.ai/
4. Save the file
5. Run application

**Then:**
- Chatbot will respond to your questions
- Price comparison will work with AI suggestions
- No more JSON parsing errors

---

**Next step:** Create your `.env` file now! 🚀
