Multi-Chat Assistant (Streamlit + OpenRouter)
=============================================

Quick start
-----------
1) Create venv and install requirements
   - Windows (PowerShell):
     python -m venv .venv
     .venv\Scripts\activate
     pip install -r requirements.txt

   - Linux/macOS:
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt

2) Add your OpenRouter key to .streamlit/secrets.toml:
   OPENROUTER_API_KEY = "your-key"

3) Run:
   streamlit run app.py

Features
--------
- Multiple conversations & local persistence in ./chat_history
- Sidebar to create/switch/delete chats
- Model selector & persona selector
- Translation mode with auto language detection
- Dark/Light theme (CSS injected)
- Streaming responses
- Conversation summarization expander
- Export current chat: TXT, JSON, CSV