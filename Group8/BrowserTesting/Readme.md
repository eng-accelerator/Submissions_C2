# AI Browser Automation Lab 🧪

An intelligent browser automation system that converts natural language goals into self-healing Playwright test scripts, with optional AI-powered chatbot assistance.

---

## 📌 Project Versions

This project has **two versions** of the main application:

### Version 1: `main.py` - Core Browser Automation with AI Chatbot Assistant(lite Version)
**Pure browser testing automation without chatbot**
- Focus: Browser test generation and execution
- Features: All 6 automation agents
- Use when: You only need browser testing capabilities
- Run: `streamlit run main.py`

### Version 2: `main_Chatbot_latest.py` - Enhanced with AI Chatbot Assistant
**Browser automation + Integrated AI chatbot**
- Focus: Browser testing + Intelligent assistance
- Features: All agents + AI Assistant with multimodal support
- Use when: You want AI help alongside browser testing
- Run: `streamlit run main_Chatbot_latest.py`

**Recommendation:** Use `main_Chatbot_latest.py` for the full experience!

---

## 🎯 Overview

### What This Does

This AI-powered system automates browser testing by:

1. **Understanding Goals**: Takes natural language descriptions like "Test login flow"
2. **Discovering Steps**: Maps your goal to concrete user actions
3. **Generating Code**: Creates executable Playwright test scripts
4. **Running Tests**: Executes scripts in real browsers
5. **Self-Healing**: Automatically fixes broken tests when UI changes
6. **Visual Monitoring**: Detects unwanted UI/layout changes

### Why This Matters

**Traditional Testing Problems:**
- ✅ Manual script writing is time-consuming
- ❌ Tests break when UI changes
- ❌ Expensive to maintain
- ❌ Requires programming expertise

**Our Solution:**
- ✅ Natural language → Working test scripts
- ✅ Self-healing when UI changes
- ✅ Visual regression detection
- ✅ AI assistance (Version 2)
- ✅ Transparent, reviewable code

---

## 📁 Project Structure

```
BrowserTesting_latest/
│
├── main.py                      # Version 1: Core browser automation
├── main_Chatbot_latest.py       # Version 2: With AI Assistant
│
├── chatbot_rag_backend.py       # RAG chatbot backend (LangGraph)
├── chatbot_ui.py                # Chatbot UI component
│
├── requirements.txt             # Python dependencies
├── .env                         # Environment configuration (create this)
│
├── agents/                      # Core automation agents
│   ├── __init__.py
│   ├── flow_discovery.py        # Discovers user journey steps
│   ├── script_generator.py      # Generates Playwright scripts
│   ├── execution.py             # Executes tests in browser
│   ├── error_diagnosis.py       # Analyzes test failures
│   ├── adaptive_repair.py       # Self-healing logic
│   ├── regression_monitor.py    # Visual regression detection
│   └── llm/                     # LLM integration utilities
│       ├── llm_client.py
│       └── llm_utils.py
│
└── Documentation/
    ├── CHATBOT_README.md        # AI Assistant complete guide
    ├── QUICK_START.md           # 5-minute setup guide
    ├── IMPLEMENTATION_SUMMARY.md # Technical details
    └── CHATBOT_FEATURE.md       # Feature documentation
```

---

## 🤖 Core Components

### 1. Flow Discovery Agent 🔍
**Purpose:** Interprets natural language and maps it to concrete steps

**Example:**
```
Input: "Test login flow with standard user"
Output:
  - Navigate to login page
  - Enter username "standard_user"
  - Enter password "secret_sauce"
  - Click login button
  - Verify products page loads
```

### 2. Script Generator Agent 🧾
**Purpose:** Converts flow steps into executable Playwright code

**Example:**
```python
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.saucedemo.com")
        page.fill("#user-name", "standard_user")
        page.fill("#password", "secret_sauce")
        page.click("#login-button")
        # ... verification code
```

### 3. Execution Agent ▶️
**Purpose:** Runs generated scripts and captures results

**Features:**
- Executes tests in real browser
- Captures screenshots on success/failure
- Logs execution details
- Returns success/failure status

### 4. Error Diagnosis Agent 🩺
**Purpose:** Analyzes failures and explains what went wrong

**Example:**
```
Error: Selector #login-button not found
Diagnosis: The login button selector has changed or the element
           is not visible. Consider using a more robust selector
           like text='Login' or waiting for page load.
```

