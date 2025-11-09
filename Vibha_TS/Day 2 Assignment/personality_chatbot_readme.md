# Personality Chatbot 🤖 - Challenge 2 - By Vibha T S

A sophisticated multi-personality AI chatbot built with Streamlit and OpenRouter API. Switch between distinct AI personalities on-the-fly, create custom personalities, and maintain separate conversation histories for each persona.

# Loom video
https://www.loom.com/share/bc88f44e42e242c98acd4ccceeec1fc1 


## ✨ Key Features

### 🎭 Multiple AI Personalities

Choose from **5 pre-built personalities**, each with unique communication styles:

| Personality | Style | Best For |
|------------|-------|----------|
| **Professional Business Assistant** | Formal, structured, results-oriented | Business strategy, professional communication, management advice |
| **Creative Writing Helper** | Imaginative, expressive, inspiring | Storytelling, creative projects, brainstorming ideas |
| **Technical Expert** | Precise, analytical, code-focused | Programming help, debugging, technical problem-solving |
| **Friendly Companion** | Casual, empathetic, supportive | General chat, emotional support, casual advice |
| **Academic Scholar** | Scholarly, research-oriented, rigorous | Research analysis, academic writing, critical thinking |

### 🔧 Custom Personality Creator

- **Define your own AI personas** with custom system prompts
- **Save and reuse** custom personalities across sessions
- **Persistent storage** - custom personalities survive app restarts
- **Flexible system prompts** - full control over AI behavior

### 💬 Advanced Conversation Management

- **Multiple concurrent chats** - maintain separate conversations
- **Chat history** - view and switch between past conversations
- **Auto-titling** - chats automatically named from first message
- **Personality tracking** - each chat remembers its personality
- **Seamless switching** - change personalities mid-conversation

### 🎨 Modern UI/UX

- **Dark theme** - easy on the eyes
- **Responsive design** - works on desktop and mobile
- **Real-time streaming** - see responses as they're generated
- **Visual indicators** - clear current personality display
- **Clean interface** - no emoji clutter, universal compatibility

### 🔌 Multi-Model Support

Compatible with multiple AI providers through OpenRouter:

