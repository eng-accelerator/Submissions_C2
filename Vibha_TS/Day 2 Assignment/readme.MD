# 🌍 Translation Assistant - Challenge 1 - By Vibha T S

An intelligent translation chatbot built with Streamlit and OpenRouter that provides automatic language detection, high-quality translations, cultural context, and comprehensive translation tracking.

# Loom video
https://www.loom.com/share/d72d95a7e2274eb4a162c11e28da80a1

## ✨ Features

### Core Features
- ✅ **Automatic Language Detection** - Detects input language automatically
- ✅ **Multi-Language Translation** - 20+ supported languages
- ✅ **Bidirectional Translation** - Translate in both directions seamlessly
- ✅ **Dual Mode Operation** - Translation mode and conversation mode

### Advanced Features
- 🌟 **Alternative Translations** - Multiple translation options when relevant
- 💡 **Cultural Context** - Cultural notes for idioms and expressions
- ✨ **Confidence Scoring** - High/Medium/Low confidence levels
- 📊 **Translation History** - Track up to 50 recent translation pairs
- 📥 **Export History** - Download translation history as JSON
- 📈 **Analytics Dashboard** - Statistics on your translations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Streamlit
- OpenAI Python SDK
- OpenRouter API key

### Installation

1. **Clone or download the project**

2. **Install dependencies**
```bash
pip install streamlit openai
```

3. **Set up your API key**

Create `.streamlit/secrets.toml`:
```toml
OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
```

4. **Run the app**
```bash
streamlit run translation_app.py
```

## 📖 How to Use

### Translation Mode

1. **Select target language** from the sidebar
2. **Type any text** in any language
3. **Get instant translation** with:
   - Detected source language
   - Confidence score
   - Main translation
   - Alternative translations (when available)
   - Cultural notes (when relevant)
   - Formality level

### Reverse Translation (Bidirectional)

After translating text, simply type:
- `"translate back"`
- `"translate it back"`
- `"reverse"`
- `"to the source"`

The system **automatically remembers** the source language and translates back without manual configuration.

**Example:**
```
You: "Bonjour, comment allez-vous?"
Bot: [French → English] "Hello, how are you?"

You: "translate it back"
Bot: [English → French] "Bonjour, comment allez-vous?"
```

### Conversation Mode

Switch to conversation mode to:
- Ask questions about languages
- Get grammar explanations
- Learn about cultural contexts
- Discuss language learning tips

## 🎯 Key Components

### Sidebar Features

1. **Translation Settings**
   - Target language selector
   - Mode toggle (Translation/Conversation)
   - Last detected language indicator

2. **Conversation Management**
   - New translation button
   - Translation history (last 10)
   - Delete conversations

3. **Settings**
   - Model selection (GPT-3.5, GPT-4, Claude, etc.)
   - Clear chat button

4. **Translation History Panel**
   - View recent translations
   - Export history as JSON
   - Clear all history

### Main Interface

1. **Statistics Dashboard** (when history exists)
   - Total translations count
   - High confidence translations
   - Unique languages used
   - Translations with cultural notes

2. **Chat Interface**
   - Persistent conversation history
   - Real-time streaming responses
   - Formatted translation results

## 📊 Translation History

The app tracks detailed information for each translation:

```json
{
  "timestamp": "2025-11-01T10:30:00",
  "original_text": "Bonjour",
  "original_language": "French",
  "translated_text": "Hello",
  "target_language": "English",
  "confidence": "High",
  "alternatives": ["Hi", "Good day"],
  "cultural_notes": "Formal greeting in French",
  "formality": "formal"
}
```

### Export Format
- JSON file with timestamp
- All translation details included
- Easy to import/analyze

## 🔧 Configuration

### Supported Languages

English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic, Hindi, Turkish, Dutch, Polish, Swedish, Greek, Hebrew, Thai, Vietnamese

### Available Models

- **Free Models:**
  - `openai/gpt-3.5-turbo` (Default)
  - `meta-llama/llama-3.1-8b-instruct:free`

- **Premium Models:**
  - `openai/gpt-4o-mini`
  - `openai/gpt-4o`
  - `anthropic/claude-3-haiku`
  - `google/gemini-flash-1.5`

## 🎨 UI Features

- **Dark Theme** - Eye-friendly dark interface
- **Responsive Design** - Works on desktop and mobile
- **Color-Coded Messages** - Easy to distinguish user/assistant
- **Emoji Indicators** - Visual cues for different features
- **Expandable Sections** - Clean, organized layout

## ⚡ Performance Tips

1. **Use Free Models** for testing (gpt-3.5-turbo)
2. **Clear History** regularly to maintain performance
3. **Export History** before clearing for backup
4. **Conversation Mode** for general language questions

## 🐛 Troubleshooting

### 401 Authentication Error
- Verify API key format: `sk-or-v1-...`
- Check OpenRouter account has credits
- Ensure `.streamlit/secrets.toml` is properly configured

### Translation Fails
- Try a different model (switch to free tier)
- Check internet connection
- Verify OpenRouter service status

### Slow Responses
- Use faster models (gpt-3.5-turbo)
- Check your internet speed
- Try during off-peak hours

## 📝 Technical Details

### Architecture
- **Frontend:** Streamlit
- **API Gateway:** OpenRouter
- **LLM Models:** OpenAI GPT, Anthropic Claude, Google Gemini, Meta Llama
- **State Management:** Streamlit session state
- **Data Format:** JSON

### System Prompt
Uses specialized translation prompt that:
- Enforces JSON response format
- Requests cultural context
- Asks for confidence scoring
- Generates alternatives
- Identifies formality levels

### Session State Variables
- `conversations` - All chat histories
- `translation_pairs` - Translation tracking (max 50)
- `last_detected_language` - For reverse translation
- `last_translated_text` - For reverse translation
- `target_language` - Current target
- `translation_mode` - Mode selection

## 🔒 Privacy & Data

- All data stored locally in session state
- No persistent storage on disk (optional file export)
- API calls made directly to OpenRouter
- Conversation history cleared on browser refresh
- Export feature for manual backup

## 📚 Use Cases

1. **Quick Translations** - Instant text translation
2. **Language Learning** - Cultural context and alternatives
3. **Document Translation** - Batch translate with history
4. **Conversation Practice** - Bidirectional dialogue
5. **Cultural Research** - Learn idioms and expressions

## 🎓 Learning Objectives

This project demonstrates:
- System prompt engineering
- Multi-stage API calls
- State management in Streamlit
- JSON parsing and error handling
- User experience design
- Session persistence
- Data export functionality

## 🚀 Future Enhancements

- [ ] Document file upload (.txt, .pdf)
- [ ] Speech-to-text translation
- [ ] Translation glossary management
- [ ] Batch translation mode
- [ ] Translation quality comparison
- [ ] Multiple target languages at once
- [ ] Pronunciation guides
- [ ] Integration with translation APIs (DeepL, Google)

## 📄 License

This is an educational project built for Challenge 1 of the OpenRouter workshop.

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Improve documentation
- Share your use cases

## 💬 Support

For issues:
1. Check the troubleshooting section
2. Verify your API key and credits
3. Try a different model
4. Check OpenRouter documentation
