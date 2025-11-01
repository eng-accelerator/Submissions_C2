# 🤖 Multi-Persona Chatbot with Export Functionality

**Part of [QUEST AND CROSSFIRE™](https://questandcrossfire.com)**

A professional, multi-session chatbot with AI persona switching, persistent storage, and conversation export capabilities. Built as part of the OutSkill AI Engineering Bootcamp 2025.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

---

## 📚 Project Context

This chatbot was developed as part of the **OutSkill AI Engineering Bootcamp 2025** to demonstrate proficiency in:
- Streamlit web application development
- OpenAI API integration
- Multi-persona AI system design
- Persistent data storage (JSON-based)
- File export functionality (TXT, JSON, CSV)
- Professional code documentation and best practices

---

## ✨ Features

### 🎭 **Multiple AI Personas**
Switch between four distinct personalities:
- **General Assistant** - Helpful, polite, and informative
- **Creative Poet** - Whimsical and artistic responses with metaphors
- **Technical Coder** - Precise, logical, code-focused answers
- **Sarcastic Robot** - Correct answers with humorous, weary tone

### 💬 **Multi-Session Chat Management**
- Create unlimited chat sessions
- Auto-save every message
- Load previous conversations instantly
- Delete old chats
- Auto-generated chat titles

### 📤 **Export Conversations**
Export any chat in three formats:
- **TXT** - Human-readable plain text
- **JSON** - Structured data with metadata
- **CSV** - Spreadsheet-compatible format

### ⚡ **Real-Time Streaming**
- Live "typing" effect as AI responds
- Smooth user experience
- Instant feedback

### 👍 **User Feedback System**
- Thumbs up/down for assistant responses
- Track response quality (decorative in current version)

### 💾 **Persistent Storage**
- JSON-based chat history
- Automatic saving after every message
- Timestamps for creation and updates

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Streamlit** | Web UI framework |
| **OpenAI API** | GPT model access |
| **OpenAI Python Library** | API client |
| **Python 3.8+** | Core language |
| **JSON** | Data persistence |
| **CSV** | Export format |

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/AsheeshSrivastava/quest-crossfire-chatbot.git
   cd quest-crossfire-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key**
   ```bash
   # Create .streamlit directory if it doesn't exist
   mkdir .streamlit

   # Copy the example secrets file
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml

   # Edit .streamlit/secrets.toml and add your OpenAI API key
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** to `http://localhost:8501`

---

## 🔑 API Key Setup

### **Get an OpenAI API Key**

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up for an account
3. Go to [API Keys](https://platform.openai.com/api-keys)
4. Create a new API key
5. Copy the key (starts with `sk-...`)

### **Add Key to Secrets**

**For Local Development:**
1. Create/edit `.streamlit/secrets.toml`
2. Add:
   ```toml
   OPENAI_API_KEY = "sk-your_key_here"
   ```

**For Streamlit Cloud Deployment:**
1. Deploy your app to Streamlit Cloud
2. Go to app settings → Secrets
3. Paste:
   ```toml
   OPENAI_API_KEY = "sk-your_key_here"
   ```

---

## 📖 Usage

### **Starting a New Chat**
1. Click "➕ New Chat" in the sidebar
2. Select a persona from the dropdown
3. Type your message in the chat input
4. Press Enter to send

### **Switching Personas**
1. Select a different persona from the sidebar dropdown
2. New messages will use the selected persona
3. Previous messages remain unchanged

### **Managing Chat History**
- **Load a chat**: Click on its title in the sidebar
- **Delete a chat**: Click the 🗑️ icon next to the chat
- **Active chat**: Indicated with 🟢 icon

### **Exporting Conversations**
1. Navigate to the chat you want to export
2. Scroll to "📤 Export Current Chat" in the sidebar
3. Click your preferred format:
   - **TXT**: Human-readable format
   - **JSON**: Structured data with metadata
   - **CSV**: Import into Excel/Google Sheets

### **Feedback System**
- Click 👍 for good responses
- Click 👎 for bad responses
- (Note: Feedback is stored but not persisted in current version)

---

## 📁 Project Structure

```
quest-crossfire-chatbot/
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── LICENSE                       # GPL-3.0 license
├── README.md                     # This file
├── .gitignore                    # Git ignore rules
├── .streamlit/
│   └── secrets.toml.example      # API key template
├── chat_history/                 # Saved chats (local only, gitignored)
│   └── chat_*.json               # Individual chat files
└── session_logs/                 # Development/deployment logs
    └── *.md                      # Session documentation
```

---

## 🎓 Educational Value

### **What This Project Demonstrates:**

**Technical Skills:**
1. ✅ Streamlit web app development
2. ✅ API integration (OpenAI)
3. ✅ Session state management
4. ✅ File I/O operations (JSON, CSV, TXT)
5. ✅ Real-time streaming responses
6. ✅ Multi-persona system architecture
7. ✅ Error handling and user feedback

**Professional Practices:**
1. ✅ Comprehensive code documentation
2. ✅ Proper project structure
3. ✅ Git version control
4. ✅ Open source licensing (GPL-3.0)
5. ✅ Transparent AI attribution
6. ✅ Deployment-ready code
7. ✅ User-focused design

---

## ⚠️ Known Limitations

### **Ephemeral Storage on Cloud Deployment**

**Issue:**
- Chat history is stored in local JSON files (`chat_history/` folder)
- On Streamlit Cloud, these files are **ephemeral** (lost on restart)
- All chat history will be deleted when the app restarts

**Workarounds:**
1. **Use export functionality** - Save important chats before shutdown
2. **Session-only usage** - Treat as temporary conversations
3. **Upgrade to persistent storage** - Implement database (future enhancement)

**For Bootcamp Submission:**
- This is acceptable for demonstration purposes
- Showcases file I/O skills
- Real production apps would use databases

---

## 🔮 Future Enhancements

### **Potential Improvements:**

1. **Persistent Cloud Storage**
   - Replace JSON files with database (PostgreSQL/SQLite)
   - Use cloud storage (AWS S3, Google Cloud Storage)

2. **Enhanced Feedback System**
   - Save feedback to database
   - Analytics dashboard
   - Use feedback to improve responses

3. **Additional Personas**
   - User-defined custom personas
   - Persona marketplace
   - Persona templates library

4. **Advanced Features**
   - Conversation search
   - Tagging system
   - Share conversations via URL
   - Multi-language support

5. **Analytics**
   - Usage statistics
   - Response time tracking
   - Token usage monitoring

---

## 🤝 Credits & Attribution

### **Project Development:**
- **Author**: Asheesh Ranjan Srivastava
- **Organization**: QUEST AND CROSSFIRE™
- **Date**: October 30, 2025

### **Learning & Support:**
- **Base Architecture**: OutSkill AI Engineering Bootcamp 2025
- **AI Assistance**: Gemini (Google) & Claude (Anthropic)
- **Implementation**: Original work by author
- **Persona System**: Original design and implementation
- **Export Functionality**: Original design and implementation

### **Technologies:**
- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI](https://openai.com/)
- AI model: GPT-3.5 Turbo

---

## 📄 License

This project is licensed under the **GPL-3.0 License** - see the [LICENSE](LICENSE) file for details.

**What this means:**
- ✅ You can use, modify, and distribute this code
- ✅ You can create commercial applications
- ⚠️ You must keep the same GPL-3.0 license
- ⚠️ You must credit QUEST AND CROSSFIRE™
- ⚠️ You cannot use QUEST AND CROSSFIRE™ branding

---

## 🏷️ Trademark Notice

**QUEST AND CROSSFIRE™** is a trademark.
Trademark filings in process.

While this code is open source (GPL-3.0), the QUEST AND CROSSFIRE™ brand name is a protected trademark. Please use your own branding when creating derivatives.

---

## 🚀 Deployment to Streamlit Cloud

### **Quick Deployment Steps:**

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Multi-Persona Chatbot"
   git remote add origin https://github.com/YOUR_USERNAME/quest-crossfire-chatbot.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Click "New app"
   - Select your repository
   - Branch: `main`
   - Main file: `app.py`

3. **Add Secrets**
   - In Advanced Settings → Secrets
   - Paste:
     ```toml
     OPENAI_API_KEY = "sk-your_key_here"
     ```

4. **Deploy!**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your app is live!

**Custom Subdomain:**
- Go to Settings → General → App URL
- Choose a custom subdomain (e.g., `quest-chatbot`)
- Your URL: `https://quest-chatbot.streamlit.app`

---

## 📞 Support & Contact

- **Organization**: [QUEST AND CROSSFIRE™](https://questandcrossfire.com)
- **GitHub Issues**: [Report a bug](https://github.com/YOUR_USERNAME/quest-crossfire-chatbot/issues)
- **Bootcamp**: OutSkill AI Engineering Bootcamp 2025

---

## 🎯 Bootcamp Submission Checklist

If you're using this as a template for your own bootcamp submission:

- [ ] Replace "YOUR_USERNAME" in README with your GitHub username
- [ ] Update .streamlit/secrets.toml with your actual API key
- [ ] Test all features locally
- [ ] Export sample conversation (include in submission)
- [ ] Document any challenges faced
- [ ] Optional: Deploy to Streamlit Cloud and include live URL

---

**Made with ❤️ by QUEST AND CROSSFIRE™**
*OutSkill AI Engineering Bootcamp 2025*

---

© 2025 QUEST AND CROSSFIRE™. Licensed under GPL-3.0.
