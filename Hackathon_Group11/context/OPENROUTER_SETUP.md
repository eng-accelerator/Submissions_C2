# OpenRouter Setup Guide

## What is OpenRouter?

OpenRouter is a unified API that provides access to multiple LLM providers through a single interface. This allows you to:
- Use models from OpenAI, Anthropic, Google, Meta, and more
- Switch between models easily
- Access models at competitive pricing
- Use a single API key for all providers

## Setup Instructions

### 1. Get Your API Key

1. Visit https://openrouter.ai/keys
2. Sign up or log in
3. Create a new API key
4. Copy your key (starts with `sk-or-`)

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
OPEN_ROUTER_KEY=sk-or-your-key-here
```

### 3. Model Selection

The system uses OpenRouter's model format. Edit `utils/llm_config.py` to change models:

**Popular Models:**
- `openai/gpt-4-turbo-preview` - OpenAI GPT-4 Turbo (default)
- `openai/gpt-3.5-turbo` - Faster, cheaper option
- `anthropic/claude-3-opus` - Anthropic's most capable model
- `anthropic/claude-3-sonnet` - Balanced performance
- `google/gemini-pro` - Google's Gemini model
- `meta-llama/llama-2-70b-chat` - Open-source option

**Full Model List:** https://openrouter.ai/models

### 4. Model Configuration

Edit `utils/llm_config.py`:

```python
# Default models (OpenRouter format)
DEFAULT_MODEL = "openai/gpt-4-turbo-preview"
ANALYZER_MODEL = "openai/gpt-4-turbo-preview"  # Analysis agent
INSIGHT_MODEL = "openai/gpt-4-turbo-preview"   # Insight generation
REPORT_MODEL = "openai/gpt-4-turbo-preview"    # Report building
```

You can use different models for different agents:
- Use `gpt-3.5-turbo` for faster, cheaper operations
- Use `claude-3-opus` for better reasoning
- Use `gpt-4-turbo` for best overall performance

## Benefits for Hackathon

1. **Cost Effective**: OpenRouter often has better pricing than direct APIs
2. **Flexibility**: Easy to switch models if one is down
3. **Reliability**: Multiple provider fallbacks
4. **Access**: Some models available without waitlists

## Testing

Run the test script to verify configuration:

```bash
python test_system.py
```

You should see:
```
✅ OpenRouter API key configured
   Using OpenRouter endpoint: https://openrouter.ai/api/v1
```

## Troubleshooting

**Invalid API Key:**
- Verify key starts with `sk-or-`
- Check key is active at https://openrouter.ai/keys
- Ensure no extra spaces in `.env` file

**Model Not Found:**
- Check model name format (must include provider, e.g., `openai/gpt-4-turbo-preview`)
- Verify model is available at https://openrouter.ai/models
- Some models may require credits or special access

**Rate Limits:**
- OpenRouter has rate limits based on your plan
- Free tier has lower limits
- Consider using faster/cheaper models for testing

## Cost Optimization

For hackathon demos, consider:
- Using `gpt-3.5-turbo` for faster responses
- Caching results (demo mode) to avoid repeated API calls
- Using cheaper models for less critical operations

---

**Ready to use OpenRouter!** 🚀

