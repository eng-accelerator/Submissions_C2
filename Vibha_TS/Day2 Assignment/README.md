# Vibha_TS - Day 2 Assignment - Customize Streamlit Chatbot using models from openrouter

# 💬 ChatBot - Multi-Model AI Assistant

A chatbot application built with Streamlit that supports multiple AI models through OpenRouter. Features include conversation management, chat history and conversation summarization.

# Loom Video
https://www.loom.com/share/64edc40b690a4c13895b155a16bec78b 


## ✨ Features

- 🤖 **Multiple AI Models**: Support for GPT-4, Claude, Gemini, and Llama models via OpenRouter
- 💾 **Chat History**: Create, save, and manage multiple conversation threads
- 📝 **Conversation Summaries**: Generate AI-powered summaries of entire conversations
- 🌙 **Dark Theme**: Modern, eye-friendly dark UI design
- 💬 **Streaming Responses**: Real-time streaming of AI responses
- 🔄 **Easy Chat Switching**: Switch between different conversations seamlessly
- 🗑️ **Chat Management**: Delete individual chats or clear current conversation

## 📋 Prerequisites

- Python 3.8 or higher
- OpenRouter API key ([Get one here](https://openrouter.ai/))

## 🚀 Installation

### 1. Clone or Download the Repository

```bash
git clone <your-repo-url>
cd assignment2
```

### 2. Install Required Packages

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install streamlit openai
```

### 3. Set Up OpenRouter API Key

You have two options:

#### Option A: Using Streamlit Secrets (Recommended)

1. Create a `.streamlit` folder in the project directory
2. Create a `secrets.toml` file inside `.streamlit/`
3. Add your API key:

```toml
OPENROUTER_API_KEY = "sk-or-v1-your-api-key-here"
```

#### Option B: Using Environment Variable

**Linux/Mac:**
```bash
export OPENROUTER_API_KEY="sk-or-v1-your-api-key-here"
```

**Windows Command Prompt:**
```cmd
set OPENROUTER_API_KEY="sk-or-v1-your-api-key-here"
```

**Windows PowerShell:**
```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-your-api-key-here"
```

## 🎮 Usage

### Running the Application

```bash
streamlit run chat_app.py
```

The application will open automatically in your default browser at `http://localhost:8501`

### Using Different Models

The application supports the following models:
- `openai/gpt-4o-mini` (Default - Fast and cost-effective)
- `openai/gpt-4o` (Most capable GPT-4 model)
- `anthropic/claude-3.5-sonnet` (Claude's latest model)
- `anthropic/claude-3-opus` (Claude's most capable model)
- `google/gemini-pro-1.5` (Google's Gemini)
- `meta-llama/llama-3.1-70b-instruct` (Open source Llama)

Select your preferred model from the **Settings** section in the sidebar.

## 📁 Project Structure

```
assignment2/
├── .streamlit/
│   └── secrets.toml          # API keys (create this)
├── chat_history/              # Created automatically for exports
├── chat_app.py               # Main application file
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🎯 Features Guide

### Creating a New Chat
1. Click the **➕ New Chat** button in the sidebar
2. Your previous chat will be automatically saved

### Switching Between Chats
1. View all your chats in the **Chat History** section
2. Click on any chat to load it
3. The current chat is marked with a 🟢 green indicator

### Deleting a Chat
1. Click the 🗑️ button next to any chat in the history
2. Note: You cannot delete the only remaining chat

### Generating a Summary
1. Open the **📋 Summarize Conversation** expander
2. Click **Generate Summary**
3. The AI will create a concise summary of the entire conversation

### Clearing Current Chat
1. Go to **Settings** in the sidebar
2. Click **🗑️ Clear Current Chat**
3. This clears all messages in the current conversation

## 🔧 Configuration

### Customizing the UI

You can modify the CSS in the `st.markdown()` section at the top of `chat_app.py` to change:
- Background colors
- Button styles
- Text colors
- Border radius
- Spacing

### Adding More Models

To add more models, edit the `model_option` selectbox in the sidebar:

```python
model_option = st.selectbox(
    "Select Model",
    [
        "openai/gpt-4o-mini",
        "your-new-model/name-here",  # Add here
    ],
    index=0,
    key="model_selector"
)
```


## 🐛 Troubleshooting

### API Key Errors
- **Error**: `OpenRouter API key not found`
  - **Solution**: Make sure your `secrets.toml` file is in the correct location: `.streamlit/secrets.toml`
  - Check that the key name is exactly `OPENROUTER_API_KEY`

### Invalid API Key
- **Error**: `Error code: 401 - invalid_api_key`
  - **Solution**: Verify your API key is correct at [OpenRouter Dashboard](https://openrouter.ai/keys)
  - Make sure you have credits in your OpenRouter account

### Port Already in Use
- **Error**: Port 8501 is already in use
  - **Solution**: Run with a different port:
    ```bash
    streamlit run chat_app.py --server.port 8502
    ```

### Module Not Found
- **Error**: `ModuleNotFoundError: No module named 'streamlit'`
  - **Solution**: Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## 💡 Tips

- Use **GPT-4o-mini** for quick, cost-effective responses
- Use **Claude 3.5 Sonnet** for creative writing and analysis
- Use **GPT-4o** for complex reasoning tasks
- Chat history persists only during your session (not saved to disk)
- First message in each chat becomes the chat title


