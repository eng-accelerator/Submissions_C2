# Web Search Update - Now Using Google!

## ✅ Update Complete

The chatbot web search has been upgraded from DuckDuckGo to **Google Custom Search API**.

---

## What Changed?

### Code Updates (Done!)
- ✅ `chatbot.py` - Now uses Google Custom Search API
- ✅ `requirements.txt` - Removed duckduckgo-search
- ✅ `.env.example` - Added Google API key templates
- ✅ `check_env.py` - Added Google key validation

### What You Need (Action Required!)

To enable web search, add to your `.env` file:

```bash
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_search_engine_id_here
```

---

## How to Get API Keys

### Quick Steps:

1. **Get Google API Key** (5 minutes)
   - Go to: https://console.cloud.google.com/
   - Create project → Enable Custom Search API → Create API key

2. **Get Search Engine ID** (5 minutes)
   - Go to: https://programmablesearchengine.google.com/
   - Create search engine → Copy Search Engine ID

3. **Add to .env File** (1 minute)
   ```bash
   GOOGLE_API_KEY=AIzaSyC-your_key_here
   GOOGLE_CSE_ID=your_cse_id_here
   ```

**Detailed Guide:** See `GOOGLE_SEARCH_SETUP.md`

---

## Why Google?

| Feature | DuckDuckGo (Old) | Google (New) |
|---------|------------------|--------------|
| Reliability | ❌ Low | ✅ High |
| Setup | ✅ None | ⚠️ API keys needed |
| Free Tier | ✅ Unlimited | ⚠️ 100/day |
| Quality | ✅ Good | ✅ Excellent |
| Official API | ❌ No | ✅ Yes |

---

## Cost

- **Free:** 100 searches per day
- **Paid:** $5 per 1,000 additional searches

Most users stay in free tier!

---

## Without Google Keys?

The chatbot will still work, but web search will show:
```
⚠️ Google Search not configured
```

You can still use the chatbot for Q&A, just without real-time web data.

---

## Quick Setup

```bash
# 1. See what you need
python check_env.py

# 2. Get API keys (follow GOOGLE_SEARCH_SETUP.md)

# 3. Add to .env file
notepad .env

# 4. Verify
python check_env.py

# 5. Test
python -c "from chatbot import search_web; print(search_web('test'))"
```

---

## Documentation

- **GOOGLE_SEARCH_SETUP.md** - Complete setup guide
- **GOOGLE_MIGRATION.md** - Why we changed
- **ENV_SETUP.md** - .env file configuration

---

**Bottom Line:** Web search now uses Google for better reliability! Add your API keys to enable it. 🚀
