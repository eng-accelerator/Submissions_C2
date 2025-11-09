# Setup Guide for New Features

## Quick Start (5 Minutes)

### Step 1: Navigate to Project
```bash
cd D:\AI\Git_hub\Sample_Project\BrowserTesting
```

### Step 2: Install New Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `duckduckgo-search` - For web search in chatbot
- All other existing dependencies

### Step 3: Verify Installation
```bash
python test_new_features.py
```

You should see:
```
✓ All core tests passed!
```

### Step 4: Configure API Key (if not done)
Create `.env` file with:
```
OPENROUTER_API_KEY=your_actual_key_here
LLM_MODEL=anthropic/claude-3.5-sonnet
```

Get your key from: https://openrouter.ai/

### Step 5: Run Application
```bash
streamlit run main.py
```

Open http://localhost:8501 in your browser.

---

## Detailed Setup

### Prerequisites

- Python 3.8 or higher ✓ (you already have this)
- pip installed ✓
- Existing browser automation project ✓

### New Files Added

```
BrowserTesting/
├── chatbot.py                       # NEW
├── feature_chatbot_ui.py           # NEW
├── price_comparison.py              # NEW
├── feature_price_comparison_ui.py   # NEW
├── test_new_features.py            # NEW
├── NEW_FEATURES.md                  # NEW
├── FEATURES_SUMMARY.md              # NEW
├── SETUP_NEW_FEATURES.md            # NEW (this file)
├── main.py                          # MODIFIED (tabs added)
└── requirements.txt                 # MODIFIED (dependency added)
```

### Modified Files

#### `main.py`
- Added tab navigation at top
- Wrapped original content in Tab 1
- Added Tab 2 for Chatbot
- Added Tab 3 for Price Comparison
- Added session state for chat history

#### `requirements.txt`
- Added `duckduckgo-search>=4.0.0`
- Other dependencies unchanged

---

## Feature 1: AI Chatbot 💬

### What You Get
- Chat with 3 different OpenAI models
- Web search for real-time information
- Conversation history
- Source citations with links

### Setup Steps

1. **Already done** - chatbot.py and feature_chatbot_ui.py are created
2. **API Key** - Add OPENROUTER_API_KEY to .env
3. **Web Search** - Install duckduckgo-search (done via requirements.txt)

### Test It
```python
from chatbot import chat_with_llm

# Test basic chat
response, _ = chat_with_llm("Hello!", model="openai/gpt-3.5-turbo")
print(response)

# Test with web search
response, results = chat_with_llm(
    "What's the weather?",
    model="openai/gpt-3.5-turbo",
    use_web_search=True
)
print(response)
print(f"Found {len(results)} search results")
```

### Usage in UI
1. Open application
2. Click **💬 AI Chatbot** tab
3. Select model (GPT-3.5 Turbo recommended for speed)
4. Toggle "Enable Web Search" if needed
5. Type question and press Enter

### Example Prompts
```
Without web search:
- Explain quantum computing
- Write a Python sorting function
- What are design patterns?

With web search:
- Latest AI news
- Current Bitcoin price
- Weather forecast for NYC
```

---

## Feature 2: Price Comparison 💰

### What You Get
- Compare prices across 4-10 e-commerce websites
- Automatic best deal detection
- Verified product links
- Custom website support

### Setup Steps

1. **Already done** - price_comparison.py and feature_price_comparison_ui.py are created
2. **Playwright** - Should already be installed
3. **No additional setup needed!**

### Test It
```python
from price_comparison import compare_prices

# Test price comparison
results = compare_prices("iPhone 15")
print(results['summary'])

if results['best_deal']:
    print(f"Best price: {results['best_deal']['price']}")
    print(f"At: {results['best_deal']['website']}")
```

### Usage in UI
1. Open application
2. Click **💰 Price Comparison** tab
3. Enter product name
4. Click "Search Prices"
5. Wait 20-40 seconds for results
6. View best deal and all prices

### Example Products
```
- iPhone 15 Pro
- PlayStation 5
- Samsung Galaxy S24
- Apple AirPods Pro
- Nike Air Max 90
```

### Advanced Options
- Add custom website URLs (one per line)
- Adjust max websites to check (2-10)
- Works with any e-commerce site

---

## Troubleshooting

### Problem: ImportError: No module named 'chatbot'
**Solution**: Make sure you're in the BrowserTesting directory
```bash
cd D:\AI\Git_hub\Sample_Project\BrowserTesting
python test_new_features.py
```

### Problem: ImportError: No module named 'duckduckgo_search'
**Solution**: Install the package
```bash
pip install duckduckgo-search
```

### Problem: Chatbot says "OPENROUTER_API_KEY not set"
**Solution**: Create/update .env file
```bash
# In BrowserTesting directory
echo OPENROUTER_API_KEY=your_key_here > .env
```

