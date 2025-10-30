import streamlit as st
import time
from datetime import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Chat Assistant", page_icon="🚀", layout="wide")

# ---------- THEME STYLES ----------
def apply_theme(theme_name):
    if theme_name == "Dark":
        st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        .stTextInput input {
            background-color: #1e2130;
            color: #fafafa;
            border: 1px solid #3d4150;
        }
        .stSelectbox select {
            background-color: #1e2130;
            color: #fafafa;
            border: 1px solid #3d4150;
        }
        .stSlider {
            color: #fafafa;
        }
        .stMarkdown {
            color: #fafafa;
        }
        .stExpander {
            background-color: #1e2130;
            border: 1px solid #3d4150;
        }
        section[data-testid="stSidebar"] {
            background-color: #0e1117;
            border-right: 1px solid #3d4150;
        }
        .stButton button {
            background-color: #1e2130;
            color: #fafafa;
            border: 1px solid #3d4150;
        }
        .stButton button:hover {
            background-color: #2e3140;
            border: 1px solid #5d6170;
        }
        </style>
        """, unsafe_allow_html=True)
    else:  # Light theme
        st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff;
            color: #1e1e1e;
        }
        .stTextInput input {
            background-color: #f0f2f6;
            color: #1e1e1e;
            border: 1px solid #d3d3d3;
        }
        .stSelectbox select {
            background-color: #f0f2f6;
            color: #1e1e1e;
            border: 1px solid #d3d3d3;
        }
        .stSlider {
            color: #1e1e1e;
        }
        .stMarkdown {
            color: #1e1e1e;
        }
        .stExpander {
            background-color: #f0f2f6;
            border: 1px solid #d3d3d3;
        }
        section[data-testid="stSidebar"] {
            background-color: #f8f9fa;
            border-right: 1px solid #d3d3d3;
        }
        .stButton button {
            background-color: #f0f2f6;
            color: #1e1e1e;
            border: 1px solid #d3d3d3;
        }
        .stButton button:hover {
            background-color: #e0e2e6;
            border: 1px solid #b3b3b3;
        }
        </style>
        """, unsafe_allow_html=True)

# ---------- INITIAL SETUP ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# ---------- SIDEBAR CONFIG ----------
st.sidebar.header("⚙️ Configuration")

# Theme Selector
theme = st.sidebar.selectbox("🎨 Theme:", ["Light", "Dark"], key="theme")

# Apply the selected theme
apply_theme(theme)

st.sidebar.text_input("Assistant Name:", "This is a cool assistant!", key="assistant_name")
st.sidebar.selectbox("Response Style:", ["Friendly", "Professional", "Casual"], key="response_style")
st.sidebar.slider("Max Chat History:", 10, 100, 40, key="max_history")

show_timestamps = st.sidebar.checkbox("Show Timestamps", True)

st.sidebar.divider()

# ---------- SESSION STATS ----------
st.sidebar.subheader("📊 Session Stats")
session_duration = time.time() - st.session_state.start_time
st.sidebar.metric("Session Duration", f"{int(session_duration//60)}m {int(session_duration%60)}s")
st.sidebar.metric("Messages Sent", len(st.session_state.messages))
st.sidebar.metric("Total Messages", len(st.session_state.messages)*2 if st.session_state.messages else 0)

# ---------- ACTIONS ----------
def clear_chat():
    st.session_state.messages = []
    st.session_state.start_time = time.time()

def export_chat():
    if not st.session_state.messages:
        st.warning("No chat to export.")
        return
    filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    chat_text = "\n".join([f"You: {m['user']}\nAssistant: {m['assistant']}\n" for m in st.session_state.messages])
    st.download_button("⬇️ Download Chat", data=chat_text, file_name=filename, mime="text/plain")

st.sidebar.button("🗑️ Clear Chat", on_click=clear_chat)
export_chat()

# ---------- MAIN CHAT UI ----------
st.title(f"🚀 {st.session_state.assistant_name}")

# ---------- EXPANDABLE SECTIONS ----------
with st.expander("📖 About Demo"):
    st.markdown("""
    ### About This Demo
    This is an interactive chat assistant built with Streamlit.

    **Features:**
    - Customizable assistant name and response styles
    - Real-time chat with timestamps
    - Session statistics tracking
    - Chat history export functionality
    - Configurable chat history limits

    **How to use:**
    1. Type your message in the chat input below
    2. Adjust settings in the sidebar to customize your experience
    3. Export your chat history anytime using the download button
    """)

with st.expander("👨‍🏫 Instructor Notes"):
    st.markdown("""
    ### Instructor Notes
    This application demonstrates several key Streamlit concepts:

    **Core Concepts Covered:**
    - Session state management (`st.session_state`)
    - Sidebar widgets and configuration
    - Dynamic UI updates with `st.rerun()`
    - File downloads with `st.download_button()`
    - Conditional rendering based on user preferences
    - Time and datetime handling

    **Suggested Exercises:**
    - Add a theme switcher (light/dark mode)
    - Implement message editing functionality
    - Add support for multiple conversation threads
    - Create a more sophisticated response generation system
    - Add user authentication
    """)

# ---------- CHAT DISPLAY ----------
for msg in st.session_state.messages:
    if show_timestamps:
        st.markdown(f"**🧑 You ({msg['time']}):** {msg['user']}")
        st.markdown(f"**🤖 {st.session_state.assistant_name} ({msg['time']}):** {msg['assistant']}")
    else:
        st.markdown(f"**🧑 You:** {msg['user']}")
        st.markdown(f"**🤖 {st.session_state.assistant_name}:** {msg['assistant']}")

# ---------- CHAT INPUT ----------
prompt = st.chat_input("Type your message...")

if prompt:
    # Generate a simple response (demo)
    style = st.session_state.response_style
    if style == "Friendly":
        response = f"Hey, great question about '{prompt}'! I'm happy to help you with that. 😊"
    elif style == "Professional":
        response = f"Thank you for your message regarding '{prompt}'. Here’s what I think..."
    else:
        response = f"Cool! So about '{prompt}' — let's dive in!"

    st.session_state.messages.append({
        "user": prompt,
        "assistant": response,
        "time": datetime.now().strftime("%H:%M:%S")
    })
    st.rerun()
