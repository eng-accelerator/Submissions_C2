# Personality Chatbot with Export Functionality - Challenge 3 - By Vibha T S

A multi-personality AI chatbot with conversation export capabilities.

# Loom video
https://www.loom.com/share/8876f8b482d546d480ae6cfd8f842e87


## What It Does

**Base Features:**
- 5 AI personalities (Professional, Creative, Technical, Friendly, Academic)
- Custom personality creator
- Multiple conversations management
- Multi-model support (GPT, Claude, Llama, Gemini)

**NEW: Export Feature**
- Export conversations in 3 formats: TXT, JSON, CSV
- One-click download with metadata
- Statistics included

---

## Quick Start

### 1. Install
```bash
pip install streamlit openai python-dotenv
```

### 2. Setup API Key
```bash
mkdir -p .streamlit
echo 'OPENROUTER_API_KEY = "sk-or-v1-YOUR-KEY"' > .streamlit/secrets.toml
```

### 3. Run
```bash
streamlit run personality_chatbot.py
```

---

## How to Export

1. **Chat** - Have a conversation
2. **Sidebar** - Scroll to "Export Chat" section
3. **Select Format** - Choose TXT, JSON, or CSV
4. **Export** - Click "Export Current Chat"
5. **Download** - Click download button

---

## Export Formats

### TXT - Human Readable
```
Chat Export - My Chat
========================
Session Information:
- Personality: Friendly Companion
- Total Messages: 6
- Export Date: 2024-11-01 15:30

[Message 1] You:
Hello!

[Message 2] Assistant:
Hi there! How can I help?
```

**Best for:** Documentation, sharing, reading

---

### JSON - Structured Data
```json
{
  "export_metadata": {
    "chat_title": "My Chat",
    "personality": "Technical Expert",
    "total_messages": 6
  },
  "conversation": [
    {
      "message_id": 1,
      "role": "user",
      "content": "Hello!",
      "word_count": 1
    }
  ],
  "statistics": {
    "user_messages": 3,
    "assistant_messages": 3,
    "total_characters": 450
  }
}
```

**Best for:** Data analysis, programming, backups

---

### CSV - Spreadsheet Format
```csv
Message_ID,Role,Content,Character_Count,Word_Count
1,user,"Hello!",6,1
2,assistant,"Hi there! How can I help?",27,6
```

**Best for:** Excel, data analysis, charts

---

## Features

### What's Included in Exports
- ✅ All conversation messages
- ✅ Chat title and personality
- ✅ Message counts
- ✅ Character and word counts
- ✅ Export timestamp
- ✅ Conversation statistics (JSON only)

### File Naming
Files are automatically named:
```
{ChatTitle}_{Personality}.{format}

Example: Python_Help_Technical_Expert.json
```

---

## Use Cases

| Use Case | Format | Why |
|----------|--------|-----|
| Share with team | TXT | Easy to read |
| Archive conversations | JSON | Complete data |
| Analyze patterns | CSV | Spreadsheet analysis |
| Documentation | TXT | Professional format |
| Training data | JSON | Machine-readable |
| Reports | TXT/CSV | Multiple formats |

---

## Requirements

```
streamlit>=1.28.0
openai>=1.3.0
python-dotenv>=1.0.0
```

---

## File Structure

```
personality-chatbot/
├── personality_chatbot.py      # Main app
├── requirements.txt            # Dependencies
└── .streamlit/
    └── secrets.toml           # API key (create this)
```

---

## Troubleshooting

**Export button disabled?**
- Start a conversation first

**Download not working?**
- Check browser download permissions
- Try a different browser

**Empty export file?**
- Ensure conversation has messages
- Try different export format

---

## Quick Commands

```bash
# Install
pip install -r requirements.txt

# Run
streamlit run personality_chatbot.py

# Export via code (if needed)
python -c "from personality_chatbot import export_as_json; print(export_as_json(messages, 'title', 'personality'))"
```

---

## What's Next?

After exporting:
- **TXT**: Open in any text editor
- **JSON**: Parse with Python, JavaScript, etc.
- **CSV**: Open in Excel/Google Sheets

---

## Get Your API Key

1. Visit https://openrouter.ai/
2. Sign up (free)
3. Go to "Keys" section
4. Create new key
5. Add to `.streamlit/secrets.toml`

---

## Support

- Check sidebar for "Export Chat" section
- Ensure conversation is active
- Select format before exporting
- File downloads to default browser folder
