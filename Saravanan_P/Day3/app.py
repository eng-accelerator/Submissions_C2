import streamlit as st
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Chat Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        background-color: #1e1e1e;
    }
    .stChatMessage {
        background-color: #2d2d2d;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #0e76a8;
        color: white;
    }
    .stDownloadButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #28a745;
        color: white;
    }
    div[data-testid="stExpander"] {
        background-color: #2d2d2d;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = datetime.now()

if "message_count" not in st.session_state:
    st.session_state.message_count = 0

if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0

if "assistant_name" not in st.session_state:
    st.session_state.assistant_name = "This is a cool asssistant!"

if "response_style" not in st.session_state:
    st.session_state.response_style = "Friendly"

if "max_history" not in st.session_state:
    st.session_state.max_history = 40

if "show_timestamps" not in st.session_state:
    st.session_state.show_timestamps = True

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Assistant Settings
    with st.expander("**Assistant Settings**", expanded=True):
        assistant_name = st.text_input(
            "Assistant Name:",
            value=st.session_state.assistant_name,
            key="assistant_name_input"
        )
        st.session_state.assistant_name = assistant_name
        
        response_style = st.selectbox(
            "Response Style:",
            ["Friendly", "Professional", "Casual", "Technical", "Humorous"],
            index=["Friendly", "Professional", "Casual", "Technical", "Humorous"].index(st.session_state.response_style)
        )
        st.session_state.response_style = response_style
        
        st.caption(f"History Limit: {st.session_state.max_history} messages")
    
    # Chat Settings
    with st.expander("**Chat Settings**", expanded=True):
        st.markdown("**Max Chat History:**")
        max_history = st.slider(
            "Max Chat History:",
            min_value=10,
            max_value=100,
            value=st.session_state.max_history,
            step=10,
            label_visibility="collapsed"
        )
        st.session_state.max_history = max_history
        
        show_timestamps = st.checkbox(
            "Show Timestamps",
            value=st.session_state.show_timestamps
        )
        st.session_state.show_timestamps = show_timestamps
    
    st.markdown("---")
    
    # Session Stats
    st.markdown("## 📊 Session Stats")
    
    # Calculate session duration
    duration = datetime.now() - st.session_state.session_start_time
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    st.markdown("**Session Duration:**")
    if hours > 0:
        st.markdown(f"{hours}h {minutes}m {seconds}s")
    elif minutes > 0:
        st.markdown(f"{minutes}m {seconds}s")
    else:
        st.markdown(f"{seconds}s")
    
    st.markdown("**Messages Sent:**")
    st.markdown(f"{st.session_state.user_message_count}")
    
    st.markdown("**Total Messages:**")
    st.markdown(f"{st.session_state.message_count}")

# Main content area
st.title(f"🚀 {st.session_state.assistant_name}")
st.markdown(f"**Response Style:** {st.session_state.response_style} | **History Limit:** {st.session_state.max_history} messages")

# Action buttons
col1, col2, col3 = st.columns([1, 1, 4])

with col1:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.message_count = 0
        st.session_state.user_message_count = 0
        st.session_state.session_start_time = datetime.now()
        st.rerun()

with col2:
    if st.session_state.messages:
        # Prepare chat export
        export_text = f"Chat Export - {st.session_state.assistant_name}\n"
        export_text += f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_text += f"Response Style: {st.session_state.response_style}\n"
        export_text += "="*60 + "\n\n"
        
        for msg in st.session_state.messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            timestamp = msg.get("timestamp", "")
            if st.session_state.show_timestamps and timestamp:
                export_text += f"[{timestamp}] {role}: {msg['content']}\n\n"
            else:
                export_text += f"{role}: {msg['content']}\n\n"
        
        st.download_button(
            label="📥 Export Chat",
            data=export_text,
            file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# Additional info expanders
with st.expander("ℹ️ About This Demo"):
    st.markdown("""
    ### Welcome to the Chat Assistant Demo!
    
    This is a fully-featured chatbot interface built with Streamlit. Features include:
    
    - 💬 **Interactive Chat Interface**: Engage in conversations with the assistant
    - ⚙️ **Customizable Settings**: Adjust assistant name, response style, and chat history
    - 📊 **Session Statistics**: Track your session duration and message counts
    - 🗑️ **Clear Chat**: Start fresh anytime
    - 📥 **Export Chat**: Download your conversation as a .txt file
    - ⏱️ **Timestamps**: Optional timestamps for each message
    
    Configure the assistant using the sidebar and start chatting!
    """)

with st.expander("📝 Instructor Notes"):
    st.markdown("""
    ### Technical Implementation Details
    
    **Technologies Used:**
    - Streamlit >= 1.28.0
    - Python 3.7+
    
    **Key Features Implemented:**
    1. **Session State Management**: Persistent chat history and stats
    2. **Real-time Stats**: Live session duration tracking
    3. **Export Functionality**: Download conversations as text files
    4. **Responsive UI**: Modern, dark-themed interface
    5. **Configuration Options**: Customizable assistant behavior
    
    **Session State Variables:**
    - `messages`: Chat message history
    - `session_start_time`: Track session duration
    - `message_count`: Total messages in conversation
    - `user_message_count`: Messages sent by user
    - Configuration settings (assistant_name, response_style, etc.)
    """)

st.markdown("---")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if st.session_state.show_timestamps and "timestamp" in message:
            st.markdown(f"*{message['timestamp']}*")
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input(f"Message {st.session_state.assistant_name}"):
    # Add user message to chat
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": timestamp
    })
    st.session_state.message_count += 1
    st.session_state.user_message_count += 1
    
    # Display user message
    with st.chat_message("user"):
        if st.session_state.show_timestamps:
            st.markdown(f"*{timestamp}*")
        st.markdown(prompt)
    
    # Generate assistant response based on response style
    with st.chat_message("assistant"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if st.session_state.show_timestamps:
            st.markdown(f"*{timestamp}*")
        
        # Simulate response based on style
        style_responses = {
            "Friendly": f"Hey, great question about '{prompt[:50]}...'! I'm happy to help with that. ",
            "Professional": f"Thank you for your inquiry regarding '{prompt[:50]}...'. I shall address this promptly. ",
            "Casual": f"Cool question! About '{prompt[:50]}...', let me think... ",
            "Technical": f"Analyzing query: '{prompt[:50]}...'. Processing technical response. ",
            "Humorous": f"Haha, interesting question about '{prompt[:50]}...'! Let me crack this one for you. "
        }
        
        base_response = style_responses.get(st.session_state.response_style, "")
        response = base_response + f"Here's what I'm thinking... (This is a demo response. In a real application, this would be connected to an AI model or backend service.)"
        
        st.markdown(response)
        
        # Add assistant message to chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": timestamp
        })
        st.session_state.message_count += 1
    
    # Enforce max history limit
    if len(st.session_state.messages) > st.session_state.max_history:
        st.session_state.messages = st.session_state.messages[-st.session_state.max_history:]
    
    st.rerun()

# Display initial message if no messages yet
if not st.session_state.messages:
    with st.chat_message("assistant"):
        initial_msg = f"Hello! I'm your demo assistant. How can I help you today?"
        st.markdown(initial_msg)

