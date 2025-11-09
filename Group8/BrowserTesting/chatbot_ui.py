"""
Chatbot UI Component with File Upload and Multimodal Support
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from chatbot_rag_backend import RAGChatbot, get_agent_features_summary


def initialize_chatbot_state():
    """Initialize session state for chatbot"""
    if "chatbot_messages" not in st.session_state:
        st.session_state.chatbot_messages = []
    if "chatbot_instance" not in st.session_state:
        st.session_state.chatbot_instance = RAGChatbot()
    if "uploaded_file_paths" not in st.session_state:
        st.session_state.uploaded_file_paths = []


def process_uploaded_files(uploaded_files) -> List[Dict[str, Any]]:
    """Process uploaded files and return file info"""
    if not uploaded_files:
        return []

    file_infos = []
    temp_dir = tempfile.gettempdir()

    for uploaded_file in uploaded_files:
        # Save to temp directory
        file_path = os.path.join(temp_dir, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Determine file type
        ext = Path(uploaded_file.name).suffix.lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            file_type = 'image'
        elif ext in ['.pdf']:
            file_type = 'pdf'
        elif ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.log']:
            file_type = 'text'
        else:
            file_type = 'unknown'

        file_infos.append({
            "name": uploaded_file.name,
            "path": file_path,
            "type": file_type,
            "size": uploaded_file.size
        })

        # Store path for cleanup
        st.session_state.uploaded_file_paths.append(file_path)

    return file_infos


def render_chatbot_ui():
    """Render the chatbot UI"""
    initialize_chatbot_state()

    st.markdown("### 🤖 AI Assistant")
    st.caption("Ask questions about the browser automation features, upload screenshots for analysis, or get help with any issues.")

    # Sidebar for chatbot settings
    with st.sidebar:
        st.markdown("### 💬 Chat Settings")

        # Web search toggle
        enable_web_search = st.checkbox(
            "Enable Web Search",
            value=False,
            help="Search the web for current information"
        )

        # Show agent features
        if st.button("📚 Show Available Features"):
            features_summary = get_agent_features_summary()
            st.info(features_summary)

        # Clear chat history
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chatbot_messages = []
            st.session_state.uploaded_file_paths = []
            st.rerun()

        st.markdown("---")
        st.markdown("**Capabilities:**")
        st.markdown("""
        - 📝 Answer questions about features
        - 🖼️ Analyze screenshots and images
        - 📄 Read and understand documents
        - 🔍 Search the web (when enabled)
        - 🤝 Help with troubleshooting
        """)

    # File uploader
    st.markdown("#### 📎 Upload Files (Optional)")
    uploaded_files = st.file_uploader(
        "Upload screenshots, logs, or documents",
        type=['png', 'jpg', 'jpeg', 'txt', 'md', 'py', 'json', 'log', 'html', 'css', 'js'],
        accept_multiple_files=True,
        key="chatbot_file_uploader",
        help="Upload images for analysis or documents for context"
    )

    # Display uploaded files
    if uploaded_files:
        st.markdown("**Uploaded files:**")
        for file in uploaded_files:
            file_size_kb = file.size / 1024
            st.text(f"📄 {file.name} ({file_size_kb:.1f} KB)")

    # Chat messages container
    st.markdown("#### 💬 Conversation")
    messages_container = st.container()

    with messages_container:
        # Display chat history
        for message in st.session_state.chatbot_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # Show sources if available
                if message.get("sources"):
                    with st.expander("🔗 Sources"):
                        for i, source in enumerate(message["sources"], 1):
                            st.markdown(f"{i}. [{source['title']}]({source['link']})")
                            st.caption(source['snippet'])

    # Chat input
    user_query = st.chat_input("Ask a question or describe an issue...")

    if user_query:
        # Process uploaded files
        file_infos = process_uploaded_files(uploaded_files)

        # Display user message
        with st.chat_message("user"):
            st.markdown(user_query)
            if file_infos:
                st.caption(f"📎 {len(file_infos)} file(s) attached")

        # Add to chat history
        st.session_state.chatbot_messages.append({
            "role": "user",
            "content": user_query
        })

        # Get response from chatbot
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Prepare conversation history
                    conversation_history = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.chatbot_messages[:-1]  # Exclude current message
                    ]

                    # Call chatbot
                    result = st.session_state.chatbot_instance.chat(
                        query=user_query,
                        uploaded_files=file_infos,
                        conversation_history=conversation_history
                    )

                    response = result["response"]
                    web_results = result.get("web_search_results", [])

                    # Display response
                    st.markdown(response)

                    # Display sources if available
                    if web_results and any(r.get('link') for r in web_results):
                        with st.expander("🔗 Sources"):
                            for i, source in enumerate(web_results[:5], 1):
                                if source.get('link'):
                                    st.markdown(f"{i}. [{source['title']}]({source['link']})")
                                    st.caption(source['snippet'])

                    # Add to chat history
                    st.session_state.chatbot_messages.append({
                        "role": "assistant",
                        "content": response,
                        "sources": web_results if web_results else None
                    })

                except Exception as e:
                    error_msg = f"Error: {str(e)}\n\nPlease make sure your OPENROUTER_API_KEY is configured in the .env file."
                    st.error(error_msg)
                    st.session_state.chatbot_messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


def render_chatbot_modal():
    """Render chatbot in a modal/sidebar style"""
    with st.expander("💬 AI Assistant", expanded=False):
        render_chatbot_ui()


if __name__ == "__main__":
    # Test the UI
    st.set_page_config(page_title="Chatbot Test", layout="wide")
    st.title("Chatbot UI Test")
    render_chatbot_ui()
