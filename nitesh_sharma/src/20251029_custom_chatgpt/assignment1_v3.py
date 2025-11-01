import streamlit as st
import time
from datetime import datetime, timedelta
import base64
import json
import os
from pathlib import Path
import glob
import re

# Optional OpenAI SDK import; handle if not installed
try:
    from openai import OpenAI
    _HAS_OPENAI = True
except Exception:
    _HAS_OPENAI = False

# OpenRouter.ai base URL
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
CHAT_HISTORY_DIR = "chat_history"

# --- Helper functions -----------------------------------------------------

def now_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_chat_filename():
    return f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def clean_message(text):
    """Remove special tags from message content"""
    patterns = [
        r'<im_start>.*?<im_end>',
        r'<\|im_start\|>.*?<\|im_end\|>',
        r'<out>.*?</out>'
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
    return text.strip()

def save_current_chat():
    """Save current chat to JSON file"""
    if not os.path.exists(CHAT_HISTORY_DIR):
        os.makedirs(CHAT_HISTORY_DIR)
    
    chat_data = {
        "messages": st.session_state.messages,
        "start_time": st.session_state.start_time,
        "settings": st.session_state.settings,
        "summary": st.session_state.get("summary", ""),
        "chat_id": st.session_state.current_chat_id
    }
    
    filename = os.path.join(CHAT_HISTORY_DIR, get_chat_filename())
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(chat_data, f, indent=2, default=str)
    return filename

def load_chat_history(filename):
    """Load chat history from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        st.session_state.messages = data["messages"]
        st.session_state.start_time = float(data["start_time"])
        st.session_state.settings.update(data["settings"])
        st.session_state.summary = data.get("summary", "")
        st.session_state.current_chat_id = data.get("chat_id", datetime.now().strftime("%Y%m%d_%H%M%S"))

def get_chat_summary(messages):
    """Generate a summary of the chat using the API"""
    if not messages:
        return "No messages to summarize"
    
    try:
        # Get API key
        api_key = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY")
        if not api_key:
            return "Cannot generate summary: No API key found"

        client = OpenAI(
            api_key=api_key,
            base_url=OPENROUTER_API_BASE,
            default_headers={
                "HTTP-Referer": "https://github.com/outskill-git/ai-accelerator",
                "X-Title": "AI Accelerator Chat"
            }
        )

        # Create a summary prompt
        summary_messages = [
            {"role": "system", "content": "Please provide a brief summary of the following conversation. Focus on the main topics discussed and key points. Keep it concise."},
            {"role": "user", "content": json.dumps([m["content"] for m in messages])}
        ]

        with st.spinner("Generating summary..."):
            result = client.chat.completions.create(
                model="gpt-oss-120b",
                messages=summary_messages,
                temperature=0.7,
                max_tokens=150
            )
            return clean_message(result.choices[0].message.content)
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# --- Session initialization -----------------------------------------------
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
if "settings" not in st.session_state:
    st.session_state.settings = {
        "assistant_name": "Chat Assistant",
        "response_style": "Professional",
        "max_history": 30,
        "show_timestamps": True,
        "theme": "Dark",
        "temperature": 1.4,
        "max_tokens": 290,
        "use_api": True,
        "api_model": "gpt-oss-120b",
    }

# --- Page config ----------------------------------------------------------
st.set_page_config(page_title="Chat Assistant v3", page_icon="💬", layout="wide")

# Theme CSS
DARK_CSS = """
<style>
body { background-color: #0b0e13; color: #e6eef6; }
.stApp { background-color: #0b0e13; }
.chat-bubble { background: #121317; padding: 1rem; border-radius: 0.75rem; margin-bottom: 0.8rem; }
.chat-bubble.user { background: #24262b; }
.chat-bubble.assistant { background: #1a2130; }
.small-muted { color: #9aa3b2; font-size: 0.85rem; }
.header-meta { color: #9aa3b2; margin-bottom: 1rem; }
.sidebar .stTextInput>div>div>input { background: #0f1720; color: #fff }
.chat-actions { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.chat-actions button { flex: 1; }
[data-testid="stToggleSwitch"] { margin-top: 2rem; }
.timestamp-toggle { margin-top: 1.5rem; text-align: right; }
</style>
"""

LIGHT_CSS = """
<style>
body { background-color: #f6f7fb; color: #111827; }
.stApp { background-color: #f6f7fb; }
.chat-bubble { background: #ffffff; padding: 1rem; border-radius: 0.75rem; margin-bottom: 0.8rem; }
.chat-bubble.user { background: #eef2ff; }
.chat-bubble.assistant { background: #eef2f6; }
.small-muted { color: #6b7280; font-size: 0.85rem; }
.header-meta { color: #6b7280; margin-bottom: 1rem; }
.chat-actions { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.chat-actions button { flex: 1; }
</style>
"""

# Apply theme CSS
if st.session_state.settings["theme"] == "Dark":
    st.markdown(DARK_CSS, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)

# --- Layout: Sidebar ------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # Chat History Section
    st.subheader("💾 Chat History")
    history_files = glob.glob(os.path.join(CHAT_HISTORY_DIR, "*.json"))
    if history_files:
        selected_file = st.selectbox(
            "Load Previous Chat",
            options=history_files,
            format_func=lambda x: Path(x).stem
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load Chat"):
                with st.spinner("Loading chat..."):
                    load_chat_history(selected_file)
                st.rerun()
        with col2:
            if st.button("Delete History"):
                with st.spinner("Deleting..."):
                    os.remove(selected_file)
                st.success("Chat history deleted!")
                st.rerun()
    
    st.markdown("---")
    st.subheader("Assistant Settings")
    st.session_state.settings["assistant_name"] = st.text_input("Assistant Name:", value=st.session_state.settings["assistant_name"])
    st.session_state.settings["response_style"] = st.selectbox("Response Style:", ["Friendly", "Professional", "Technical"], index=["Friendly", "Professional", "Technical"].index(st.session_state.settings["response_style"]))

    st.markdown("---")
    st.subheader("Chat Settings")
    st.session_state.settings["max_history"] = st.slider("Max Chat History:", 10, 100, st.session_state.settings["max_history"])
    
    st.markdown("---")
    st.subheader("🎨 Theme Settings")
    st.session_state.settings["theme"] = st.selectbox("Theme:", ["Dark", "Light"], index=["Dark", "Light"].index(st.session_state.settings["theme"]))

    st.markdown("---")
    st.subheader("🤖 GPT Parameters")
    st.session_state.settings["temperature"] = st.slider("Temperature", 0.0, 2.0, float(st.session_state.settings["temperature"]), 0.1)
    st.session_state.settings["max_tokens"] = st.slider("Max Tokens", 50, 1000, int(st.session_state.settings["max_tokens"]))

    st.markdown("---")
    st.subheader("🔌 OpenRouter.ai API")
    st.session_state.settings["use_api"] = st.checkbox("Use OpenRouter API (gpt-oss-120b)", value=st.session_state.settings.get("use_api", True))
    if st.session_state.settings["use_api"]:
        if not _HAS_OPENAI:
            st.warning("OpenAI SDK not installed. Install 'openai' in your environment to enable API calls.")
        key = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY")
        if key:
            st.success(f"✅ OpenRouter API key found - Using model: {st.session_state.settings['api_model']}")
            try:
                client = OpenAI(
                    api_key=key,
                    base_url=OPENROUTER_API_BASE,
                    default_headers={
                        "HTTP-Referer": "https://github.com/outskill-git/ai-accelerator",
                        "X-Title": "AI Accelerator Chat"
                    }
                )
                result = client.chat.completions.create(
                    model=st.session_state.settings['api_model'],
                    messages=[{"role": "system", "content": "Test message"}],
                    max_tokens=5
                )
                st.success("✅ OpenRouter API connection confirmed!")
            except Exception as e:
                st.error(f"❌ API key found but test failed: {str(e)}")
        else:
            st.info("No OpenRouter API key found. Set 'OPENROUTER_API_KEY' in environment or secrets.")

    st.markdown("---")
    st.subheader("📊 Session Stats")
    duration = time.time() - st.session_state.start_time
    st.markdown(f"""
    **Chat ID:** {st.session_state.current_chat_id}  
    **Session Duration:** {str(timedelta(seconds=int(duration)))}  
    **Messages Sent:** {st.session_state.message_count}  
    **Total Messages:** {len(st.session_state.messages)}
    """)

# Re-apply theme if sidebar changed
if st.session_state.settings["theme"] == "Dark":
    st.markdown(DARK_CSS, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)

# --- Main UI --------------------------------------------------------------
col1, col2 = st.columns([1, 3])
with col1:
    # Chat Actions
    st.markdown("### 🔄 Chat Actions")
    
    if st.button("🆕 New Chat"):
        # Save current chat if it has messages
        if st.session_state.messages:
            save_current_chat()
        # Reset session state for new chat
        st.session_state.messages = []
        st.session_state.message_count = 0
        st.session_state.start_time = time.time()
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.pop('summary', None)
        st.rerun()

    if st.button("💾 Save Chat"):
        if st.session_state.messages:
            filename = save_current_chat()
            st.success(f"Chat saved to {filename}")
        else:
            st.info("No messages to save")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.message_count = 0
        st.session_state.start_time = time.time()
        st.session_state.pop('summary', None)
        st.rerun()

    if st.button("📝 Generate Summary"):
        if st.session_state.messages:
            st.session_state.summary = get_chat_summary(st.session_state.messages)
            st.rerun()
        else:
            st.info("No messages to summarize")

with col2:
    # Chat header with controls
    col_title, col_controls = st.columns([3, 1])
    with col_title:
        st.markdown(f"# 💬 {st.session_state.settings['assistant_name']}")
        meta = f"Response Style: {st.session_state.settings['response_style']} | History Limit: {st.session_state.settings['max_history']} messages | Temperature: {st.session_state.settings['temperature']} | Max Tokens: {st.session_state.settings['max_tokens']}"
        st.markdown(f"<div class='header-meta'>{meta}</div>", unsafe_allow_html=True)
    with col_controls:
        st.session_state.settings["show_timestamps"] = st.toggle("Show Timestamps", value=st.session_state.settings.get("show_timestamps", False), help="Toggle timestamp display in chat")

    # Display summary if available
    if summary := st.session_state.get("summary"):
        with st.expander("📝 Chat Summary", expanded=True):
            st.write(summary)

    # Welcome / initial system message
    if not st.session_state.messages:
        init_msg = {
            "role": "assistant",
            "content": "Hello! I'm your chat assistant. How can I help you today?",
            "timestamp": now_ts()
        }
        st.session_state.messages.append(init_msg)

    # Enforce max history
    max_hist = st.session_state.settings["max_history"]
    if len(st.session_state.messages) > max_hist:
        st.session_state.messages = st.session_state.messages[-max_hist:]

    # Display messages
    for m in st.session_state.messages:
        role = m["role"]
        content = clean_message(m["content"])
        ts = m.get("timestamp", "")
        cls = "assistant" if role == "assistant" else "user"
        label = f"{st.session_state.settings['assistant_name']}" if role == "assistant" else "You"
        header = f"{label} - {ts}" if st.session_state.settings["show_timestamps"] else label
        st.markdown(f"<div class='chat-bubble {cls}'><div class='small-muted'>{header}</div><div>{content}</div></div>", unsafe_allow_html=True)

    # Input area - using container for dynamic updates
    input_container = st.container()
    with input_container:
        # Using a form for enter key submission
        with st.form(key="message_form", clear_on_submit=True):
            user_input = st.text_input("Message", key="user_input_v3")
            submit_button = st.form_submit_button("Send")

        if submit_button and user_input:
            # Append user message
            user_msg = {"role": "user", "content": user_input, "timestamp": now_ts()}
            st.session_state.messages.append(user_msg)
            st.session_state.message_count += 1

            # Show spinner during API call
            with st.spinner("Thinking..."):
                # If API usage is enabled, attempt to call OpenAI
                resp = None
                if st.session_state.settings.get("use_api"):
                    if not _HAS_OPENAI:
                        resp = "Error: OpenAI SDK not installed in the environment. Falling back to simulated response."
                    else:
                        api_key = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY")
                        if not api_key:
                            resp = "Error: No OpenRouter API key found in environment. Falling back to simulated response."
                        else:
                            try:
                                client = OpenAI(
                                    api_key=api_key,
                                    base_url=OPENROUTER_API_BASE,
                                    default_headers={
                                        "HTTP-Referer": "https://github.com/outskill-git/ai-accelerator",
                                        "X-Title": "AI Accelerator Chat"
                                    }
                                )
                                messages = []
                                for m in st.session_state.messages[-st.session_state.settings.get("max_history", 30):]:
                                    role_name = m.get("role")
                                    api_role = role_name
                                    messages.append({"role": api_role, "content": m.get("content")})

                                result = client.chat.completions.create(
                                    model=st.session_state.settings.get("api_model", "gpt-oss-120b"),
                                    messages=messages,
                                    temperature=float(st.session_state.settings.get("temperature", 1.0)),
                                    max_tokens=int(st.session_state.settings.get("max_tokens", 290)),
                                )
                                try:
                                    resp = clean_message(result.choices[0].message.content)
                                except Exception:
                                    resp = str(result)
                            except Exception as e:
                                resp = f"OpenRouter API error: {str(e)}. Falling back to simulated response."

                if resp is None or resp.startswith("Error:") or resp.startswith("OpenRouter API error"):
                    style = st.session_state.settings["response_style"]
                    if style == "Friendly":
                        resp = f"Hey! Thanks for your message: '{user_input}'. I'm happy to help ❤️"
                    elif style == "Professional":
                        resp = f"Thank you for your message. I'll help you with: '{user_input}'"
                    else:
                        resp = f"Processing query: {user_input}. Analysis: (simulated)."

            # Append assistant response
            assistant_msg = {"role": "assistant", "content": resp, "timestamp": now_ts()}
            st.session_state.messages.append(assistant_msg)
            st.session_state.message_count += 1

            # Auto-save chat after each message
            save_current_chat()

            # Trim history if needed
            if len(st.session_state.messages) > st.session_state.settings["max_history"]:
                st.session_state.messages = st.session_state.messages[-st.session_state.settings["max_history"]:]

            st.rerun()

# Footer / help
st.markdown("---")
st.markdown("*Tips: Press Enter to send a message. Use sidebar to adjust settings. Click 'New Chat' to start fresh while saving current chat.*")