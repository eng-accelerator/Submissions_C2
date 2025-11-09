# 🚂 Railway Deployment Guide

This guide explains how to deploy the Log Error Analyzer Streamlit app to Railway.

## 📋 Prerequisites

1. ✅ GitHub account with this repository pushed
2. ✅ Railway account (sign up at https://railway.com)
3. ✅ Your API keys ready:
   - OpenRouter API key (or OpenAI)
   - Slack webhook URL (optional)
   - JIRA credentials (optional)

## 🚀 Quick Deployment Steps

### Step 1: Connect Repository

1. Go to [Railway New Project](https://railway.com/new/github)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Authorize Railway to access your GitHub
4. Select repository: `ai-accelerator-group2`
5. Railway will auto-detect it's a Python app

### Step 2: Configure Environment Variables

In Railway dashboard → Your Project → **Variables** tab, add:

```env
# Required
OPENAI_API_KEY=your_openrouter_api_key_here

# Optional - Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Optional - JIRA Integration
JIRA_SERVER=https://yourcompany.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=PROJ
JIRA_ISSUE_TYPE=Task
```

**Note:** Railway automatically sets `PORT` - no need to configure it.

### Step 3: Deploy

Railway will automatically:
- ✅ Detect `requirements.txt` in root
- ✅ Use `Procfile` for start command
- ✅ Build and deploy your app
- ✅ Provide a public URL

Check the **Deployments** tab for build progress and logs.

## 📁 Files Created for Railway

### 1. `Procfile` (Root directory)
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```
- Tells Railway how to start the app
- Uses Railway's `$PORT` environment variable
- Runs in headless mode for production

### 2. `railway.json` (Root directory)
- Railway-specific deployment configuration
- Defines build and start commands
- Sets restart policy

### 3. `nixpacks.toml` (Root directory)
- Custom build configuration
- Specifies Python version (3.11)
- Defines install and start commands

### 4. `requirements.txt` (Root directory)
- All Python dependencies
- Railway will automatically install these

### 5. `.railwayignore` (Root directory)
- Files/directories to exclude from deployment
- Reduces build size and time

## ⚙️ Configuration Details

### Port Configuration
Railway automatically sets the `PORT` environment variable. The app is configured to:
- Use `$PORT` for the server port
- Bind to `0.0.0.0` (required for Railway)
- Run in headless mode (`--server.headless=true`)

### Environment Variables
The app uses `os.getenv()` which works with Railway's environment variables:
- ✅ No `.env` file needed in production
- ✅ Set all variables in Railway dashboard
- ✅ Variables are automatically available to the app

### File Structure
```
ai-accelerator-group2/
├── Procfile                    # Railway start command
├── railway.json               # Railway config
├── nixpacks.toml              # Build config
├── requirements.txt            # Dependencies
├── .railwayignore             # Ignore patterns
├── app.py                     # Main Streamlit app
├── error_analyzer.py
├── notification_agents.py
├── agents/                    # Multi-agent framework
│   ├── __init__.py
│   ├── agent_orchestrator.py
│   ├── error_classification_agent.py
│   ├── solution_agent.py
│   └── notification_agent.py
└── .gitignore
```

## 🔍 Verification Checklist

Before deploying, ensure:

- [x] `requirements.txt` is in root directory
- [x] `Procfile` exists with correct path to `app.py`
- [x] All environment variables are set in Railway dashboard
- [x] No hardcoded paths that won't work in production
- [x] `.gitignore` excludes `.env` files (use Railway variables instead)

## 🐛 Troubleshooting

### Build Fails
**Problem:** Build fails during dependency installation
- **Solution:** Check Railway build logs for specific package errors
- Verify all packages in `requirements.txt` are valid
- Check Python version compatibility

### App Doesn't Start
**Problem:** Deployment succeeds but app doesn't load
- **Solution:** 
  - Check Railway logs for errors
  - Verify `Procfile` path is correct: `app.py`
  - Ensure PORT is being used (Railway sets it automatically)

### Import Errors
**Problem:** ModuleNotFoundError in logs
- **Solution:**
  - Verify `requirements.txt` includes all dependencies
  - Check that `agents/` directory is included in deployment
  - Ensure all imports use relative paths correctly

### Environment Variables Not Working
**Problem:** App can't find API keys
- **Solution:**
  - Verify variables are set in Railway → Variables tab
  - Check variable names match exactly (case-sensitive)
  - Restart deployment after adding variables
  - The app uses `os.getenv()` which works with Railway's env vars

### Port Already in Use
**Problem:** Port binding errors
- **Solution:** Railway handles this automatically via `$PORT` variable
- Don't hardcode port numbers

## 📊 Monitoring

### View Logs
1. Go to Railway dashboard
2. Select your project
3. Click **Deployments** tab
4. Select a deployment
5. View **Logs** tab for real-time logs

### Metrics
- Monitor CPU, Memory, and Network usage in **Metrics** tab
- Set up alerts if needed

## 🔄 Updating the App

### Automatic Deployment
Railway automatically redeploys when you:
- Push to the connected GitHub branch
- Merge pull requests (if configured)

### Manual Redeploy
1. Go to Railway dashboard
2. Select your project
3. Click **Deployments**
4. Click **Redeploy** on latest deployment

## 🌐 Custom Domain (Optional)

1. Go to Railway project → **Settings** → **Domains**
2. Click **"Generate Domain"** or **"Add Custom Domain"**
3. Follow DNS configuration instructions
4. Railway provides SSL certificates automatically

## 📝 Important Notes

1. **No `.env` file needed**: Railway uses environment variables from the dashboard
2. **Port is automatic**: Railway sets `$PORT`, don't hardcode it
3. **Headless mode**: Streamlit runs in headless mode for production
4. **File paths**: All files are in root directory, `app.py` is the entry point
5. **Dependencies**: All in root `requirements.txt`

## 🎯 Quick Start Command Reference

If you need to test locally with Railway-like settings:

```bash
# Set PORT (Railway does this automatically)
export PORT=8501

# Run with Railway-like settings
streamlit run app.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true
```

## ✅ Success Indicators

After deployment, you should see:
- ✅ Build completes successfully
- ✅ Deployment shows "Active" status
- ✅ Public URL is available
- ✅ App loads in browser
- ✅ No errors in Railway logs

## 🔗 Useful Links

- [Railway Documentation](https://docs.railway.app/)
- [Streamlit Deployment Guide](https://docs.streamlit.io/deploy)
- [Railway Status](https://status.railway.app/)

---

**Ready to deploy?** Go to https://railway.com/new/github and connect your repository!
