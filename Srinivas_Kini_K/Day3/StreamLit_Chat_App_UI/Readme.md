🚀 This is a Cool Assistant — Streamlit Chatbot UI

A simple, modern Streamlit-based Chatbot Interface with sidebar configuration, session stats, and local chat persistence.
Built with Streamlit ≥ 1.28.0 and ideal for experimenting with chat UIs or integrating AI assistants.

📸 Preview
![Uploading image.png…]()


🧩 Project Structure
chatbot-ui/
│
├── app.py                # Main Streamlit application
├── chat_history.json     # (auto-created) Chat logs saved locally
└── requirements.txt      # Dependencies

⚙️ Prerequisites

Make sure you have:

🐍 Python 3.8+

📦 pip (Python package manager)

💻 VSCode or any IDE of your choice

🌐 Streamlit ≥ 1.28.0

🛠️ Installation

Clone or create the project folder:

mkdir chatbot-ui && cd chatbot-ui


Create a virtual environment (recommended):

python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows


Add the required dependencies:

echo "streamlit>=1.28.0" > requirements.txt
pip install -r requirements.txt


Run the Streamlit app:

streamlit run app.py

💬 Features
Feature	Description
🧠 Chat Interface	Interactive message exchange using st.chat_message() and st.chat_input()
⚙️ Sidebar Configuration	Change assistant name and tone dynamically
⏱️ Session Stats	Shows session duration and message count
💾 Local Persistence	Saves chat logs to chat_history.json
🧹 Clear Chat	Clears session + deletes local chat file
📁 Export Chat	Download chat as a .txt file
💡 Expandable Sections	“About”, “Instructor Notes”, and “Development Info”
🧠 Code Overview

The main logic is inside app.py:

Uses st.session_state to maintain state during the session

Automatically saves chat messages to chat_history.json

Re-loads chat history when you restart the app

Includes export and clear actions

📁 Example Chat Log Format

When saved, chat_history.json looks like:

[
  {
    "role": "user",
    "content": "Hello 🕒 15:32:10"
  },
  {
    "role": "assistant",
    "content": "Hey, great question about 'Hello'! I'm happy to help you with that. 🕒 15:32:10"
  }
]

🧹 Resetting the App

To clear everything (including chat history):

rm chat_history.json   # macOS/Linux
del chat_history.json  # Windows


Or use the 🧹 Clear Chats button in the sidebar.

🌟 Future Enhancements (Optional Ideas)

🤖 Integrate LLMs (OpenAI / Hugging Face)

🎨 Dark & Light theme toggle

💾 Export as CSV/JSON

📈 Usage analytics and word count
