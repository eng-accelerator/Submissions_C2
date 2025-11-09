🌍 AI Translation Assistant

An intelligent, interactive translation chatbot built with Streamlit and OpenAI / OpenRouter, capable of automatically detecting languages, translating text, and providing cultural context and alternative translations.

This project is part of the "AI Chatbot Challenge – Translation Mode", focusing on system-prompt design, multi-step reasoning, and professional UI/UX in AI-assisted translation.

🚀 Features
🧩 Core Features

✅ Automatic Language Detection – Detects the input language automatically

✅ Translation Engine – Translates text into your selected target language

✅ Language Selection – Choose your preferred target language via sidebar

✅ Bidirectional Translation – Works from and to any supported language (via force-source)

🌟 Advanced Features

✨ Cultural Context – Provides notes for idioms or expressions

✨ Alternative Translations – Offers multiple translation variations

✨ Confidence Scoring – Shows how confident the AI is in the result

✨ Translation History – Keeps track of previous translations

✨ Error Handling – Gracefully handles malformed responses and API errors

🧠 Learning Objectives

By using this app you will learn how to:

Engineer system prompts for specialized AI tasks

Handle multi-stage model calls (detection → translation) or single structured calls

Manage session state and persistent history in Streamlit

Parse JSON-formatted model responses reliably

Present translations with UX-friendly features (alternatives, cultural notes, confidence)

🛠️ Tech Stack
Component	Technology
Frontend / UI	Streamlit
AI Model	OpenAI GPT model via openai package (compatible with OpenRouter)
Persistence	Local JSON files
Language Detection & Translation	Model-driven (system prompts)
Language	Python 3.10+
📁 Project Structure (example)
translation_assistant/
│
├── translation_app.py    # Main Streamlit app (provided)
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── translation_history/  # Directory where history JSON is stored

🔧 Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/yourusername/translation-assistant.git
cd translation-assistant

2️⃣ Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows (PowerShell)

3️⃣ Install dependencies
pip install -r requirements.txt


Example requirements.txt (you can create this file with these lines):

streamlit>=1.20.0
openai>=1.0.0


(If using OpenRouter's client differently, adapt accordingly — the app uses the openai-compatible client API surface.)

4️⃣ Configure API key

You can either:

Enter your OpenRouter/OpenAI API key in the app sidebar at runtime, or

Create a .env file or export the environment variable before running.

Example .env snippet:

OPENROUTER_API_KEY=your_openrouter_api_key_here


Export environment variable (example Linux/macOS):

export OPENROUTER_API_KEY="your_openrouter_api_key_here"


Note: The supplied translation_app.py also accepts entering the API key in the sidebar for convenience.

5️⃣ Run the app
streamlit run translation_app.py


Open the URL the Streamlit server prints (typically http://localhost:8501).

💬 How to Use

Launch the app with streamlit run translation_app.py.

Enter your OpenRouter/OpenAI API key in the sidebar (if not provided via env).

Select the Target Language in the sidebar.

Optionally toggle Manually specify source language to force the source.

Type or paste text into the chat input and press Enter.

The assistant will display:

🔍 Detected Language

🎯 Translation (target language)

🌟 Alternative translations (if any)

💡 Cultural note (if relevant)

📊 Confidence (progress bar)

Review translations under Translation History, and export history via the Export button.

🧩 Example Interactions
Example 1

Input:

Bonjour, comment allez-vous ?


Output:

🔍 Detected Language: French  
🎯 Translation (English): "Hello, how are you?"  
💡 Cultural Note: This is a formal greeting in French. Informally, you might say "Salut, ça va ?"

Example 2

Input:

I love this weather


Output:

🔍 Detected Language: English  
🎯 Translation (Spanish): "Me encanta este clima"  
🌟 Alternative: "Adoro este tiempo" (more emphatic)  
💡 Regional Note: In Mexico, you might also hear "Está padrísimo el clima"

🧭 Implementation Details
System prompt sample

The app uses a system prompt instructing the model to reply in JSON for reliable parsing. Example pattern:

You are a professional translator. Return JSON only with keys:
detected_language, translation, alternatives, cultural_note, confidence.


Then the user prompt includes the exact text to translate and the target language, with explicit instructions to format output as JSON.

Robust JSON parsing

The app looks for the first { in the model output and attempts json.loads(...). If parsing fails, it warns the user and suggests simplifying the input.

Session & persistence

Translations are kept in st.session_state["translation_history"] and written to a local JSON file (e.g., translation_history/history.json) to persist across sessions.

⚠️ Error Handling & Edge Cases

The app gracefully handles:

Malformed JSON responses from the model (shows an error and suggests retry)

Network or API failures (displays a helpful error)

Cases where the source language equals the target language (suggests paraphrase instead)

Missing API key (prompts the user to supply it)

🧩 Extensions & Ideas

If you'd like to extend the app, consider:

🗂️ Batch Translation: accept multiple lines or file upload and translate each line

🧾 Document Translation: support .txt, .docx, or .pdf translation pipelines

🗣️ Pronunciation Guide: add phonetic spelling or romanization

📈 Confidence Calibration: average results from multiple model calls or use model-provided scores

🔤 Glossary / Terminology: let users pin preferred translations for domain-specific terms

📁 Cloud Storage: sync translation history to Google Drive or an S3 bucket