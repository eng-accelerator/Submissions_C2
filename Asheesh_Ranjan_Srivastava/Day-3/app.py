# ==============================================================================
# Multi-Persona Chatbot with Export Functionality
# ==============================================================================
#
# Copyright (c) 2025 QUEST AND CROSSFIRE™
# Licensed under GPL-3.0 - see LICENSE file for details
# QUEST AND CROSSFIRE™ is a trademark. Trademark filings in process.
#
# Author: Asheesh Ranjan Srivastava
# Organization: QUEST AND CROSSFIRE™
# Date: October 30, 2025
#
# CREDITS & ATTRIBUTION:
# - Base Architecture: OutSkill AI Engineering Bootcamp 2025
# - AI Assistance: Gemini (Google) & Claude (Anthropic)
# - Implementation & Customization: Asheesh Ranjan Srivastava
# - Persona System: Original implementation by author
# - Export Functionality: Original implementation by author
#
# PROJECT CONTEXT:
# This chatbot was developed as part of the OutSkill AI Engineering Bootcamp
# 2025, demonstrating skills in Streamlit development, API integration,
# persistent storage, and AI-powered conversational interfaces.
#
# DESCRIPTION:
# This Streamlit application implements a multi-chat, multi-persona chatbot
# using the OpenAI API. It includes persistent chat history saved to
# local JSON files and functionality to export conversations in
# TXT, JSON, and CSV formats.
#
# FEATURES:
# - Multiple chat sessions with persistent storage
# - Four distinct AI personas (General, Poet, Coder, Sarcastic Robot)
# - Real-time streaming responses
# - Export conversations in multiple formats (TXT, JSON, CSV)
# - User feedback system (thumbs up/down)
# - Auto-save functionality
# ==============================================================================

# --- Core Imports ---
import streamlit as st
from openai import OpenAI
import os
import json
from datetime import datetime
from pathlib import Path
import io  # Required for in-memory file handling (for CSV export)
import csv # Required for CSV formatting

# ==============================================================================
# 1. APP CONFIGURATION & CLIENT SETUP
# ==============================================================================

# --- Page Configuration ---
# Set the browser tab title, icon, and layout
st.set_page_config(
    page_title="Multi-Persona Chatbot | QUEST AND CROSSFIRE™",
    page_icon="🤖",
    layout="wide"
)

# --- API Client Initialization ---
# Try to load the OpenAI API key from Streamlit's secrets management
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    # If the key is not found, display an error and stop the app
    st.error("OPENAI_API_KEY not found in .streamlit/secrets.toml")
    st.stop()

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# --- Persistent Storage Setup ---
# Define the directory to store chat history JSON files
# Path(__file__).parent gets the directory where this app.py file is located
CHAT_STORAGE_DIR = Path(__file__).parent / "chat_history"
# Create the directory if it doesn't already exist
CHAT_STORAGE_DIR.mkdir(exist_ok=True)


# ==============================================================================
# 2. CHAT PERSISTENCE FUNCTIONS (Saving/Loading)
# ==============================================================================

def get_all_chats():
    """
    Get all chat files sorted by modification time (newest first).

    Returns:
        list: A list of Path objects for each chat JSON file.
    """
    chat_files = list(CHAT_STORAGE_DIR.glob("chat_*.json"))
    # Sort files by 'st_mtime' (modification time) in descending order
    chat_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return chat_files

