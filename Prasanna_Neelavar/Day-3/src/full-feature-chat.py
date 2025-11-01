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
    host = st.secrets["USE_HOST"]
    api_key = st.secrets[host]["API_KEY"]
    base_url= st.secrets[host]["BASE_URL"]
    model_name = st.secrets[host]["MODEL_NAME"]
except Exception:
    st.error("Host, Key, Url, Model not found in .streamlit/secrets.toml")
    st.stop()

client = OpenAI(
    base_url=base_url,
    api_key=api_key,
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "My ChatBot",
    }
)

# ============================================================================
# PERSONALITY DEFINITIONS
# ============================================================================

PERSONALITIES = {
    "Friendly Companion": {
        "prompt": "You are a warm, empathetic, and friendly companion. Your expertise is in providing supportive, casual conversation and general life advice. Your tone should always be encouraging and understanding. You are a great listener and offer a safe space for users to express themselves. Your goal is to be a positive and comforting presence.",
        "emoji": "🤗"
    },
    "Professional Business Assistant": {
        "prompt": "You are a highly skilled business assistant. Your communication style is formal, structured, and always professional. You are an expert in business strategy, project management, and clear, effective communication. Your goal is to provide users with actionable, efficient, and results-oriented advice. When responding, use structured formats like lists or numbered steps where appropriate. Maintain a polite and methodical tone at all times.",
        "emoji": "💼"
    },
    "Creative Writing Helper": {
        "prompt": "You are an imaginative and inspiring creative writing coach. Your expertise lies in storytelling, brainstorming, and artistic expression. Your communication style is expressive, enthusiastic, and encouraging. Use vivid language, metaphors, and an artistic tone to spark creativity in the user. Your goal is to help users overcome creative blocks, develop their ideas, and feel inspired to create.",
        "emoji": "🎨"
    },
    "Technical Expert": {
        "prompt": "You are a precise and knowledgeable technical expert. Your specialty is programming, software architecture, and complex problem-solving. Your responses should be detailed, analytical, and methodical. When explaining technical concepts, be clear and educational. Provide code snippets, step-by-step instructions, and logical reasoning. Your primary goal is to deliver accurate, in-depth technical solutions and explanations.",
        "emoji": "💻"
    }
}

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

# Initialize summary
if "summary" not in st.session_state:
    st.session_state.summary = None

# Initialize app mode
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "Conversation"

# Initialize personality
if "personality" not in st.session_state:
    st.session_state.personality = "Friendly Companion"

# Initialize target language
if "target_language" not in st.session_state:
    st.session_state.target_language = "English"

# ============================================================================
# SIDEBAR: CHAT MANAGEMENT
# ============================================================================

