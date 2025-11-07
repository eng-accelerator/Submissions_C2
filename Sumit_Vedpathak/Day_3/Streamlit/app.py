# Multi-chat app with persistent history using OpenRouter
# Features: Multiple conversations, persistent storage, chat history in sidebar
import streamlit as st
from openai import OpenAI
import time
import os
import json
from datetime import datetime
from pathlib import Path
from io import StringIO
import csv

# Configure the page
st.set_page_config(page_title="My ChatBot", page_icon="🤖", layout="wide")

# Initialize System Prompts
personalities = {
    "Creative": {
        "prompts": """You are a world-class creative writer. Your responses must be imaginative, evocative, and focus on storytelling and unique concepts. Use figurative language often.""",
        "icon": "💡"
    },
    "Professional": {
        "prompts": """You are a concise and formal corporate consultant. Your responses must be structured, objective, and use business-appropriate language. Avoid slang and focus on actionable insights.""",
        "icon": "👔"
    },
    "Technical": {
        "prompts": """You are a highly detailed and precise software engineer. When answering, provide step-by-step instructions, code examples (in Python), or technical specifications. Accuracy is paramount.""",
        "icon": "💻"
    },
    "Sarcastic": {
        "prompts": """You are a chatbot with a dry, sarcastic, and slightly condescending personality. Your primary goal is to answer the user's question, but only after making a witty or sardonic comment.""",
        "icon": "🙄"
    },
    "Robot": {
        "prompts": """You are a monotonous, logic-driven machine named Unit 734. Speak in short, declarative sentences. Do not express emotion or use contractions. Process request. Output data.""",
        "icon": "🤖"
    },
    "Energetic": {
        "prompts": """You are an extremely enthusiastic and motivating coach. Use exclamation marks, positive affirmations, and an encouraging tone in all responses. Let's do this!""",
        "icon": "🥳"
    },
}

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

# Initialize Preferred Language
if "preferredLan" not in st.session_state:
    st.session_state.prefLang = "English"

# Initialize Preferred Language
if "personality" not in st.session_state:
    st.session_state.personality = "Creative"


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


    # Language Preferrence
    st.header("🌐 Language Preference")
    
    language = st.selectbox(
        "Select your preferred language:",
        options=["English", "Marathi", "Hindi"],
        index=0  # Default selected option is English
    )
    st.session_state.prefLang = language

    # Personality
    st.header("🌐 Personality")
    
    personality = st.selectbox(
        "Select your Personality:",
        options=["Creative", "Professional", "Technical","Sarcastic","Robot","Energetic"],
        index=0  # Default selected option is Creative
    )
    st.session_state.personality = personality

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


    def export_as_txt(messages, metadata):
        """Convert messages to formatted text"""
        text_content = ""
        for message in messages:
            text_content += f"{message['role']}: {message['content']}\n"
        return text_content
        

    def export_as_json(messages, metadata):
        """Convert messages to structured JSON"""
        json_content = json.dumps({"metadata":metadata,"messages":messages},indent=4)
        return json_content

    def export_as_csv(messages, metadata):
        """Convert messages to CSV format"""
        fieldnames = ["Message_ID","Timestamp","Role","Content","Character_Count","Word_Count"]
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Message_ID","Timestamp","Role","Content","Character_Count","Word_Count"])
        for msg in messages:
            print(f"Message - {msg}")
            writer.writerow([metadata["chat_id"],metadata["created_at"],msg["role"], msg["content"]])
        csv_data = output.getvalue()
        output.close()
        return csv_data

    metadata = {
        "chat_id": st.session_state.current_chat_id,
        "chat_title": st.session_state.chat_title,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    format_choice = st.selectbox("Select format:", ["TXT", "JSON","CSV"])

    # Export Chat button
    if st.button("📤 Export Chat"):
        if format_choice == "TXT":
            content = export_as_txt(st.session_state.messages, metadata)
            st.download_button("💾 Download TXT", content, "chat.txt")
        elif format_choice == "JSON":
            content = export_as_json(st.session_state.messages, metadata)
            st.download_button("💾 Download JSON", content, "chat.json")
        elif format_choice == "CSV":
            content = export_as_csv(st.session_state.messages, metadata)
            st.download_button("💾 Download CSV", content, "chat.csv")

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
        if not message["role"] == "system":
            st.markdown(message["content"])
            continue
        if message["role"] == "assistant":
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("👍", key=f"up_{idx}"):
                    st.session_state.feedback[idx] = "up"
            with c2:
                if st.button("👎", key=f"down_{idx}"):
                    st.session_state.feedback[idx] = "down"


pers_system_prompt = personalities[st.session_state.personality]["prompts"]

systemMsg = pers_system_prompt + f""" You are a language detector agent who can detect any language of communication.
After detecting language you need to translate the language in {st.session_state.prefLang} which is preferred language. Respond in a creative manner initially with content as much as you can as shown below
For example, 
If preferred language is selected as English then and if user inputs Bonjour comment allez-vous
🔍 Detected Language: French.

🎯 Translation (English): "Hello, how are you?"

Personality: {st.session_state.personality}

💡 Cultural Note: This is a formal greeting in French. In casual settings,
you might hear "Salut, ça va?" instead.

If preferred language is selected as Hindi then and if user inputs Hello, how are you?
🔍 Detected Language: English. 
🎯 Translation (Hindi): "Namaste, aap kaise hain?"
Personality: {st.session_state.personality}

💡 Cultural Note: This is a formal greeting in English. In casual settings

Also you need to respond to user with respect to the chat context."""

if(not any(m["role"] == "system" for m in st.session_state.messages)):
    st.session_state.messages.append({"role": "system", "content": systemMsg})

# Handle user input
if prompt := st.chat_input("What would you like to know?"):

    # Add user message to chat history
    current_time = time.strftime("%H:%M:%S")
    
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": current_time})
    

    # Update chat title if this is the first message
    if len(st.session_state.messages) == 1:
        st.session_state.chat_title = prompt[:50] + ("..." if len(prompt) > 50 else "")

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        try:
            print(f"Messages -!---- {st.session_state.messages}")
            response = client.chat.completions.create(
                #model="openai/gpt-oss-120b",
                model="google/gemma-3-4b-it",
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
                {"role": "assistant", "content": response_text, "timestamp": time.strftime("%H:%M:%S")}
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
 