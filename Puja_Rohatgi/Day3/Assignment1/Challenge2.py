import streamlit as st
from openai import OpenAI

# Page config
st.set_page_config(page_title="AI Personalities", page_icon="🎭", layout="wide")

# Personality definitions
PERSONALITIES = {
    "Professional 💼": {
        "prompt": "You are a professional business consultant. Use formal language, provide structured responses with clear points, and focus on practical solutions. Always maintain a corporate tone.",
        "color": "blue"
    },
    "Creative 🎨": {
        "prompt": "You are an imaginative creative assistant. Use expressive, colorful language, metaphors, and storytelling. Encourage wild ideas and think outside the box. Be enthusiastic and inspiring!",
        "color": "purple"
    },
    "Technical 💻": {
        "prompt": "You are a technical expert and senior engineer. Provide precise, detailed explanations with code examples. Use technical terminology, mention best practices, and focus on implementation details.",
        "color": "green"
    },
    "Friendly 😊": {
        "prompt": "You are a warm, supportive friend. Be casual, use friendly language, show empathy, and make the conversation feel comfortable. Add encouragement and positivity!",
        "color": "orange"
    },
    "Wise Sage 🧙": {
        "prompt": "You are an ancient wise sage with deep philosophical insights. Speak with wisdom, use thoughtful metaphors, and provide profound perspectives on life and knowledge.",
        "color": "gray"
    },
    "Custom ✨": {
        "prompt": "",
        "color": "red"
    }
}

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'personality' not in st.session_state:
    st.session_state.personality = "Friendly 😊"
if 'custom_prompt' not in st.session_state:
    st.session_state.custom_prompt = "You are a helpful assistant that..."

# Sidebar
with st.sidebar:
    st.title("🎭 Personality Selector")
    
    api_key = st.text_input("OpenRouter API Key", type="password", key="api_key")
    
    st.divider()
    
    # Personality selector
    new_personality = st.selectbox(
        "Choose Personality:",
        list(PERSONALITIES.keys()),
        index=list(PERSONALITIES.keys()).index(st.session_state.personality)
    )
    
    # Detect personality change
    if new_personality != st.session_state.personality:
        st.session_state.personality = new_personality
        st.session_state.messages.append({
            "role": "system",
            "content": f"🔄 Switched to **{new_personality}** mode"
        })
        st.rerun()
    
    # Show current personality info
    current = PERSONALITIES[st.session_state.personality]
    st.info(f"**Active:** {st.session_state.personality}")
    
    # Custom personality setup
    if st.session_state.personality == "Custom ✨":
        st.divider()
        custom = st.text_area(
            "Define Custom Personality:",
            value=st.session_state.custom_prompt,
            height=150,
            help="Describe how the AI should behave"
        )
        if st.button("💾 Save Custom", use_container_width=True):
            st.session_state.custom_prompt = custom
            st.success("Saved!")
    
    st.divider()
    
    # Model selection
    model = st.selectbox(
        "Model:",
        ["google/gemini-flash-1.5", "meta-llama/llama-3.1-8b-instruct", "anthropic/claude-3-haiku"],
        help="Cheaper models = lower cost"
    )
    
    # Stats
    st.metric("Messages", len([m for m in st.session_state.messages if m["role"] in ["user", "assistant"]]))
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main content
st.title(f"🤖 AI Assistant - {st.session_state.personality}")

if not api_key:
    st.info("👈 Enter your OpenRouter API key to start")
    st.markdown("Get your key at [openrouter.ai](https://openrouter.ai)")
    st.stop()

# Initialize client
client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

def get_system_prompt():
    """Get the current personality's system prompt"""
    if st.session_state.personality == "Custom ✨":
        return st.session_state.custom_prompt
    return PERSONALITIES[st.session_state.personality]["prompt"]

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "system":
        st.info(msg["content"])
    elif msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner(f"Thinking as {st.session_state.personality}..."):
            try:
                # Build messages with system prompt
                api_messages = [{"role": "system", "content": get_system_prompt()}]
                
                # Add conversation history (exclude system messages)
                for m in st.session_state.messages:
                    if m["role"] in ["user", "assistant"]:
                        api_messages.append({"role": m["role"], "content": m["content"]})
                
                # API call
                response = client.chat.completions.create(
                    model=model,
                    messages=api_messages,
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
                
                # Save assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer with quick personality examples
st.divider()
with st.expander("💡 Try asking the same question to different personalities"):
    st.markdown("""
    **Example questions to test:**
    - "How do I learn programming?"
    - "I'm feeling stressed about work"
    - "Explain quantum computing"
    - "Should I start a business?"
    
    Switch personalities and see how responses change!
    """)

# Personality comparison hint
if len(st.session_state.messages) > 0:
    st.caption(f"💬 Currently speaking as: **{st.session_state.personality}**")