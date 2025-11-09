# AI Assistant Chatbot - Quick Guide

## Setup

### 1. Install Dependencies

```bash
cd BrowserTesting_latest
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file with:

```bash
# Required for AI Assistant
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: For web search
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_search_engine_id_here

# LLM Model
LLM_MODEL=anthropic/claude-3.5-sonnet
```

### 3. Run the Application

```bash
streamlit run main_Chatbot_latest.py
```

## Using the AI Assistant

### Access
Click the **🤖 AI Assistant** button next to "Generate & Run"

### Capabilities
- **Understand Features**: Ask about any agent or feature
- **Troubleshoot Issues**: Get help with errors and problems
- **Analyze Screenshots**: Upload images for visual analysis  
- **Read Documents**: Upload logs, scripts, configs
- **Web Search**: Find latest information (when enabled)

### Example Questions

**About Features:**
- "What agents are available?"
- "How does self-healing work?"
- "Explain the visual regression feature"

**Troubleshooting:**
- "My test failed, what should I check?"
- "How do I fix selector errors?"
- Upload a screenshot: "What's wrong with this error?"

**Usage:**
- "How do I test a login flow?"
- "Best practices for dynamic content?"

## Architecture

### Backend (chatbot_rag_backend.py)
- **LangGraph Workflow**: State machine for query processing
- **RAG System**: Context-aware responses with document retrieval
- **Multimodal**: Supports text, images, and documents
- **Web Search**: Google Custom Search API integration
- **Agent Analyzer**: Understands project capabilities

### Frontend (chatbot_ui.py)
- **File Upload**: Drag & drop images and documents
- **Chat Interface**: Conversation history with context
- **Source Citations**: Shows web search sources
- **Settings**: Toggle features, clear history

### Models Used
- **Chat**: anthropic/claude-3.5-sonnet (via OpenRouter)
- **Vision**: anthropic/claude-3.5-sonnet (multimodal)
- **Web Search**: Google Custom Search API

## Features in Detail

### 1. Multimodal Understanding

**Text Processing:**
- Natural language understanding
- Context-aware responses
- Conversation memory

**Image Analysis:**
- Screenshot analysis
- Error message recognition
- UI element identification
- Visual regression review

**Document Processing:**
- Log file analysis
- Script review
- Configuration understanding
- Code explanation

### 2. Agent Feature Knowledge

The chatbot understands all project agents:

- **Flow Discovery**: Maps user goals to test steps
- **Script Generator**: Creates Playwright code
- **Execution**: Runs tests and captures results
- **Error Diagnosis**: Analyzes failures
- **Adaptive Repair**: Self-healing test fixes
- **Visual Regression**: UI change detection

### 3. Web Search Integration

When enabled, searches the web for:
- Latest documentation
- Current best practices
- Error solutions
- Tool updates

### 4. Context-Aware Help

The assistant:
- Remembers conversation history
- Provides relevant follow-ups
- Suggests next steps
- Links related features

## File Upload Guide

### Supported Files

**Images** (for visual analysis):
- `.png`, `.jpg`, `.jpeg`, `.webp`
- Screenshots, error messages, UI elements

**Text Files** (for content analysis):
- `.txt` - Plain text logs
- `.md` - Documentation
- `.log` - Application logs

**Code Files** (for code review):
- `.py` - Python scripts
- `.js` - JavaScript
- `.html` - HTML pages
- `.css` - Stylesheets
- `.json` - Configuration

### How to Upload

1. Click **"Upload screenshots, logs, or documents"**
2. Select files (multiple allowed)
3. Files are automatically processed
4. Ask questions about uploaded content

## Troubleshooting

### Chatbot Not Available

**Error**: Button is disabled

**Solution**:
```bash
pip install langgraph langchain langchain-core
```

### API Key Errors

**Error**: "OPENROUTER_API_KEY not configured"

**Solution**:
1. Create `.env` file
2. Add `OPENROUTER_API_KEY=your_key`
3. Get key from https://openrouter.ai/

### Web Search Not Working

**Error**: "Google Search not configured"

**Solution**:
1. Add `GOOGLE_API_KEY` to `.env`
2. Add `GOOGLE_CSE_ID` to `.env`
3. See main README for setup guide

### Image Upload Issues

**Error**: Images not being analyzed

**Check**:
- File format is supported (.png, .jpg, .jpeg)
- File size is reasonable (< 10 MB)
- OPENROUTER_API_KEY is configured

## Technical Details

### LangGraph Workflow

```
User Query
    ↓
[Analyze Query]
    ↓
[Web Search] (if needed)
    ↓
[Process Documents] (if uploaded)
    ↓
[Generate Response]
    ↓
Response + Sources
```

### State Management

```python
ChatbotState = {
    "messages": [],           # Conversation history
    "context": "",            # Document context
    "web_search_results": [], # Search results
    "uploaded_files": [],     # File info
    "agent_features": {},     # Project capabilities
    "current_query": "",      # User question
    "response": ""            # AI response
}
```

### Model Selection

- **Text-only queries**: claude-3.5-sonnet
- **Image queries**: claude-3.5-sonnet (vision)
- Automatic model selection based on content

## Advanced Usage

### Custom Queries

**Analyze execution logs:**
```
Upload: execution.log
Ask: "Why did this test fail?"
```

**Review generated scripts:**
```
Upload: generated_test.py
Ask: "How can I improve this script?"
```

**Understand errors:**
```
Upload: error_screenshot.png
Ask: "What does this error mean?"
```

### Workflow Integration

**Before running tests:**
- Ask: "How should I structure my test goal?"
- Get: Best practices and examples

**After test failure:**
- Upload: Error screenshot
- Ask: "What went wrong?"
- Get: Diagnosis and solutions

**For optimization:**
- Upload: Current script
- Ask: "How can I make this more reliable?"
- Get: Improvement suggestions

## Best Practices

1. **Be Specific**: Ask clear, focused questions
2. **Provide Context**: Upload relevant files
3. **Enable Web Search**: For latest information
4. **Use Conversation**: Build on previous answers
5. **Review Sources**: Check web search citations

## Cost Information

### OpenRouter API
- GPT-3.5 Turbo: ~$0.001-0.002 per query
- GPT-4: ~$0.03-0.06 per query
- Claude 3.5 Sonnet: ~$0.015-0.03 per query

### Google Search (Optional)
- Free: 100 searches/day
- Paid: $5 per 1,000 additional

**Most usage stays within free tiers!**

## Files Created

- `chatbot_rag_backend.py` - RAG backend with LangGraph
- `chatbot_ui.py` - Streamlit UI component
- `main_Chatbot_latest.py` - Updated with chatbot button
- `requirements.txt` - Updated with dependencies
- `CHATBOT_README.md` - This file

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Configure `.env` file
3. Run: `streamlit run main_Chatbot_latest.py`
4. Click **🤖 AI Assistant** button
5. Start asking questions!

## Support

For issues or questions:
1. Use the AI Assistant itself!
2. Check main project README
3. Review agent documentation

---

**Built with:**
- LangGraph for workflow orchestration
- Claude 3.5 Sonnet for multimodal AI
- Google Custom Search for web search
- Streamlit for interactive UI
