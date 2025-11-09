# ⚡ Quick Start Guide

Get the Multi-Agent DevOps Incident Suite running in **under 5 minutes**!

## 🎯 Prerequisites

- Python 3.8 or higher
- OpenAI API key (required)
- Slack/JIRA credentials (optional)

## 📦 Step 1: Install Dependencies

```bash
cd Hackathon
pip install -r requirements.txt
```

**Estimated time:** 2-3 minutes

## 🔑 Step 2: Configure API Keys

Create a `.env` file in the Hackathon directory:

```bash
# Copy the example
cp .env.example .env

# Edit with your keys
nano .env
```

**Minimum required:**
```env
OPENAI_API_KEY=sk-your-key-here
```

Get your OpenAI key: https://platform.openai.com/api-keys

**Optional (for full features):**
```env
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL_ID=C01234567
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-token
```

## 🚀 Step 3: Launch the App

```bash
streamlit run app.py
```

The app will open automatically at: **http://localhost:8501**

## 🎮 Step 4: Analyze Logs

### Option A: Use Sample Logs (Quickest!)

1. Click **"Load Sample Logs"** in the sidebar
2. Click **"🚀 Analyze Incident"**
3. Watch the magic happen! ✨

### Option B: Upload Your Own Logs

1. Click **"📤 Upload Logs"** tab
2. Drag & drop a `.log` file **OR** paste logs in the text area
3. Click **"🚀 Analyze Incident"**

### Option C: Try Sample File

```bash
# Use the provided sample
# In the UI, click "Upload log file" and select:
# sample_logs.txt
```

## 📊 What You'll See

### 1. Agent Execution Timeline
Watch each agent work in real-time:
- 🔍 Log Reader Agent
- 💊 Remediation Agent
- 📢 Notification Agent
- 🎫 JIRA Agent
- 📚 Cookbook Agent

### 2. Analysis Results
- **Executive Summary** - High-level overview
- **Critical Issues Gauge** - Visual metrics
- **Remediation Plans** - Detailed solutions
- **JIRA Tickets** - Auto-created tickets
- **Incident Playbook** - Downloadable guide

## 🎨 UI Features

- **Live Agent Status** - See which agents are running
- **Integration Status** - Check API connections
- **Progress Tracking** - Visual progress bars
- **Interactive Charts** - Gauge charts for metrics
- **Download Playbooks** - Save for future reference

## 🐛 Common Issues

### "Invalid API Key"
- Ensure your key starts with `sk-`
- Check for extra spaces or quotes
- Get a new key: https://platform.openai.com/api-keys

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Port Already in Use
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

### Slow Performance
- First analysis is slower (initializing models)
- Subsequent analyses are faster
- Consider upgrading to GPT-4 for better quality

## 🎯 Quick Test Commands

### Test Configuration
```bash
python -c "from config import Config; print('✅ Config OK' if Config.validate_api_key() else '❌ API Key Invalid')"
```

### Test Agents
```bash
# Coming soon: Unit tests
pytest tests/
```

### Test Orchestrator
```python
python -c "
from orchestrator import IncidentOrchestrator
import asyncio

orch = IncidentOrchestrator()
print('✅ Orchestrator initialized')
print(f'Agent status: {orch.get_agent_status()}')
"
```

## 📚 Next Steps

Once you have the basic setup working:

1. **Add Custom Knowledge**
   - Add documents to `knowledge_base/` folder
   - Rebuild vector store

2. **Configure Slack**
   - Create Slack app
   - Get bot token
   - Add to `.env`

3. **Configure JIRA**
   - Generate API token
   - Add to `.env`

4. **Customize Agents**
   - Modify agent behavior in `agents/` folder
   - Add new agents by extending `BaseAgent`

5. **Enable LangSmith**
   - Sign up at https://smith.langchain.com
   - Add keys to `.env`
   - View traces and debugging

## 💡 Pro Tips

1. **Sample Logs First** - Always start with sample logs to verify setup
2. **Check Agent Status** - Monitor in sidebar during execution
3. **Download Playbooks** - Save successful analyses for reference
4. **Test Integrations** - Verify Slack/JIRA work before production use
5. **Monitor Costs** - OpenAI API calls cost money, monitor usage

## 🎉 You're Ready!

You now have a fully functional Multi-Agent DevOps Incident Analysis Suite!

**Questions?** Check the main README.md or create an issue.

**Enjoying the app?** ⭐ Star the repo!

---

**Happy Analyzing! 🚀**