- **OpenAI**: GPT-3.5 Turbo, GPT-4o Mini, GPT-4o
- **Anthropic**: Claude 3 Haiku
- **Meta**: Llama 3.1 8B Instruct
- **Google**: Gemini Flash 1.5

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenRouter API key ([Get one here](https://openrouter.ai/))

### Installation

1. **Clone or download the files**
   ```bash
   # Place personality_chatbot.py in your project directory
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit openai python-dotenv
   ```

3. **Set up your API key**
   ```bash
   # Create .streamlit directory
   mkdir -p .streamlit
   
   # Create secrets file
   echo 'OPENROUTER_API_KEY = "sk-or-v1-YOUR-KEY-HERE"' > .streamlit/secrets.toml
   ```

4. **Run the application**
   ```bash
   streamlit run personality_chatbot.py
   ```

5. **Open in browser**
   - App automatically opens at `http://localhost:8501`

---

## 📖 How to Use

### Basic Usage

1. **Select a Personality** from the sidebar dropdown
2. **Type your message** in the chat input at the bottom
3. **View the response** - AI responds in the selected personality style
4. **Switch personalities** anytime to get different perspectives

### Creating Custom Personalities

1. Click **"Create Custom Personality"** in the sidebar
2. Enter a **Personality Name** (e.g., "Motivational Coach")
3. Write a **System Prompt** defining the personality:
   ```
   You are a motivational coach who inspires people to achieve their goals.
   Your style is energetic, positive, and action-oriented.
   Always provide practical steps and encourage persistence.
   ```
4. Click **"Save Custom Personality"**
5. Your custom personality appears in the dropdown!

### Managing Conversations

- **New Chat**: Click "+ New Chat" to start fresh
- **Switch Chats**: Click any chat in history to load it
- **Delete Chat**: Click "X" next to a chat to remove it
- **Clear Chat**: Use "Clear Current Chat" to erase current conversation

### Changing Models

1. Go to **Settings** in sidebar
2. Select from available models
3. Model applies to all new messages

---

## 🏗️ Technical Architecture

### Core Components

```
personality_chatbot.py
├── Configuration
│   ├── Page setup (Streamlit config)
│   ├── Custom CSS (dark theme styling)
│   └── Personality definitions (PERSONALITIES dict)
│
├── OpenRouter Integration
│   ├── Client initialization (@st.cache_resource)
│   ├── API key validation
│   └── Connection error handling
│
├── Helper Functions
│   ├── create_new_chat() - Initialize new conversation
│   ├── load_chat() - Restore conversation with personality
│   ├── save_current_chat() - Persist chat state
│   ├── delete_chat() - Remove conversation
│   ├── update_chat_title() - Auto-title from first message
│   ├── get_all_chats() - Retrieve sorted chat list
│   └── chat_with_personality() - Send messages with system prompt
│
├── Session State Management
│   ├── conversations - All chat histories
│   ├── current_chat_id - Active conversation
│   ├── messages - Current chat messages
│   ├── current_personality - Active personality
│   ├── model_choice - Selected AI model
│   └── custom personalities - User-created personas
│
├── User Interface
│   ├── Sidebar
│   │   ├── Personality selector
│   │   ├── Personality details
│   │   ├── Custom personality creator
│   │   ├── Conversation management
│   │   ├── Chat history
│   │   └── Settings
│   │
│   └── Main Area
│       ├── Personality badge (current selection)
│       ├── Info expander (help section)
│       ├── Chat message display
│       └── Chat input field
│
└── Message Processing
    ├── User input capture
    ├── Message history management
    ├── API request with system prompt
    ├── Streaming response display
    └── Error handling
```

### Data Structures

#### Personality Object
```python
{
    "description": str,      # Brief description of style
    "expertise": str,        # Areas of knowledge
    "tone": str,            # Communication tone
    "system_prompt": str,   # Full system instructions
    "example": str          # Sample response
}
```

#### Chat Object
```python
{
    "chat_id": str,         # Unique identifier
    "title": str,           # Chat title (from first message)
    "messages": list,       # Message history
    "personality": str,     # Personality used
    "created_at": str       # ISO timestamp
}
```

#### Message Object
```python
{
    "role": str,           # "user" or "assistant"
    "content": str         # Message text
}
```

### System Prompt Engineering

Each personality uses a carefully crafted system prompt that defines:

1. **Role Definition** - Who the AI is
2. **Communication Style** - How it should speak
3. **Behavioral Guidelines** - What to always do
4. **Response Format** - Structure preferences
5. **Constraints** - What to avoid

**Example**:
```python
"system_prompt": """You are a Professional Business Assistant.

Your communication style is:
- Formal and structured
- Clear and concise
- Results-oriented

Always:
- Start with a clear summary
- Use numbered lists for action items
- Provide professional advice

Format responses professionally."""
```

### Message Flow

```
User Input
    ↓
Add to messages list
    ↓
Update chat title (if first message)
    ↓
Prepare API request
    ├── Get personality system prompt
    ├── Prepend as system message
    └── Add conversation history
    ↓
Send to OpenRouter API
    ├── Stream response chunks
    ├── Display with typing indicator
    └── Handle errors
    ↓
Add response to messages
    ↓
Save chat state
```

---

## 🔒 Security & Privacy

### API Key Protection

- ✅ Keys stored in `.streamlit/secrets.toml` (gitignored)
- ✅ Keys never exposed in UI or logs
- ✅ Validation before API calls
- ✅ Cached client initialization

### Data Storage

- ✅ **All data stored locally** in Streamlit session state
- ✅ **No external database** - conversations exist only in session
- ✅ **No cloud storage** - everything stays on your machine
- ✅ **Clears on browser close** - unless explicitly saved

### Best Practices

```bash
# Add to .gitignore
.streamlit/secrets.toml
*.pyc
__pycache__/
.env
```

---

## ⚙️ Configuration Options

### Model Selection

Edit available models in the code:

```python
model_option = st.selectbox(
    "Select Model",
    [
        "openai/gpt-3.5-turbo",      # Fast, cost-effective
        "openai/gpt-4o-mini",        # Balanced
        "openai/gpt-4o",             # Most capable
        "anthropic/claude-3-haiku",  # Fast Claude
        "meta-llama/llama-3.1-8b-instruct:free",  # Free option
        "google/gemini-flash-1.5"    # Google's model
    ]
)
```

### Temperature & Token Limits

Adjust in `chat_with_personality()`:

```python
response = client.chat.completions.create(
    model=model,
    messages=full_messages,
    temperature=0.7,      # Creativity (0.0-1.0)
    max_tokens=2000,      # Response length limit
    stream=True
)
```

### Custom CSS Styling

Modify the dark theme colors:

```python
st.markdown("""
<style>
    .stApp {
        background-color: #1e1e1e;  # Main background
    }
    .stButton>button {
        background-color: #9c27b0;  # Button color
    }
</style>
""", unsafe_allow_html=True)
```

---

## 🐛 Troubleshooting

### Common Issues

#### "API key not found"
**Solution**: Check `.streamlit/secrets.toml` exists and contains:
```toml
OPENROUTER_API_KEY = "sk-or-v1-your-key"
```

#### "Invalid API key format"
**Solution**: Ensure key starts with `sk-or-v1-`

#### "ValueError: personality not in list"
**Solution**: Already fixed! The app now handles missing personalities gracefully.

#### Slow responses
**Solution**: 
- Try a faster model (GPT-3.5 Turbo or Gemini Flash)
- Check your internet connection
- Verify OpenRouter service status

#### Chat history not persisting
**Solution**: 
- Chats only persist during session
- Use "New Chat" to save current before closing
- Session clears on browser close (by design)

---

## 📊 Performance Optimization

### Caching Strategy

```python
@st.cache_resource
def get_openrouter_client():
    """Client initialized once and reused"""
    return OpenAI(...)
```

### Session State Management

- **Minimal recomputation** - only updates on user actions
- **Efficient chat loading** - direct dictionary access
- **Lazy evaluation** - personalities loaded on demand

### API Efficiency

- **Streaming responses** - better UX, no timeout waiting
- **Conversation context** - only sends necessary history
- **Error recovery** - graceful degradation on failures

---

## 🔮 Future Enhancements

### Potential Features

- [ ] **Export conversations** - Download as JSON/Markdown
- [ ] **Personality templates** - Pre-built custom personality examples
- [ ] **Voice input/output** - Speech integration
- [ ] **Personality mixing** - Combine traits from multiple personas
- [ ] **Conversation search** - Find past discussions
- [ ] **Chat analytics** - Usage statistics and insights
- [ ] **Cloud sync** - Save conversations to cloud storage
- [ ] **Shareable personalities** - Export/import personality configs
- [ ] **RAG integration** - Connect to knowledge bases
- [ ] **Multi-language support** - Personality translations

### Advanced Modifications

#### Add a new personality:
```python
PERSONALITIES["Your Personality"] = {
    "description": "Brief description",
    "expertise": "Areas of expertise",
    "tone": "Communication tone",
    "system_prompt": """Detailed system instructions...""",
    "example": "Example response"
}
```

#### Implement conversation export:
```python
def export_conversation():
    chat_data = st.session_state.conversations[st.session_state.current_chat_id]
    json_str = json.dumps(chat_data, indent=2)
    st.download_button(
        label="Download Conversation",
        data=json_str,
        file_name=f"{chat_data['title']}.json",
        mime="application/json"
    )
```

#### Add conversation search:
```python
def search_conversations(query):
    results = []
    for chat_id, chat_data in st.session_state.conversations.items():
        for message in chat_data['messages']:
            if query.lower() in message['content'].lower():
                results.append((chat_id, chat_data['title'], message))
    return results
```

---

## 📝 Code Quality

### Error Handling

- ✅ **API failures** - Graceful error messages, no crashes
- ✅ **Missing personalities** - Auto-restoration with placeholders
- ✅ **Invalid inputs** - Validation and user feedback
- ✅ **Network issues** - Clear error reporting

### Safe Dictionary Access

All personality access uses `.get()` with fallbacks:
```python
current_p = PERSONALITIES.get(
    selected_personality, 
    default_personality_dict
)
description = current_p.get('description', 'N/A')
```

### Type Safety

Clear type expectations in docstrings:
```python
def load_chat(chat_id: str) -> dict:
    """Load a chat conversation
    
    Args:
        chat_id: Unique chat identifier
        
    Returns:
        dict: Chat data or None
    """
```

---

## 🤝 Contributing

### How to Extend

1. **Add personalities** - Extend PERSONALITIES dict
2. **Modify UI** - Update Streamlit components
3. **Change models** - Add to model selector
4. **Enhance features** - Follow existing patterns

### Code Style

- Clear function names
- Comprehensive docstrings
- Logical component separation
- Consistent formatting

---

## 📄 License

MIT License - Free to use, modify, and distribute

---

## 🙏 Credits

Built with:
- **Streamlit** - UI framework
- **OpenRouter** - Unified AI API
- **OpenAI Python SDK** - API client

---

## 📧 Support

Having issues? Check:
1. This README troubleshooting section
2. `EMOJI_FREE_SUMMARY.md` - UI compatibility
3. `CUSTOM_PERSONALITY_FIX.md` - Personality handling
4. OpenRouter documentation: https://openrouter.ai/docs

---

## 🎯 Use Cases

### Professional
- **Business consulting** - Get structured business advice
- **Technical debugging** - Solve programming problems
- **Academic research** - Analyze complex topics

### Creative
- **Story writing** - Brainstorm plot ideas
- **Content creation** - Generate creative content
- **Problem solving** - Think outside the box

### Personal
- **Learning** - Get explanations in different styles
- **Decision making** - See multiple perspectives
- **Casual chat** - Friendly conversation
