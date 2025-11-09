# Google Custom Search API Setup Guide

## Overview

The chatbot now uses **Google Custom Search API** for web search instead of DuckDuckGo. This provides more reliable and higher-quality search results.

---

## What You Need

To enable web search in the chatbot, you need two things:

1. **Google API Key** - From Google Cloud Console
2. **Custom Search Engine ID (CSE ID)** - From Programmable Search Engine

---

## Step 1: Get Google API Key

### 1.1 Create a Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Sign in with your Google account
3. Click **"Select a project"** dropdown (top left)
4. Click **"New Project"**
5. Name it: `Browser Automation AI`
6. Click **"Create"**

### 1.2 Enable Custom Search API

1. In your project, go to: https://console.cloud.google.com/apis/library
2. Search for: `Custom Search API`
3. Click on **"Custom Search API"**
4. Click **"Enable"**

### 1.3 Create API Key

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **"Create Credentials"** → **"API Key"**
3. Your API key will be created (starts with `AIza...`)
4. **Copy the API key** - you'll need it for the .env file
5. (Optional) Click **"Restrict Key"** to limit to Custom Search API only

---

## Step 2: Create Custom Search Engine

### 2.1 Create Search Engine

1. Go to: https://programmablesearchengine.google.com/
2. Click **"Add"** or **"Get Started"**
3. Enter a name: `AI Chatbot Search`
4. In **"What to search"**: Select **"Search the entire web"**
5. Click **"Create"**

### 2.2 Get Search Engine ID

1. After creation, you'll see your search engine listed
2. Click on the search engine you just created
3. Click **"Setup"** or **"Control Panel"**
4. Look for **"Search engine ID"** (also called CSE ID)
5. It looks like: `a1b2c3d4e5f6g7h8i:ab1cd2ef3gh`
6. **Copy the Search Engine ID**

### 2.3 Configure Search Settings

1. In the Control Panel, go to **"Setup"** tab
2. Under **"Search features"**:
   - Enable: ✅ **Image search** (optional)
   - Enable: ✅ **SafeSearch** (recommended)
3. Click **"Update"**

---

## Step 3: Add to .env File

Create or edit the `.env` file in your BrowserTesting directory:

```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Google Custom Search API Configuration
GOOGLE_API_KEY=AIzaSyC-1234567890abcdefghijklmnopqrstuvwxyz
GOOGLE_CSE_ID=a1b2c3d4e5f6g7h8i:ab1cd2ef3gh

# LLM Model
LLM_MODEL=anthropic/claude-3.5-sonnet
```

**Replace:**
- `GOOGLE_API_KEY` with your actual API key from Step 1.3
- `GOOGLE_CSE_ID` with your actual Search Engine ID from Step 2.2

---

## Step 4: Verify Setup

Run the diagnostic script:

```bash
python check_env.py
```

You should see:
```
✅ GOOGLE_API_KEY is set (39 characters)
✅ GOOGLE_CSE_ID is set: a1b2c3d4e5...
```

---

## Step 5: Test Web Search

### Test from Command Line

```bash
python -c "from chatbot import search_web; results = search_web('Python programming'); print(f'Found {len(results)} results'); print(results[0] if results else 'No results')"
```

Should output search results from Google.

### Test in Application

1. Run: `streamlit run main.py`
2. Go to **💬 AI Chatbot** tab
3. Enable **"🌐 Enable Web Search"**
4. Ask: "What's the latest AI news?"
5. You should see search results in the response

---

## Pricing & Quotas

### Free Tier

Google Custom Search API includes:
- **100 search queries per day** for FREE
- Perfect for testing and personal use

### Paid Tier

If you need more:
- **$5 per 1,000 queries** after free tier
- Max 10,000 queries per day

### Check Your Usage

Monitor your usage at:
https://console.cloud.google.com/apis/dashboard

---

## Troubleshooting

### Error: "Google Search not configured"

**Problem:** API keys not set in .env file

**Solution:**
1. Make sure `.env` file exists
2. Check that both `GOOGLE_API_KEY` and `GOOGLE_CSE_ID` are set
3. No spaces around the `=` sign
4. No quotes around the values

### Error: "Invalid Google API configuration"

**Problem:** API key or CSE ID is incorrect

