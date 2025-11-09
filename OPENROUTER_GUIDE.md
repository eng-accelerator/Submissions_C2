# 🔑 OpenRouter Integration Guide

The Multi-Agent DevOps Incident Suite now supports **OpenRouter** for accessing multiple AI models!

## 🎯 Why OpenRouter?

### Access 100+ AI Models
- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo
- **Anthropic**: Claude 3 (Opus, Sonnet, Haiku)
- **Google**: Gemini Pro, Gemini Ultra
- **Meta**: Llama 3 (8B, 70B, 405B)
- **Mistral AI**: Mistral Large, Medium, Small
- **And many more!**

### Single API Key
- One key for all models
- No need to manage multiple accounts
- Easy switching between models

### Smart Routing
- Automatic failover
- Cost optimization
- Performance monitoring

## 🚀 Quick Setup

### 1. Get Your OpenRouter API Key

1. Go to: **https://openrouter.ai/keys**
2. Sign up or log in
3. Create a new API key
4. Copy the key (format: `sk-or-v1-xxxxx`)

### 2. Configure in the App

**In the Streamlit UI:**
1. Open **http://localhost:8502**
2. In the **sidebar**, check **"Use OpenRouter"**
3. Paste your OpenRouter API key
4. Done! ✅

**Or via Environment File:**
```bash
# Edit .env file
nano .env

# Set these values:
USE_OPENROUTER=true
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=openai/gpt-3.5-turbo
```

## 📋 Available Models

### Recommended for DevOps Analysis

| Model | Provider | Speed | Cost | Quality |
|-------|----------|-------|------|---------|
| `openai/gpt-3.5-turbo` | OpenAI | ⚡⚡⚡ | 💰 | ⭐⭐⭐ |
| `openai/gpt-4` | OpenAI | ⚡⚡ | 💰💰💰 | ⭐⭐⭐⭐⭐ |
| `anthropic/claude-3-sonnet` | Anthropic | ⚡⚡ | 💰💰 | ⭐⭐⭐⭐ |
| `google/gemini-pro` | Google | ⚡⚡⚡ | 💰 | ⭐⭐⭐⭐ |
| `meta-llama/llama-3-70b-instruct` | Meta | ⚡⚡ | 💰 | ⭐⭐⭐⭐ |

### Budget-Friendly Options

- `openai/gpt-3.5-turbo` - Best balance (default)
- `meta-llama/llama-3-8b-instruct` - Very cheap, good quality
- `google/gemini-pro` - Free tier available

### High-Quality Options

- `openai/gpt-4` - Best for complex analysis
- `anthropic/claude-3-opus` - Excellent reasoning
- `openai/gpt-4-turbo` - Faster GPT-4

## 🔧 Configuration Options

### Via Environment Variables

```bash
# Enable OpenRouter
USE_OPENROUTER=true

# Your API key
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Choose your model
OPENROUTER_MODEL=openai/gpt-3.5-turbo
# or
OPENROUTER_MODEL=anthropic/claude-3-sonnet
# or
OPENROUTER_MODEL=google/gemini-pro
```

### Via Code

```python
from config import Config

# Enable OpenRouter
Config.USE_OPENROUTER = True
Config.OPENROUTER_API_KEY = "sk-or-v1-xxxxx"
Config.OPENROUTER_MODEL = "openai/gpt-4"
```

## 💡 Usage Tips

### 1. Start with GPT-3.5 Turbo
- Fast and cheap
- Good for most incident analysis
- Our default configuration

### 2. Upgrade to GPT-4 for Complex Issues
- Better reasoning
- More accurate remediation plans
- Worth the extra cost for critical incidents

### 3. Try Claude for Different Perspective
- Excellent at explaining complex issues
- Good at step-by-step remediation
- Alternative if OpenAI is down

### 4. Use Gemini for Cost Efficiency
- Free tier available
- Good performance
- Great for testing

## 🔄 Switching Between OpenAI and OpenRouter

### In the UI
Simply **check/uncheck** the "Use OpenRouter" checkbox in the sidebar.

### In .env File
```bash
# Use OpenRouter
USE_OPENROUTER=true

# Or use OpenAI directly
USE_OPENROUTER=false
OPENAI_API_KEY=sk-your-openai-key
```

## 💰 Pricing

OpenRouter charges based on the model you use:

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| GPT-3.5 Turbo | $0.50 | $1.50 |
| GPT-4 | $30.00 | $60.00 |
| Claude 3 Sonnet | $3.00 | $15.00 |
| Gemini Pro | Free tier, then $0.50 | $1.50 |
| Llama 3 70B | $0.90 | $0.90 |

**Typical Analysis Cost:**
- Small log analysis (20 entries): $0.01 - $0.05
- Medium analysis (100 entries): $0.05 - $0.20
- Large analysis (500 entries): $0.20 - $1.00

## 🔒 Security

### API Key Safety
- Keys are stored in `.env` (not committed to git)
- Encrypted transmission to OpenRouter
- No logging of API keys

### Headers
The app automatically adds:
```python
{
    "HTTP-Referer": "https://github.com/devops-incident-suite",
    "X-Title": "DevOps Incident Analysis Suite"
}
```

## 🐛 Troubleshooting

### "Invalid API Key" Error
- Check key starts with `sk-or-v1-`
- Verify key at https://openrouter.ai/keys
- Make sure "Use OpenRouter" is checked

### "Model Not Found" Error
- Check model name is correct
- See full list: https://openrouter.ai/models
- Try default: `openai/gpt-3.5-turbo`

### Slow Response
- Some models are slower than others
- Try GPT-3.5 for faster results
- Check OpenRouter status page

### Rate Limiting
- OpenRouter has rate limits per model
- Add credits to your account
- Switch to different model if one is limited

## 📚 Resources

### OpenRouter
- **Website**: https://openrouter.ai
- **API Keys**: https://openrouter.ai/keys
- **Models**: https://openrouter.ai/models
- **Docs**: https://openrouter.ai/docs
- **Pricing**: https://openrouter.ai/pricing

### Model Comparisons
- **LLM Leaderboard**: https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard
- **Model Cards**: Check each provider's documentation

## 🎉 Benefits for This App

### Multi-Agent System
Each of the 5 agents can use any OpenRouter model:
1. **Log Reader** - Fast parsing with GPT-3.5
2. **Remediation** - Deep analysis with GPT-4
3. **Notification** - Formatting with Claude
4. **JIRA** - Ticket creation with Gemini
5. **Cookbook** - Documentation with Llama

### Flexibility
- Switch models without code changes
- A/B test different models
- Failover if one provider is down

### Cost Optimization
- Use cheap models for simple tasks
- Use premium models for complex analysis
- Monitor usage in OpenRouter dashboard

## 🚀 Advanced: Model Selection Strategy

```python
# In config.py or .env

# For budget-conscious usage
OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct

# For balanced performance
OPENROUTER_MODEL=openai/gpt-3.5-turbo  # Default

# For best quality
OPENROUTER_MODEL=openai/gpt-4

# For alternative provider
OPENROUTER_MODEL=anthropic/claude-3-sonnet
```

## 💬 Support

- **OpenRouter Support**: https://openrouter.ai/discord
- **App Issues**: Check README.md or create GitHub issue

---

**Ready to use OpenRouter? Get your key and start analyzing! 🎯**