### 5. Adaptive Repair Agent 🔁
**Purpose:** Self-healing - automatically fixes broken tests

**How it works:**
1. Test fails due to changed selector
2. Analyzes the error and page structure
3. Finds the correct new selector
4. Generates repaired script
5. Offers to re-run with fix

**Example:**
```
Original: page.click("#old-button-id")
Repaired: page.click("button:has-text('Submit')")
```

### 6. Visual Regression Monitor 🖼️
**Purpose:** Detects unwanted UI/layout changes

**How it works:**
1. First run: Creates baseline screenshot
2. Subsequent runs: Compares against baseline
3. Highlights visual differences
4. Alerts on regressions

### 7. AI Assistant Chatbot 🤖 (Version 2 Only)
**Purpose:** Intelligent help and guidance

**Features:**
- **Multimodal Understanding**: Text + images + documents
- **Agent Knowledge**: Knows all project capabilities
- **Web Search**: Google Custom Search integration
- **File Analysis**: Upload screenshots/logs for analysis
- **Context-Aware**: Remembers conversation history
- **Troubleshooting**: Helps debug test failures

**Capabilities:**
- Answer questions about features
- Analyze error screenshots
- Review generated scripts
- Suggest improvements
- Search for latest documentation
- Guide test creation

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Browser**: Chromium (installed automatically by Playwright)

### Installation

#### 1. Install Dependencies

```bash
# Navigate to project folder
cd BrowserTesting_latest

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

#### 2. Configure Environment Variables

Create a `.env` file in the `BrowserTesting_latest` folder:

```bash
# Required for all features
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: For AI Assistant web search (Version 2)
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_search_engine_id_here

# LLM Model
LLM_MODEL=anthropic/claude-3.5-sonnet
```

**Where to get API keys:**

**OpenRouter API Key** (Required):
1. Visit: https://openrouter.ai/
2. Sign up and create an account
3. Go to "Keys" section
4. Create a new API key
5. Copy the key (starts with `sk-or-v1-`)

**Google API Key** (Optional - for web search):
1. Visit: https://console.cloud.google.com/
2. Create a new project
3. Enable "Custom Search API"
4. Create credentials → API Key
5. Copy the key (starts with `AIza`)

**Google CSE ID** (Optional - for web search):
1. Visit: https://programmablesearchengine.google.com/
2. Create a new search engine
3. Select "Search the entire web"
4. Copy the Search Engine ID

For detailed setup, see: `QUICK_START.md`

#### 3. Run the Application

**Version 1 - Core Automation Only:**
```bash
streamlit run main.py
```

**Version 2 - With AI Assistant (Recommended):**
```bash
streamlit run main_Chatbot_latest.py
```

The application will open in your default browser at `http://localhost:8501`

---

## 💡 How to Use

### Version 1: main.py (Core Automation)

1. **Enter Target URL**
   - Example: `https://www.saucedemo.com`

2. **Describe Your Goal**
   - Example: "Log in with standard_user and verify products page"

3. **Click "🚀 Generate & Run"**

4. **Watch the Pipeline:**
   - ⏳ Stage 1: Flow Discovery
   - ⏳ Stage 2: Script Generation
   - ⏳ Stage 3: Execution
   - ⏳ Stage 4: Diagnosis & Self-Heal (if failed)
   - ⏳ Stage 5: Visual Regression Guard

5. **Review Results:**
   - See discovered flow steps
   - View generated Playwright code
   - Check execution logs and screenshots
   - Apply fixes if suggested

### Version 2: main_Chatbot_latest.py (With AI Assistant)

**Same as Version 1, PLUS:**

6. **Click "🤖 AI Assistant"** button (next to Generate & Run)

7. **Use the AI Assistant:**
   - Ask questions: "What agents are available?"
   - Upload screenshots: "What's wrong with this error?"
   - Get help: "How do I test dynamic content?"
   - Search web: Enable web search for latest info

8. **Upload Files to Assistant:**
   - Screenshots of errors
   - Generated test scripts
   - Execution logs
   - Configuration files

---

## 📝 Example Scenarios

### Example 1: Basic Login Test

**Goal:** Test login with standard credentials

```
URL: https://www.saucedemo.com
Goal: Log in with username 'standard_user' and password 'secret_sauce',
      then verify the products page loads
```

**What happens:**
1. Flow Discovery identifies login steps
2. Script Generator creates Playwright code
3. Execution runs the test
4. Visual Monitor captures baseline screenshot

