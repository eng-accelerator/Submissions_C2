from httpx import Client
import streamlit as st
import time
from io import StringIO
import pandas as pd
import os
import json
from dotenv import load_dotenv
from openai import OpenAI



# --- Helper Functions for Actions ---

def clear_chat():
    """Clears the chat history in the session state and refreshes the greeting."""
    st.session_state.messages = []
    initial_greeting = f"Hello! I'm your demo assistant. How can I help you today? My current style is **{st.session_state.response_style}**."
    st.session_state.messages.append({"role": "assistant", "content": initial_greeting, "timestamp": time.strftime("%H:%M:%S")})
    st.rerun() # Reruns the app to immediately show the cleared state

def download_chat_history():
    """Formats the chat history into a downloadable .txt file."""
    chat_text = []
    
    # Iterate through messages and format them
    for message in st.session_state.messages:
        role = message["role"].capitalize()
        timestamp = message.get("timestamp", "N/A")
        content = message["content"]
        
        chat_text.append(f"[{timestamp}] {role}: {content}\n{'='*50}\n")
    
    # Join all messages into a single string
    return "".join(chat_text)

# --- Configuration for Page and Sidebar ---

api_key = st.secrets["OPEN_ROUTER"]

Client = OpenAI(base_url="",api_key=api_key,default_headers={
    "HTTP-Referer": "http://localhost:8504",
    "X-Title": "My ChatBot",})



# Set a title for the page and use a wider layout
st.set_page_config(page_title="Custom Streamlit Chatbot", layout="wide")

# Initialize session state variables if they don't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
if "response_style" not in st.session_state:
    st.session_state.response_style = "Friendly"


# The sidebar for Configuration and Settings
with st.sidebar:
    st.header("⚙️ Configuration")

    # Assistant Settings Section
    st.subheader("Assistant Settings")
    st.text_input("Assistant Name:", value="This is a cool assistant!", key="assistant_name")
    st.selectbox("Response Style:", ["Friendly", "Professional", "Witty"], index=0, key="response_style")
    
    # Chat Settings Section
    st.subheader("Chat Settings")
    st.slider("Max Chat History", min_value=1, max_value=100, value=40, key="max_history")
    st.checkbox("Show Timestamps", value=True, key="show_timestamps")

    st.markdown("---")
    
    # Session Stats Section
    st.subheader("📊 Session Stats")
    # In a real app, you would track start time for accurate duration
    st.metric(label="Session Duration", value="2m 9s (Simulated)") 
    # Count of messages *after* the initial assistant message (user + assistant)
    total_messages = len(st.session_state.messages) 
    messages_sent = len([m for m in st.session_state.messages if m['role'] == 'user'])

    st.metric(label="Messages Sent (User)", value=messages_sent)
    st.metric(label="Total Messages (All)", value=total_messages)
    
    st.markdown("---")

    # Action Section (NEW FEATURES)
    st.subheader("⚡ Actions")
    
    # 1. Clear Chats Button
    st.button("🗑️ Clear Chats", on_click=clear_chat, help="Wipe all messages from the current session.")

    # 2. Export Chat Button
    if st.session_state.messages: # Only show download if there are messages
        # Use st.download_button for direct file creation
        st.download_button(
            label="⬇️ Export Chat (.txt)",
            data=download_chat_history(),
            file_name="chatbot_history.txt",
            mime="text/plain",
            help="Download the entire chat history as a text file."
        )


# --- Main Application Area ---

st.title(f"🚀 {st.session_state.get('assistant_name', 'This is a cool assistant!')}")
st.caption(f"Response Style: {st.session_state.response_style} | History Limit: {st.session_state.max_history} Messages")


# --- Ensure initial greeting exists (or re-run if needed) ---
# This ensures the greeting reappears after 'Clear Chats' or on first run
if not st.session_state.messages or st.session_state.messages[0]['role'] != 'assistant':
    clear_chat() 
    
# --- Display Chat History ---
for message in st.session_state.messages:
    # Use st.chat_message to display the messages
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if st.session_state.show_timestamps:
            # Display timestamp if configured
            st.caption(message.get("timestamp", "")) 

# --- Information/Development Section ---
st.markdown("---") 
st.expander("About This Demo").markdown("""
* A configurable sidebar.
* Chat history management using `st.session_state`.
* **New:** Buttons to clear chat and export history.
""")

st.expander("Instructor Notes").markdown("""
* This section can hold debug info or specific deployment notes.
""")

st.checkbox("Show Development Info") 

# --- Chat Input and Response Logic ---

# Check for user input at the bottom of the app
if prompt := st.chat_input(f"Message {st.session_state.get('assistant_name', 'This is a cool assistant!...')}", key="chat_input"):
    
    # 1. Add user message to chat history
    current_time = time.strftime("%H:%M:%S")
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": current_time})
    
    # Rerun the app to display the user message immediately
    st.rerun()

# Logic to generate and display assistant response (only runs on new message)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    
    prompt = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant"):
        # Simulated response logic based on style
        if st.session_state.response_style == "Witty":
            response = f"Ah, asking about '{prompt}'? I'd tell you, but then I'd have to use a whole lotta brainpower. Next question!"
        elif st.session_state.response_style == "Professional":
            response = f"In reference to your query: '{prompt}'. Our system is designed to handle this. We can confirm the following..."
        else: # Friendly
            response = f"Hey, great question about: '{prompt}'! I'm happy to help you with that. That's what I'm thinking..."

        # Stream the response for a dynamic effect
        message_placeholder = st.empty()
        full_response = ""
        for chunk in response.split():
            full_response += chunk + " "
            time.sleep(0.05) 
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response) # Final write

    # 4. Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response, "timestamp": time.strftime("%H:%M:%S")})
    
    # 5. Trim history if necessary
    max_hist = st.session_state.max_history
    if len(st.session_state.messages) > max_hist:
        st.session_state.messages = st.session_state.messages[-max_hist:]
    
    # You must re-run to update the sidebar metrics and the chat history correctly after the response
    st.rerun()