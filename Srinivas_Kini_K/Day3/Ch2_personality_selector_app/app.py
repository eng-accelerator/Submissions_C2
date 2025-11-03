# Multi-chat app with persistent history and personality selector using OpenRouter
# Features: Multiple conversations, persistent storage, chat history in sidebar, personality modes

import streamlit as st
from openai import OpenAI
import os
import json
from datetime import datetime
from pathlib import Path

# Configure the page
st.set_page_config(page_title="My ChatBot", page_icon="🤖", layout="wide")

# Initialize the OpenAI client with OpenRouter
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    st.error("OPENROUTER_API_KEY not found in .streamlit/secrets.toml")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    default_headers={
        "HTTP-Referer": "http://localhost:8504",
        "X-Title": "My ChatBot",
    }
)

# ======================================================================
# PERSONALITY DEFINITIONS
# ======================================================================

PERSONALITIES = {
    "Professional Business Assistant": {
        "prompt": (
            "You are a Professional Business Assistant. "
            "Respond formally, clearly, and efficiently. "
            "Focus on strategy, communication, and professional problem-solving."
        ),
        "description": "Formal and efficient — great for business strategy, emails, and meetings.",
        "emoji": "💼"
    },
    "Creative Writing Helper": {
        "prompt": (
            "You are a Creative Writing Assistant. "
            "Respond with imagination and flair. "
            "Use metaphors, emotions, and artistic expression to help writers."
        ),
        "description": "Expressive and inspiring — perfect for stories, poems, and ideas.",
        "emoji": "🎨"
    },
    "Technical Expert": {
        "prompt": (
            "You are a Technical Expert. "
            "Be precise, methodical, and detail-oriented. "
            "Focus on technology, programming, and step-by-step reasoning."
        ),
        "description": "Analytical and detail-focused — ideal for code help or explanations.",
        "emoji": "🧠"
    },
    "Friendly Companion": {
        "prompt": (
            "You are a Friendly Companion. "
            "Speak warmly and empathetically. "
            "Offer casual conversation and emotional support."
        ),
        "description": "Casual and supportive — great for general chat or friendly talk.",
        "emoji": "😊"
    },
    "Custom Personality": {
        "prompt": "",
        "description": "Define your own style and expertise!",
        "emoji": "✨"
    }
}

# ======================================================================
# CHAT PERSISTENCE FUNCTIONS
# ======================================================================

CHAT_STORAGE_DIR = Path(__file__).parent / "chat_history"
CHAT_STORAGE_DIR.mkdir(exist_ok=True)

def get_all_chats():
    chat_files = list(CHAT_STORAGE_DIR.glob("chat_*.json"))
    chat_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return chat_files

