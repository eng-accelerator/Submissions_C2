# 🚀 Streamlit Chatbot Assistant

A feature-rich chatbot interface built with Streamlit, featuring configurable settings, session statistics, and chat management capabilities.

## 📋 Prerequisites

1. **Streamlit** >= 1.28.0
2. **Python** >= 3.7
3. **pip** package manager
4. **VSCode** (recommended IDE)

## ✨ Features

### 💬 Chat Interface
- Interactive chat messages with user and assistant roles
- Real-time message display
- Clean, modern dark-themed UI

### ⚙️ Sidebar Configuration
- **Assistant Settings**
  - Customizable assistant name
  - Response style selection (Friendly, Professional, Casual, Technical, Humorous)
  
- **Chat Settings**
  - Adjustable max chat history (10-100 messages)
  - Toggle timestamps on/off
  - Real-time configuration updates

### 📊 Session Stats
- **Session Duration**: Live tracking of session time
- **Messages Sent**: Count of user messages
- **Total Messages**: Count of all messages (user + assistant)
- Auto-refreshing statistics

### 🎯 Actions
- **Clear Chat**: Reset the entire conversation and session stats
- **Export Chat**: Download conversation history as a `.txt` file with:
  - Timestamp of export
  - Assistant configuration details
  - Complete message history
  - Optional timestamps per message

### 📝 Additional Features
- "About This Demo" expandable section
- "Instructor Notes" with technical details
- Automatic message history management
- Session state persistence

## 🚀 Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

Or install Streamlit directly:
```bash
pip install streamlit>=1.28.0
```

## ▶️ Running the Application

1. **Navigate to the project directory**:
```bash
cd /Users/psaravanan/Downloads/outskill/Test
```

2. **Run the Streamlit app**:
```bash
streamlit run app.py
```

3. **Access the application**:
   - The app will automatically open in your default browser
   - Default URL: `http://localhost:8501`

## 🎮 Usage

1. **Configure the Assistant** (Sidebar):
   - Enter a custom assistant name
   - Select your preferred response style
   - Adjust max chat history limit
   - Toggle timestamps on/off

2. **Start Chatting**:
   - Type your message in the chat input at the bottom
   - Press Enter to send
   - The assistant will respond based on the selected response style

3. **Monitor Session Stats**:
   - View live session duration in the sidebar
   - Track message counts

4. **Manage Your Chat**:
   - Click "🗑️ Clear Chat" to start fresh
   - Click "📥 Export Chat" to download conversation as `.txt` file

## 📁 Project Structure

```
Test/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🛠️ Technical Details

### Session State Variables
- `messages`: List of chat messages with role, content, and timestamp
- `session_start_time`: DateTime when session started
- `message_count`: Total number of messages
- `user_message_count`: Number of user messages
- `assistant_name`: Customizable assistant name
- `response_style`: Selected response style
- `max_history`: Maximum number of messages to keep
- `show_timestamps`: Boolean for timestamp display

### Key Components
- **Streamlit Chat Components**: Native chat message display
- **Session State Management**: Persistent data across reruns
- **Real-time Updates**: Auto-refreshing session stats
- **File Export**: Dynamic text file generation
- **Responsive UI**: CSS-styled modern interface

## 🎨 Customization

### Modify Response Styles
Edit the `style_responses` dictionary in `app.py`:
```python
style_responses = {
    "Friendly": "Your friendly response template...",
    "Professional": "Your professional response template...",
    # Add more styles here
}
```

### Change Theme Colors
Modify the CSS in the `st.markdown()` section of `app.py`.

### Adjust History Limits
Change the slider range in the Chat Settings section:
```python
max_history = st.slider(
    "Max Chat History:",
    min_value=10,
    max_value=200,  # Increase maximum
    value=40
)
```

## 🔧 Troubleshooting

### Issue: App won't start
- Ensure Streamlit is installed: `pip install streamlit`
- Check Python version: `python --version` (should be >= 3.7)

### Issue: Messages disappear
- This is expected when history exceeds max_history setting
- Increase max_history slider value in sidebar

### Issue: Export button not showing
- Ensure you have sent at least one message
- Export button only appears when messages exist

## 📝 Future Enhancements

- Integration with AI models (OpenAI, Anthropic, etc.)
- Message search functionality
- Chat history persistence (database)
- Multiple chat sessions
- File upload capability
- Voice input/output
- Multi-language support

## 📄 License

This project is open source and available for educational purposes.

## 👨‍💻 Author

Created as a demo chatbot interface using Streamlit.

---

**Note**: This is a demo application with simulated responses. To integrate with real AI models, connect to APIs like OpenAI, Anthropic Claude, or other LLM services.