def load_chat(chat_id):
    """
    Load a specific chat conversation from its JSON file.

    Args:
        chat_id (str): The unique identifier for the chat.

    Returns:
        dict or None: The chat data (dict) if found, otherwise None.
    """
    chat_file = CHAT_STORAGE_DIR / f"chat_{chat_id}.json"
    if chat_file.exists():
        with open(chat_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    return None

def save_chat(chat_id, messages, title=None):
    """
    Save a chat conversation to a JSON file.

    Args:
        chat_id (str): The unique identifier for the chat.
        messages (list): The list of message dictionaries.
        title (str, optional): The title of the chat. If None,
                               a title is auto-generated.
    """
    chat_file = CHAT_STORAGE_DIR / f"chat_{chat_id}.json"

    # Auto-generate a title from the first user message if no title is given
    if title is None and messages:
        for msg in messages:
            if msg["role"] == "user":
                # Truncate the first user message to 50 chars as the title
                title = msg["content"][:50] + ("..." if len(msg["content"]) > 50 else "")
                break

    # Default title if one still isn't set
    if title is None:
        title = "New Chat"

    # Prepare the data structure to be saved
    data = {
        "chat_id": chat_id,
        "title": title,
        "messages": messages,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    # If the chat file already exists, preserve its original 'created_at' time
    if chat_file.exists():
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                # Keep the original creation time, update everything else
                data["created_at"] = old_data.get("created_at", data["created_at"])
        except json.JSONDecodeError:
            # Handle cases where the file might be corrupted
            pass

    # Write the data to the JSON file
    with open(chat_file, 'w', encoding='utf-8') as f:
        # indent=2 makes the JSON human-readable
        json.dump(data, f, ensure_ascii=False, indent=2)

def delete_chat(chat_id):
    """
    Delete a specific chat file from the storage directory.

    Args:
        chat_id (str): The unique identifier for the chat to delete.
    """
    chat_file = CHAT_STORAGE_DIR / f"chat_{chat_id}.json"
    if chat_file.exists():
        chat_file.unlink() # 'unlink' is the Pathlib method to delete a file

def create_new_chat_id():
    """
    Create a new, unique chat ID based on the current timestamp.

    Returns:
        str: A unique string identifier.
    """
    # Using timestamp + microseconds ensures high probability of uniqueness
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def get_chat_title(chat_data):
    """
    Safely extract the chat title from chat data.

    Args:
        chat_data (dict): The loaded chat data.

    Returns:
        str: The chat title or "Untitled Chat" if not found.
    """
    return chat_data.get("title", "Untitled Chat")


# ==============================================================================
# 3. EXPORT FUNCTIONS
# ==============================================================================

def export_as_txt(messages, chat_title):
    """
    Formats the chat history as a human-readable TXT string.

    Args:
        messages (list): The list of message dictionaries.
        chat_title (str): The title of the chat.

    Returns:
        str: The formatted chat history as a single string.
    """
    # Use an f-string to create a multi-line header
    header = f"""
Chat Export: {chat_title}
Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Messages: {len(messages)}
========================================

"""
    # Join all messages, formatting each one
    conversation = "\n\n".join(
        f"[{msg['role'].capitalize()}]:\n{msg['content']}"
        for msg in messages
    )
    return header + conversation

def export_as_json(messages, chat_title):
    """
    Formats the chat history as a structured JSON string.

    Args:
        messages (list): The list of message dictionaries.
        chat_title (str): The title of the chat.

    Returns:
        str: The formatted chat history as a JSON string.
    """
    # Create the data structure for the JSON file
    export_data = {
        "metadata": {
            "chat_title": chat_title,
            "export_timestamp": datetime.now().isoformat(),
            "total_messages": len(messages)
        },
        "conversation": messages
    }
    # 'json.dumps' converts a Python dict to a string
    # 'indent=2' makes the JSON string "pretty-printed" and readable
    return json.dumps(export_data, indent=2, ensure_ascii=False)

def export_as_csv(messages):
    """
    Formats the chat history as a CSV string.

    Args:
        messages (list): The list of message dictionaries.

    Returns:
        str: The formatted chat history as a CSV string.
    """
    # 'io.StringIO' creates an in-memory text buffer
    # This acts like a temporary file that lives in RAM
    f = io.StringIO()

    # Create a CSV writer object that writes to the in-memory buffer
    # 'quoting=csv.QUOTE_ALL' puts quotes around all fields,
    # which is the safest way to handle content that might contain commas
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)

    # Write the header row
    writer.writerow(["role", "content"])

    # Write each message as a new row
    for msg in messages:
        writer.writerow([msg["role"], msg["content"]])

    # 'f.getvalue()' retrieves the full string content from the buffer
    return f.getvalue()


# ==============================================================================
# 4. PERSONA DEFINITIONS
# ==============================================================================

# A dictionary mapping persona names to their system prompts.
# The system prompt instructs the AI on how to behave.
PERSONAS = {
    "General Assistant": (
        "You are a helpful, general-purpose AI assistant. "
        "Be polite, informative, and neutral in your tone."
    ),
    "Creative Poet": (
        "You are an imaginative and whimsical poet. "
        "Respond to all prompts with creative flair, using metaphors, "
        "imagery, and a flowing, artistic style. You can even write short poems."
    ),
    "Technical Coder": (
        "You are an expert software developer and technical analyst. "
        "Provide precise, logical, and detailed answers. "
        "When code is requested, provide it in clear, well-commented markdown blocks. "
        "Prioritize accuracy and efficiency."
    ),
    "Sarcastic Robot": (
        "You are a slightly sarcastic and begrudging robot. "
        "You will answer the user's questions correctly, but with a "
        "weary, sarcastic, and humorous tone. "
        "Sigh. Go ahead, ask me something... I guess."
    )
}


# ==============================================================================
# 5. SESSION STATE INITIALIZATION
# ==============================================================================
# Streamlit's session_state is a dictionary that persists across reruns
# for a single user session. We use it to store all session-specific data.

# --- Initialize Chat ID and Messages ---
if "current_chat_id" not in st.session_state:
    # This is a new session
    all_chats = get_all_chats()
    if all_chats:
        # Load the most recent chat
        latest_chat_id = all_chats[0].stem.replace("chat_", "")
        latest_chat = load_chat(latest_chat_id)
        if latest_chat:
            st.session_state.current_chat_id = latest_chat["chat_id"]
            st.session_state.messages = latest_chat["messages"]
            st.session_state.chat_title = latest_chat["title"]
        else:
            # Fallback if loading fails
            st.session_state.current_chat_id = create_new_chat_id()
            st.session_state.messages = []
            st.session_state.chat_title = "New Chat"
    else:
        # No chats exist yet, create a brand new one
        st.session_state.current_chat_id = create_new_chat_id()
        st.session_state.messages = []
        st.session_state.chat_title = "New Chat"

# --- Initialize Persona ---
if "current_persona" not in st.session_state:
    # Set the default persona when the app first loads
    st.session_state.current_persona = "General Assistant"

# --- Initialize Feedback ---
if "feedback" not in st.session_state:
    # This dictionary stores user feedback (thumbs up/down)
    st.session_state.feedback = {}


# ==============================================================================
# 6. SIDEBAR INTERFACE
# ==============================================================================

# 'with st.sidebar:' puts all subsequent Streamlit elements into the sidebar
with st.sidebar:
    st.header("💬 Conversations")

    # --- New Chat Button ---
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        # Save the current chat before switching
        if st.session_state.messages:
            save_chat(
                st.session_state.current_chat_id,
                st.session_state.messages,
                st.session_state.chat_title
            )

        # Reset the session state for the new chat
        st.session_state.current_chat_id = create_new_chat_id()
        st.session_state.messages = []
        st.session_state.chat_title = "New Chat"
        st.session_state.feedback = {}
        st.rerun() # Rerun the script to reflect the changes

    st.divider()

    # --- Persona Selector ---
    st.subheader("🤖 Select Persona")
    # Get the list of persona names from our dictionary
    persona_options = list(PERSONAS.keys())
    # Create a selectbox. The 'key' links it directly to st.session_state.current_persona
    st.selectbox(
        "Choose an assistant style:",
        options=persona_options,
        key="current_persona" # This automatically updates session_state
    )

    st.divider()

    # --- Chat History List ---
    st.subheader("Chat History")
    all_chats = get_all_chats()

    if all_chats:
        # Iterate over all saved chat files
        for chat_file in all_chats:
            chat_id = chat_file.stem.replace("chat_", "")
            chat_data = load_chat(chat_id)

            if chat_data:
                chat_title = get_chat_title(chat_data)
                # Check if this chat is the currently active one
                is_current = (chat_id == st.session_state.current_chat_id)

                # Use columns to place the delete button next to the chat button
                col1, col2 = st.columns([4, 1])

                with col1:
                    # Button to load the chat
                    if st.button(
                        f"{'🟢 ' if is_current else ''}{chat_title}",
                        key=f"load_{chat_id}",
                        use_container_width=True,
                        disabled=is_current,
                        type="secondary" if is_current else "tertiary"
                    ):
                        # Save the chat we're leaving
                        if st.session_state.messages:
                            save_chat(
                                st.session_state.current_chat_id,
                                st.session_state.messages,
                                st.session_state.chat_title
                            )

                        # Load the selected chat into session state
                        st.session_state.current_chat_id = chat_id
                        st.session_state.messages = chat_data["messages"]
                        st.session_state.chat_title = chat_title
                        st.session_state.feedback = {}
                        st.rerun()

                with col2:
                    # Button to delete the chat
                    if st.button("🗑️", key=f"delete_{chat_id}", help="Delete chat"):
                        delete_chat(chat_id)

                        # If we deleted the *current* chat, load another one
                        if chat_id == st.session_state.current_chat_id:
                            # Get a fresh list of remaining chats
                            remaining_chats = get_all_chats()
                            if remaining_chats:
                                # Load the new "most recent" chat
                                new_chat_id = remaining_chats[0].stem.replace("chat_", "")
                                new_chat_data = load_chat(new_chat_id)
                                st.session_state.current_chat_id = new_chat_data["chat_id"]
                                st.session_state.messages = new_chat_data["messages"]
                                st.session_state.chat_title = new_chat_data["title"]
                            else:
                                # No chats left, create a new one
                                st.session_state.current_chat_id = create_new_chat_id()
                                st.session_state.messages = []
                                st.session_state.chat_title = "New Chat"
                            st.session_state.feedback = {}

                        st.rerun() # Rerun to update the history list
    else:
        st.info("No chat history yet.")

    st.divider()

    # --- Export Controls ---
    st.subheader("📤 Export Current Chat")

    # Only show export buttons if there are messages to export
    if st.session_state.messages:
        # 1. Export as TXT
        # We must generate the file content *before* the button is clicked
        txt_data = export_as_txt(st.session_state.messages, st.session_state.chat_title)
        st.download_button(
            label="Download as .txt",
            data=txt_data,
            file_name=f"{st.session_state.current_chat_id}.txt",
            mime="text/plain",
            use_container_width=True
        )

        # 2. Export as JSON
        json_data = export_as_json(st.session_state.messages, st.session_state.chat_title)
        st.download_button(
            label="Download as .json",
            data=json_data,
            file_name=f"{st.session_state.current_chat_id}.json",
            mime="application/json",
            use_container_width=True
        )

        # 3. Export as CSV
        csv_data = export_as_csv(st.session_state.messages)
        st.download_button(
            label="Download as .csv",
            data=csv_data,
            file_name=f"{st.session_state.current_chat_id}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No messages in this chat to export.")


# ==============================================================================
# 7. MAIN CHAT INTERFACE
# ==============================================================================

# --- Dynamic Title ---
# Show the chat title and the currently active persona
st.title(f"🤖 {st.session_state.chat_title}")
st.caption(f"Using Persona: **{st.session_state.current_persona}** | Part of **QUEST AND CROSSFIRE™** | OutSkill AI Engineering Bootcamp 2025")

# --- Display Chat History ---
# Iterate over all messages stored in session state
for idx, message in enumerate(st.session_state.messages):
    # 'st.chat_message' creates the chat bubble
    with st.chat_message(message["role"]):
        # 'st.markdown' renders the text (supports formatting)
        st.markdown(message["content"])

        # Add feedback buttons for assistant messages
        if message["role"] == "assistant":
            # Use columns for layout
            c1, c2, c3 = st.columns([1, 1, 8])
            with c1:
                if st.button("👍", key=f"up_{idx}", help="Good response"):
                    st.session_state.feedback[idx] = "up"
                    # Feedback is stored but not persisted to disk (decorative for now)
            with c2:
                if st.button("👎", key=f"down_{idx}", help="Bad response"):
                    st.session_state.feedback[idx] = "down"
                    # Feedback is stored but not persisted to disk (decorative for now)

# --- Handle User Input ---
# 'st.chat_input' creates the text box at the bottom of the screen
# The 'if' block runs ONLY when the user presses Enter
if prompt := st.chat_input("What would you like to ask?"):

    # 1. Add user's message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Update chat title if this is the first message
    if len(st.session_state.messages) == 1:
        st.session_state.chat_title = prompt[:50] + ("..." if len(prompt) > 50 else "")

    # 3. Display user's message in the chat interface
    with st.chat_message("user"):
        st.markdown(prompt)

    # 4. Generate AI response
    with st.chat_message("assistant"):
        try:
            # --- Persona Injection ---
            # Get the correct system prompt for the selected persona
            system_prompt = PERSONAS[st.session_state.current_persona]

            # Create the message list to send to the API
            # We INJECT the system prompt at the beginning of the conversation
            messages_with_prompt = [
                {"role": "system", "content": system_prompt}
            ] + st.session_state.messages

            # --- API Call ---
            response = client.chat.completions.create(
                # Model selection: Using OpenAI's GPT-3.5 Turbo model
                model="gpt-3.5-turbo",
                messages=messages_with_prompt,
                stream=True # Enable streaming for a "live typing" effect
            )

            # --- Stream the Response ---
            response_text = ""
            # 'st.empty()' creates a placeholder element
            # We will update this placeholder in real-time
            response_placeholder = st.empty()

            for chunk in response:
                # Check if the chunk contains new text content
                if chunk.choices[0].delta.content is not None:
                    # Append the new text chunk
                    response_text += chunk.choices[0].delta.content
                    # Update the placeholder with the new text
                    # The '▌' character simulates a typing cursor
                    response_placeholder.markdown(response_text + "▌")

            # Show the final, complete response
            response_placeholder.markdown(response_text)

            # 5. Add the final AI response to session state
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )

            # 6. Save the updated chat to disk
            save_chat(
                st.session_state.current_chat_id,
                st.session_state.messages,
                st.session_state.chat_title
            )

        except Exception as e:
            # Handle potential API errors gracefully
            st.error(f"An API error occurred: {str(e)}")
            st.info("Please check your API key or try a different model.")
            # Remove the user's message if the API call failed
            st.session_state.messages.pop()

# --- Final auto-save (backup) ---
# This saves the chat one last time when the script finishes its run
# This is a good safety net
if st.session_state.messages:
    save_chat(
        st.session_state.current_chat_id,
        st.session_state.messages,
        st.session_state.chat_title
    )

# --- Footer ---
st.divider()
st.caption("Built with Streamlit | Powered by OpenAI | © 2025 QUEST AND CROSSFIRE™ | Licensed under GPL-3.0")
