# Browser Automation AI Agent 🧠

An intelligent browser automation system with AI-powered chatbot and price comparison features.

## Overview

This project is a comprehensive AI-powered automation suite with **three main features**:

### 🤖 Browser Testing (Original)
An intelligent browser automation agent that:
- Takes a **URL** and a **natural language goal** (e.g., "Test login flow", "Add item to cart")
- **Discovers** the expected user journey
- **Generates** an executable Playwright script
- **Runs** it automatically
- On failure, **diagnoses** the issue and attempts a **self-healing fix**

### 💬 AI Chatbot (NEW!)
An intelligent chatbot powered by OpenAI models with:
- **Multiple AI Models**: GPT-4 Turbo, GPT-4, GPT-3.5 Turbo
- **Web Search Integration**: Real-time information using Google Custom Search API
- **Conversation History**: Maintains context across messages
- **Source Citations**: Shows sources with clickable links

### 💰 Price Comparison (NEW!)
Smart price comparison tool that:
- **Multi-Website Search**: Compares prices across Amazon, eBay, Walmart, Best Buy
- **Best Deal Detection**: Automatically highlights the lowest price
- **Verified Links**: Direct links to product pages
- **Custom Websites**: Support for additional e-commerce sites

### Why This Matters

Traditional browser tests have several challenges:
- ✅ Manual to create
- ❌ Fragile when UI changes
- ❌ Expensive to maintain

Our solution addresses these by:
- Reducing repetitive manual testing/scripting work
- Maintaining test stability via adaptive repairs
- Providing transparent, reviewable code (no black box)

## Project Structure

```
├── main.py                          # Main Streamlit application (3 tabs)
├── chatbot.py                       # AI Chatbot with Google Search
├── price_comparison.py              # Price comparison tool
├── feature_chatbot_ui.py            # Chatbot UI component
├── feature_price_comparison_ui.py   # Price comparison UI component
├── requirements.txt                 # Project dependencies
├── generated_test.py                # Generated test scripts
├── .env                             # Environment variables (API keys)
└── agents/                          # Core agent modules
    ├── flow_discovery.py            # Discovers user journey steps
    ├── script_generator.py          # Generates Playwright scripts
    ├── execution.py                 # Executes and monitors tests
    ├── error_diagnosis.py           # Analyzes test failures
    ├── adaptive_repair.py           # Implements self-healing
    └── regression_monitor.py        # Monitors visual regressions
```

## Core Components

1. **Flow Discovery Agent** 🔍
   - Interprets natural language goals
   - Maps goals to concrete user steps
   - Understands application context

2. **Script Generator Agent** 🧾
   - Converts steps into Playwright code
   - Generates maintainable test scripts
   - Implements best practices

3. **Execution Agent** ▶️
   - Runs generated scripts
   - Captures logs and screenshots
   - Reports execution status

4. **Error Diagnosis Agent** 🩺
   - Analyzes test failures
   - Identifies root causes
   - Provides human-readable explanations

5. **Adaptive Repair Agent** 🔁
   - Suggests fixes for failing tests
   - Implements self-healing strategies
   - Maintains test stability

6. **Regression Monitor Agent** 🖼️
   - Tracks visual changes over time
   - Detects UI/layout regressions
   - Ensures visual consistency

## Features

### Browser Testing Features
- Natural language to Playwright script conversion
- Self-healing test maintenance
- Visual regression monitoring
- Automatic error diagnosis and repair
- Screenshot capture on failure

### AI Chatbot Features
- Multiple OpenAI model selection (GPT-4 Turbo, GPT-4, GPT-3.5 Turbo)
- Real-time web search with Google Custom Search API
- Conversation history with context
- Source citations with clickable links
- Clear chat history option

### Price Comparison Features
- Multi-website price scraping (Amazon, eBay, Walmart, Best Buy)
- Automatic best deal detection
- Direct product links
- Custom website support
- Advanced search options

## Requirements

- Python 3.8+ (tested on 3.8, 3.9, 3.10, 3.11, 3.12, 3.13)
- Streamlit >= 1.28.0
- Playwright >= 1.40.0
- OpenRouter API key (for AI agents and chatbot)
- Google API key + Custom Search Engine ID (for web search in chatbot)

## Getting Started

### 1. Install Dependencies

**Windows:**
```bash
pip install -r requirements.txt
playwright install chromium
```

**Linux/Mac:**
```bash
pip install -r requirements.txt
playwright install chromium
```

