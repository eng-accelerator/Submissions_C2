# 🤖 Multi-Chat AI Assistant with Personality Selector

A Streamlit-powered multi-chat AI assistant that connects to **OpenRouter** and lets users choose from multiple **AI personalities** such as **Professional**, **Creative**, **Technical**, and **Friendly** — or even create their own custom personality!

---

![Uploading image.png…]()


## 🚀 Features

### 🧠 Core Functionality
- **Multi-Chat System** — Create, rename, and switch between multiple chat sessions.
- **Persistent History** — Conversations are saved in JSON and loaded automatically.
- **OpenRouter Integration** — Uses any supported OpenRouter model for chat completions.
- **Markdown Support** — Rich rendering of AI responses including code blocks.

### 🎭 Personality Selector (Challenge 2)
- **Personality Dropdown** — Choose from multiple distinct AI personalities.
- **Dynamic System Prompts** — Each personality has its own style and tone.
- **Custom Personality Mode** — Define your own assistant behavior and tone.
- **Visual Indicators** — Current personality shown in chat header and sidebar.
- **Mid-Chat Switching** — Change personality anytime during a conversation.

---

## 🧩 Personality Options

| Personality | Emoji | Style | Expertise | Tone |
|--------------|--------|--------|------------|------|
| **Professional Business Assistant** | 💼 | Formal, structured | Business strategy, communication | Polite, efficient, results-oriented |
| **Creative Writing Helper** | 🎨 | Imaginative, expressive | Storytelling, artistic writing | Enthusiastic, inspiring |
| **Technical Expert** | 🧠 | Precise, detailed | Programming, problem-solving | Analytical, methodical |
| **Friendly Companion** | 😊 | Casual, supportive | General chat, emotional support | Warm, empathetic |
| **Custom Personality** | ✨ | User-defined | User-specified | Customizable |

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python (OpenRouter API)
- **Data Storage:** JSON (Local persistence)
- **Libraries:**
  - `streamlit`
  - `json`
  - `datetime`
  - `openai` (via OpenRouter-compatible client)

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/multi-chat-ai.git
cd multi-chat-ai
2️⃣ Install Dependencies
pip install -r requirements.txt


requirements.txt

streamlit>=1.28.0
openai

3️⃣ Add Your API Key

Create a .streamlit/secrets.toml file:

[general]
OPENROUTER_API_KEY = "your_openrouter_api_key_here"


Alternatively, set it as an environment variable:

export OPENROUTER_API_KEY="your_openrouter_api_key_here"

▶️ Run the App
streamlit run app.py

💬 Example Interaction
Professional Mode

User: “How do I handle a difficult client meeting?”
Assistant (💼):

I recommend a structured approach to managing challenging client interactions:

Preparation: Review all relevant documentation

Active Listening: Allow the client to express their concerns fully

Solution-Focused Discussion: Present 2–3 concrete options

Clear Next Steps: Document agreed actions with timelines

Creative Mode

User: “How do I handle a difficult client meeting?”
Assistant (🎨):

Ah, the art of navigating stormy client waters! 🎭
Picture this: you're not just attending a meeting — you're crafting a story where everyone wins.
Transform the tension into creative energy and surprise them with innovative approaches they never saw coming! ✨

🧩 Folder Structure
📦 multi-chat-ai
 ┣ 📜 app.py
 ┣ 📜 requirements.txt
 ┣ 📜 README.md
 ┗ 📂 data/
    ┗ 📜 chat_history.json

🌟 Future Enhancements

🧩 Add AI avatars for each personality

💾 Cloud-based chat history (e.g., Supabase / Firebase)

🗂️ Personality profiles with detailed descriptions

🔄 Mix multiple personality traits dynamically