### Example 2: E-commerce Flow

**Goal:** Add product to cart

```
URL: https://www.saucedemo.com
Goal: Log in with standard_user, add 'Sauce Labs Backpack' to cart,
      open cart and verify the item is listed
```

**What happens:**
1. Discovers multi-step user journey
2. Generates script with product selection logic
3. Executes full flow
4. Verifies cart contents

### Example 3: Self-Healing Demo

**Goal:** Demonstrate automatic fix capability

```
URL: https://www.demoblaze.com
Goal: Go to Laptops, add 'Sony vaio i5' to cart, place order
```

**What happens:**
1. Script may fail due to selector issues
2. Error Diagnosis identifies the problem
3. Adaptive Repair suggests a fix
4. You click "Apply Fix & Re-Run"
5. Test passes with repaired selectors

### Example 4: Visual Regression

**Goal:** Detect UI changes

```
URL: https://www.saucedemo.com
Goal: Log in and add Sauce Labs Backpack to cart
```

**What happens:**
1. First run: Creates baseline screenshot
2. Subsequent runs: Compares against baseline
3. Alerts if UI changes detected
4. Shows diff image highlighting changes

---

## 🤖 AI Assistant Features (Version 2)

### What Can It Do?

#### 1. Answer Questions
```
User: What agents are available?
AI: [Lists all 6 agents with descriptions and examples]
```

#### 2. Analyze Screenshots
```
User: [Uploads error screenshot]
      "What does this error mean?"
AI: [Analyzes image, explains error, suggests solution]
```

#### 3. Review Scripts
```
User: [Uploads generated_test.py]
      "How can I improve this script?"
AI: [Reviews code, suggests improvements]
```

#### 4. Web Search
```
User: "What's new in Playwright 2024?"
AI: [Searches web, summarizes with source citations]
```

#### 5. Troubleshooting Help
```
User: "My test keeps failing on dynamic content"
AI: [Explains waits, suggests solutions, provides examples]
```

### Supported File Types

**Images** (Vision analysis):
- `.png`, `.jpg`, `.jpeg`, `.webp`
- Screenshots, error messages, UI elements

**Text Files** (Content extraction):
- `.txt` - Plain text logs
- `.md` - Documentation
- `.log` - Application logs

**Code Files** (Syntax-aware):
- `.py` - Python scripts
- `.js` - JavaScript
- `.html` - HTML pages
- `.css` - Stylesheets
- `.json` - Configuration

### AI Assistant Architecture

**Backend:** LangGraph workflow with RAG
**Model:** Claude 3.5 Sonnet (multimodal)
**Search:** Google Custom Search API
**Context:** Documents + History + Agent features

For complete guide, see: `CHATBOT_README.md`

---

## 📊 Dependencies

### Core Dependencies
```
streamlit>=1.28.0          # Web UI framework
playwright>=1.40.0          # Browser automation
python-dotenv>=1.0.0        # Environment config
requests>=2.31.0            # HTTP requests
```

### AI Assistant Dependencies (Version 2)
```
langgraph>=0.0.40          # Workflow orchestration
langchain>=0.1.0           # LLM integration
langchain-core>=0.1.0      # Core components
```

### Supporting Packages
```
pandas>=2.0.0              # Data processing
numpy>=1.24.0              # Numerical operations
pillow>=10.0.0             # Image processing
```

---

## ⚙️ Configuration

### Environment Variables

**Required:**
- `OPENROUTER_API_KEY` - For LLM access (all agents + chatbot)

**Optional:**
- `GOOGLE_API_KEY` - For web search in AI Assistant
- `GOOGLE_CSE_ID` - Google Custom Search Engine ID
- `LLM_MODEL` - Default: `anthropic/claude-3.5-sonnet`

### Model Options

**Recommended (Default):**
- `anthropic/claude-3.5-sonnet` - Best balance of quality and cost

**Alternatives:**
- `openai/gpt-4-turbo` - High quality, higher cost
- `openai/gpt-3.5-turbo` - Faster, lower cost
- `google/gemini-pro` - Google's model

---

## 💰 Cost Estimates

### OpenRouter API Costs

**Per Query:**
- Claude 3.5 Sonnet: ~$0.015-0.03
- GPT-4 Turbo: ~$0.03-0.06
- GPT-3.5 Turbo: ~$0.001-0.002