**Solution:**
1. Verify your API key from: https://console.cloud.google.com/apis/credentials
2. Verify your CSE ID from: https://programmablesearchengine.google.com/
3. Make sure you copied the entire key/ID
4. Try creating a new API key

### Error: "Search quota exceeded"

**Problem:** Used more than 100 searches today

**Solutions:**
1. Wait until tomorrow (quota resets daily)
2. Enable billing in Google Cloud Console to get more quota
3. Or disable web search and use chatbot without search

### Error: "API key not valid"

**Problem:** Custom Search API not enabled

**Solution:**
1. Go to: https://console.cloud.google.com/apis/library
2. Search for "Custom Search API"
3. Make sure it's **Enabled** for your project
4. Wait a few minutes for it to activate

### No Results Found

**Problem:** Search engine might be misconfigured

**Solution:**
1. Go to: https://programmablesearchengine.google.com/
2. Edit your search engine
3. Make sure **"Search the entire web"** is selected
4. Not just specific sites

---

## Security Notes

### API Key Security

**Important:** Your Google API Key is sensitive!

- ✅ Keep it in `.env` file only
- ✅ Don't commit it to Git (it's in .gitignore)
- ✅ Don't share it publicly
- ❌ Don't hardcode it in your code

### If Key is Compromised

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your API key
3. Click **"Delete"** or **"Regenerate"**
4. Create a new API key
5. Update your `.env` file

### Restrict Your API Key

For better security:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your API key
3. Under **"API restrictions"**:
   - Select: **"Restrict key"**
   - Choose: **"Custom Search API"**
4. Click **"Save"**

This prevents the key from being used for other Google APIs.

---

## Benefits Over DuckDuckGo

### Why Google Custom Search?

1. **More Reliable** - Better uptime and stability
2. **Higher Quality** - Google's search algorithm
3. **Better Results** - More relevant search results
4. **Configurable** - Control SafeSearch, filters, etc.
5. **Official API** - Supported by Google
6. **Free Tier** - 100 queries/day for free

### Comparison

| Feature | Google CSE | DuckDuckGo |
|---------|-----------|------------|
| API Quality | Official | Third-party wrapper |
| Free Queries | 100/day | Unlimited (but unstable) |
| Result Quality | Excellent | Good |
| Reliability | High | Medium |
| Setup Required | API key + CSE ID | None |
| Rate Limits | Clear (100/day) | Unclear |

---

## Quick Setup Commands

```bash
# 1. Navigate to project
cd D:\AI\Git_hub\Sample_Project\BrowserTesting

# 2. Edit .env file (add your keys)
notepad .env

# 3. Verify configuration
python check_env.py

# 4. Test search
python -c "from chatbot import search_web; print(search_web('test'))"

# 5. Run application
streamlit run main.py
```

---

## Complete .env File Example

```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-v1-1234567890abcdefghijklmnopqrstuvwxyz1234567890

# Google Custom Search API Configuration
GOOGLE_API_KEY=AIzaSyC-1234567890abcdefghijklmnopqrstuvwxyz
GOOGLE_CSE_ID=a1b2c3d4e5f6g7h8i:ab1cd2ef3gh

# LLM Model
LLM_MODEL=anthropic/claude-3.5-sonnet
```

---

## Need Help?

### Google Cloud Console
- Main: https://console.cloud.google.com/
- API Library: https://console.cloud.google.com/apis/library
- Credentials: https://console.cloud.google.com/apis/credentials
- API Dashboard: https://console.cloud.google.com/apis/dashboard

### Programmable Search Engine
- Main: https://programmablesearchengine.google.com/
- Documentation: https://developers.google.com/custom-search/v1/overview

### Google Custom Search API Docs
- Overview: https://developers.google.com/custom-search/v1/overview
- Reference: https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list

---

## Summary

**What you need:**
1. Google API Key from Google Cloud Console
2. Custom Search Engine ID from Programmable Search Engine
3. Add both to your `.env` file

**Benefits:**
- 100 free searches per day
- Higher quality results
- More reliable than DuckDuckGo
- Official Google API support

**Cost:**
- Free: 100 queries/day
- Paid: $5 per 1,000 additional queries

**Setup time:** 10-15 minutes

---

**Next Step:** Follow Step 1 above to get your Google API Key! 🚀