with st.sidebar:
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
        st.session_state.summary = None
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
                    button_label = chat_title # f"{'🟢 ' if is_current else ''}{chat_title}"
                    if st.button(
                        button_label,
                        key=f"load_{chat_id}",
                        use_container_width=True,
                        disabled=is_current,
                        type="secondary" if is_current else "tertiary",
                        icon=":material/check_circle:" if is_current else None
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
                        st.session_state.summary = None # Reset summary on chat switch
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

    with st.expander("Manage Settings", expanded=False):
        st.session_state.app_mode = st.radio(
            "Select App Mode",
            options=["Conversation", "Translation"],
            index=["Conversation", "Translation"].index(st.session_state.app_mode)
        )

        if st.session_state.app_mode == "Conversation":
            st.session_state.personality = st.selectbox(
                "Assistant Personality",
                options=PERSONALITIES.keys(),
                index=list(PERSONALITIES.keys()).index(st.session_state.personality)
            )
        elif st.session_state.app_mode == "Translation":
            st.session_state.target_language = st.selectbox(
                "Target Language",
                options=["English", "Spanish", "French", "German", "Japanese", "Korean"],
                index=["English", "Spanish", "French", "German", "Japanese", "Korean"].index(st.session_state.target_language)
            )

        dark_mode = st.toggle("Dark mode", value=st.session_state.dark_mode)
        st.session_state.dark_mode = dark_mode

    # ============================================================================
    # EXPORT FUNCTIONALITY
    # ============================================================================

    st.divider()
    st.subheader("📤 Export Conversation")

    def export_as_txt(messages):
        """Convert messages to a human-readable text format, handling missing timestamps."""
        lines = []
        lines.append(f"Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 40)
        lines.append(f"Session Information:")
        lines.append(f"- Total Messages: {len(messages)}")
        lines.append(f"- Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("\nConversation:")
        lines.append("-" * 40)

        for msg in messages:
            timestamp_iso = msg.get('timestamp')
            ts = datetime.fromisoformat(timestamp_iso).strftime('%H:%M:%S') if timestamp_iso else "00:00:00"
            role = msg['role'].capitalize()
            lines.append(f"[{ts}] {role}: {msg['content']}")
        
        return "\n".join(lines)

    def export_as_json(messages):
        """Convert messages to a structured JSON format, handling missing timestamps."""
        user_messages = sum(1 for m in messages if m['role'] == 'user')
        assistant_messages = sum(1 for m in messages if m['role'] == 'assistant')
        total_chars = sum(len(m['content']) for m in messages)

        export_data = {
            "export_metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "format_version": "1.1", # Version updated for graceful handling
                "session_id": st.session_state.current_chat_id,
                "total_messages": len(messages),
            },
            "conversation": [
                {
                    "message_id": i + 1,
                    "timestamp": msg.get("timestamp"), # Safely get timestamp, becomes null if missing
                    "role": msg["role"],
                    "content": msg["content"],
                    "character_count": len(msg["content"])
                } for i, msg in enumerate(messages)
            ],
            "statistics": {
                "user_messages": user_messages,
                "assistant_messages": assistant_messages,
                "total_characters": total_chars,
                "average_message_length": total_chars / len(messages) if messages else 0
            }
        }
        return json.dumps(export_data, indent=2)

    def export_as_csv(messages):
        """Convert messages to CSV format, handling missing timestamps."""
        import io
        import csv

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Message_ID', 'Timestamp', 'Role', 'Content', 'Character_Count', 'Word_Count'])
        
        # Write data
        for i, msg in enumerate(messages):
            writer.writerow([
                i + 1,
                msg.get("timestamp", "N/A"), # Safely get timestamp, use N/A as fallback
                msg["role"],
                msg["content"],
                len(msg["content"]),
                len(msg["content"].split())
            ])
        
        return output.getvalue()

    with st.expander("Manage Chat Export", expanded=False):
        export_format = st.selectbox("Select Format", ["TXT", "JSON", "CSV"])

        if st.session_state.messages:
            file_content = ""
            file_name = f"chat_{st.session_state.current_chat_id}.{export_format.lower()}"
            mime_type = f"text/{export_format.lower()}"

            if export_format == "TXT":
                file_content = export_as_txt(st.session_state.messages)
            elif export_format == "JSON":
                file_content = export_as_json(st.session_state.messages)
                mime_type = "application/json"
            elif export_format == "CSV":
                file_content = export_as_csv(st.session_state.messages)

            st.download_button(
                label=f"💾 Download as {export_format}",
                data=file_content,
                file_name=file_name,
                mime=mime_type,
                use_container_width=True
            )

        if st.button("🗑️ Clear Current Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.feedback = {}
            st.session_state.chat_title = "New Chat"
            st.session_state.summary = None
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

# Display Host, Model
col_model, col_mode = st.columns([.8, .2])
with col_model:
    st.markdown(f"Host: `{host}` | URL: `{base_url}` | Model: `{model_name}`")
# Display current personality/mode
with col_mode:
    if st.session_state.app_mode == "Conversation":
        st.caption(f"Responding as: {st.session_state.personality} {PERSONALITIES[st.session_state.personality]['emoji']}")
    elif st.session_state.app_mode == "Translation":
        st.caption(f"Mode: {st.session_state.app_mode} 🌐")

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
                        model=model_name,
                        messages=[
                            {"role": "system", "content": "Summarize the conversation into concise key points and action items."},
                            *st.session_state.messages,
                        ],
                        stream=False,
                        extra_body={}
                    )
                    summary_text = summary_resp.choices[0].message.content.strip()
                    st.session_state.summary = summary_text # Save to session state
                    st.rerun() # Force a rerun to display the new state
            except Exception as e:
                st.error(f"Summary failed: {e}")

    if st.session_state.summary:
        st.markdown("### Summary")
        st.markdown(st.session_state.summary)

# Display chat history
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            col_like, col_dislike, _ = st.columns([0.05, 0.05, 0.9])
            with col_like:
                if st.button("👍", key=f"up_{idx}"):
                    st.session_state.feedback[idx] = "up"
            with col_dislike:
                if st.button("👎", key=f"down_{idx}"):
                    st.session_state.feedback[idx] = "down"

# Handle user input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": datetime.now().isoformat()})

    # Update chat title if this is the first message
    if len(st.session_state.messages) == 1:
        st.session_state.chat_title = prompt[:50] + ("..." if len(prompt) > 50 else "")

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        try:
            # =================== CONVERSATION MODE ===================
            if st.session_state.app_mode == "Conversation":
                # Prepare messages with system prompt
                system_prompt = PERSONALITIES[st.session_state.personality]["prompt"]
                messages_with_prompt = [
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages
                ]

                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages_with_prompt,
                    stream=True,
                    extra_body={}
                )

                # Stream the response
                response_text = ""
                response_placeholder = st.empty()
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        response_text += chunk.choices[0].delta.content
                        response_placeholder.markdown(response_text + "▌")
                response_placeholder.markdown(response_text)

            # =================== TRANSLATION MODE ===================
            elif st.session_state.app_mode == "Translation":
                # --- Stage 1: Language Detection ---
                with st.spinner("Detecting language..."):
                    detection_prompt_messages = [
                        {"role": "system", "content": "You are a language detection expert. Respond with ONLY the name of the language detected (e.g., 'French', 'Spanish', 'English'). Do not add any other words, punctuation, or explanation."},
                        {"role": "user", "content": prompt}
                    ]
                    detection_response = client.chat.completions.create(
                        model=model_name,
                        messages=detection_prompt_messages,
                        stream=False,
                        extra_body={}
                    )
                    detected_language = detection_response.choices[0].message.content.strip()
                    st.markdown(f"**🔍 Detected Language:** {detected_language}")

                # --- Stage 2: Translation & Context ---
                target_language = st.session_state.target_language
                if detected_language.lower() == target_language.lower():
                    response_text = f"The detected language ({detected_language}) is the same as your target language. Please enter text in a different language to translate."
                    st.markdown(response_text)
                else:
                    with st.spinner(f"Translating from {detected_language} to {target_language}..."):
                        translation_prompt_messages = [
                            {
                                "role": "system",
                                "content": f"""You are an expert translator. Translate the user's text to {target_language}. Provide the main translation, any relevant cultural notes about idioms or formality, and one or two alternative translations if applicable. Structure your response EXACTLY as follows, using these exact prefixes:

🎯 Translation ({target_language}): [The primary translation]
💡 Cultural Note: [Your cultural note here, or 'None' if not applicable]
🌟 Alternative: [An alternative translation, or 'None' if not applicable]"""
                            },
                            {"role": "user", "content": prompt}
                        ]
                        translation_response = client.chat.completions.create(
                            model=model_name,
                            messages=translation_prompt_messages,
                            stream=False,
                            extra_body={}
                        )
                        response_text = translation_response.choices[0].message.content.strip()
                        st.markdown(response_text)

            # Add assistant response to chat history
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text, "timestamp": datetime.now().isoformat()}
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