### Problem: Price comparison shows "No prices found"
**Causes**:
- Product not available on checked websites
- Websites blocking automated access
- Internet connection issues

**Solutions**:
- Try different product name (be specific: "iPhone 15 Pro 256GB")
- Add custom websites in Advanced Options
- Check internet connection

### Problem: Tabs not showing in UI
**Solution**: Check for Python errors
```bash
python main.py
# Look for syntax errors or import errors
```

If you see errors, make sure all files are in place:
```bash
ls -la *.py
# Should show: chatbot.py, price_comparison.py, etc.
```

### Problem: "SyntaxError" on line with union types
**Solution**: This was already fixed! Make sure you have latest main.py
- Check line 11 in chatbot.py uses `Optional[str]` not `str | None`

---

## Verification Checklist

Run through this checklist to ensure everything works:

### Installation
- [ ] Ran `pip install -r requirements.txt`
- [ ] No errors during installation
- [ ] `test_new_features.py` runs successfully

### Configuration
- [ ] `.env` file exists in BrowserTesting directory
- [ ] OPENROUTER_API_KEY is set in `.env`
- [ ] API key is valid (test with chatbot)

### Application
- [ ] `streamlit run main.py` starts without errors
- [ ] Application opens in browser
- [ ] Can see 3 tabs at top
- [ ] Can switch between tabs

### Chatbot Feature
- [ ] Can access **💬 AI Chatbot** tab
- [ ] Can see model selection dropdown
- [ ] Can see "Enable Web Search" checkbox
- [ ] Can type in chat input
- [ ] Chatbot responds (may show API key warning)
- [ ] Clear chat button works

### Price Comparison Feature
- [ ] Can access **💰 Price Comparison** tab
- [ ] Can enter product name
- [ ] "Search Prices" button is visible
- [ ] Advanced Options expander works
- [ ] Can see example products section

### Original Feature
- [ ] Can access **🤖 Browser Testing** tab
- [ ] Original testing features still work
- [ ] Example scenarios are visible
- [ ] Generate & Run button works

---

## Performance Expectations

### Chatbot Response Times
- GPT-3.5 Turbo: 2-5 seconds
- GPT-4: 5-10 seconds
- GPT-4 Turbo: 5-15 seconds
- With web search: +2-3 seconds

### Price Comparison Times
- Per website: 5-10 seconds
- 4 websites: ~20-40 seconds
- 10 websites: ~50-100 seconds

### Tips for Speed
- Use GPT-3.5 Turbo for faster chatbot responses
- Start with 4 websites for price comparison
- Enable web search only when needed
- Use cached results when possible

---

## Cost Considerations

### OpenRouter API Costs
- **GPT-3.5 Turbo**: ~$0.001-0.002 per message
- **GPT-4**: ~$0.03-0.06 per message
- **GPT-4 Turbo**: ~$0.01-0.03 per message

### Free Resources
- **Web Search**: Completely free (DuckDuckGo)
- **Price Comparison**: Free (uses Playwright)
- **No credit card** required for testing with small limits

### Recommendations
- Start with GPT-3.5 Turbo (cheapest)
- Enable web search only when needed
- Monitor usage on OpenRouter dashboard

---

## Next Steps

### 1. Test Basic Functionality
```bash
python test_new_features.py
```

### 2. Try Chatbot
- Ask simple question
- Try with and without web search
- Test different models

### 3. Try Price Comparison
- Search for a popular product
- Try with custom websites
- Check verified links

### 4. Explore Advanced Features
- Chatbot: Maintain conversation context
- Price Comparison: Use advanced options
- Integration: Switch between all 3 tabs

### 5. Read Documentation
- `NEW_FEATURES.md` - Detailed feature docs
- `FEATURES_SUMMARY.md` - Quick reference
- `Readme.md` - Original documentation

---

## Support Resources

| Issue Type | Resource |
|------------|----------|
| Installation problems | `WINDOWS_FIX.md` |
| Python compatibility | `WINDOWS_FIX.md` |
| Feature documentation | `NEW_FEATURES.md` |
| Quick reference | `FEATURES_SUMMARY.md` |
| Testing | `test_new_features.py` |
| General help | `Readme.md` |

---

## Success!

If you can:
1. ✅ Run `streamlit run main.py` without errors
2. ✅ See all 3 tabs in the application
3. ✅ Use chatbot to get a response
4. ✅ Use price comparison to find prices

Then you're all set! 🎉

Enjoy your enhanced Browser Automation AI Agent with Chatbot and Price Comparison features!

---

**Questions?**
- Check the documentation files listed above
- Run `python test_new_features.py` for diagnostics
- Review error messages in the console
- Verify `.env` configuration

**Happy automating!** 🚀
