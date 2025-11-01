"""
Streamlit Chat Application
A modern chat interface with customizable settings and session management
"""

import streamlit as st
import time
import random
from datetime import datetime
from huggingface_integration import (
    initialize_openroute_chat, 
    set_openroute_api_key,
    set_openroute_model,
    generate_openroute_response, 
    reset_openroute_conversation,
    get_openroute_model_info,
    get_model_list,
    get_model_by_category,
    export_chat_history
)

# Page configuration
st.set_page_config(
    page_title="Chat Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables with defaults"""
    defaults = {
        "messages": [
            {"role": "assistant", "content": "Hello! I'm your chat assistant. How can I help you today?"}
        ],
        "settings": {
            "assistant_name": "Chat Assistant",
            "response_style": "Friendly",
            "max_history": 50,
            "show_timestamps": True,
            "theme": "Light"
        },
        "gpt_params": {
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 150,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "response_length": "Medium"
        },
        "openroute_params": {
            "model_id": "meta-llama/llama-3.1-8b-instruct:free",
            "api_key": "",
            "use_openroute": False,
            "max_length": 150,
            "temperature": 0.7,
            "top_p": 0.9
        },
        "stats": {
            "total_messages": 0,
            "session_start": datetime.now()
        }
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Initialize app
initialize_session_state()

# Helper functions
def add_message(role, content):
    """Add a message to chat history with timestamp"""
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now()
    }
    st.session_state.messages.append(message)

    # Trim history if too long
    max_history = st.session_state.settings["max_history"]
    if len(st.session_state.messages) > max_history:
        # Keep first message (greeting) and trim from the middle
        st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-(max_history-1):]

def generate_response(user_input):
    """Generate response using either OpenRoute API or GPT-style parameters"""
    openroute_params = st.session_state.openroute_params
    
    # Use OpenRoute API if enabled
    if openroute_params["use_openroute"]:
        try:
            response = generate_openroute_response(
                user_input,
                max_length=openroute_params["max_length"],
                temperature=openroute_params["temperature"],
                top_p=openroute_params["top_p"]
            )
            return response
        except Exception as e:
            st.error(f"OpenRoute API error: {str(e)}")
            return "Sorry, there was an error with the OpenRoute API. Please try again."
    
    # Use GPT-style parameters for demo responses
    style = st.session_state.settings["response_style"]
    params = st.session_state.gpt_params
    model = params["model"]
    
    # Base responses by style
    if style == "Professional":
        base_responses = [
            f"Thank you for your message regarding '{user_input}'. I've processed your request and understand your query.",
            f"I acknowledge your input: '{user_input}'. Please allow me to provide you with a comprehensive response.",
            f"Your inquiry about '{user_input}' has been noted. I'm here to assist you with professional guidance."
        ]
    elif style == "Creative":
        base_responses = [
            f"🎨 Wow! '{user_input}' - that sparks so many creative possibilities! Let me paint you a picture with words...",
            f"✨ Your message '{user_input}' is like a canvas waiting for artistic interpretation! Here's my creative take...",
            f"🌟 '{user_input}' - what an inspiring prompt! Let me weave some creative magic around that idea..."
        ]
    else:  # Friendly
        base_responses = [
            f"That's really interesting! You mentioned '{user_input}' and I think that's a great topic to explore together! 😊",
            f"I love that you brought up '{user_input}'! It's always exciting to chat about new things. Let me share my thoughts!",
            f"Hey, great question about '{user_input}'! I'm happy to help you with that. Here's what I'm thinking..."
        ]
    
    # Apply GPT parameters to modify response
    response = apply_gpt_parameters(base_responses, user_input, params)
    
    # Add model-specific behavior
    if "gpt-4o" in model:
        response += f" (Powered by {model})"
    elif "gpt-4" in model:
        response += f" (Using {model})"
    elif "gpt-3.5" in model:
        response += f" (via {model})"
    
    return response