**Browser Test Run (5 agents):**
- Flow Discovery: ~$0.02
- Script Generation: ~$0.02
- Error Diagnosis: ~$0.02
- Adaptive Repair: ~$0.02
- Total per test: ~$0.08

**AI Assistant:**
- Text query: ~$0.015
- Image analysis: ~$0.02-0.03
- With web search: +$0.005

**Typical Monthly Usage:**
- 50 test runs: ~$4
- 100 chatbot queries: ~$2
- **Total: $5-10/month**

### Google Search Costs

- Free: 100 searches/day
- Paid: $5 per 1,000 additional queries

**Most users stay within free tiers!**

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Module not found" errors

**Solution:**
```bash
pip install -r requirements.txt
playwright install chromium
```

#### 2. "OPENROUTER_API_KEY not configured"

**Solution:**
1. Create `.env` file
2. Add: `OPENROUTER_API_KEY=your_key_here`
3. Get key from: https://openrouter.ai/

#### 3. AI Assistant button disabled

**Solution:**
```bash
pip install langgraph langchain langchain-core
```

#### 4. "Google Search not configured"

**Solution:**
1. Add to `.env`:
   ```
   GOOGLE_API_KEY=your_google_key
   GOOGLE_CSE_ID=your_cse_id
   ```
2. Or use without web search

#### 5. Tests fail immediately

**Check:**
- Is the target URL accessible?
- Is Playwright installed? (`playwright install chromium`)
- Check execution logs for specific errors

#### 6. Self-healing not working

**Check:**
- Did the test actually fail?
- Are you using Version 1 or 2?
- Check if repair script was generated
- Click "Apply Fix & Re-Run" if available

---

## 📚 Documentation

### Quick References
- **`QUICK_START.md`** - 5-minute setup guide
- **`CHATBOT_README.md`** - Complete AI Assistant guide
- **`IMPLEMENTATION_SUMMARY.md`** - Technical architecture

### Feature Guides
- **`CHATBOT_FEATURE.md`** - AI Assistant feature details

### Main Documentation
- **`README.md`** - This file

---

## 🎓 Use Cases

### Software Testing
- Automated regression testing
- UI flow validation
- Cross-browser testing setup
- Continuous integration tests

### QA Automation
- Self-healing test suites
- Visual regression monitoring
- Exploratory testing assistance
- Test maintenance reduction

### Development
- Rapid test prototyping
- Testing new features quickly
- Understanding user flows
- Debugging UI interactions

### Learning
- Understanding Playwright
- Learning test automation
- AI-assisted coding
- Browser automation concepts

---

## 🛠️ Advanced Usage

### Custom Selectors

The Script Generator uses multiple selector strategies:
- ID selectors: `#login-button`
- Text-based: `button:has-text('Login')`
- CSS selectors: `.submit-btn`
- XPath: `//button[@class='submit']`

### Baseline Management

Visual regression baselines are stored in `screenshots/` folder:
- `{test_id}_baseline.png` - Original baseline
- `{test_id}_current.png` - Latest screenshot
- `{test_id}_diff.png` - Visual difference

To reset baselines: Delete old baseline screenshots

### Script Customization

Generated scripts can be:
1. Copied from the UI
2. Modified manually
3. Saved to files
4. Integrated into test suites

---

## 🚦 Workflow Pipeline

```
User Input (URL + Goal)
    ↓
[Flow Discovery Agent]
    ↓
Discovered Steps
    ↓
[Script Generator Agent]
    ↓
Playwright Code
    ↓
[Execution Agent]
    ↓
Success? ──→ Yes ──→ [Visual Regression Monitor]
    │                       ↓
    No                   Baseline
    ↓                    Check
[Error Diagnosis]           ↓
    ↓                   Pass/Fail
[Adaptive Repair]
    ↓
Fixed Script
    ↓
Re-run Option
```

---

## 🔐 Security Notes

### API Keys
- Never commit `.env` file to version control
- Keep API keys secret
- Rotate keys periodically
- Use environment variables in production

### Data Privacy
- Tests run locally in your browser
- No data sent to external services except:
  - LLM API calls (OpenRouter)
  - Web search API calls (Google)
- Review generated scripts before running
- Be cautious with sensitive test data

---

## 🤝 Best Practices

### Writing Goals
**Good:**
- "Log in with username 'test' and password 'pass123'"
- "Add the 'Sauce Labs Backpack' product to cart"
- "Navigate to checkout and verify total is displayed"

