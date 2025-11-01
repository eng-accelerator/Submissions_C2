import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import os
import uuid

# Page config
st.set_page_config(
    page_title="ChatBot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and styling
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #1e1e1e;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #2d2d2d;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: #2d2d2d;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #ff6b6b;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #ff5252;
    }
    
    /* Text input styling */
    .stTextInput>div>div>input {
        background-color: #3d3d3d;
        color: white;
        border-radius: 8px;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #2d2d2d;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenRouter client
@st.cache_resource
def get_openrouter_client():
    api_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))
    if not api_key:
        st.error("⚠️ OpenRouter API key not found! Please add it to .streamlit/secrets.toml or set OPENROUTER_API_KEY environment variable")
        st.stop()
    
    # Configure OpenAI client to use OpenRouter
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

client = get_openrouter_client()

# Helper functions
def create_new_chat():
    """Create a new chat conversation"""
    chat_id = f"chat_{uuid.uuid4().hex[:8]}"
    
    # Save current chat before creating new one (only if current_chat_id exists)
    if (st.session_state.get('current_chat_id') and 
        st.session_state.current_chat_id in st.session_state.get('conversations', {})):
        save_current_chat()
    
    # Create new chat
    st.session_state.conversations[chat_id] = {
        'chat_id': chat_id,
        'title': 'New Chat',
        'messages': [],
        'created_at': datetime.now().isoformat()
    }
    
    # Set as current chat
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []
    st.session_state.chat_title = 'New Chat'
    
    return chat_id

def load_chat(chat_id):
    """Load a chat conversation"""
    if chat_id in st.session_state.conversations:
        chat_data = st.session_state.conversations[chat_id]
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = chat_data.get('messages', [])
        st.session_state.chat_title = chat_data.get('title', 'New Chat')
        return chat_data
    return None

def save_current_chat():
    """Save the current chat to conversations"""
    if st.session_state.current_chat_id:
        st.session_state.conversations[st.session_state.current_chat_id] = {
            'chat_id': st.session_state.current_chat_id,
            'title': st.session_state.chat_title,
            'messages': st.session_state.messages.copy(),
            'created_at': st.session_state.conversations[st.session_state.current_chat_id].get('created_at', datetime.now().isoformat())
        }

def delete_chat(chat_id):
    """Delete a chat conversation"""
    # Don't delete if it's the only chat
    if len(st.session_state.conversations) <= 1:
        st.warning("Cannot delete the only remaining chat!")
        return
    
    # Remove from conversations
    if chat_id in st.session_state.conversations:
        del st.session_state.conversations[chat_id]
    
    # If we deleted the current chat, switch to another
    if st.session_state.current_chat_id == chat_id:
        # Get remaining chat IDs sorted by creation time
        remaining_chats = sorted(
            st.session_state.conversations.items(),
            key=lambda x: x[1].get('created_at', ''),
            reverse=True
        )
        
        if remaining_chats:
            # Load the most recent remaining chat
            new_chat_id = remaining_chats[0][0]
            load_chat(new_chat_id)
        else:
            # Create a new chat if somehow all were deleted
            create_new_chat()

def update_chat_title(content):
    """Update chat title based on first user message"""
    if len(st.session_state.messages) <= 2 and st.session_state.chat_title == "New Chat":
        # Extract first 50 characters for title
        st.session_state.chat_title = content[:50] + ('...' if len(content) > 50 else '')
        save_current_chat()

def get_all_chats():
    """Get all chats sorted by creation time (newest first)"""
    return sorted(
        st.session_state.conversations.items(),
        key=lambda x: x[1].get('created_at', ''),
        reverse=True
    )

