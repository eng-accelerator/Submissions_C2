import random
import time
from datetime import datetime
import streamlit as st
import requests

# -----------------------
# Page config & defaults
# -----------------------
st.set_page_config(page_title="Demo Assistant", layout="wide", initial_sidebar_state="expanded")

DEFAULTS = {
    "theme": "Dark",
    "assistant_name": "Demo Assistant",
    "response_style": "Friendly",
    "max_history": 50,
    "show_timestamps": True,
}

# -----------------------
# Session state init
# -----------------------
if "settings" not in st.session_state:
    st.session_state.settings = DEFAULTS.copy()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": f"Hello! I'm your {st.session_state.settings['assistant_name']}. How can I help you today?",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }
    ]

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

# -----------------------
# Helper functions
# -----------------------
def save_settings(new_settings):
    st.session_state.settings.update(new_settings)
    st.success("✅ Settings saved!")

def reset_settings():
    st.session_state.settings = DEFAULTS.copy()
    st.success("🔄 Reset to defaults!")

def add_message(role, content):
    ts = datetime.now().strftime("%H:%M:%S") if st.session_state.settings.get("show_timestamps", True) else ""
    st.session_state.chat_messages.append({"role": role, "content": content, "timestamp": ts})
    # Enforce max history
    max_h = st.session_state.settings.get("max_history", DEFAULTS["max_history"])
    while len(st.session_state.chat_messages) > max_h and len(st.session_state.chat_messages) > 1:
        st.session_state.chat_messages.pop(0)

def generate_demo_response(user_text):
    """Generate a demo response based on the response style"""
    style = st.session_state.settings.get("response_style", "Friendly")

    responses = {
        "Friendly": [
            f"Hey, great question about: '{user_text}'. I'm happy to help!",
            "That's interesting — let me think about that.",
            f"I heard you! Here's what I think about: {user_text[:100]}...",
            "Good point! Tell me more about what you're looking for.",
            f"Thanks for sharing that. Here's my take on it...",
        ],
        "Professional": [
            f"I acknowledge your inquiry regarding: '{user_text}'.",
            "Thank you for your question. I'll provide a comprehensive response.",
            "I understand your concern. Let me address that professionally.",
            "Your query has been noted. Here's my analysis.",
            "I appreciate your input. Allow me to elaborate.",
        ],
        "Funny": [
            f"Oh wow, '{user_text}'! That's a spicy question! 🌶️",
            "LOL, good one! Let me think... *puts on thinking cap* 🤔",
            "Haha, you're asking the real questions now! Here's the deal...",
            "Plot twist: I actually know the answer to that! 😄",
            "*Adjusts glasses* Ah yes, the classic question. Here goes...",
        ],
        "Teacher": [
            f"Excellent question! Let's explore '{user_text}' together.",
            "Great thinking! To understand this, we need to consider...",
            "I'm glad you asked! This is a wonderful learning opportunity.",
            "Let me break this down for you step by step:",
            "That's a very thoughtful question. Here's what you need to know...",
        ],
    }

    return random.choice(responses.get(style, [f"I heard: '{user_text}'. Nice question!"]))

import json
import io

def export_chat(format: str = "txt"):
    """Export the chat messages in different formats."""
    data = st.session_state.chat_messages

    if format == "json":
        content = json.dumps(data, indent=2)
        mime = "application/json"
        filename = "chat_history.json"

    elif format == "csv":
        # Convert to CSV-like string manually
        lines = ["role,content,timestamp"]
        for m in data:
            # Escape commas and quotes
            content = m['content'].replace('"', '""').replace('\n', ' ')
            lines.append(f"{m['role']},\"{content}\",{m.get('timestamp','')}")
        content = "\n".join(lines)
        mime = "text/csv"
        filename = "chat_history.csv"

    else:  # default: txt
        lines = []
        for m in data:
            ts = f"[{m.get('timestamp','')}]" if m.get('timestamp') else ""
            lines.append(f"{ts} {m['role'].upper()}: {m['content']}")
        content = "\n\n".join(lines)
        mime = "text/plain"
        filename = "chat_history.txt"

    return content, mime, filename


# HF API call example (not used in demo response generation)

from huggingface_hub import InferenceClient