**Too Vague:**
- "Test the website"
- "Check if it works"
- "Do stuff"

### Using AI Assistant
1. **Be Specific**: Ask clear, focused questions
2. **Provide Context**: Upload relevant files
3. **Enable Search**: For latest information
4. **Build Conversations**: Follow up on previous answers
5. **Review Sources**: Check web search citations

### Self-Healing
1. **Review Repairs**: Check suggested fixes before applying
2. **Learn Patterns**: Understand what changed
3. **Update Goals**: Adjust if flow changed significantly
4. **Baseline Reset**: After intentional UI changes

---

## 🌟 Version Comparison

| Feature | Version 1 (main.py) | Version 2 (main_Chatbot_latest.py) |
|---------|---------------------|-------------------------------------|
| **Browser Automation** | ✅ Yes | ✅ Yes |
| **6 Agent Pipeline** | ✅ Yes | ✅ Yes |
| **Self-Healing** | ✅ Yes | ✅ Yes |
| **Visual Regression** | ✅ Yes | ✅ Yes |
| **AI Assistant** | ❌ No | ✅ Yes |
| **File Upload** | ❌ No | ✅ Yes |
| **Image Analysis** | ❌ No | ✅ Yes |
| **Web Search** | ❌ No | ✅ Yes |
| **Context-Aware Help** | ❌ No | ✅ Yes |
| **Dependencies** | Minimal | + LangGraph |
| **Setup Complexity** | Simple | Moderate |
| **Best For** | Pure testing | Testing + Assistance |

**Recommendation:** Start with Version 2 for the complete experience!

---

## 📖 Learn More

### External Resources
- **Playwright Documentation**: https://playwright.dev/
- **OpenRouter API**: https://openrouter.ai/docs
- **LangGraph Guide**: https://langchain-ai.github.io/langgraph/
- **Streamlit Docs**: https://docs.streamlit.io/

### Project Documentation
- All markdown files in this folder
- Inline code comments
- Agent module docstrings

---

## 🐛 Known Limitations

1. **Language Support**: Currently optimized for English
2. **Browser Support**: Primarily tested with Chromium
3. **Complex Flows**: Very complex multi-page flows may need manual adjustment
4. **Dynamic Content**: Heavy JavaScript SPAs may require additional waits
5. **Rate Limits**: API rate limits apply (OpenRouter, Google)

---

## 🔄 Updates & Maintenance

### Keeping Up to Date

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update Playwright
playwright install chromium --force
```

### Version History

**Version 2 (Current):**
- Added AI Assistant chatbot
- Multimodal support (text + images + docs)
- Web search integration
- RAG backend with LangGraph
- Enhanced troubleshooting

**Version 1:**
- Core 6-agent pipeline
- Self-healing capabilities
- Visual regression monitoring
- Basic browser automation

---

## 💬 Support

### Getting Help

1. **Use AI Assistant** (Version 2): Ask it directly!
2. **Check Documentation**: Review markdown files
3. **Review Examples**: Try example scenarios
4. **Error Messages**: Read carefully for clues

### Common Questions

**Q: Which version should I use?**
A: Version 2 (`main_Chatbot_latest.py`) for full features

**Q: Do I need Google API keys?**
A: No, only for web search in AI Assistant

**Q: Can I use without OpenRouter?**
A: No, OpenRouter API key is required

**Q: How much does it cost?**
A: ~$5-10/month for typical usage

**Q: Is my data safe?**
A: Tests run locally; only API calls sent to OpenRouter/Google

---

## 📄 License

This project is open source. Check the repository for license details.

---

## 🎉 Get Started Now!

### Quick Commands

```bash
# Install everything
pip install -r requirements.txt
playwright install chromium

# Configure (create .env file)
echo "OPENROUTER_API_KEY=your_key_here" > .env

# Run Version 1 (Core)
streamlit run main.py

# Run Version 2 (With AI Assistant) - Recommended!
streamlit run main_Chatbot_latest.py
```

### First Steps

1. Run `streamlit run main_Chatbot_latest.py`
2. Click an example scenario
3. Click "🚀 Generate & Run"
4. Watch the magic happen!
5. Click "🤖 AI Assistant" to get help

---

**Built with:** Playwright • Streamlit • LangGraph • Claude 3.5 Sonnet

**Happy Testing!** 🚀