def load_chat(chat_id):
    chat_file = CHAT_STORAGE_DIR / f"chat_{chat_id}.json"
    if chat_file.exists():
        with open(chat_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_chat(chat_id, messages, title=None):
    chat_file = CHAT_STORAGE_DIR / f"chat_{chat_id}.json"
    if title is None and messages:
        for msg in messages:
            if msg["role"] == "user":
                title = msg["content"][:50] + ("..." if len(msg["content"]) > 50 else "")
                break
    if title is None:
        title = "New Chat"

    data = {
        "chat_id": chat_id,
        "title": title,
        "messages": messages,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    if chat_file.exists():
        with open(chat_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            data["created_at"] = old_data.get("created_at", data["created_at"])

    with open(chat_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def delete_chat(chat_id):
    chat_file = CHAT_STORAGE_DIR / f"chat_{chat_id}.json"
    if chat_file.exists():
        chat_file.unlink()

def create_new_chat():
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def get_chat_title(chat_data):
    return chat_data.get("title", "Untitled Chat")

# ======================================================================
# SESSION STATE INITIALIZATION
# ======================================================================

if "current_chat_id" not in st.session_state:
    all_chats = get_all_chats()
    if all_chats:
        latest_chat = load_chat(all_chats[0].stem.replace("chat_", ""))
        st.session_state.current_chat_id = latest_chat["chat_id"]
        st.session_state.messages = latest_chat["messages"]
        st.session_state.chat_title = latest_chat["title"]
    else:
        st.session_state.current_chat_id = create_new_chat()
        st.session_state.messages = []
        st.session_state.chat_title = "New Chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"

if "feedback" not in st.session_state:
    st.session_state.feedback = {}

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "personality" not in st.session_state:
    st.session_state.personality = "Professional Business Assistant"

if "custom_personality_prompt" not in st.session_state:
    st.session_state.custom_personality_prompt = ""

# ======================================================================
# SIDEBAR: CHAT MANAGEMENT
# ======================================================================

with st.sidebar:
    st.header("💬 Conversations")

    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        if st.session_state.messages:
            save_chat(
                st.session_state.current_chat_id,
                st.session_state.messages,
                st.session_state.chat_title
            )
        st.session_state.current_chat_id = create_new_chat()
        st.session_state.messages = []
        st.session_state.chat_title = "New Chat"
        st.session_state.feedback = {}
        st.rerun()

    st.divider()
    st.subheader("Chat History")

    all_chats = get_all_chats()
    if all_chats:
        for chat_file in all_chats:
            chat_id = chat_file.stem.replace("chat_", "")
            chat_data = load_chat(chat_id)
            if chat_data:
                chat_title = get_chat_title(chat_data)
                is_current = chat_id == st.session_state.current_chat_id
                col1, col2 = st.columns([4, 1])
                with col1:
                    button_label = f"{'🟢 ' if is_current else ''}{chat_title}"
                    if st.button(
                        button_label,
                        key=f"load_{chat_id}",
                        use_container_width=True,
                        disabled=is_current,
                        type="secondary" if is_current else "tertiary"
                    ):
                        if st.session_state.messages:
                            save_chat(
                                st.session_state.current_chat_id,
                                st.session_state.messages,
                                st.session_state.chat_title
                            )
                        st.session_state.current_chat_id = chat_id
                        st.session_state.messages = chat_data["messages"]
                        st.session_state.chat_title = chat_title
                        st.session_state.feedback = {}
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"delete_{chat_id}", help="Delete chat"):
                        delete_chat(chat_id)
                        remaining_chats = [
                            c for c in all_chats if c.stem.replace("chat_", "") != chat_id
                        ]
                        if chat_id == st.session_state.current_chat_id:
                            if remaining_chats:
                                new_chat_data = load_chat(remaining_chats[0].stem.replace("chat_", ""))
                                st.session_state.current_chat_id = new_chat_data["chat_id"]
                                st.session_state.messages = new_chat_data["messages"]
                                st.session_state.chat_title = new_chat_data["title"]
                            else:
                                st.session_state.current_chat_id = create_new_chat()
                                st.session_state.messages = []
                                st.session_state.chat_title = "New Chat"
                            st.session_state.feedback = {}
                        st.rerun()
    else:
        st.info("No chat history yet. Start a new conversation!")

    st.divider()
    st.subheader("⚙️ Settings")

    dark_mode = st.toggle("Dark mode", value=st.session_state.dark_mode)
    st.session_state.dark_mode = dark_mode

    if st.button("🗑️ Clear Current Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback = {}
        st.session_state.chat_title = "New Chat"
        save_chat(st.session_state.current_chat_id, [], "New Chat")
        st.rerun()

    st.divider()
    st.subheader("🎭 Personality Selector")

    selected_personality = st.selectbox(
        "Choose AI Personality",
        options=list(PERSONALITIES.keys()),
        index=list(PERSONALITIES.keys()).index(st.session_state.personality),
    )

    if selected_personality != st.session_state.personality:
        st.session_state.personality = selected_personality
        st.rerun()

    personality_data = PERSONALITIES[st.session_state.personality]
    st.markdown(f"**{personality_data['emoji']} {st.session_state.personality}**")
    st.caption(personality_data["description"])

    if st.session_state.personality == "Custom Personality":
        st.text_area(
            "Define your custom personality prompt:",
            value=st.session_state.custom_personality_prompt,
            key="custom_personality_prompt",
            placeholder="Describe your custom assistant's tone, expertise, and style here..."
        )

# ======================================================================
# APPLY THEMING
# ======================================================================

if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        .stApp { background-color: #0f1115; color: #e6e6e6; }
        .stChatMessage, .stMarkdown { color: #e6e6e6; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ======================================================================
# MAIN CHAT INTERFACE
# ======================================================================

st.title(f"🤖 {st.session_state.chat_title} — {PERSONALITIES[st.session_state.personality]['emoji']} {st.session_state.personality}")

with st.expander("📝 Summarize Conversation", expanded=False):
    st.write("Generate a summary of the entire conversation in this chat")
    if st.button("Generate Summary", use_container_width=True):
        if not st.session_state.messages:
            st.warning("No messages to summarize yet!")
        else:
            try:
                with st.spinner("Generating summary..."):
                    system_prompt = PERSONALITIES[st.session_state.personality]["prompt"]
                    if st.session_state.personality == "Custom Personality" and st.session_state.custom_personality_prompt.strip():
                        system_prompt = st.session_state.custom_personality_prompt.strip()

                    summary_resp = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "system", "content": f"{system_prompt}\nNow summarize the conversation into concise key points and action items."},
                            *st.session_state.messages,
                        ],
                        stream=False,
                    )
                    summary_text = summary_resp.choices[0].message.content.strip()
                    st.markdown("### Summary")
                    st.markdown(summary_text)
            except Exception as e:
                st.error(f"Summary failed: {e}")

for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("👍", key=f"up_{idx}"):
                    st.session_state.feedback[idx] = "up"
            with c2:
                if st.button("👎", key=f"down_{idx}"):
                    st.session_state.feedback[idx] = "down"

# ======================================================================
# CHAT INPUT HANDLING
# ======================================================================

if prompt := st.chat_input("What would you like to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    if len(st.session_state.messages) == 1:
        st.session_state.chat_title = prompt[:50] + ("..." if len(prompt) > 50 else "")

    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare system message based on personality
    if st.session_state.personality == "Custom Personality" and st.session_state.custom_personality_prompt.strip():
        system_prompt = st.session_state.custom_personality_prompt.strip()
    else:
        system_prompt = PERSONALITIES[st.session_state.personality]["prompt"]

    system_message = {"role": "system", "content": system_prompt}

    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[system_message, *st.session_state.messages],
                stream=True,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8503",
                    "X-Title": "My ChatBot"
                },
            )

            response_text = ""
            response_placeholder = st.empty()

            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    content = (
                        content.replace('<s>', '')
                        .replace('<|im_start|>', '')
                        .replace('<|im_end|>', '')
                        .replace("<|OUT|>", "")
                    )
                    response_text += content
                    response_placeholder.markdown(response_text + "▌")

            response_text = (
                response_text.replace('<s>', '')
                .replace('<|im_start|>', '')
                .replace('<|im_end|>', '')
                .replace("<|OUT|>", "")
                .strip()
            )
            response_placeholder.markdown(response_text)

            st.session_state.messages.append({"role": "assistant", "content": response_text})
            save_chat(st.session_state.current_chat_id, st.session_state.messages, st.session_state.chat_title)

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Please check your API key and try again.")

if st.session_state.messages:
    save_chat(
        st.session_state.current_chat_id,
        st.session_state.messages,
        st.session_state.chat_title
    )
