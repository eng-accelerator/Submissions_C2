import streamlit as st
from datetime import datetime
from utils.config_manager import load_config, save_config, get_active_model, get_provider_config
from utils.file_processor import process_uploaded_file
from utils.llm_provider import LLMProvider, prepare_messages_with_files
from utils.chat_history import save_chat, load_chat, list_chats, delete_chat, generate_chat_title
from utils.personality_prompts import get_personality_prompt, get_personality_descriptions
from utils.export_manager import export_to_txt, export_to_json, export_to_csv, generate_filename, calculate_statistics

st.set_page_config(
    page_title="ChatGPT-like App",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

if 'config' not in st.session_state:
    st.session_state.config = load_config()

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

if 'current_chat_title' not in st.session_state:
    st.session_state.current_chat_title = "New Chat"

if 'pending_file_uploads' not in st.session_state:
    st.session_state.pending_file_uploads = []

if 'translation_mode' not in st.session_state:
    st.session_state.translation_mode = False

if 'target_language' not in st.session_state:
    st.session_state.target_language = "English"

if 'personality_mode' not in st.session_state:
    st.session_state.personality_mode = "Professional"

if 'custom_personality' not in st.session_state:
    st.session_state.custom_personality = ""

def initialize_session_from_config():
    config = st.session_state.config

    if 'provider' not in st.session_state:
        st.session_state.provider = config['settings']['provider']

    if 'mode' not in st.session_state:
        st.session_state.mode = config['settings']['mode']

    if 'temperature' not in st.session_state:
        st.session_state.temperature = config['settings']['temperature']

    if 'max_tokens' not in st.session_state:
        st.session_state.max_tokens = config['settings']['max_tokens']

    if 'custom_instructions' not in st.session_state:
        st.session_state.custom_instructions = config['settings']['custom_instructions']

    if 'translation_mode' not in st.session_state:
        st.session_state.translation_mode = config['settings'].get('translation_mode', False)

    if 'target_language' not in st.session_state:
        st.session_state.target_language = config['settings'].get('target_language', 'English')

    if 'personality_mode' not in st.session_state:
        st.session_state.personality_mode = config['settings'].get('personality_mode', 'Professional')

    if 'custom_personality' not in st.session_state:
        st.session_state.custom_personality = config['settings'].get('custom_personality', '')

initialize_session_from_config()

with st.sidebar:
    st.title("⚙️ Settings")

    with st.expander("🎭 AI Personality", expanded=False):
        personality_descriptions = get_personality_descriptions()

        personality_mode = st.selectbox(
            "Select Personality Mode",
            ["Professional", "Creative", "Technical", "Friendly", "Custom"],
            index=["Professional", "Creative", "Technical", "Friendly", "Custom"].index(st.session_state.personality_mode),
            key="personality_select",
            help="Choose the AI personality that best fits your needs"
        )

        previous_personality = st.session_state.personality_mode
        st.session_state.personality_mode = personality_mode
        st.session_state.config['settings']['personality_mode'] = personality_mode

        st.caption(personality_descriptions.get(personality_mode, ""))

        if personality_mode == "Custom":
            custom_personality = st.text_area(
                "Custom Personality Instructions",
                value=st.session_state.custom_personality,
                height=200,
                key="custom_personality_input",
                placeholder="Define your custom AI personality here. Describe the style, tone, expertise, and approach you want the AI to use...",
                help="Create your own AI personality by describing how you want it to respond"
            )
            st.session_state.custom_personality = custom_personality
            st.session_state.config['settings']['custom_personality'] = custom_personality

            if not custom_personality.strip():
                st.warning("⚠️ Custom personality is empty. The AI will use default behavior.")
        else:
            personality_info = get_personality_prompt(personality_mode)
            with st.expander("ℹ️ View Personality Details", expanded=False):
                st.markdown(f"**Name:** {personality_info['name']}")
                st.markdown(f"**Expertise:** {personality_info['expertise']}")
                st.markdown(f"**Example Response:** *{personality_info['example']}*")

        if personality_mode != previous_personality:
            st.info("💡 Personality changed! The new personality will apply to your next message.")

    with st.expander("🌍 Translation Settings", expanded=False):
        translation_mode = st.toggle(
            "Enable Translation Mode",
            value=st.session_state.translation_mode,
            key="translation_toggle",
            help="When enabled, automatically detects language and translates to your target language"
        )

        previous_language = st.session_state.target_language
        st.session_state.translation_mode = translation_mode
        st.session_state.config['settings']['translation_mode'] = translation_mode

        if translation_mode:
            st.info("Translation mode is active. Every message will be translated to your target language with cultural context.")

        languages = [
            "English", "Spanish", "French", "German", "Italian", "Portuguese",
            "Russian", "Japanese", "Chinese (Simplified)", "Chinese (Traditional)",
            "Korean", "Arabic", "Hindi", "Turkish", "Dutch", "Polish",
            "Swedish", "Norwegian", "Danish", "Finnish", "Greek", "Hebrew",
            "Thai", "Vietnamese", "Indonesian", "Malay", "Tagalog"
        ]

        target_language = st.selectbox(
            "Target Language",
            languages,
            index=languages.index(st.session_state.target_language) if st.session_state.target_language in languages else 0,
            key="target_lang_select"
        )

        if target_language != previous_language:
            st.session_state.messages = []
            st.session_state.uploaded_files = []
            st.session_state.current_chat_id = None
            st.session_state.current_chat_title = "New Chat"

        st.session_state.target_language = target_language
        st.session_state.config['settings']['target_language'] = target_language

    with st.expander("📝 Custom Instructions", expanded=False):
        custom_instructions = st.text_area(
            "Custom Instructions (System Prompt)",
            value=st.session_state.custom_instructions,
            height=150,
            key="custom_inst",
            disabled=st.session_state.translation_mode,
            help="Disabled when translation mode is active" if st.session_state.translation_mode else ""
        )
        if not st.session_state.translation_mode:
            st.session_state.custom_instructions = custom_instructions
            st.session_state.config['settings']['custom_instructions'] = custom_instructions

        char_count = len(custom_instructions)
        st.caption(f"Characters: {char_count}")

    with st.expander("🔌 Provider Configuration", expanded=False):
        provider = st.radio(
            "Select Provider",
            ["openrouter", "ollama"],
            index=0 if st.session_state.provider == "openrouter" else 1,
            key="provider_radio"
        )
        st.session_state.provider = provider

        if provider == "openrouter":
            st.subheader("OpenRouter")
            base_url = st.text_input(
                "Base URL",
                value=st.session_state.config['openrouter']['base_url'],
                key="or_base_url"
            )
            api_key = st.text_input(
                "API Key",
                value=st.session_state.config['openrouter']['api_key'],
                type="password",
                key="or_api_key"
            )
            mini_model = st.text_input(
                "Mini Model",
                value=st.session_state.config['openrouter']['mini_model'],
                key="or_mini"
            )
            thinking_model = st.text_input(
                "Thinking Model",
                value=st.session_state.config['openrouter']['thinking_model'],
                key="or_thinking"
            )
            multimodal_model = st.text_input(
                "Multimodal Model",
                value=st.session_state.config['openrouter']['multimodal_model'],
                key="or_multimodal"
            )

            st.session_state.config['openrouter']['base_url'] = base_url
            st.session_state.config['openrouter']['api_key'] = api_key
            st.session_state.config['openrouter']['mini_model'] = mini_model
            st.session_state.config['openrouter']['thinking_model'] = thinking_model
            st.session_state.config['openrouter']['multimodal_model'] = multimodal_model

            if st.button("Test OpenRouter Connection", key="test_or"):
                provider_config = get_provider_config(st.session_state.config)
                llm = LLMProvider("openrouter", provider_config, st.session_state.config['settings'])
                success, message = llm.test_connection()
                if success:
                    st.success(message)
                else:
                    st.error(f"Connection failed: {message}")

        else:
            st.subheader("Ollama")
            endpoint = st.text_input(
                "Endpoint URL",
                value=st.session_state.config['ollama']['endpoint'],
                key="ollama_endpoint"
            )
            mini_model = st.text_input(
                "Mini Model",
                value=st.session_state.config['ollama']['mini_model'],
                key="ollama_mini"
            )
            thinking_model = st.text_input(
                "Thinking Model",
                value=st.session_state.config['ollama']['thinking_model'],
                key="ollama_thinking"
            )
            multimodal_model = st.text_input(
                "Multimodal Model",
                value=st.session_state.config['ollama']['multimodal_model'],
                key="ollama_multimodal"
            )

            st.session_state.config['ollama']['endpoint'] = endpoint
            st.session_state.config['ollama']['mini_model'] = mini_model
            st.session_state.config['ollama']['thinking_model'] = thinking_model
            st.session_state.config['ollama']['multimodal_model'] = multimodal_model

            if st.button("Test Ollama Connection", key="test_ollama"):
                provider_config = get_provider_config(st.session_state.config)
                llm = LLMProvider("ollama", provider_config, st.session_state.config['settings'])
                success, message = llm.test_connection()
                if success:
                    st.success(message)
                else:
                    st.error(f"Connection failed: {message}")

    with st.expander("🎛️ Model Settings", expanded=False):
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.temperature,
            step=0.1,
            key="temp_slider"
        )
        st.session_state.temperature = temperature

        max_tokens = st.slider(
            "Max Tokens",
            min_value=100,
            max_value=8000,
            value=st.session_state.max_tokens,
            step=100,
            key="tokens_slider"
        )
        st.session_state.max_tokens = max_tokens

        st.session_state.config['settings']['temperature'] = temperature
        st.session_state.config['settings']['max_tokens'] = max_tokens
        st.session_state.config['settings']['provider'] = provider


    with st.expander("📁 Current Context Files", expanded=False):
        if st.session_state.uploaded_files:
            st.subheader("Files in Context:")
            for idx, file in enumerate(st.session_state.uploaded_files):
                col1, col2 = st.columns([4, 1])
                with col1:
                    if file.get('error'):
                        st.error(f"❌ {file['name']}: {file['error']}")
                    else:
                        st.success(f"✅ {file['name']} ({file['type']})")
                with col2:
                    if st.button("🗑️", key=f"remove_{idx}"):
                        st.session_state.uploaded_files.pop(idx)
                        st.rerun()
        else:
            st.caption("No files uploaded yet")

    with st.expander("📤 Export Conversation", expanded=False):
        if st.session_state.messages:
            stats = calculate_statistics(st.session_state.messages)

            st.markdown("**Conversation Statistics**")
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("Total Messages", stats['total_messages'])
                st.metric("User Messages", stats['user_messages'])
            with col_stat2:
                st.metric("AI Messages", stats['assistant_messages'])
                st.metric("Total Words", stats['total_words'])

            st.divider()
            st.markdown("**Export Formats**")

            txt_data = export_to_txt(
                st.session_state.messages,
                st.session_state.current_chat_title,
                st.session_state.personality_mode,
                st.session_state.translation_mode,
                st.session_state.target_language
            )
            st.download_button(
                label="📄 Download as TXT",
                data=txt_data,
                file_name=generate_filename(st.session_state.current_chat_title, "txt"),
                mime="text/plain",
                use_container_width=True,
                key="export_txt"
            )

            json_data = export_to_json(
                st.session_state.messages,
                st.session_state.current_chat_title,
                st.session_state.personality_mode,
                st.session_state.translation_mode,
                st.session_state.target_language
            )
            st.download_button(
                label="📋 Download as JSON",
                data=json_data,
                file_name=generate_filename(st.session_state.current_chat_title, "json"),
                mime="application/json",
                use_container_width=True,
                key="export_json"
            )

            csv_data = export_to_csv(
                st.session_state.messages,
                st.session_state.current_chat_title
            )
            st.download_button(
                label="📊 Download as CSV",
                data=csv_data,
                file_name=generate_filename(st.session_state.current_chat_title, "csv"),
                mime="text/csv",
                use_container_width=True,
                key="export_csv"
            )

            st.caption("💡 TXT for reading, JSON for data, CSV for analysis")
        else:
            st.info("Start a conversation to enable export")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Config", use_container_width=True):
            if save_config(st.session_state.config):
                st.success("Saved!")
            else:
                st.error("Save failed")

    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.config = load_config()
            st.rerun()

    st.divider()
    st.subheader("💬 Chat History")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.uploaded_files = []
            st.session_state.current_chat_id = None
            st.session_state.current_chat_title = "New Chat"
            st.rerun()

    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.uploaded_files = []
            st.session_state.current_chat_id = None
            st.session_state.current_chat_title = "New Chat"
            st.rerun()

    chats = list_chats()
    if chats:
        st.caption(f"Found {len(chats)} saved chat(s)")
        for chat in chats[:10]:
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(
                    f"📄 {chat['title'][:30]}",
                    key=f"load_{chat['id']}",
                    use_container_width=True
                ):
                    chat_data = load_chat(chat['id'])
                    if chat_data:
                        st.session_state.messages = chat_data['messages']
                        st.session_state.current_chat_id = chat['id']
                        st.session_state.current_chat_title = chat['title']
                        st.session_state.uploaded_files = []
                        st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{chat['id']}"):
                    if delete_chat(chat['id']):
                        st.rerun()
    else:
        st.caption("No saved chats")

