import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import csv
from io import StringIO

# Page config
st.set_page_config(page_title="Chat with Export", page_icon="💬", layout="wide")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()

# Export functions
def get_statistics(messages):
    """Calculate conversation statistics"""
    # Filter only user and assistant messages
    valid_msgs = [m for m in messages if m["role"] in ["user", "assistant"]]
    user_msgs = [m for m in valid_msgs if m["role"] == "user"]
    assistant_msgs = [m for m in valid_msgs if m["role"] == "assistant"]
    
    total_chars = sum(len(m["content"]) for m in valid_msgs)
    total_words = sum(len(m["content"].split()) for m in valid_msgs)
    
    return {
        "total_messages": len(valid_msgs),
        "user_messages": len(user_msgs),
        "assistant_messages": len(assistant_msgs),
        "total_characters": total_chars,
        "total_words": total_words,
        "average_message_length": total_chars // len(valid_msgs) if valid_msgs else 0
    }

def export_as_txt(messages):
    """Export as formatted text"""
    # Filter only user and assistant messages
    valid_msgs = [m for m in messages if m["role"] in ["user", "assistant"]]
    
    now = datetime.now()
    stats = get_statistics(messages)
    duration = (now - st.session_state.session_start).total_seconds() / 60
    
    output = f"""Chat Export - {now.strftime('%Y-%m-%d %H:%M')}
{'=' * 60}

Session Information:
- Total Messages: {stats['total_messages']}
- Duration: {duration:.1f} minutes
- Export Date: {now.strftime('%Y-%m-%d %H:%M:%S')}
- User Messages: {stats['user_messages']}
- Assistant Messages: {stats['assistant_messages']}

Conversation:
{'=' * 60}

"""
    
    for i, msg in enumerate(valid_msgs, 1):
        timestamp = msg.get('timestamp', now.strftime('%H:%M:%S'))
        role = "You" if msg["role"] == "user" else "Assistant"
        output += f"[{timestamp}] {role}:\n{msg['content']}\n\n{'-' * 60}\n\n"
    
    output += f"""
Statistics:
- Total Characters: {stats['total_characters']:,}
- Total Words: {stats['total_words']:,}
- Average Message Length: {stats['average_message_length']} characters
"""
    
    return output

def export_as_json(messages):
    """Export as structured JSON"""
    # Filter only user and assistant messages
    valid_msgs = [m for m in messages if m["role"] in ["user", "assistant"]]
    
    now = datetime.now()
    stats = get_statistics(messages)
    
    export_data = {
        "export_metadata": {
            "export_timestamp": now.isoformat(),
            "format_version": "1.0",
            "session_start": st.session_state.session_start.isoformat(),
            "total_messages": stats['total_messages'],
            "session_duration_minutes": round((now - st.session_state.session_start).total_seconds() / 60, 2)
        },
        "conversation": [
            {
                "message_id": i,
                "timestamp": msg.get('timestamp', now.isoformat()),
                "role": msg["role"],
                "content": msg["content"],
                "character_count": len(msg["content"]),
                "word_count": len(msg["content"].split())
            }
            for i, msg in enumerate(valid_msgs, 1)
        ],
        "statistics": stats
    }
    
    return json.dumps(export_data, indent=2)

def export_as_csv(messages):
    """Export as CSV"""
    # Filter only user and assistant messages
    valid_msgs = [m for m in messages if m["role"] in ["user", "assistant"]]
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Message_ID', 'Timestamp', 'Role', 'Content', 'Character_Count', 'Word_Count'])
    
    # Data
    now = datetime.now()
    for i, msg in enumerate(valid_msgs, 1):
        writer.writerow([
            i,
            msg.get('timestamp', now.strftime('%Y-%m-%d %H:%M:%S')),
            msg['role'],
            msg['content'],
            len(msg['content']),
            len(msg['content'].split())
        ])
    
    return output.getvalue()

# Sidebar
with st.sidebar:
    st.title("💬 Chat Assistant")
    
    api_key = st.text_input("OpenRouter API Key", type="password", key="api_key")
    
    st.divider()
    
    model = st.selectbox(
        "Model:",
        ["google/gemini-flash-1.5", "meta-llama/llama-3.1-8b-instruct", "anthropic/claude-3-haiku"]
    )
    
    st.divider()
    
    # Statistics
    if st.session_state.messages:
        stats = get_statistics(st.session_state.messages)
        st.metric("Messages", stats['total_messages'])
        st.metric("Words", f"{stats['total_words']:,}")
        
        duration = (datetime.now() - st.session_state.session_start).total_seconds() / 60
        st.metric("Duration", f"{duration:.1f} min")
    
    st.divider()
    
    # Export section
    st.subheader("📤 Export Chat")
    
    # Check if there are valid messages (user/assistant only)
    valid_messages = [m for m in st.session_state.messages if m["role"] in ["user", "assistant"]]
    
    if not valid_messages:
        st.info("No messages to export yet")
    else:
        export_format = st.selectbox(
            "Format:",
            ["TXT (Human Readable)", "JSON (Structured)", "CSV (Data Analysis)"]
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Preview", use_container_width=True):
                st.session_state.show_preview = True
        
        with col2:
            # Generate export based on format
            if "TXT" in export_format:
                content = export_as_txt(st.session_state.messages)
                filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                mime = "text/plain"
            elif "JSON" in export_format:
                content = export_as_json(st.session_state.messages)
                filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                mime = "application/json"
            else:  # CSV
                content = export_as_csv(st.session_state.messages)
                filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                mime = "text/csv"
            
            st.download_button(
                "💾 Download",
                data=content,
                file_name=filename,
                mime=mime,
                use_container_width=True
            )
    
    st.divider()
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_start = datetime.now()
        if 'show_preview' in st.session_state:
            del st.session_state.show_preview
        st.rerun()

# Main content
st.title("💬 Chat Assistant with Export")

# Show preview if requested
if st.session_state.get('show_preview', False):
    with st.expander("📋 Export Preview", expanded=True):
        if "TXT" in export_format:
            st.text(export_as_txt(st.session_state.messages)[:1000] + "\n\n... (preview truncated)")
        elif "JSON" in export_format:
            st.json(json.loads(export_as_json(st.session_state.messages)))
        else:  # CSV
            st.code(export_as_csv(st.session_state.messages)[:1000] + "\n\n... (preview truncated)", language="csv")
        
        if st.button("✖️ Close Preview"):
            st.session_state.show_preview = False
            st.rerun()

if not api_key:
    st.info("👈 Enter your OpenRouter API key to start chatting")
    st.markdown("""
    ### Features:
    - 💬 Full conversation history
    - 📤 Export in 3 formats (TXT, JSON, CSV)
    - 📊 Real-time statistics
    - 🔄 Streaming responses
    """)
    st.stop()

# Initialize client
client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add timestamp
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": timestamp
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": m["role"], "content": m["content"]} 
                             for m in st.session_state.messages],
                    temperature=0.7,
                    max_tokens=500,
                    stream=True
                )
                
                # Stream response
                response_text = ""
                response_placeholder = st.empty()
                
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        response_text += chunk.choices[0].delta.content
                        response_placeholder.markdown(response_text + "▌")
                
                response_placeholder.markdown(response_text)
                
                # Save assistant message with timestamp
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now().strftime('%H:%M:%S')
                })
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
if st.session_state.messages:
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    stats = get_statistics(st.session_state.messages)
    
    with col1:
        st.metric("Total Messages", stats['total_messages'])
    with col2:
        st.metric("Total Words", f"{stats['total_words']:,}")
    with col3:
        st.metric("Avg Length", f"{stats['average_message_length']} chars")