def generate_summary():
    """Generate a summary of the entire conversation"""
    if not st.session_state.messages:
        return "No messages to summarize."
    
    try:
        # Prepare conversation text
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}" 
            for msg in st.session_state.messages
        ])
        
        # Generate summary using OpenRouter
        summary_resp = client.chat.completions.create(
            model=st.session_state.model_choice,
            messages=[
                {"role": "system", "content": "Summarize the conversation concisely."},
                {"role": "user", "content": f"Summarize this conversation:\n\n{conversation_text}"}
            ],
            stream=False
        )
        
        summary_text = summary_resp.choices[0].message.content.strip()
        return summary_text
        
    except Exception as e:
        return f"Summary failed: {e}"

def chat_with_openrouter(messages, model):
    """Send messages to OpenRouter and get response"""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=2000,
        stream=True
    )
    return response

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if 'conversations' not in st.session_state:
        st.session_state.conversations = {}
    
    if 'current_chat_id' not in st.session_state:
        st.session_state.current_chat_id = None
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'chat_title' not in st.session_state:
        st.session_state.chat_title = "New Chat"
    
    if 'model_choice' not in st.session_state:
        st.session_state.model_choice = "openai/gpt-4o-mini"
    
    # Create initial chat if none exists
    if not st.session_state.conversations:
        create_new_chat()

init_session_state()

# Sidebar
with st.sidebar:
    st.title("💬 Conversations")
    
    # New Chat button
    if st.button("➕ New Chat", use_container_width=True):
        save_current_chat()  # Save current chat before creating new
        create_new_chat()
        st.rerun()
    
    st.divider()
    
    # Chat History
    st.subheader("Chat History")
    
    # Display conversations
    all_chats = get_all_chats()
    
    for chat_id, chat_data in all_chats:
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Chat button - show green dot for current chat
            is_current = chat_id == st.session_state.current_chat_id
            button_label = f"{'🟢' if is_current else '⚪'} {chat_data.get('title', 'New Chat')}"
            
            if st.button(
                button_label,
                key=f"chat_{chat_id}",
                use_container_width=True,
                type="primary" if is_current else "secondary"
            ):
                save_current_chat()  # Save before switching
                load_chat(chat_id)
                st.rerun()
        
        with col2:
            # Delete button (only show for non-current chats or if there are multiple chats)
            if not is_current or len(st.session_state.conversations) > 1:
                if st.button("🗑️", key=f"delete_{chat_id}", help="Delete chat"):
                    delete_chat(chat_id)
                    st.rerun()
    
    st.divider()
    
    # Settings
    st.subheader("⚙️ Settings")
    
    # Model selection - OpenRouter models
    model_option = st.selectbox(
        "Select Model",
        [
            "openai/gpt-4o-mini",
            "openai/gpt-4o",
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3-opus",
            "google/gemini-pro-1.5",
            "meta-llama/llama-3.1-70b-instruct"
        ],
        index=0,
        key="model_selector"
    )
    st.session_state.model_choice = model_option
    
    # Clear current chat
    if st.button("🗑️ Clear Current Chat", use_container_width=True):
        if st.session_state.current_chat_id:
            st.session_state.messages = []
            st.session_state.chat_title = "New Chat"
            save_current_chat()
            st.rerun()

# Main chat area
st.title("👋 Hello")

# Summarize Conversation Section
with st.expander("📋 Summarize Conversation", expanded=False):
    st.write("Generate a summary of the entire conversation in this chat")
    
    if st.button("Generate Summary", use_container_width=True):
        if not st.session_state.messages:
            st.warning("No messages to summarize yet!")
        else:
            try:
                with st.spinner("Generating summary..."):
                    summary = generate_summary()
                    st.markdown("### Summary")
                    st.markdown(summary)
            except Exception as e:
                st.error(f"Summary failed: {e}")

st.divider()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    update_chat_title(prompt)
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Prepare messages for OpenRouter
        messages_for_api = [
            {"role": m["role"], "content": m["content"]} 
            for m in st.session_state.messages
        ]
        
        try:
            # Stream response
            for chunk in chat_with_openrouter(messages_for_api, st.session_state.model_choice):
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Add assistant response to messages
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Save to conversation
            save_current_chat()
            
        except Exception as e:
            st.error(f"Error generating response: {e}")
            # Remove the user message if there was an error
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()