st.title("💬 ChatGPT-like App")

col_title1, col_title2, col_title3 = st.columns([2, 1, 1])
with col_title1:
    st.caption(f"**Chat:** {st.session_state.current_chat_title}")
with col_title2:
    if not st.session_state.translation_mode:
        personality_emoji = {
            "Professional": "💼",
            "Creative": "🎨",
            "Technical": "⚙️",
            "Friendly": "😊",
            "Custom": "✨"
        }
        emoji = personality_emoji.get(st.session_state.personality_mode, "🤖")
        st.caption(f"{emoji} {st.session_state.personality_mode}")
with col_title3:
    if st.session_state.translation_mode:
        st.caption(f"🌍 {st.session_state.target_language}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

col1, col2, col3 = st.columns([1, 6, 1])

with col1:
    mode = st.selectbox(
        "Mode",
        ["mini", "thinking"],
        index=0 if not hasattr(st.session_state, 'mode') or st.session_state.mode == "mini" else 1,
        key="mode_selector",
        label_visibility="collapsed"
    )
    st.session_state.mode = mode

with col2:
    prompt = st.chat_input("Type your message...")

with col3:
    uploaded_file_input = st.file_uploader(
        "📎",
        accept_multiple_files=True,
        type=['txt', 'pdf', 'docx', 'png', 'jpg', 'jpeg', 'csv', 'md', 'py', 'js', 'html', 'css', 'json'],
        key="inline_file_uploader",
        label_visibility="collapsed"
    )

    if uploaded_file_input:
        for uploaded_file in uploaded_file_input:
            if not any(f['name'] == uploaded_file.name for f in st.session_state.uploaded_files):
                processed = process_uploaded_file(uploaded_file)
                st.session_state.uploaded_files.append(processed)

has_files = len(st.session_state.uploaded_files) > 0
active_model = get_active_model(st.session_state.config, has_files)

if prompt:
    if not st.session_state.current_chat_id and not st.session_state.messages:
        st.session_state.current_chat_title = generate_chat_title(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            provider_config = get_provider_config(st.session_state.config)
            settings = {
                'temperature': st.session_state.temperature,
                'max_tokens': st.session_state.max_tokens
            }

            llm = LLMProvider(st.session_state.provider, provider_config, settings)

            prepared_messages = prepare_messages_with_files(
                st.session_state.messages,
                st.session_state.uploaded_files,
                st.session_state.custom_instructions,
                st.session_state.provider,
                st.session_state.translation_mode,
                st.session_state.target_language,
                st.session_state.personality_mode,
                st.session_state.custom_personality
            )

            for chunk in llm.chat_completion(prepared_messages, active_model, stream=True):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"**Error:** {str(e)}"
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    chat_id = save_chat(
        st.session_state.messages,
        st.session_state.current_chat_id,
        st.session_state.current_chat_title
    )
    if chat_id:
        st.session_state.current_chat_id = chat_id

    st.rerun()
