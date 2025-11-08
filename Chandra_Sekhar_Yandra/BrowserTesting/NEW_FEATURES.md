# New Features Documentation

## Overview

Two powerful new features have been added to the Browser Automation AI Agent:

1. **💬 AI Chatbot** - Intelligent conversational AI with web search capabilities
2. **💰 Price Comparison** - Automated product price comparison across e-commerce websites

---

## 1. AI Chatbot 💬

### Features

- **Multiple OpenAI Models**: Choose from 3 different models:
  - GPT-4 Turbo (most capable)
  - GPT-4 (balanced performance)
  - GPT-3.5 Turbo (fast and cost-effective)

- **Web Search Integration**: Enable real-time web search to get current information
  - Uses DuckDuckGo search (no API key required for search)
  - Automatically integrates search results into AI responses
  - Shows sources and links for verification

- **Conversation History**: Maintains context across multiple messages
  - Clear chat button to start fresh conversations
  - Messages persisted within session

### Usage

1. Navigate to the **💬 AI Chatbot** tab
2. Select your preferred AI model
3. (Optional) Enable "🌐 Enable Web Search" for real-time information
4. Type your question in the chat input
5. View AI responses with optional search results

### Example Queries

**Without Web Search:**
- Explain how neural networks work
- What are the differences between Python 2 and 3?
- Write a Python function to sort a list

**With Web Search:**
- What are the latest news about AI?
- What's the weather forecast for tomorrow?
- Tell me about recent tech announcements
- What are the current cryptocurrency prices?

### Technical Details

- **File**: `chatbot.py`
- **UI Component**: `feature_chatbot_ui.py`
- **API**: OpenRouter API (requires OPENROUTER_API_KEY)
- **Search**: DuckDuckGo Search (no API key needed)
- **Dependencies**: `duckduckgo-search>=4.0.0`

---

## 2. Price Comparison 💰

### Features

- **Multi-Website Comparison**: Automatically checks prices across major e-commerce sites:
  - Amazon
  - eBay
  - Walmart
  - Best Buy
  - And more...

- **Best Deal Detection**: Highlights the lowest price found
  - Shows price differences
  - Provides direct links to products
  - Verified links to actual product pages

- **Custom Website Support**: Add your own e-commerce URLs
  - Flexible search across any website
  - Adjustable number of sites to check

- **Smart Product Matching**: Uses AI to suggest appropriate websites for each product category

### Usage

1. Navigate to the **💰 Price Comparison** tab
2. Enter the product name (e.g., "iPhone 15 Pro")
3. (Optional) Expand "Advanced Options" to:
   - Add custom website URLs
   - Adjust maximum websites to check
4. Click "🔍 Search Prices"
5. View results with best deal highlighted

### Example Products

**Electronics:**
- iPhone 15 Pro
- Samsung Galaxy S24
- Sony WH-1000XM5 headphones
- Apple Watch Series 9

**Gaming:**
- PlayStation 5
- Xbox Series X
- Nintendo Switch OLED

**Other:**
- Nike Air Max 90
- Dyson V15 vacuum
- Instant Pot Duo

### Technical Details

- **File**: `price_comparison.py`
- **UI Component**: `feature_price_comparison_ui.py`
- **Scraping**: Playwright (headless browser automation)
- **Price Extraction**: Regex pattern matching
- **API**: OpenRouter API (optional, for smart website suggestions)

### Important Notes

- Prices are scraped from public websites and may not always be accurate
- Always verify prices on the actual website before purchasing
- Some websites may block automated access
- Results depend on website structure and availability

---

## Installation

### 1. Install Dependencies

```bash
cd D:\AI\Git_hub\Sample_Project\BrowserTesting
pip install -r requirements.txt
```

New packages installed:
- `duckduckgo-search>=4.0.0` - For web search in chatbot

### 2. Configure API Key

Your `.env` file should contain:

```
OPENROUTER_API_KEY=your_api_key_here
LLM_MODEL=anthropic/claude-3.5-sonnet
```

### 3. Run the Application

```bash
streamlit run main.py
```

---

## Architecture

### Main Application Structure

```
BrowserTesting/
├── main.py                          # Main app with 3 tabs
├── chatbot.py                       # Chatbot core logic
├── feature_chatbot_ui.py           # Chatbot Streamlit UI
├── price_comparison.py              # Price comparison core logic
├── feature_price_comparison_ui.py   # Price comparison Streamlit UI
└── agents/                          # Original agent modules
```

### Tab Organization

The application now uses Streamlit tabs for better organization:

1. **🤖 Browser Testing** - Original automated testing features
2. **💬 AI Chatbot** - New conversational AI assistant
3. **💰 Price Comparison** - New price comparison tool

---

## API Requirements

### Required

- **OPENROUTER_API_KEY**: Required for both features
  - Get from: https://openrouter.ai/
  - Used for: AI chatbot responses and smart price comparison

### Optional

- Web search in chatbot works without additional API keys
- Price comparison can work with custom website lists

---

## Troubleshooting

### Chatbot Issues

**"OPENROUTER_API_KEY not set"**
- Solution: Add key to `.env` file

**"Web search unavailable"**
- Solution: Install duckduckgo-search: `pip install duckduckgo-search`

**No response from model**
- Check: API key is valid
- Check: Internet connection
- Try: Different model (GPT-3.5 Turbo is fastest)

### Price Comparison Issues

**"No prices found"**
- Product may not be available on checked websites
- Try: Different product name or add custom websites
- Try: More specific product name (include brand and model)

**"Page took too long to load"**
- Website may be slow or blocking automated access
- Try: Reducing number of websites to check
- Try: Different websites in custom list

**Incorrect prices**
- Prices may have changed since scraping
- Always verify on actual website before purchasing

---

## Future Enhancements

### Planned Features

1. **Chatbot**
   - Support for more LLM providers
   - Image analysis capabilities
   - Voice input/output
   - Document Q&A

2. **Price Comparison**
   - Price history tracking
   - Price alerts and notifications
   - More sophisticated product matching
   - Support for international websites

---

## Examples

### Example 1: Research with Web Search

1. Go to **💬 AI Chatbot** tab
2. Enable "🌐 Enable Web Search"
3. Ask: "What are the latest developments in quantum computing?"
4. View AI response with current information and sources

### Example 2: Find Best Deal

1. Go to **💰 Price Comparison** tab
2. Enter: "PlayStation 5"
3. Click "🔍 Search Prices"
4. View results showing:
   - Best price: $499.99 at Walmart
   - All prices found across websites
   - Direct links to each product page

### Example 3: Custom Price Search

1. Go to **💰 Price Comparison** tab
2. Expand "⚙️ Advanced Options"
3. Add custom websites:
   ```
   https://www.amazon.com
   https://www.bestbuy.com
   https://www.target.com
   ```
4. Set maximum websites to 3
5. Search for product
6. View targeted results

---

## Support

For issues or questions:
1. Check this documentation
2. Review `WINDOWS_FIX.md` for installation issues
3. Check `Readme.md` for general information
4. Verify `.env` configuration

---

## Credits

- **AI Models**: OpenRouter API (OpenAI GPT models)
- **Web Search**: DuckDuckGo Search
- **Browser Automation**: Playwright
- **UI Framework**: Streamlit

---

**Last Updated**: 2025-11-08
**Version**: 2.0.0 with Chatbot and Price Comparison features
