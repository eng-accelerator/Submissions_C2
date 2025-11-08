# 🤖 Multi-Persona Streamlit Chatbot (with OpenRouter Integration)

An advanced chatbot built using **Streamlit** and **OpenRouter**, supporting multiple AI personas, automatic language detection, and translation with cultural context.

---

## 🚀 Features

- 🌍 **OpenRouter Integration** – Access the latest LLMs like GPT-4o, Claude-3, and Mixtral through the OpenAI SDK.  
- 🧠 **Multi-Persona Conversations** – Chat with different assistant personalities in one interface.  
- 🗣️ **Automatic Language Detection & Translation** – Detects input language and translates to your preferred target language.  
- 💬 **Streaming Chat Responses** – Smooth, real-time message streaming in the UI.  
- 🧱 **Modular Code Design** – Easy to extend and maintain.

---

## 🧰 Requirements

- **Python** 3.9 or higher  
- **pip** (Python package manager)

---

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/multi-persona-chatbot.git
   cd multi-persona-chatbot
Create a virtual environment

python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate # On macOS/Linux


Install dependencies

pip install -r requirements.txt

📜 requirements.txt
streamlit>=1.28.0
googletrans==4.0.0-rc1
openai>=1.35.0
httpx>=0.27.0

🔑 API Key Setup

You’ll need an OpenRouter API key from https://openrouter.ai/settings/keys
.

Create a .streamlit/secrets.toml file in your project root:

OPENROUTER_API_KEY = "your_openrouter_api_key_here"

🧠 Example: Client Initialization
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="your_openrouter_api_key_here"
)


Example chat completion:

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Hello from OpenRouter!"}
    ]
)

print(response.choices[0].message.content)

🧩 Running the Streamlit App
streamlit run app.py


Then open the link in your browser (usually http://localhost:8501).

⚙️ Troubleshooting

ImportError: cannot import name 'OpenAI' from 'openai'

→ You have an outdated SDK. Run:

pip uninstall openai -y
pip install "openai>=1.35.0"


ImportError: cannot import name 'BaseTransport' from 'httpx'

→ Upgrade httpx:

pip install --upgrade httpx