def generate_hf_response(user_text):
    """Generate a real AI response using Hugging Face Inference API."""
    try:
        api_key = st.secrets.get("HF_API_KEY", None)
        if not api_key:
            return "⚠️ Hugging Face API key not found. Please add it in .streamlit/secrets.toml"

        # ✅ Publicly available chat model
        client = InferenceClient(api_key=api_key)
        model_id = "HuggingFaceH4/zephyr-7b-beta"  # or "mistralai/Mistral-7B-Instruct-v0.2"

        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are a helpful and friendly assistant."},
                {"role": "user", "content": user_text},
            ],
            max_tokens=300,
        )

        return response.choices[0].message["content"].strip()

    except Exception as e:
        return f"⚠️ HF API error: {e}"


# -----------------------
# Sidebar (controls)
# -----------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    with st.expander("Assistant Settings", expanded=True):
        assistant_name = st.text_input(
            "Assistant Name:",
            st.session_state.settings.get("assistant_name", DEFAULTS["assistant_name"])
        )
        response_style = st.selectbox(
            "Response Style:",
            ["Friendly", "Professional", "Funny", "Teacher"],
            index=["Friendly", "Professional", "Funny", "Teacher"].index(
                st.session_state.settings.get("response_style", "Friendly")
            ),
        )

    with st.expander("Chat Settings", expanded=False):
        max_history = st.slider(
            "Max Chat History:",
            10, 500,
            int(st.session_state.settings.get("max_history", DEFAULTS["max_history"]))
        )
        show_timestamps = st.checkbox(
            "Show Timestamps",
            value=st.session_state.settings.get("show_timestamps", True)
        )

    st.markdown("---")
    st.subheader("📊 Session Stats")
    elapsed = int(time.time() - st.session_state.start_time)
    st.write(f"**Session Duration:** {elapsed//60}m {elapsed%60}s")
    st.write(f"**Messages Sent:** {sum(1 for m in st.session_state.chat_messages if m['role'] == 'user')}")
    st.write(f"**Total Messages:** {len(st.session_state.chat_messages)}")

    if st.button("💾 Save Settings", use_container_width=True):
        save_settings({
            "assistant_name": assistant_name,
            "response_style": response_style,
            "max_history": max_history,
            "show_timestamps": show_timestamps,
        })
        st.rerun()

    st.subheader("💾 Export Chat")

    fmt = st.radio("Choose Format", ["txt", "json", "csv"], horizontal=True)
    content, mime, filename = export_chat(fmt)
    st.download_button(
        label=f"⬇️ Download Chat ({fmt.upper()})",
        data=content,
        file_name=filename,
        mime=mime,
        use_container_width=True
    )

    if st.button("🔄 Reset to Defaults", use_container_width=True):
        reset_settings()
        st.rerun()

# -----------------------
# Apply Updated Settings
# -----------------------
st.session_state.settings.update({
    "assistant_name": assistant_name,
    "response_style": response_style,
    "max_history": max_history,
    "show_timestamps": show_timestamps,
})

# -----------------------
# Main layout
# -----------------------
st.title(f"🚀 Meet {st.session_state.settings['assistant_name']}!")
st.caption(
    f"Response Style: {st.session_state.settings.get('response_style')} | "
    f"History Limit: {st.session_state.settings.get('max_history')} messages"
)

# Display chat messages
for msg in st.session_state.chat_messages:
    role = msg["role"]
    content = msg["content"]
    ts = msg.get("timestamp", "")

    with st.chat_message(role):
        if ts and st.session_state.settings.get("show_timestamps"):
            st.caption(ts)
        st.markdown(content)

# Chat input
user_input = st.chat_input("Message your assistant...")

if user_input:
    add_message("user", user_input)
    ai_text = generate_hf_response(user_input)
    add_message("assistant", ai_text)
    st.rerun()

# -----------------------
# Bottom expanders
# -----------------------
with st.expander("ℹ️ About This Demo"):
    st.write("""
    This is a configurable chat assistant demo built with Streamlit.
    - Configure assistant settings in the sidebar
    - Chat history is limited based on your settings
    - Different response styles for various use cases
    """)

with st.expander("📝 Instructor Notes"):
    st.write("This demo showcases Streamlit's chat functionality with customizable settings and response styles.")

with st.expander("🔧 Show Development Info"):
    if st.checkbox("Display raw message data"):
        st.json(st.session_state.chat_messages)
