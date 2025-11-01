# -*- coding: utf-8 -*-
"""
Personality Chatbot - A Streamlit app with multiple AI personalities
No emojis - works on all systems and terminals
"""

import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import os
import uuid

# Page config
st.set_page_config(
    page_title="Personality Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and styling
st.markdown("""
<style>
    .stApp {
        background-color: #1e1e1e;
    }
    [data-testid="stSidebar"] {
        background-color: #2d2d2d;
    }
    .stChatMessage {
        background-color: #2d2d2d;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
    }
    .stButton>button {
        background-color: #9c27b0;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #7b1fa2;
    }
    .stTextInput>div>div>input {
        background-color: #3d3d3d;
        color: white;
        border-radius: 8px;
    }
    h1, h2, h3 {
        color: white;
    }
    .streamlit-expanderHeader {
        background-color: #2d2d2d;
        border-radius: 8px;
    }
    .personality-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 8px 16px;
        border-radius: 20px;
        display: inline-block;
        margin: 5px 0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PERSONALITY CONFIGURATIONS
# ============================================================================

PERSONALITIES = {
    "Professional Business Assistant": {
        "description": "Formal, structured, business-focused communication",
        "expertise": "Business strategy, professional communication, management",
        "tone": "Polite, efficient, results-oriented",
        "system_prompt": """You are a Professional Business Assistant with extensive experience in corporate environments.

Your communication style is:
- Formal and structured
- Clear and concise
- Results-oriented and actionable
- Uses business terminology appropriately
- Provides step-by-step recommendations
- Focuses on measurable outcomes

Always:
- Start with a clear summary
- Use numbered lists for action items
- Provide professional, diplomatic advice
- Consider business implications
- Be respectful and courteous

Format responses professionally with clear sections when appropriate.""",
        "example": "I recommend a structured approach: 1) Analyze the situation, 2) Develop action items, 3) Set clear timelines."
    },
    
    "Creative Writing Helper": {
        "description": "Imaginative, expressive, inspiring communication",
        "expertise": "Creative writing, storytelling, artistic projects, brainstorming",
        "tone": "Enthusiastic, artistic, encouraging",
        "system_prompt": """You are a Creative Writing Helper - an imaginative and inspiring assistant who loves storytelling and artistic expression.

Your communication style is:
- Vivid and descriptive
- Uses metaphors and creative language
- Enthusiastic and encouraging
- Thinks outside the box
- Embraces originality and innovation

Always:
- Paint pictures with words
- Inspire creativity and imagination
- Offer multiple creative angles
- Be enthusiastic and supportive
- Use storytelling techniques
- Embrace unconventional ideas

Make every response feel like a creative adventure!""",
        "example": "Imagine this: Your story unfolds like a butterfly emerging from its cocoon - each word a delicate wing carrying your readers into magical realms!"
    },
    
    "Technical Expert": {
        "description": "Precise, detailed, code-focused communication",
        "expertise": "Programming, technology, debugging, system architecture",
        "tone": "Analytical, methodical, educational",
        "system_prompt": """You are a Technical Expert with deep knowledge in programming, software engineering, and technology.

Your communication style is:
- Precise and technically accurate
- Detailed and thorough
- Code-focused with examples
- Systematic and logical
- Educational and explanatory
- Uses technical terminology correctly

Always:
- Provide code examples when relevant
- Explain technical concepts clearly
- Consider edge cases and best practices
- Use proper formatting for code
- Reference documentation when helpful
- Break down complex problems step-by-step

Be thorough but avoid unnecessary complexity. Focus on practical, implementable solutions.""",
        "example": "Here's the implementation:\n```python\ndef solution():\n    # Step 1: Initialize variables\n    pass\n```\nThis approach has O(n) complexity."
    },
    
    "Friendly Companion": {
        "description": "Casual, supportive, conversational communication",
        "expertise": "General chat, emotional support, casual advice, daily life",
        "tone": "Warm, empathetic, encouraging",
        "system_prompt": """You are a Friendly Companion - a warm, supportive friend who's always here to chat and help.

Your communication style is:
- Casual and conversational
- Warm and empathetic
- Encouraging and positive
- Understanding and non-judgmental
- Uses natural, friendly language
- Relates to human experiences

Always:
- Be genuine and authentic
- Show empathy and understanding
- Offer emotional support when needed
- Keep things light and positive
- Use casual language and contractions
- Be encouraging and uplifting
- Share relatable perspectives

Talk like a good friend would - caring, supportive, and real!""",
        "example": "Hey! That sounds tough, but I totally get it. You know what? You're doing better than you think! Let's figure this out together."
    },
    
    "Academic Scholar": {
        "description": "Scholarly, research-oriented, intellectually rigorous",
        "expertise": "Research, academic writing, critical analysis, education",
        "tone": "Scholarly, precise, intellectually curious",
        "system_prompt": """You are an Academic Scholar with expertise in research methodology and critical analysis.

Your communication style is:
- Scholarly and well-researched
- References theories and concepts
- Analytical and critical
- Evidence-based reasoning
- Precise academic language
- Intellectually thorough

Always:
- Provide context and background
- Reference relevant theories or frameworks
- Consider multiple perspectives
- Use formal academic language
- Cite reasoning and logic
- Encourage critical thinking
- Structure arguments clearly

Maintain academic rigor while being accessible and informative.""",
        "example": "From a theoretical perspective, this phenomenon can be understood through the lens of cognitive psychology. Research suggests..."
    }
}

# ============================================================================
# INITIALIZE OPENROUTER CLIENT
# ============================================================================

@st.cache_resource
def get_openrouter_client():
    """Initialize OpenRouter client with proper configuration"""
    api_key = None
    
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]
    except:
        api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        st.error("OpenRouter API key not found!")
        st.info("Please add OPENROUTER_API_KEY to .streamlit/secrets.toml")
        st.stop()
    
    if not api_key.startswith("sk-or-v1-"):
        st.error("Invalid API key format! OpenRouter keys should start with 'sk-or-v1-'")
        st.stop()
    
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "Personality Chatbot"
            }
        )
        return client
    except Exception as e:
        st.error(f"Failed to initialize OpenRouter client: {e}")
        st.stop()

client = get_openrouter_client()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def export_as_txt(messages, chat_title, personality):
    """Export conversation as formatted text"""
    from datetime import datetime
    
    export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    txt_content = f"""Chat Export - {chat_title}
{'=' * 60}

Session Information:
- Personality: {personality}
- Total Messages: {len(messages)}
- Export Date: {export_time}

Conversation:
{'-' * 60}

"""
    
    for i, msg in enumerate(messages, 1):
        role = "You" if msg["role"] == "user" else "Assistant"
        content = msg["content"]
        txt_content += f"[Message {i}] {role}:\n{content}\n\n"
    
    return txt_content

def export_as_json(messages, chat_title, personality):
    """Export conversation as JSON"""
    from datetime import datetime
    import json
    
    export_data = {
        "export_metadata": {
            "export_timestamp": datetime.now().isoformat(),
            "chat_title": chat_title,
            "personality": personality,
            "total_messages": len(messages),
            "format_version": "1.0"
        },
        "conversation": [
            {
                "message_id": i,
                "role": msg["role"],
                "content": msg["content"],
                "character_count": len(msg["content"]),
                "word_count": len(msg["content"].split())
            }
            for i, msg in enumerate(messages, 1)
        ],
        "statistics": {
            "user_messages": sum(1 for m in messages if m["role"] == "user"),
            "assistant_messages": sum(1 for m in messages if m["role"] == "assistant"),
            "total_characters": sum(len(m["content"]) for m in messages),
            "average_message_length": sum(len(m["content"]) for m in messages) // len(messages) if messages else 0
        }
    }
    
    return json.dumps(export_data, indent=2)

def export_as_csv(messages, chat_title, personality):
    """Export conversation as CSV"""
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["Message_ID", "Role", "Content", "Character_Count", "Word_Count"])
    
    # Write messages
    for i, msg in enumerate(messages, 1):
        writer.writerow([
            i,
            msg["role"],
            msg["content"],
            len(msg["content"]),
            len(msg["content"].split())
        ])
    
    return output.getvalue()

def create_new_chat():
    """Create a new chat conversation"""
    chat_id = f"chat_{uuid.uuid4().hex[:8]}"
    
    if (st.session_state.get('current_chat_id') and 
        st.session_state.current_chat_id in st.session_state.get('conversations', {})):
        save_current_chat()
    
    st.session_state.conversations[chat_id] = {
        'chat_id': chat_id,
        'title': 'New Chat',
        'messages': [],
        'personality': st.session_state.current_personality,
        'created_at': datetime.now().isoformat()
    }
    
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
        
        # Load the personality from that chat
        loaded_personality = chat_data.get('personality', 'Friendly Companion')
        
        # If personality doesn't exist in PERSONALITIES, create a placeholder or fall back
        if loaded_personality not in PERSONALITIES:
            # Create a basic entry for the missing personality
            PERSONALITIES[loaded_personality] = {
                "description": "Custom personality (restored from chat history)",
                "expertise": "Previously defined",
                "tone": "As previously configured",
                "system_prompt": f"You are {loaded_personality}. Respond in a helpful and appropriate manner.",
                "example": "Custom personality response."
            }
        
        st.session_state.current_personality = loaded_personality
        return chat_data
    return None

def save_current_chat():
    """Save the current chat to conversations"""
    if st.session_state.current_chat_id:
        st.session_state.conversations[st.session_state.current_chat_id] = {
            'chat_id': st.session_state.current_chat_id,
            'title': st.session_state.chat_title,
            'messages': st.session_state.messages.copy(),
            'personality': st.session_state.current_personality,
            'created_at': st.session_state.conversations[st.session_state.current_chat_id].get('created_at', datetime.now().isoformat())
        }

def delete_chat(chat_id):
    """Delete a chat conversation"""
    if len(st.session_state.conversations) <= 1:
        st.warning("Cannot delete the only remaining chat!")
        return
    
    if chat_id in st.session_state.conversations:
        del st.session_state.conversations[chat_id]
    
    if st.session_state.current_chat_id == chat_id:
        remaining_chats = sorted(
            st.session_state.conversations.items(),
            key=lambda x: x[1].get('created_at', ''),
            reverse=True
        )
        
        if remaining_chats:
            new_chat_id = remaining_chats[0][0]
            load_chat(new_chat_id)
        else:
            create_new_chat()

def update_chat_title(content):
    """Update chat title based on first user message"""
    if len(st.session_state.messages) <= 2 and st.session_state.chat_title == "New Chat":
        st.session_state.chat_title = content[:50] + ('...' if len(content) > 50 else '')
        save_current_chat()

def get_all_chats():
    """Get all chats sorted by creation time (newest first)"""
    return sorted(
        st.session_state.conversations.items(),
        key=lambda x: x[1].get('created_at', ''),
        reverse=True
    )

def chat_with_personality(messages, model, personality):
    """Send messages to OpenRouter with personality-specific system prompt"""
    # Get the system prompt for the selected personality with fallback
    personality_data = PERSONALITIES.get(personality, {
        "system_prompt": "You are a helpful AI assistant. Respond in a clear, friendly, and informative manner."
    })
    system_prompt = personality_data.get("system_prompt", "You are a helpful AI assistant.")
    
    # Prepend system message
    full_messages = [
        {"role": "system", "content": system_prompt},
        *messages
    ]
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=0.7,
            max_tokens=2000,
            stream=True
        )
        return response
    except Exception as e:
        st.error(f"Chat API error: {str(e)}")
        raise

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

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
        st.session_state.model_choice = "openai/gpt-3.5-turbo"
    
    if 'current_personality' not in st.session_state:
        st.session_state.current_personality = "Friendly Companion"
    
    if 'custom_personality_name' not in st.session_state:
        st.session_state.custom_personality_name = ""
    
    if 'custom_personality_prompt' not in st.session_state:
        st.session_state.custom_personality_prompt = ""
    
    if 'personality_switch_count' not in st.session_state:
        st.session_state.personality_switch_count = 0
    
    # Create initial chat if none exists
    if not st.session_state.conversations:
        create_new_chat()

init_session_state()

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("Personality Chatbot")
    
    # Personality Selection
    st.subheader("Select Personality")
    
    personality_options = list(PERSONALITIES.keys())
    
    # Ensure current personality is in the list (handles custom personalities)
    if st.session_state.current_personality not in personality_options:
        personality_options.append(st.session_state.current_personality)
    
    # Create a nice display for personality selection
    selected_personality = st.selectbox(
        "Choose a personality",
        options=personality_options,
        index=personality_options.index(st.session_state.current_personality),
        key="personality_selector"
    )
    
    # Check if personality changed
    if selected_personality != st.session_state.current_personality:
        old_personality = st.session_state.current_personality
        st.session_state.current_personality = selected_personality
        st.session_state.personality_switch_count += 1
        
        # Add system message about personality switch
        if st.session_state.messages:
            switch_message = f"*Personality switched from {old_personality} to {selected_personality}*"
            st.session_state.messages.append({
                "role": "assistant",
                "content": switch_message
            })
        
        save_current_chat()
    
    # Show personality details
    current_p = PERSONALITIES.get(selected_personality, {
        "description": "Custom personality",
        "expertise": "User-defined",
        "tone": "Customizable",
        "example": "Custom response style"
    })
    
    st.markdown(f"**Current Personality:**")
    st.markdown(f"**Description:** {current_p.get('description', 'N/A')}")
    st.markdown(f"**Expertise:** {current_p.get('expertise', 'N/A')}")
    st.markdown(f"**Tone:** {current_p.get('tone', 'N/A')}")
    
    # Show example response
    with st.expander("Example Response Style"):
        st.markdown(current_p.get('example', 'Custom personality example'))
    
    st.divider()
    
    # Custom Personality (Advanced Feature)
    with st.expander("Create Custom Personality"):
        st.markdown("**Define your own AI personality!**")
        
        custom_name = st.text_input(
            "Personality Name",
            value=st.session_state.custom_personality_name,
            placeholder="e.g., Motivational Coach"
        )
        
        custom_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.custom_personality_prompt,
            placeholder="You are a motivational coach who...",
            height=150
        )
        
        if st.button("Save Custom Personality", use_container_width=True):
            if custom_name and custom_prompt:
                # Add custom personality to PERSONALITIES
                PERSONALITIES[custom_name] = {
                    "description": "Custom user-defined personality",
                    "expertise": "User-specified",
                    "tone": "Customizable",
                    "system_prompt": custom_prompt,
                    "example": "Custom personality response..."
                }
                st.session_state.custom_personality_name = custom_name
                st.session_state.custom_personality_prompt = custom_prompt
                st.session_state.current_personality = custom_name
                st.success(f"Created '{custom_name}' personality!")
                st.rerun()
            else:
                st.warning("Please provide both name and prompt!")
    
    st.divider()
    
    # Conversation Management
    st.subheader("Conversations")
    if st.button("+ New Chat", use_container_width=True):
        save_current_chat()
        create_new_chat()
        st.rerun()
    
    st.divider()
    
    # Chat History
    st.subheader("Chat History")
    
    all_chats = get_all_chats()
    
    if all_chats:
        for chat_id, chat_data in all_chats[:10]:
            col1, col2 = st.columns([4, 1])
            
            with col1:
                is_current = chat_id == st.session_state.current_chat_id
                chat_personality = chat_data.get('personality', 'Friendly Companion')
                
                # Use simple indicator instead of emojis
                indicator = "[Active] " if is_current else ""
                button_label = f"{indicator}{chat_data.get('title', 'New Chat')}"
                
                if st.button(
                    button_label,
                    key=f"chat_{chat_id}",
                    use_container_width=True,
                    type="primary" if is_current else "secondary"
                ):
                    save_current_chat()
                    load_chat(chat_id)
                    st.rerun()
            
            with col2:
                if not is_current or len(st.session_state.conversations) > 1:
                    if st.button("X", key=f"delete_{chat_id}", help="Delete"):
                        delete_chat(chat_id)
                        st.rerun()
    else:
        st.info("No chat history yet!")
    
    st.divider()
    
    # Settings
    st.subheader("Settings")
    
    # Model selection
    model_option = st.selectbox(
        "Select Model",
        [
            "openai/gpt-3.5-turbo",
            "openai/gpt-4o-mini",
            "openai/gpt-4o",
            "anthropic/claude-3-haiku",
            "meta-llama/llama-3.1-8b-instruct:free",
            "google/gemini-flash-1.5"
        ],
        index=0,
        key="model_selector"
    )
    st.session_state.model_choice = model_option
    
    # Clear current chat
    if st.button("Clear Current Chat", use_container_width=True):
        if st.session_state.current_chat_id:
            st.session_state.messages = []
            st.session_state.chat_title = "New Chat"
            save_current_chat()
            st.rerun()
    
    # Statistics
    st.divider()
    st.subheader("Statistics")
    st.metric("Total Chats", len(st.session_state.conversations))
    st.metric("Personality Switches", st.session_state.personality_switch_count)
    
    # Export Functionality
    st.divider()
    st.subheader("Export Chat")
    
    if st.session_state.messages:
        export_format = st.selectbox(
            "Export Format",
            ["TXT (Human Readable)", "JSON (Structured)", "CSV (Data Analysis)"],
            key="export_format"
        )
        
        if st.button("Export Current Chat", use_container_width=True):
            # Generate export based on format
            if "TXT" in export_format:
                content = export_as_txt(
                    st.session_state.messages,
                    st.session_state.chat_title,
                    st.session_state.current_personality
                )
                file_ext = "txt"
                mime_type = "text/plain"
            elif "JSON" in export_format:
                content = export_as_json(
                    st.session_state.messages,
                    st.session_state.chat_title,
                    st.session_state.current_personality
                )
                file_ext = "json"
                mime_type = "application/json"
            else:  # CSV
                content = export_as_csv(
                    st.session_state.messages,
                    st.session_state.chat_title,
                    st.session_state.current_personality
                )
                file_ext = "csv"
                mime_type = "text/csv"
            
            # Create filename
            filename = f"{st.session_state.chat_title.replace(' ', '_')}_{st.session_state.current_personality.replace(' ', '_')}.{file_ext}"
            
            # Download button
            st.download_button(
                label=f"Download {file_ext.upper()}",
                data=content,
                file_name=filename,
                mime=mime_type,
                use_container_width=True
            )
            st.success(f"Ready to download as {file_ext.upper()}!")
    else:
        st.info("Start a conversation to enable export")

# ============================================================================
# MAIN INTERFACE
# ============================================================================

# Display personality badge at top
current_p = PERSONALITIES.get(st.session_state.current_personality, {
    "description": "Custom personality",
    "expertise": "User-defined",
    "tone": "Customizable",
    "system_prompt": "You are a helpful assistant.",
    "example": "Custom response"
})

st.markdown(f"""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
    <h2 style="margin: 0; color: white;">
        {st.session_state.current_personality}
    </h2>
    <p style="margin: 5px 0 0 0; color: #e0e0e0; font-size: 14px;">
        {current_p.get('description', 'Custom personality')} | Model: {st.session_state.model_choice}
    </p>
</div>
""", unsafe_allow_html=True)

# Info expander
with st.expander("About Personality Chatbot", expanded=False):
    st.markdown("""
    ### How It Works
    
    Choose from different AI personalities, each with unique:
    - **Communication Style** - How the AI speaks
    - **Expertise Areas** - What they know best
    - **Tone & Approach** - Their attitude and method
    
    ### Features
    - 5 Built-in Personalities
    - Custom Personality Creator
    - Mid-Conversation Switching
    - Personality-Specific Responses
    - Conversation History per Personality
    
    ### Tips
    - Try the same question with different personalities to see how responses vary!
    - Switch personalities mid-conversation for different perspectives
    - Create custom personalities for specific use cases
    """)

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
    
    # Generate response with current personality
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Prepare messages for API
        messages_for_api = [
            {"role": m["role"], "content": m["content"]} 
            for m in st.session_state.messages
        ]
        
        try:
            # Stream response with personality
            for chunk in chat_with_personality(
                messages_for_api, 
                st.session_state.model_choice,
                st.session_state.current_personality
            ):
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            save_current_chat()
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            # Remove the user message if there was an error
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()