def apply_gpt_parameters(base_responses, user_input, params):
    """Apply GPT-style parameters to modify response generation"""
    # Select base response
    base_response = random.choice(base_responses)
    
    # Apply temperature (creativity/randomness)
    temperature = params["temperature"]
    if temperature > 0.8:
        # High creativity - add more varied elements
        creativity_additions = [
            " Let me think outside the box here...",
            " This is fascinating from multiple angles!",
            " I'm seeing this through a completely different lens now...",
            " What an intriguing perspective!",
            " This opens up so many possibilities!"
        ]
        if random.random() < temperature:
            base_response += random.choice(creativity_additions)
    elif temperature < 0.3:
        # Low creativity - more focused, direct
        base_response = base_response.replace("!", ".").replace("😊", "").replace("🎨", "").replace("✨", "").replace("🌟", "")
    
    # Apply response length based on max_tokens
    max_tokens = params["max_tokens"]
    response_length = params["response_length"]
    
    if response_length == "Short" or max_tokens < 100:
        # Shorten response
        if len(base_response) > 100:
            base_response = base_response[:100] + "..."
    elif response_length == "Long" or max_tokens > 200:
        # Extend response
        extensions = [
            " I'd love to dive deeper into this topic with you.",
            " There are several aspects we could explore further.",
            " This is definitely worth discussing in more detail.",
            " I have many thoughts on this subject that might interest you.",
            " This connects to so many other interesting concepts."
        ]
        if random.random() < 0.7:
            base_response += random.choice(extensions)
    
    # Apply frequency penalty (avoid repetition)
    frequency_penalty = params["frequency_penalty"]
    if frequency_penalty > 0.5:
        # Reduce repetitive words
        words = base_response.split()
        if len(set(words)) < len(words) * 0.7:  # If too repetitive
            base_response = base_response.replace("really", "quite").replace("very", "quite").replace("so", "quite")
    
    # Apply presence penalty (encourage new topics)
    presence_penalty = params["presence_penalty"]
    if presence_penalty > 0.5:
        # Add topic variation
        topic_variations = [
            " Speaking of which, have you considered the broader implications?",
            " This reminds me of related concepts we could explore.",
            " There's an interesting parallel to other areas of discussion.",
            " This connects to some fascinating broader themes."
        ]
        if random.random() < presence_penalty:
            base_response += random.choice(topic_variations)
    
    # Apply top_p (nucleus sampling effect)
    top_p = params["top_p"]
    if top_p < 0.5:
        # More focused, conservative responses
        base_response = base_response.replace("!", ".").replace("?", ".")
    elif top_p > 0.9:
        # More diverse, exploratory responses
        if not any(char in base_response for char in ["!", "?", "😊", "🎨"]):
            base_response += " What do you think about this perspective?"
    
    return base_response

