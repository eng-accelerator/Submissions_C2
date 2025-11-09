# Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your prompt.

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Or use the setup script:
```bash
python setup.py
```

### Step 3: Configure API Keys
1. Copy `env.example` to `.env` (or create `.env` file)
2. Get your API keys:
   - OpenRouter API key from https://openrouter.ai/keys
   - Tavily API key from https://tavily.com/
3. Add to `.env`:
```
OPEN_ROUTER_KEY=sk-or-your-key-here
TAVILY_API_KEY=your_tavily_key_here
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

**Note:** Make sure your virtual environment is activated (you should see `(venv)` in your prompt).

### Deactivate Virtual Environment (When Done)
```bash
deactivate
```

---

## 📖 Detailed Setup

For complete step-by-step instructions with troubleshooting, see:
- **`VIRTUAL_ENV_SETUP.md`** - Comprehensive virtual environment setup guide

## 🎯 Demo Mode

For hackathon presentations:

1. **First Run**: Execute a query normally to cache results
2. **Demo Mode**: Check "Use Demo Mode" checkbox in sidebar
3. **Select Query**: Click a demo query button for instant results

## 📝 Example Queries

Try these queries:
- "Latest developments in quantum computing 2024"
- "Current state of AI safety research and regulations"
- "Emerging climate technology solutions 2024"

## ⚠️ Troubleshooting

**No API Key?**
- System will use mock/template responses
- Full functionality requires OpenRouter API key
- Get your key from https://openrouter.ai/keys

**Search Not Working?**
- DuckDuckGo may be rate-limited
- System continues with available sources

**Import Errors?**
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Python version: 3.8+

## 🏗️ Project Structure

```
├── agents/              # Agent implementations
├── orchestration/        # LangGraph workflow
├── utils/               # Utilities (caching, etc.)
├── app.py              # Streamlit UI
├── requirements.txt    # Dependencies
└── README.md           # Full documentation
```

## 🎨 Customization

**Change LLM Model:**
Edit `agents/analyzer.py`, `agents/insight_generator.py`, `agents/report_builder.py`

**Add New Agent:**
1. Create file in `agents/`
2. Add node to `orchestration/coordinator.py`
3. Update UI in `app.py`

## 📊 Demo Checklist

Before hackathon:
- [ ] Test with 2-3 queries
- [ ] Cache results for demo mode
- [ ] Verify all agents working
- [ ] Test download functionality
- [ ] Prepare backup cached results

---

**Ready to demo!** 🎉

