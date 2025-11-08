# Installation & Setup Guide

## Quick Start

The Browser Automation AI Agent has been successfully installed and tested. Follow these steps to run it:

### Prerequisites

- Python 3.13+ ✓ (installed)
- pip ✓ (installed)
- All dependencies ✓ (installed)

### Running the Application

#### Method 1: Using the Run Script (Recommended)

```bash
cd /tmp/cc-agent/59885138/project/BrowserTesting
./run.sh
```

#### Method 2: Direct Command

```bash
cd /tmp/cc-agent/59885138/project/BrowserTesting
streamlit run main.py
```

The application will start and be accessible at:
- **Local**: http://localhost:8501
- **Network**: http://YOUR_IP:8501

### Setting Up AI Capabilities

To enable full AI agent functionality, you need an OpenRouter API key:

1. Get your API key from: https://openrouter.ai/

2. Create a `.env` file:
   ```bash
   cd /tmp/cc-agent/59885138/project/BrowserTesting
   cp .env.example .env
   ```

3. Edit `.env` and add your key:
   ```
   OPENROUTER_API_KEY=your_actual_key_here
   LLM_MODEL=anthropic/claude-3.5-sonnet
   ```

4. Restart the application

### Verification

Run the system check to verify everything is working:

```bash
python3 test_app.py
```

You should see:
```
✓ All systems operational!
🚀 Ready to run!
```

## Installed Components

### Core Dependencies
- ✓ Streamlit 1.51.0 - Web application framework
- ✓ Playwright 1.55.0 - Browser automation
- ✓ Pandas 2.3.3 - Data manipulation
- ✓ Python-dotenv - Environment variable management
- ✓ Requests - HTTP client

### Agent Modules
- ✓ Flow Discovery Agent - Interprets natural language goals
- ✓ Script Generator Agent - Creates Playwright test scripts
- ✓ Execution Agent - Runs tests and captures results
- ✓ Error Diagnosis Agent - Analyzes failures
- ✓ Adaptive Repair Agent - Self-healing capabilities
- ✓ Regression Monitor Agent - Visual change detection

## Troubleshooting

### Port Already in Use

If port 8501 is busy, run with a different port:
```bash
streamlit run main.py --server.port 8502
```

### Import Errors

If you get import errors, reinstall dependencies:
```bash
pip install --break-system-packages -r requirements.txt
```

### Playwright Browsers Missing

Install Playwright browsers:
```bash
playwright install chromium
```

### API Key Not Working

Verify your `.env` file:
```bash
cat .env
```

Make sure OPENROUTER_API_KEY is set correctly.

## Usage Tips

1. **Start with examples**: Use the built-in example scenarios to learn the system
2. **Be specific**: More detailed goals produce better test scripts
3. **Review generated code**: Always check the generated script before relying on it
4. **Iterate**: If a test fails, the adaptive repair agent will suggest fixes

## Example Workflow

1. Open http://localhost:8501
2. Select an example scenario or enter:
   - URL: `https://www.saucedemo.com/`
   - Goal: `Login with standard_user and verify the products page is visible`
3. Click "🚀 Generate & Run"
4. Watch as the agents:
   - Discover the flow steps
   - Generate a Playwright script
   - Execute the test
   - Report results

## Support

For issues or questions, refer to:
- Main README: `Readme.md`
- Agent documentation in `agents/` directory
- Playwright docs: https://playwright.dev/python/
- Streamlit docs: https://docs.streamlit.io/
