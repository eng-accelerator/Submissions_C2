# Migration to Google Custom Search API

## What Changed?

The chatbot web search has been **upgraded from DuckDuckGo to Google Custom Search API**.

---

## Summary of Changes

### Code Changes

**File: `chatbot.py`**
- ✅ Replaced DuckDuckGo search with Google Custom Search API
- ✅ Added `GOOGLE_API_KEY` and `GOOGLE_CSE_ID` environment variables
- ✅ Better error handling with specific messages
- ✅ Support for up to 10 results per query

**File: `requirements.txt`**
- ✅ Removed `duckduckgo-search` dependency (no longer needed)
- ✅ Only uses standard `requests` library now

**File: `.env.example`**
- ✅ Added `GOOGLE_API_KEY` template
- ✅ Added `GOOGLE_CSE_ID` template

**File: `check_env.py`**
- ✅ Added checks for Google API credentials

---

## Why the Change?

### Problems with DuckDuckGo

1. ❌ Unreliable - Often fails or times out
2. ❌ Unofficial API - Uses third-party wrapper
3. ❌ Rate limiting - Unclear limits, blocks frequently
4. ❌ Maintenance - Breaks with website changes

### Benefits of Google Search

1. ✅ **Reliable** - Official Google API with 99.9% uptime
2. ✅ **Better Results** - Google's superior search algorithm
3. ✅ **Clear Limits** - 100 free queries/day, $5 per 1,000 after
4. ✅ **Stable** - Won't break with website changes
5. ✅ **Configurable** - SafeSearch, filters, image search
6. ✅ **Professional** - Enterprise-grade API

---

## What You Need to Do

### If You Already Have the Application

**Option 1: Add Google Search (Recommended)**

1. Follow `GOOGLE_SEARCH_SETUP.md` to get API keys
2. Add to your `.env` file:
   ```
   GOOGLE_API_KEY=your_key_here
   GOOGLE_CSE_ID=your_cse_id_here
   ```
3. Restart the application

**Option 2: Use Without Web Search**

The chatbot will still work! If Google Search is not configured:
- You'll see: "Google Search not configured"
- The chatbot will still answer questions
- Just without real-time web search

---

## Migration Steps

### Step 1: Update Code (Already Done!)

The code has been updated. No action needed.

### Step 2: Remove Old Dependency

If you previously installed `duckduckgo-search`:

```bash
pip uninstall duckduckgo-search
```

Or simply reinstall from requirements.txt:

```bash
pip install -r requirements.txt
```

### Step 3: Get Google API Credentials

See **GOOGLE_SEARCH_SETUP.md** for detailed instructions.

Quick summary:
1. Go to: https://console.cloud.google.com/
2. Create project → Enable Custom Search API → Create API key
3. Go to: https://programmablesearchengine.google.com/
4. Create search engine → Get Search Engine ID

### Step 4: Update .env File

Add these lines to your `.env`:

```bash
GOOGLE_API_KEY=AIzaSyC-your_actual_key_here
GOOGLE_CSE_ID=your_actual_cse_id_here
```

### Step 5: Verify Setup

```bash
python check_env.py
```

Should show:
```
✅ GOOGLE_API_KEY is set
✅ GOOGLE_CSE_ID is set
```

### Step 6: Test Search

```bash
python -c "from chatbot import search_web; print(search_web('Python'))"
```

Should show Google search results.

---

## Comparison

| Feature | DuckDuckGo (Old) | Google CSE (New) |
|---------|------------------|------------------|
| Setup Required | None | API Key + CSE ID |
| Free Tier | "Unlimited" | 100/day |
| Reliability | Low | High |
| Result Quality | Good | Excellent |
| API Type | Unofficial wrapper | Official Google API |
| Rate Limits | Unclear | Clear (100/day) |
| Breaks Often | Yes | No |
| Configuration | None | SafeSearch, filters, etc. |
| Cost After Free | N/A | $5 per 1,000 queries |

---

## Backward Compatibility

### Will Old Code Break?

**No!** The function signature is identical:

```python
# This still works exactly the same
results = search_web("query", num_results=5)
```

### What If I Don't Configure Google?

The chatbot will still work, but web search will show:

```
⚠️ Google Search not configured
Please add GOOGLE_API_KEY and GOOGLE_CSE_ID to your .env file
```

---

## Cost Analysis

### Free Tier (100 queries/day)

**For typical usage:**
- 10 searches per day = **Free**
- 50 searches per day = **Free**
- 100 searches per day = **Free**

Perfect for:
- Personal use
- Testing
- Small projects
- Learning

### Paid Tier ($5 per 1,000 queries)

**Example costs:**
- 200 queries/day (100 over limit) = $0.50/day = $15/month
- 500 queries/day (400 over limit) = $2/day = $60/month
- 1,000 queries/day (900 over limit) = $4.50/day = $135/month

**Most users will stay in free tier!**

---

## Troubleshooting Migration

### Error: "Google Search not configured"

**Solution:** Add `GOOGLE_API_KEY` and `GOOGLE_CSE_ID` to .env file.

### Error: "duckduckgo_search module not found"

**Solution:** This is fine! We don't use it anymore. Remove with:
```bash
pip uninstall duckduckgo-search
```

### Error: "Invalid Google API configuration"

**Solution:**
1. Check your API key at: https://console.cloud.google.com/apis/credentials
2. Make sure Custom Search API is enabled
3. Verify CSE ID at: https://programmablesearchengine.google.com/

### Search Still Not Working

**Check:**
1. Run `python check_env.py` - are keys set?
2. Check `.env` file - no spaces around `=`?
3. Custom Search API enabled in Google Cloud?
4. CSE configured to search entire web?

---

## Documentation

**Setup Guide:**
- `GOOGLE_SEARCH_SETUP.md` - Complete setup instructions

**Configuration:**
- `.env.example` - Template with Google keys
- `ENV_SETUP.md` - Updated with Google configuration

**Verification:**
- `check_env.py` - Now checks Google keys

---

## Quick Reference

### Old Way (DuckDuckGo)

```bash
# No setup needed
pip install duckduckgo-search

# Just worked (sometimes)
results = search_web("query")
```

### New Way (Google)

```bash
# One-time setup (15 minutes)
1. Get Google API key
2. Get Google CSE ID
3. Add to .env file

# Works reliably
results = search_web("query")
```

---

## FAQ

### Q: Do I have to use Google Search?

**A:** No! The chatbot works without web search. You just won't get real-time information.

### Q: Can I keep using DuckDuckGo?

**A:** No, the code has been replaced. But Google is more reliable!

### Q: Is Google Search free?

**A:** First 100 queries per day are free. $5 per 1,000 after that.

### Q: What if I exceed 100 queries?

**A:** You'll get an error. Either wait until tomorrow or enable billing in Google Cloud.

### Q: Is it hard to set up?

**A:** Takes about 10-15 minutes. Follow `GOOGLE_SEARCH_SETUP.md`.

### Q: Can I use my existing Google account?

**A:** Yes! No need to create a new account.

### Q: Will my search history be tracked?

**A:** Google logs API usage for billing, but it's your own API key, not shared.

---

## Summary

✅ **Migration complete** - Code updated to Google Custom Search API

⚠️ **Action required** - Add Google API keys to .env file

📚 **Guide available** - See GOOGLE_SEARCH_SETUP.md

🎉 **Benefits** - More reliable, better results, professional API

💰 **Cost** - 100 free searches/day, $5 per 1,000 after

⏱️ **Setup time** - 10-15 minutes

---

**Next Step:** Follow `GOOGLE_SEARCH_SETUP.md` to get your API keys! 🚀
