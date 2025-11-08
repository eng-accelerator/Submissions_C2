import streamlit as st
from datetime import datetime
import time
import io

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="🚀 This is a cool assistant!",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- SIDEBAR CONFIG ----------
with st.sidebar:
    st.title("⚙️ Configuration")

    st.subheader("Assistant Settings")
    assistant_name = st.text_input("Assistant Name", "This is a cool assistant!")
    response_style = st.selectbox("Response Style", ["Friendly", "Professional", "Concise", "Humorous"])

    st.divider()

    st.subheader("Chat Settings")
    show_history = st.toggle("Show Chat History", value=True)
    show_timestamps = st.toggle("Show Timestamps", value=True)

    st.divider()

    st.subheader("Session Stats")
    start_time = st.session_state.get("start_time", None)
    if start_time is None:
        st.session_state.start_time = time.time()

    duration = time.time() - st.session_state.start_time
    st.write(f"⏱️ Session Duration: {int(duration // 60)}m {int(duration % 60)}s")
    st.write(f"💬 Total Messages: {len(st.session_state.get('chat_history', []))}")

    # Action Buttons
    st.divider()
    st.subheader("Actions")
    clear_chat = st.button("🧹 Clear Chats")
    export_chat = st.button("📁 Export Chat (.txt)")

# ---------- CHAT SECTION ----------
st.title(f"🚀 {assistant_name}")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Clear chat logic
if clear_chat:
    st.session_state.chat_history = []
    st.session_state.start_time = time.time()
    st.rerun()

# Export chat logic
if export_chat and st.session_state.chat_history:
    chat_text = "\n".join(
        [f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.chat_history]
    )
    buffer = io.StringIO(chat_text)
    st.download_button(
        label="Download Chat Log",
        data=buffer.getvalue(),
        file_name="chat_history.txt",
        mime="text/plain"
    )

# Chat interface
user_input = st.chat_input("Message: Type here...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    response = f"Hey, great question about '{user_input}'! I'm happy to help you with that."
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# Display chat history
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

# ---------- FOOTER INFO ----------
with st.expander("ℹ️ About This Demo"):
    st.markdown("""
    This Streamlit app simulates a chatbot UI similar to a dark-theme assistant dashboard.
    It includes configurable sidebar settings, chat history, and session stats.
    """)

with st.expander("📘 Instructor Notes"):
    st.markdown("""
    - Uses `st.chat_message()` and `st.chat_input()` for real-time interaction.
    - Maintains state using `st.session_state`.
    - Allows chat export as `.txt`.
    """)

with st.expander("🧑‍💻 Show Development Info"):
    st.code("""
    Streamlit Version >= 1.28.0
    Run with: streamlit run app.py
    """)

