# Multi-chat app with persistent history using OpenRouter
# Features: Multiple conversations, persistent storage, chat history in sidebar


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

# Setup persistent storage directory
CHAT_STORAGE_DIR = Path(__file__).parent / "chat_history"
CHAT_STORAGE_DIR.mkdir(exist_ok=True)

# ============================================================================
# CHAT PERSISTENCE FUNCTIONS
# ============================================================================

def get_all_chats():
    """Get all chat files sorted by modification time (newest first)"""
    chat_files = list(CHAT_STORAGE_DIR.glob("chat_*.json"))
    chat_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return chat_files

def load_chat(chat_id):
    """Load a specific chat by ID"""
    chat_file = CHAT_STORAGE_DIR / f"chat_{chat_id}.json"
    if chat_file.exists():
        with open(chat_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    return None

def save_chat(chat_id, messages, title=None):
    """Save chat to disk"""
    chat_file = CHAT_STORAGE_DIR / f"chat_{chat_id}.json"

    # Auto-generate title from first user message if not provided
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

    # If file exists, preserve created_at
    if chat_file.exists():
        with open(chat_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            data["created_at"] = old_data.get("created_at", data["created_at"])

    with open(chat_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def delete_chat(chat_id):
    """Delete a chat file"""
    chat_file = CHAT_STORAGE_DIR / f"chat_{chat_id}.json"
    if chat_file.exists():
        chat_file.unlink()

def create_new_chat():
    """Create a new chat with unique ID"""
    chat_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return chat_id

def get_chat_title(chat_data):
    """Extract chat title from chat data"""
    return chat_data.get("title", "Untitled Chat")

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

# Initialize current chat ID
if "current_chat_id" not in st.session_state:
    # Try to load the most recent chat, or create new one
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

# Initialize messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize chat title
if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"

# Initialize feedback
if "feedback" not in st.session_state:
    st.session_state.feedback = {}

# Initialize dark mode
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# ============================================================================
# SIDEBAR: CHAT MANAGEMENT
# ============================================================================

with st.sidebar:
    target_language = st.selectbox(
        "Target Language:",
        ["English", "Spanish", "French", "German", "Italian"]
    )
    st.header("💬 Conversations")

    # New Chat button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        # Save current chat before creating new one
        if st.session_state.messages:
            save_chat(
                st.session_state.current_chat_id,
                st.session_state.messages,
                st.session_state.chat_title
            )

        # Create new chat
        st.session_state.current_chat_id = create_new_chat()
        st.session_state.messages = []
        st.session_state.chat_title = "New Chat"
        st.session_state.feedback = {}
        st.rerun()

    st.divider()

    # List all chats
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
                    # Show current chat with indicator
                    button_label = f"{'🟢 ' if is_current else ''}{chat_title}"
                    if st.button(
                        button_label,
                        key=f"load_{chat_id}",
                        use_container_width=True,
                        disabled=is_current,
                        type="secondary" if is_current else "tertiary"
                    ):
                        # Save current chat before switching
                        if st.session_state.messages:
                            save_chat(
                                st.session_state.current_chat_id,
                                st.session_state.messages,
                                st.session_state.chat_title
                            )

                        # Load selected chat
                        st.session_state.current_chat_id = chat_id
                        st.session_state.messages = chat_data["messages"]
                        st.session_state.chat_title = chat_title
                        st.session_state.feedback = {}
                        st.rerun()

                with col2:
                    # Delete button (only for non-current chats or if it's the only chat)
                    if st.button("🗑️", key=f"delete_{chat_id}", help="Delete chat"):
                        delete_chat(chat_id)

                        # If we deleted the current chat, switch to another or create new
                        if chat_id == st.session_state.current_chat_id:
                            remaining_chats = [c for c in all_chats if c.stem.replace("chat_", "") != chat_id]
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

    # Settings section
    st.subheader("⚙️ Settings")
    dark_mode = st.toggle("Dark mode", value=st.session_state.dark_mode)
    st.session_state.dark_mode = dark_mode

    # Clear current chat
    if st.button("🗑️ Clear Current Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback = {}
        st.session_state.chat_title = "New Chat"
        save_chat(st.session_state.current_chat_id, [], "New Chat")
        st.rerun()

# ============================================================================
# APPLY THEMING
# ============================================================================

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

# ============================================================================
# MAIN CHAT INTERFACE
# ============================================================================

# App title with current chat title
st.title(f"🤖 {st.session_state.chat_title}")

# Summarize conversation - for entire current chat
with st.expander("📝 Summarize Conversation", expanded=False):
    st.write("Generate a summary of the entire conversation in this chat")

    if st.button("Generate Summary", use_container_width=True):
        if not st.session_state.messages:
            st.warning("No messages to summarize yet!")
        else:
            try:
                with st.spinner("Generating summary..."):
                    summary_resp = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "system", "content": "Summarize the conversation into concise key points and action items."},
                            *st.session_state.messages,
                        ],
                        stream=False,
                        extra_body={}
                    )
                    summary_text = summary_resp.choices[0].message.content.strip()
                    st.markdown("### Summary")
                    st.markdown(summary_text)
            except Exception as e:
                st.error(f"Summary failed: {e}")

# Display chat history
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

# Handle user input
if prompt := st.chat_input("What would you like to know?"):
    prompt1 = f"""
    Translate "{prompt}" to {target_language}.

    Also provide:
    - Alternative translations if applicable
    - Cultural context for idioms or expressions
    - Formality level notes

    Format clearly for the user.
    """



    #prompt1 = f"""
    #Translate this text to {target_language}: "{prompt}"

    #Respond in JSON format:
    #{{
    #    "detected_language": "language name",
    #    "translation": "translated text",
    #    "confidence": "high/medium/low"
    #}}
    #"""


    #prompt1 = f"""
    #    Text: "{prompt}"
    #    Task:
    #    1. Identify the language
    #    2. Translate to {target_language}

    #    Format:
    #    Language: [detected language] \n        
    #   Translation: [translation here]
    #   """
    
    
    #translation_prompt = f"""You are a professional translator.
    #For the text: "{prompt}"

    #1. Detect the source language
    #2. Translate it to {target_language}
    #3. Format your response clearly

    #Be accurate and natural."""




    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt1})
    st.session_state.messages.append({"role": "system", "content": prompt1})

    # Update chat title if this is the first message
    if len(st.session_state.messages) == 1:
        st.session_state.chat_title = prompt[:50] + ("..." if len(prompt) > 50 else "")

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=st.session_state.messages,
                stream=True,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8503",
                    "X-Title": "My ChatBot"
                },
                extra_body={}
            )

            # Stream the response
            response_text = ""
            response_placeholder = st.empty()

            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    # Clean up unwanted tokens
                    content = chunk.choices[0].delta.content
                    content = (
                        content.replace('<s>', '')
                        .replace('<|im_start|>', '')
                        .replace('<|im_end|>', '')
                        .replace("<|OUT|>", "")
                    )
                    response_text += content
                    response_placeholder.markdown(response_text + "▌")


            #import json
            #result = json.loads(response_text)
            #if "translation_history" not in st.session_state:
            #    st.session_state.translation_history = []

            



            # Final cleanup of response text
            response_text = (
                response_text.replace('<s>', '')
                .replace('<|im_start|>', '')
                .replace('<|im_end|>', '')
                .replace("<|OUT|>", "")
                .strip()
            )
            response_placeholder.markdown(response_text)

            # Add assistant response to chat history
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )

            # Save chat to disk
            save_chat(
                st.session_state.current_chat_id,
                st.session_state.messages,
                st.session_state.chat_title
            )

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Please check your API key and try again.")

# Auto-save chat when messages change (backup mechanism)
if st.session_state.messages:
    save_chat(
        st.session_state.current_chat_id,
        st.session_state.messages,
        st.session_state.chat_title
    )
if "translation_history" not in st.session_state:
    st.session_state.translation_history = []

# After each translation:
st.session_state.translation_history.append({
    "original": prompt1,
    "translation": response_text,
    #"source_lang": ,
    "target_lang": target_language,
    "timestamp": datetime.now()
})