def apply_theme(theme):
    """Apply CSS theme based on user selection"""
    if theme == "Dark":
        dark_theme_css = """
        <style>
        /* Main background */
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        
        /* Sidebar background */
        [data-testid="stSidebar"] {
            background-color: #1e2130;
        }
        
        /* Text colors */
        .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {
            color: #fafafa !important;
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            background-color: #262730;
            color: #fafafa;
            border-color: #3a3b4a;
        }
        
        /* Slider */
        .stSlider > div > div {
            background-color: #262730;
        }
        
        /* Checkbox */
        .stCheckbox > label {
            color: #fafafa !important;
        }
        
        /* Button styling */
        button {
            background-color: #262730 !important;
            color: #fafafa !important;
            border-color: #3a3b4a !important;
        }
        
        button:hover {
            background-color: #3a3b4a !important;
        }
        
        /* Chat messages */
        .stChatMessage {
            background-color: #1e2130;
        }
        
        /* Chat input */
        [data-baseweb="input"] {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #1e2130;
            color: #fafafa;
        }
        
        /* Divider */
        hr {
            border-color: #3a3b4a;
        }
        
        /* Metric containers */
        [data-testid="stMetricContainer"] {
            background-color: #1e2130;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        
        /* Code blocks */
        code {
            background-color: #262730;
            color: #fafafa;
        }
        </style>
        """
        st.markdown(dark_theme_css, unsafe_allow_html=True)
    else:
        light_theme_css = """
        <style>
        /* Reset to default light theme */
        .stApp {
            background-color: #ffffff;
            color: #262730;
        }
        
        [data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }
        
        .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {
            color: #262730 !important;
        }
        
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            background-color: #ffffff;
            color: #262730;
            border-color: #d3d8e0;
        }
        
        .stSlider > div > div {
            background-color: #ffffff;
        }
        
        .stCheckbox > label {
            color: #262730 !important;
        }
        
        button {
            background-color: #ffffff !important;
            color: #262730 !important;
            border-color: #d3d8e0 !important;
        }
        
        button:hover {
            background-color: #f0f2f6 !important;
        }
        
        .stChatMessage {
            background-color: #f0f2f6;
        }
        
        [data-baseweb="input"] {
            background-color: #ffffff !important;
            color: #262730 !important;
        }
        
        .streamlit-expanderHeader {
            background-color: #ffffff;
            color: #262730;
        }
        
        hr {
            border-color: #d3d8e0;
        }
        
        [data-testid="stMetricContainer"] {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        
        code {
            background-color: #f0f2f6;
            color: #262730;
        }
        </style>
        """
        st.markdown(light_theme_css, unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Assistant settings
    st.subheader("Assistant Settings")
    assistant_name = st.text_input(
        "Assistant Name:",
        value=st.session_state.settings["assistant_name"]
    )

    response_style = st.selectbox(
        "Response Style:",
        ["Friendly", "Professional", "Creative"],
        index=["Friendly", "Professional", "Creative"].index(st.session_state.settings["response_style"])
    )

    # Chat settings
    st.subheader("Chat Settings")
    max_history = st.slider(
        "Max Chat History:",
        min_value=10,
        max_value=100,
        value=st.session_state.settings["max_history"],
        help="Maximum number of messages to keep in chat history"
    )

    show_timestamps = st.checkbox(
        "Show Timestamps",
        value=st.session_state.settings["show_timestamps"]
    )

    # Theme settings
    st.subheader("🎨 Theme Settings")
    theme = st.selectbox(
        "Theme:",
        ["Light", "Dark"],
        index=["Light", "Dark"].index(st.session_state.settings["theme"]),
        help="Choose between light and dark mode"
    )

    st.divider()

    # Model Selection
    st.subheader("🤖 Model Selection")
    
    # Model provider toggle
    use_openroute = st.checkbox(
        "Use OpenRoute API",
        value=st.session_state.openroute_params["use_openroute"],
        help="Switch between GPT-style demo responses and real OpenRoute API models"
    )
    
    if use_openroute:
        # OpenRoute API Configuration
        st.subheader("🌐 OpenRoute API")
        
        # API Key input
        api_key = st.text_input(
            "OpenRoute API Key:",
            value=st.session_state.openroute_params["api_key"],
            type="password",
            help="Enter your OpenRoute API key. Get one at https://openrouter.ai/"
        )
        
        # Get models for OpenRoute
        available_models = get_model_by_category("conversational")
        model_options = list(available_models.keys())
        model_names = [available_models[model_id]["name"] for model_id in model_options]
        
        # Model selection
        selected_model_idx = st.selectbox(
            "Select Model:",
            range(len(model_names)),
            index=model_options.index(st.session_state.openroute_params["model_id"]) if st.session_state.openroute_params["model_id"] in model_options else 0,
            format_func=lambda x: f"{model_names[x]} - {available_models[model_options[x]]['description']}",
            help="Choose an OpenRoute model to use"
        )
        
        selected_model_id = model_options[selected_model_idx]
        selected_model_info = available_models[selected_model_id]
        
        # Display model info
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Model Size", selected_model_info["size"])
        with col2:
            st.metric("Type", selected_model_info["type"])
        
        # Test API connection
        if st.button("🔗 Test API Connection", type="primary"):
            if api_key:
                with st.spinner("Testing API connection..."):
                    set_openroute_api_key(api_key)
                    set_openroute_model(selected_model_id)
                    test_response = generate_openroute_response("Hello", max_length=10)
                    if "Error" not in test_response:
                        st.success("API connection successful!")
                        st.session_state.openroute_params["api_key"] = api_key
                        st.session_state.openroute_params["model_id"] = selected_model_id
                    else:
                        st.error(f"API connection failed: {test_response}")
            else:
                st.error("Please enter your API key first.")
        
        # OpenRoute parameters
        st.subheader("⚙️ OpenRoute Parameters")
        
        openroute_max_length = st.slider(
            "Max Length:",
            min_value=50,
            max_value=500,
            value=st.session_state.openroute_params["max_length"],
            step=10,
            help="Maximum length of generated response"
        )
        
        openroute_temperature = st.slider(
            "Temperature:",
            min_value=0.1,
            max_value=2.0,
            value=st.session_state.openroute_params["temperature"],
            step=0.1,
            help="Controls randomness in generation"
        )
        
        openroute_top_p = st.slider(
            "Top-p:",
            min_value=0.1,
            max_value=1.0,
            value=st.session_state.openroute_params["top_p"],
            step=0.1,
            help="Nucleus sampling parameter"
        )
        
        # Update OpenRoute parameters
        st.session_state.openroute_params.update({
            "use_openroute": use_openroute,
            "api_key": api_key,
            "model_id": selected_model_id,
            "max_length": openroute_max_length,
            "temperature": openroute_temperature,
            "top_p": openroute_top_p
        })
        
        # Model info display
        with st.expander("📊 OpenRoute Model Info", expanded=False):
            model_info = get_openroute_model_info()
            for key, value in model_info.items():
                st.write(f"**{key.title()}:** {value}")
        
        # Chat history management
        st.subheader("💾 Chat History")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Reset Conversation"):
                reset_openroute_conversation()
                st.success("OpenRoute conversation reset!")
        
        with col2:
            if st.button("📤 Export History"):
                filename = export_chat_history()
                if filename:
                    st.success(f"Chat history exported to {filename}")
        
        with col3:
            if st.button("📊 View History"):
                model_info = get_openroute_model_info()
                st.info(f"Total messages: {model_info.get('conversation_length', 0)}")
    
    else:
        # GPT Parameters (when HF is disabled)
        st.subheader("🤖 GPT Parameters")
        st.caption("Fine-tune response generation behavior")
        
        # Model selection
        model = st.selectbox(
            "OpenAI Model:",
            [
                "gpt-4o",
                "gpt-4o-mini", 
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ],
            index=[
                "gpt-4o",
                "gpt-4o-mini", 
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ].index(st.session_state.gpt_params["model"]),
            help="Select the OpenAI model to use for responses"
        )
        
        # Model info display
        model_info = {
            "gpt-4o": "Latest GPT-4 model with vision capabilities",
            "gpt-4o-mini": "Faster, cheaper version of GPT-4o",
            "gpt-4-turbo": "High-performance GPT-4 with large context",
            "gpt-4": "Standard GPT-4 model",
            "gpt-3.5-turbo": "Fast and efficient GPT-3.5 model",
            "gpt-3.5-turbo-16k": "GPT-3.5 with extended context length"
        }
        st.caption(f"ℹ️ {model_info[model]}")
        
        # Temperature (creativity)
        temperature = st.slider(
            "Temperature:",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.gpt_params["temperature"],
            step=0.1,
            help="Controls randomness. Lower = more focused, Higher = more creative"
        )
        
        # Max tokens
        max_tokens = st.slider(
            "Max Tokens:",
            min_value=50,
            max_value=500,
            value=st.session_state.gpt_params["max_tokens"],
            step=10,
            help="Maximum length of response"
        )
        
        # Top-p (nucleus sampling)
        top_p = st.slider(
            "Top-p:",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.gpt_params["top_p"],
            step=0.1,
            help="Controls diversity. Lower = more focused, Higher = more diverse"
        )
        
        # Frequency penalty
        frequency_penalty = st.slider(
            "Frequency Penalty:",
            min_value=-2.0,
            max_value=2.0,
            value=st.session_state.gpt_params["frequency_penalty"],
            step=0.1,
            help="Reduces repetition. Positive = less repetitive"
        )
        
        # Presence penalty
        presence_penalty = st.slider(
            "Presence Penalty:",
            min_value=-2.0,
            max_value=2.0,
            value=st.session_state.gpt_params["presence_penalty"],
            step=0.1,
            help="Encourages new topics. Positive = more diverse topics"
        )
        
        # Response length preset
        response_length = st.selectbox(
            "Response Length:",
            ["Short", "Medium", "Long"],
            index=["Short", "Medium", "Long"].index(st.session_state.gpt_params["response_length"]),
            help="Quick preset for response length"
        )
        
        # Model-specific parameter adjustments
        if model != st.session_state.gpt_params["model"]:
            # Auto-adjust parameters based on model
            if "gpt-4o" in model:
                # GPT-4o models work well with higher creativity
                if temperature < 0.5:
                    temperature = 0.7
            elif "gpt-3.5" in model:
                # GPT-3.5 models work better with moderate settings
                if temperature > 1.5:
                    temperature = 1.0
                if max_tokens > 300:
                    max_tokens = 200
        
        # Preset buttons
        st.write("**Quick Presets:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎯 Focused", help="Low temperature, focused responses"):
                st.session_state.gpt_params.update({
                    "temperature": 0.3,
                    "top_p": 0.5,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0,
                    "response_length": "Medium"
                })
                st.rerun()
        
        with col2:
            if st.button("🎨 Creative", help="High temperature, creative responses"):
                st.session_state.gpt_params.update({
                    "temperature": 1.2,
                    "top_p": 0.9,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0,
                    "response_length": "Long"
                })
                st.rerun()
        
        with col3:
            if st.button("⚖️ Balanced", help="Default balanced settings"):
                st.session_state.gpt_params.update({
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0,
                    "response_length": "Medium"
                })
                st.rerun()
        
        # Current parameter display
        with st.expander("📊 Current Parameters", expanded=False):
            st.write(f"**Model:** {model}")
            st.write(f"**Temperature:** {temperature}")
            st.write(f"**Max Tokens:** {max_tokens}")
            st.write(f"**Top-p:** {top_p}")
            st.write(f"**Frequency Penalty:** {frequency_penalty}")
            st.write(f"**Presence Penalty:** {presence_penalty}")
            st.write(f"**Response Length:** {response_length}")

    # Update settings
    previous_theme = st.session_state.settings["theme"]
    st.session_state.settings.update({
        "assistant_name": assistant_name,
        "response_style": response_style,
        "max_history": max_history,
        "show_timestamps": show_timestamps,
        "theme": theme
    })
    
    # Update GPT parameters (only if not using OpenRoute)
    if not st.session_state.openroute_params["use_openroute"]:
        st.session_state.gpt_params.update({
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "response_length": response_length
        })
    
    # Apply theme change and rerun if theme changed
    if theme != previous_theme:
        st.rerun()

    st.divider()

    # Statistics
    st.subheader("📊 Session Stats")
    session_duration = datetime.now() - st.session_state.stats["session_start"]
    minutes = session_duration.seconds // 60
    seconds = session_duration.seconds % 60
    st.metric("Session Duration", f"{minutes}m {seconds}s")
    st.metric("Messages Sent", st.session_state.stats["total_messages"])
    st.metric("Total Messages", len(st.session_state.messages))

    st.divider()

    # Actions
    st.subheader("🔧 Actions")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.messages = [
                {"role": "assistant", "content": f"Hello! I'm {assistant_name}. Chat cleared - let's start fresh!"}
            ]
            st.rerun()

    with col2:
        if st.button("📤 Export Chat", type="secondary"):
            chat_export = f"Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            chat_export += "=" * 50 + "\n\n"

            for msg in st.session_state.messages:
                role = "You" if msg["role"] == "user" else assistant_name
                timestamp = msg.get("timestamp", datetime.now()).strftime("%H:%M")
                chat_export += f"[{timestamp}] {role}: {msg['content']}\n\n"

            st.download_button(
                "💾 Download",
                chat_export,
                file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

# Apply theme
apply_theme(st.session_state.settings["theme"])

# Main content area
st.title(f"💬 {assistant_name}")

# Display current model info
if st.session_state.openroute_params["use_openroute"]:
    model_info = get_openroute_model_info()
    model_name = st.session_state.openroute_params["model_id"].split("/")[-1]
    st.caption(f"🌐 OpenRoute: {model_name} | Style: {response_style} | History: {max_history} | Temp: {st.session_state.openroute_params['temperature']} | Max Length: {st.session_state.openroute_params['max_length']}")
else:
    st.caption(f"🤖 GPT Model: {st.session_state.gpt_params['model']} | Style: {response_style} | History: {max_history} | Temp: {st.session_state.gpt_params['temperature']} | Tokens: {st.session_state.gpt_params['max_tokens']}")

# Chat display
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        role_display = "You" if message["role"] == "user" else assistant_name

        with st.chat_message(message["role"]):
            if show_timestamps and "timestamp" in message:
                timestamp = message["timestamp"].strftime("%H:%M:%S")
                st.caption(f"{role_display} - {timestamp}")

            st.write(message["content"])

# Chat input
if prompt := st.chat_input(f"Message {assistant_name}..."):
    # Add user message
    add_message("user", prompt)
    st.session_state.stats["total_messages"] += 1

    # Display user message
    with st.chat_message("user"):
        if show_timestamps:
            st.caption(f"You - {datetime.now().strftime('%H:%M:%S')}")
        st.write(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        if show_timestamps:
            st.caption(f"{assistant_name} - {datetime.now().strftime('%H:%M:%S')}")

        # Show typing indicator
        with st.spinner(f"{assistant_name} is thinking..."):
            time.sleep(random.uniform(0.5, 2.0))  # Realistic delay

        # Generate response
        response = generate_response(prompt)
        st.write(response)

        # Add assistant response to history
        add_message("assistant", response)

        # Rerun to update the display
        st.rerun()

# Footer with helpful info
st.write("---")
with st.expander("ℹ️ About This App"):
    st.write(f"""
    **Streamlit Chat Application**

    This is a complete chat interface built with Streamlit featuring:

    ✅ **Session State Management**: Persistent chat history and settings
    ✅ **Professional UI**: Clean layout with sidebar configuration
    ✅ **Customizable Settings**: Change assistant name, response style, and more
    ✅ **Export Functionality**: Download chat history as text file
    ✅ **Statistics Tracking**: Session metrics and usage data
    ✅ **Modern Chat Interface**: Using Streamlit's chat components

    Current session: {len(st.session_state.messages)} messages in {max_history} message limit
    """)