**Note:** If you encounter permission issues on Linux, you may need to use `pip install --user` or create a virtual environment.

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here
LLM_MODEL=anthropic/claude-3.5-sonnet
```

#### How to Get OpenRouter API Key

1. Visit https://openrouter.ai/
2. Sign up or log in
3. Go to the Keys section
4. Create a new API key
5. Copy the key (starts with `sk-or-v1-`)

#### How to Get Google API Key (for Web Search)

The chatbot feature uses Google Custom Search API for web search. Here's how to set it up:

**Step 1: Create Google Cloud Project**

1. Go to https://console.cloud.google.com/
2. Sign in with your Google account
3. Click **"Select a project"** → **"New Project"**
4. Name it: `Browser Automation AI` (or any name you prefer)
5. Click **"Create"**

**Step 2: Enable Custom Search API**

1. Go to https://console.cloud.google.com/apis/library
2. Search for: `Custom Search API`
3. Click on **"Custom Search API"**
4. Click **"Enable"**

**Step 3: Create API Key**

1. Go to https://console.cloud.google.com/apis/credentials
2. Click **"Create Credentials"** → **"API Key"**
3. Copy the API key (starts with `AIza...`)
4. (Optional) Click **"Restrict Key"** and select **"Custom Search API"** for better security

#### How to Get Google Custom Search Engine ID (CSE ID)

**Step 1: Create Search Engine**

1. Go to https://programmablesearchengine.google.com/
2. Click **"Add"** or **"Get Started"**
3. Enter a name: `AI Chatbot Search`
4. Select **"Search the entire web"**
5. Click **"Create"**

**Step 2: Get Search Engine ID**

1. Click on your newly created search engine
2. Go to **"Setup"** or **"Control Panel"**
3. Find **"Search engine ID"** (looks like: `a1b2c3d4e5f6g7h8i:ab1cd2ef3gh`)
4. Copy the Search Engine ID

**Step 3: Configure Settings** (Optional)

1. In the Control Panel, go to **"Setup"** tab
2. Enable **"SafeSearch"** (recommended)
3. Click **"Update"**

#### Cost Information

- **Google Custom Search API:**
  - Free: 100 searches per day
  - Paid: $5 per 1,000 additional queries
  - Most users stay within the free tier!

For detailed setup instructions, see `GOOGLE_SEARCH_SETUP.md`.

### 3. Run the Application

Option A - Using the run script:
```bash
chmod +x run.sh
./run.sh
```

Option B - Direct streamlit command:
```bash
streamlit run main.py
```

### 4. Access the Web Interface

Open your browser to:
- Local: http://localhost:8501
- Network: http://YOUR_IP:8501

The application has **three tabs**:

**Tab 1: 🤖 Browser Testing**
- Enter your target URL
- Describe your testing goal
- Click "Generate & Run"
- Watch as AI generates and runs your test

**Tab 2: 💬 AI Chatbot**
- Select your preferred AI model (GPT-4 Turbo, GPT-4, or GPT-3.5 Turbo)
- Enable web search for real-time information
- Ask questions and get intelligent responses
- View source citations

**Tab 3: 💰 Price Comparison**
- Enter a product name
- Click "Compare Prices"
- See prices from multiple websites
- Get direct links to the best deals

## Example Usage

### Browser Testing Examples
Try these example scenarios:
1. **SauceDemo Login**: Test login with standard_user and verify products page
2. **Add to Cart**: Login, add item to cart, verify cart contents
3. **Checkout Flow**: Complete end-to-end purchase flow
4. **Price Sorting**: Sort products and add cheapest item to cart

### AI Chatbot Examples
Try asking:
1. **General Questions**: "What is machine learning?"
2. **With Web Search**: "What's the latest AI news?" (enable web search)
3. **Technical Help**: "How do I use Python asyncio?"
4. **Research**: "Compare React vs Vue.js" (with web search)

### Price Comparison Examples
Try searching for:
1. **Electronics**: "iPhone 15 Pro"
2. **Laptops**: "MacBook Air M2"
3. **Gaming**: "PlayStation 5"
4. **Smart Home**: "Amazon Echo Dot"

## Use Cases

### Browser Testing
- Automated testing of web applications
- UI regression testing
- User flow validation
- Continuous integration testing
- QA automation
- Self-healing test maintenance

### AI Chatbot
- Quick information lookup
- Research assistance with web search
- Technical documentation help
- General knowledge questions
- Real-time information retrieval

### Price Comparison
- Finding best deals online
- Price shopping across multiple retailers
- Product research and comparison
- Deal hunting and savings
- E-commerce price monitoring

## Documentation

For detailed setup and usage information, see:

### Setup Guides
- **`GOOGLE_SEARCH_SETUP.md`** - Complete guide to setting up Google Custom Search API
- **`ENV_SETUP.md`** - Environment variable configuration guide
- **`INSTALL_WINDOWS.md`** - Windows-specific installation instructions
- **`INSTALLATION.md`** - General installation guide

### Feature Documentation
- **`NEW_FEATURES.md`** - Complete documentation for chatbot and price comparison features
- **`FEATURES_SUMMARY.md`** - Quick reference guide for all features
- **`WEB_SEARCH_UPDATE.md`** - Information about the Google Search integration

### Migration & Updates
- **`GOOGLE_MIGRATION.md`** - Why we migrated from DuckDuckGo to Google
- **`PYTHON_COMPATIBILITY_FIXES.md`** - Python 3.8+ compatibility documentation

### Troubleshooting
- **`check_env.py`** - Run this to diagnose configuration issues
- **`verify_setup.py`** - Complete system verification script
- **`CURRENT_ISSUE.md`** - Common issues and solutions

## Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv'"
**Solution:** Install dependencies with `pip install -r requirements.txt`

### "Error connecting to OpenRouter API"
**Solution:**
1. Make sure `.env` file exists
2. Add your `OPENROUTER_API_KEY` to `.env`
3. Get key from https://openrouter.ai/

### "Google Search not configured"
**Solution:**
1. Add `GOOGLE_API_KEY` to `.env`
2. Add `GOOGLE_CSE_ID` to `.env`
3. See `GOOGLE_SEARCH_SETUP.md` for detailed instructions

### General Issues
Run the diagnostic script:
```bash
python check_env.py
```

This will show exactly what's missing or misconfigured.

## Future Work

- Enhanced visual regression analysis
- Support for additional automation frameworks
- Advanced self-healing strategies
- Integration with CI/CD pipelines
- Extended browser compatibility testing
- More AI model options for chatbot
- Additional e-commerce sites for price comparison

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.