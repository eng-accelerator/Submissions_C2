import streamlit as st
import time
# Import the ollama client library
import ollama 

# --- Helper Functions for Actions ---

def clear_chat():
    """Clears the chat history in the session state and refreshes the greeting."""
    # Ensure all model-related keys are set before clearing the chat
    if "ollama_model" not in st.session_state:
        st.session_state.ollama_model = "llama3.2" 
        
    st.session_state.messages = []
    initial_greeting = f"Hello! I'm running **{st.session_state.ollama_model}** locally. How can I help you today?"
    st.session_state.messages.append({"role": "assistant", "content": initial_greeting, "timestamp": time.strftime("%H:%M:%S")})
    st.rerun() 

def download_chat_history():
    """Formats the chat history into a downloadable .txt file."""
    chat_text = []
    for message in st.session_state.messages:
        role = message["role"].capitalize()
        timestamp = message.get("timestamp", "N/A")
        content = message["content"]
        chat_text.append(f"[{timestamp}] {role}: {content}\n{'='*50}\n")
    return "".join(chat_text)

def stream_ollama_response(messages_list):
    """
    Connects to the local Ollama service and streams a response.
    
    Args:
        messages_list (list): The list of chat messages for context.
    
    Yields:
        str: Chunks of the LLM's response text.
    """
    # The list of messages needs to be in the Ollama API format: 
    # [{"role": "user", "content": "..."}]
    ollama_messages = [{"role": m["role"], "content": m["content"]} for m in messages_list]
    
    # Call the Ollama chat endpoint
    try:
        stream = ollama.chat(
            model=st.session_state.ollama_model, 
            messages=ollama_messages, 
            stream=True
        )
        
        for chunk in stream:
            # Check if the chunk has content and yield it
            if chunk['message']['content']:
                yield chunk['message']['content']
                
    except Exception as e:
        # Handle case where Ollama server might not be running
        yield f"ERROR: Could not connect to Ollama server. Is the service running and is **{st.session_state.ollama_model}** pulled? ({e})"


# --- Configuration for Page and Sidebar ---

st.set_page_config(page_title="Local Ollama Chatbot", layout="wide")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ollama_model" not in st.session_state:
    st.session_state.ollama_model = "llama3.2" # Default to llama3.2
if "show_timestamps" not in st.session_state:
    st.session_state.show_timestamps = True


# The sidebar for Configuration and Settings
with st.sidebar:
    st.header("⚙️ Configuration")

    # LLM Settings Section (NEW)
    st.subheader("Ollama Model")
    # You can let the user pick from models they might have pulled
    st.session_state.ollama_model = st.selectbox(
        "Choose Model:", 
        options=["llama3.2", "mistral", "phi3", "llama2", "gemma:2b"], 
        index=0, 
        key="model_selector",
        help="Make sure this model is pulled in your local Ollama instance (e.g., `ollama pull llama3.2`)."
    )
    
    # Assistant Settings Section
    st.subheader("Assistant Settings")
    st.text_input("Assistant Name:", value=f"Local {st.session_state.ollama_model} Bot", key="assistant_name")
    
    # Chat Settings Section
    st.subheader("Chat Settings")
    st.slider("Max Chat History", min_value=1, max_value=100, value=40, key="max_history")
    st.checkbox("Show Timestamps", value=st.session_state.show_timestamps, key="show_timestamps_toggle")

    # Sync checkbox to session state (since selectbox above uses a key)
    st.session_state.show_timestamps = st.session_state.show_timestamps_toggle

    st.markdown("---")
    
    # Session Stats Section
    st.subheader("📊 Session Stats")
    total_messages = len(st.session_state.messages) 
    messages_sent = len([m for m in st.session_state.messages if m['role'] == 'user'])

    st.metric(label="Messages Sent (User)", value=messages_sent)
    st.metric(label="Total Messages (All)", value=total_messages)
    
    st.markdown("---")

    # Action Section 
    st.subheader("⚡ Actions")
    
    st.button("🗑️ Clear Chats", on_click=clear_chat, help="Wipe all messages from the current session.")

    if st.session_state.messages: 
        st.download_button(
            label="⬇️ Export Chat (.txt)",
            data=download_chat_history(),
            file_name="ollama_chatbot_history.txt",
            mime="text/plain",
        )


# --- Main Application Area ---

st.title(f"🚀 {st.session_state.get('assistant_name', 'Local Ollama Bot')}")
st.caption(f"Powered by Ollama / Model: **{st.session_state.ollama_model}**")

# --- Ensure initial greeting exists ---
if not st.session_state.messages or st.session_state.messages[0]['role'] != 'assistant':
    clear_chat() 
    
# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if st.session_state.show_timestamps:
            st.caption(message.get("timestamp", "")) 

# --- Information/Development Section ---
st.markdown("---") 
st.expander("About This Demo").markdown("""
This chat connects directly to your local **Ollama** server using the selected model. 
1. Ensure Ollama is running in the background.
2. Ensure you have the model pulled (e.g., `ollama pull llama3.2`).
""")

st.expander("Instructor Notes").markdown("LLM integration is in the `stream_ollama_response` function.")


# --- Chat Input and Response Logic ---

# Check for user input at the bottom of the app
if prompt := st.chat_input("Ask me anything about " + st.session_state.ollama_model + "..."):
    
    # 1. Add user message to history and display immediately
    current_time = time.strftime("%H:%M:%S")
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": current_time})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate and stream the LLM response
    with st.chat_message("assistant"):
        # The key to streaming is st.write_stream
        full_response = st.write_stream(stream_ollama_response(st.session_state.messages))

    # 3. Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response, "timestamp": time.strftime("%H:%M:%S")})
    
    # 4. Trim history and Rerun
    max_hist = st.session_state.max_history
    if len(st.session_state.messages) > max_hist:
        st.session_state.messages = st.session_state.messages[-max_hist:]
    
    # Note: st.write_stream already handles the streaming, 
    # but we use rerun here to update the sidebar stats.
    st.rerun()