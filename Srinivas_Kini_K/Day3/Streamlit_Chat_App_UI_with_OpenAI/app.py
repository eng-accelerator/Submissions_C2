import streamlit as st
from openai import OpenAI
import os
import json
from datetime import datetime
from pathlib import Path
import io
import csv

# ==============================================================================
# 1. APP CONFIGURATION & CLIENT SETUP
# ==============================================================================

st.set_page_config(
    page_title="🤖 Multi-Persona Chatbot",
    page_icon="🧠",
    layout="wide",
)

# --- Inject a clean CSS style ---
st.markdown(
    """
    <style>
    /* Global adjustments */
    body {
        background-color: #f9fafb;
    }
    section[data-testid="stSidebar"] {
        background-color: #f1f5f9;
        border-right: 1px solid #d1d5db;
    }
    .stChatMessage {
        border-radius: 10px !important;
        padding: 0.6rem 0.9rem !important;
        margin-bottom: 0.8rem !important;
    }
    /* Custom chat bubbles */
    [data-testid="stChatMessage"][data-testid="stChatMessage-user"] {
        background-color: #dcfce7 !important;
    }
    [data-testid="stChatMessage"][data-testid="stChatMessage-assistant"] {
        background-color: #e0f2fe !important;
    }
    /* Header style */
    .main-header {
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .main-header h1 {
        font-size: 1.6rem;
        margin-bottom: 0;
    }
    .persona-badge {
        background: #fff;
        color: #3b82f6;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-weight: 600;
    }
    .export-buttons button {
        border-radius: 8px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- API Setup ---
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except KeyError:
    st.error("❌ OPENROUTER_API_KEY not found in .streamlit/secrets.toml")
    st.stop()

# Initialize client with OpenRouter endpoint
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)


CHAT_STORAGE_DIR = Path(__file__).parent / "chat_history"
CHAT_STORAGE_DIR.mkdir(exist_ok=True)

# ==============================================================================
# 2. CHAT PERSISTENCE FUNCTIONS
# ==============================================================================

def get_all_chats():
    files = list(CHAT_STORAGE_DIR.glob("chat_*.json"))
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return files

def load_chat(chat_id):
    path = CHAT_STORAGE_DIR / f"chat_{chat_id}.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_chat(chat_id, messages, title=None):
    file = CHAT_STORAGE_DIR / f"chat_{chat_id}.json"
    if title is None and messages:
        for msg in messages:
            if msg["role"] == "user":
                title = msg["content"][:50] + ("..." if len(msg["content"]) > 50 else "")
                break
    if title is None:
        title = "Untitled Chat"
    data = {
        "chat_id": chat_id,
        "title": title,
        "messages": messages,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    if file.exists():
        try:
            old = json.load(open(file))
            data["created_at"] = old.get("created_at", data["created_at"])
        except Exception:
            pass
    json.dump(data, open(file, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def delete_chat(chat_id):
    file = CHAT_STORAGE_DIR / f"chat_{chat_id}.json"
    if file.exists():
        file.unlink()

def create_new_chat_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

# ==============================================================================
# 3. PERSONAS
# ==============================================================================

PERSONAS = {
    "General Assistant": "You are a helpful, neutral AI assistant.",
    "Creative Poet": "You are a whimsical poet who replies with creativity and rhythm.",
    "Technical Coder": "You are a precise and experienced software developer.",
    "Sarcastic Robot": "You are a sarcastic but knowledgeable robot.",
}

# ==============================================================================
# 4. SESSION INITIALIZATION
# ==============================================================================

if "current_chat_id" not in st.session_state:
    chats = get_all_chats()
    if chats:
        latest = load_chat(chats[0].stem.replace("chat_", ""))
        st.session_state.current_chat_id = latest["chat_id"]
        st.session_state.messages = latest["messages"]
        st.session_state.chat_title = latest["title"]
    else:
        st.session_state.current_chat_id = create_new_chat_id()
        st.session_state.messages = []
        st.session_state.chat_title = "New Chat"

if "current_persona" not in st.session_state:
    st.session_state.current_persona = "General Assistant"
if "feedback" not in st.session_state:
    st.session_state.feedback = {}

# ==============================================================================
# 5. SIDEBAR
# ==============================================================================

with st.sidebar:
    st.markdown("### 💬 Conversations")
    if st.button("➕ Start New Chat", use_container_width=True, type="primary"):
        if st.session_state.messages:
            save_chat(
                st.session_state.current_chat_id,
                st.session_state.messages,
                st.session_state.chat_title,
            )
        st.session_state.current_chat_id = create_new_chat_id()
        st.session_state.messages = []
        st.session_state.chat_title = "New Chat"
        st.session_state.feedback = {}
        st.rerun()

    st.divider()

    st.markdown("### 🎭 Persona Mode")
    st.selectbox(
        "Choose assistant style:",
        options=list(PERSONAS.keys()),
        key="current_persona",
    )

    st.divider()

    st.markdown("### 🕑 Chat History")
    for f in get_all_chats():
        cid = f.stem.replace("chat_", "")
        data = load_chat(cid)
        if data:
            title = data.get("title", "Untitled Chat")
            cols = st.columns([5, 1])
            if cols[0].button(f"💬 {title}", key=f"load_{cid}", use_container_width=True):
                save_chat(
                    st.session_state.current_chat_id,
                    st.session_state.messages,
                    st.session_state.chat_title,
                )
                st.session_state.current_chat_id = cid
                st.session_state.messages = data["messages"]
                st.session_state.chat_title = title
                st.session_state.feedback = {}
                st.rerun()
            if cols[1].button("🗑️", key=f"del_{cid}"):
                delete_chat(cid)
                st.rerun()

    st.divider()
    st.markdown("### 📤 Export Chat")
    if st.session_state.messages:
        txt = "\n\n".join(
            f"{m['role'].capitalize()}: {m['content']}"
            for m in st.session_state.messages
        )
        st.download_button("⬇️ Download TXT", txt, file_name="chat.txt", mime="text/plain")
    else:
        st.info("No chat to export yet.")

# ==============================================================================
# 6. MAIN INTERFACE
# ==============================================================================

st.markdown(
    f"""
    <div class="main-header">
        <h1>🤖 {st.session_state.chat_title}</h1>
        <p><span class="persona-badge">{st.session_state.current_persona}</span></p>
    </div>
    """,
    unsafe_allow_html=True,
)

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            c1, c2 = st.columns([1, 1])
            if c1.button("👍", key=f"up_{i}"):
                st.session_state.feedback[i] = "up"
            if c2.button("👎", key=f"down_{i}"):
                st.session_state.feedback[i] = "down"

if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        sys_prompt = PERSONAS[st.session_state.current_persona]
        messages = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
        try:
            stream = client.chat.completions.create(
                model="gpt-oss-120b",
                messages=messages,
                stream=True,
            )
            response_text = ""
            box = st.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    response_text += chunk.choices[0].delta.content
                    box.markdown(response_text + "▌")
            box.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            save_chat(
                st.session_state.current_chat_id,
                st.session_state.messages,
                st.session_state.chat_title,
            )
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
