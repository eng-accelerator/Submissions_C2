import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import os
import uuid

# Page config
st.set_page_config(
    page_title="Translation Assistant 🌍",
    page_icon="🌍",
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
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #45a049;
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
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE OPENROUTER CLIENT WITH PROPER ERROR HANDLING
# ============================================================================

@st.cache_resource
def get_openrouter_client():
    """Initialize OpenRouter client with proper configuration"""
    # Try to get API key from secrets first, then environment variable
    api_key = None
    
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]
    except:
        api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        st.error("⚠️ OpenRouter API key not found!")
        st.info("Please add OPENROUTER_API_KEY to .streamlit/secrets.toml")
        st.code("""
# .streamlit/secrets.toml
OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
        """)
        st.stop()
    
    # Verify API key format
    if not api_key.startswith("sk-or-v1-"):
        st.error("⚠️ Invalid API key format! OpenRouter keys should start with 'sk-or-v1-'")
        st.stop()
    
    # Create client with minimal configuration
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:8501",  # Changed to default Streamlit port
                "X-Title": "Translation Assistant"
            }
        )
        return client
    except Exception as e:
        st.error(f"Failed to initialize OpenRouter client: {e}")
        st.stop()

client = get_openrouter_client()

# ============================================================================
# TRANSLATION CONFIGURATION
# ============================================================================

SUPPORTED_LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese (Simplified)": "zh",
    "Arabic": "ar",
    "Hindi": "hi",
    "Turkish": "tr",
    "Dutch": "nl",
    "Polish": "pl",
    "Swedish": "sv",
    "Greek": "el",
    "Hebrew": "he",
    "Thai": "th",
    "Vietnamese": "vi"
}

TRANSLATION_SYSTEM_PROMPT = """You are an expert translation assistant with deep knowledge of languages and cultures.

Your tasks:
1. DETECT the input language
2. TRANSLATE to the target language accurately
3. PROVIDE cultural context for idioms or culturally-specific expressions
4. OFFER alternative translations when they add value
5. SCORE your confidence (High/Medium/Low)

Format your response as JSON:
{
    "detected_language": "language name",
    "confidence": "High/Medium/Low",
    "translation": "translated text",
    "alternatives": ["alternative 1", "alternative 2"],
    "cultural_notes": "relevant cultural context",
    "formality": "formal/informal/neutral"
}

Guidelines:
- Be accurate and culturally sensitive
- Preserve tone and intent
- Note regional variations when important
- Explain idioms that don't translate literally
- Only include alternatives if they genuinely add value
- Only include cultural_notes if there's something culturally significant to mention
"""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_new_chat():
    """Create a new chat conversation"""
    chat_id = f"chat_{uuid.uuid4().hex[:8]}"
    
    if (st.session_state.get('current_chat_id') and 
        st.session_state.current_chat_id in st.session_state.get('conversations', {})):
        save_current_chat()
    
    st.session_state.conversations[chat_id] = {
        'chat_id': chat_id,
        'title': 'New Translation',
        'messages': [],
        'created_at': datetime.now().isoformat()
    }
    
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []
    st.session_state.chat_title = 'New Translation'
    
    return chat_id

def load_chat(chat_id):
    """Load a chat conversation"""
    if chat_id in st.session_state.conversations:
        chat_data = st.session_state.conversations[chat_id]
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = chat_data.get('messages', [])
        st.session_state.chat_title = chat_data.get('title', 'New Translation')
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
    if len(st.session_state.messages) <= 2 and st.session_state.chat_title == "New Translation":
        st.session_state.chat_title = content[:50] + ('...' if len(content) > 50 else '')
        save_current_chat()

def get_all_chats():
    """Get all chats sorted by creation time (newest first)"""
    return sorted(
        st.session_state.conversations.items(),
        key=lambda x: x[1].get('created_at', ''),
        reverse=True
    )

# ============================================================================
# TRANSLATION FUNCTIONS WITH BETTER ERROR HANDLING
# ============================================================================

def detect_and_translate(text, target_language, model):
    """Detect language and translate text"""
    try:
        # Check if user wants to translate back to source language
        # Look for phrases like "translate back", "translate to source", "reverse translation"
        reverse_keywords = ["translate back", "translate it back", "reverse", "to the source", "to original", "back to"]
        text_lower = text.lower()
        
        is_reverse_request = any(keyword in text_lower for keyword in reverse_keywords)
        
        # If it's a reverse request and we have a last detected language
        if is_reverse_request and st.session_state.last_detected_language:
            # Extract the text to translate (remove the command part)
            actual_text = st.session_state.last_translated_text
            target_language = st.session_state.last_detected_language
            
            # Show info about reverse translation
            st.info(f"🔄 Reverse translating back to **{target_language}**")
        
        messages = [
            {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
            {"role": "user", "content": f"Translate this text to {target_language}: {text if not is_reverse_request else actual_text}"}
        ]
        
        # Make API call with explicit parameters
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
            stream=False
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            # Store the detected language and translated text for potential reverse translation
            st.session_state.last_detected_language = result.get('detected_language', 'Unknown')
            st.session_state.last_translated_text = result.get('translation', '')
            
            return result
        except json.JSONDecodeError as je:
            st.warning(f"JSON parsing failed, using fallback format")
            # Fallback: return the text as-is
            return {
                "detected_language": "Unknown",
                "confidence": "Medium",
                "translation": result_text,
                "alternatives": [],
                "cultural_notes": "",
                "formality": "neutral"
            }
            
    except Exception as e:
        error_msg = str(e)
        st.error(f"Translation API error: {error_msg}")
        
        # Provide helpful error messages
        if "401" in error_msg:
            st.error("🔑 Authentication failed. Please check your OpenRouter API key.")
            st.info("Make sure your API key is valid and has credits available.")
        elif "429" in error_msg:
            st.error("⏱️ Rate limit exceeded. Please wait a moment and try again.")
        elif "500" in error_msg or "502" in error_msg or "503" in error_msg:
            st.error("🔧 OpenRouter service issue. Please try again in a moment.")
        
        return None

def format_translation_response(result, target_language, original_text):
    """Format the translation result into a nice display"""
    response_text = f"""
🔍 **Detected Language**: {result.get('detected_language', 'Unknown')}  
✨ **Confidence**: {result.get('confidence', 'Unknown')}  

---

### 🎯 Translation ({target_language})
> {result.get('translation', '')}

"""
    
    # Add alternatives if available
    alternatives = result.get('alternatives', [])
    if alternatives and len(alternatives) > 0:
        valid_alts = [alt for alt in alternatives if alt and alt.strip()]
        if valid_alts:
            response_text += "\n### 🌟 Alternative Translations\n"
            for i, alt in enumerate(valid_alts, 1):
                response_text += f"{i}. {alt}\n"
            response_text += "\n"
    
    # Add cultural notes if available
    cultural_notes = result.get('cultural_notes', '')
    if cultural_notes and cultural_notes.strip():
        response_text += f"### 💡 Cultural Notes\n{cultural_notes}\n\n"
    
    # Add formality level
    formality = result.get('formality', 'neutral')
    if formality and formality != 'neutral':
        response_text += f"📋 **Formality Level**: {formality.capitalize()}\n"
    
    # Save translation pair to history
    translation_pair = {
        'timestamp': datetime.now().isoformat(),
        'original_text': original_text,
        'original_language': result.get('detected_language', 'Unknown'),
        'translated_text': result.get('translation', ''),
        'target_language': target_language,
        'confidence': result.get('confidence', 'Unknown'),
        'alternatives': valid_alts if 'valid_alts' in locals() else [],
        'cultural_notes': cultural_notes if cultural_notes else None,
        'formality': formality
    }
    
    # Add to translation pairs history (keep last 50)
    st.session_state.translation_pairs.insert(0, translation_pair)
    if len(st.session_state.translation_pairs) > 50:
        st.session_state.translation_pairs = st.session_state.translation_pairs[:50]
    
    return response_text

def chat_with_openrouter(messages, model):
    """Send messages to OpenRouter and get streaming response"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
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
        st.session_state.chat_title = "New Translation"
    
    if 'model_choice' not in st.session_state:
        st.session_state.model_choice = "openai/gpt-3.5-turbo"  # Changed to more reliable free model
    
    if 'target_language' not in st.session_state:
        st.session_state.target_language = "Spanish"
    
    if 'translation_mode' not in st.session_state:
        st.session_state.translation_mode = "Translation Mode"
    
    if 'translation_pairs' not in st.session_state:
        st.session_state.translation_pairs = []
    
    if 'last_detected_language' not in st.session_state:
        st.session_state.last_detected_language = None
    
    if 'last_translated_text' not in st.session_state:
        st.session_state.last_translated_text = None
    
    # Create initial chat if none exists
    if not st.session_state.conversations:
        create_new_chat()

init_session_state()

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("🌍 Translation Assistant")
    
    # Translation Settings
    st.subheader("Translation Settings")
    
    # Show last detected language if available
    if st.session_state.last_detected_language:
        st.success(f"💡 Last detected: **{st.session_state.last_detected_language}**")
        st.caption("💬 You can say 'translate back' to reverse translate!")
    
    # Target language selection
    target_lang = st.selectbox(
        "Target Language",
        options=list(SUPPORTED_LANGUAGES.keys()),
        index=list(SUPPORTED_LANGUAGES.keys()).index(st.session_state.target_language),
        key="target_lang_selector"
    )
    st.session_state.target_language = target_lang
    
    # Mode selection
    mode = st.radio(
        "Mode",
        ["Translation Mode", "Conversation Mode"],
        index=0 if st.session_state.translation_mode == "Translation Mode" else 1,
        key="mode_selector"
    )
    st.session_state.translation_mode = mode
    
    st.divider()
    
    # New Chat button
    st.subheader("💬 Conversations")
    if st.button("➕ New Translation", use_container_width=True):
        save_current_chat()
        create_new_chat()
        st.rerun()
    
    st.divider()
    
    # Chat History
    st.subheader("Translation History")
    
    all_chats = get_all_chats()
    
    if all_chats:
        for chat_id, chat_data in all_chats[:10]:
            col1, col2 = st.columns([4, 1])
            
            with col1:
                is_current = chat_id == st.session_state.current_chat_id
                button_label = f"{'🟢' if is_current else '⚪'} {chat_data.get('title', 'New Translation')}"
                
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
                    if st.button("🗑️", key=f"delete_{chat_id}", help="Delete"):
                        delete_chat(chat_id)
                        st.rerun()
    else:
        st.info("No translation history yet!")
    
    st.divider()
    
    # Settings
    st.subheader("⚙️ Settings")
    
    # Model selection - Using more reliable models
    model_option = st.selectbox(
        "Select Model",
        [
            "openai/gpt-3.5-turbo",  # Free, reliable
            "openai/gpt-4o-mini",
            "openai/gpt-4o",
            "anthropic/claude-3-haiku",
            "meta-llama/llama-3.1-8b-instruct:free",  # Free tier
            "google/gemini-flash-1.5"
        ],
        index=0,
        key="model_selector",
        help="Free models: gpt-3.5-turbo, llama-3.1-8b-instruct:free"
    )
    st.session_state.model_choice = model_option
    
    # Clear current chat
    if st.button("🗑️ Clear Current Chat", use_container_width=True):
        if st.session_state.current_chat_id:
            st.session_state.messages = []
            st.session_state.chat_title = "New Translation"
            save_current_chat()
            st.rerun()
    
    st.divider()
    
    # Translation Pairs History
    st.subheader("📊 Translation History")
    
    if st.session_state.translation_pairs:
        # Show count
        st.caption(f"Total translations: {len(st.session_state.translation_pairs)}")
        
        # Export button
        if st.button("📥 Export History", use_container_width=True):
            # Convert to JSON for download
            history_json = json.dumps(st.session_state.translation_pairs, indent=2, ensure_ascii=False)
            st.download_button(
                label="Download as JSON",
                data=history_json,
                file_name=f"translation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Clear history button
        if st.button("🗑️ Clear Translation History", use_container_width=True):
            st.session_state.translation_pairs = []
            st.rerun()
        
        # Show recent translations in expander
        with st.expander("📜 View Recent Translations", expanded=False):
            for i, pair in enumerate(st.session_state.translation_pairs[:10]):
                st.markdown(f"""
**{i+1}. {pair['original_language']} → {pair['target_language']}** ({pair['confidence']})
- **Original**: {pair['original_text'][:100]}{'...' if len(pair['original_text']) > 100 else ''}
- **Translation**: {pair['translated_text'][:100]}{'...' if len(pair['translated_text']) > 100 else ''}
- **Time**: {datetime.fromisoformat(pair['timestamp']).strftime('%Y-%m-%d %H:%M')}
---
""")
    else:
        st.info("No translation history yet. Start translating!")

# ============================================================================
# MAIN INTERFACE
# ============================================================================

st.title("🌍 Translation Assistant")
st.caption(f"Mode: **{st.session_state.translation_mode}** | Target: **{st.session_state.target_language}** | Model: **{st.session_state.model_choice}**")

# Translation Statistics Dashboard
if st.session_state.translation_pairs:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Translations", len(st.session_state.translation_pairs))
    
    with col2:
        high_confidence = sum(1 for p in st.session_state.translation_pairs if p['confidence'] == 'High')
        st.metric("High Confidence", high_confidence)
    
    with col3:
        unique_languages = len(set(p['original_language'] for p in st.session_state.translation_pairs))
        st.metric("Languages Used", unique_languages)
    
    with col4:
        with_cultural_notes = sum(1 for p in st.session_state.translation_pairs if p.get('cultural_notes'))
        st.metric("Cultural Notes", with_cultural_notes)
    
    st.divider()

# Info expander
with st.expander("ℹ️ How to use", expanded=False):
    st.markdown("""
    ### Translation Mode
    - Type any text in any language
    - The bot will automatically detect the language
    - Get translations with cultural context and alternatives
    - See confidence scores for translations
    
    ### Conversation Mode
    - Chat normally with the assistant
    - Ask questions about languages, grammar, and culture
    - Get explanations and learning tips
    
    ### Features
    - ✅ Automatic language detection
    - ✅ 20+ supported languages
    - ✅ Cultural context and notes
    - ✅ Alternative translations
    - ✅ Confidence scoring
    - ✅ Persistent translation history
    - ✅ **Reverse translation** - Just say "translate back" or "translate it back"!
    
    ### Bidirectional Translation
    After translating text, you can:
    - Type: **"translate back"** or **"translate it back"**
    - The system will automatically translate to the original source language
    - Example: Translate French→English, then say "translate back" for English→French
    
    ### Troubleshooting
    If you get errors:
    1. Check your OpenRouter API key in secrets.toml
    2. Verify you have credits in your OpenRouter account
    3. Try a free model like gpt-3.5-turbo or llama-3.1-8b-instruct:free
    """)

st.divider()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type text to translate or ask a question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    update_chat_title(prompt)
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response based on mode
    with st.chat_message("assistant"):
        if st.session_state.translation_mode == "Translation Mode":
            # Translation mode
            with st.spinner("🔍 Detecting language and translating..."):
                result = detect_and_translate(
                    prompt, 
                    st.session_state.target_language,
                    st.session_state.model_choice
                )
                
                if result:
                    response_text = format_translation_response(result, st.session_state.target_language, prompt)
                    st.markdown(response_text)
                    
                    # Save to session state
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response_text}
                    )
                    save_current_chat()
                else:
                    error_msg = "❌ Translation failed. Please check your API key and try again."
                    st.error(error_msg)
                    # Remove user message since we failed
                    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                        st.session_state.messages.pop()
        
        else:
            # Conversation mode
            message_placeholder = st.empty()
            full_response = ""
            
            # Prepare messages for API
            messages_for_api = [
                {"role": "system", "content": "You are a helpful language learning assistant. Help users understand languages, grammar, and cultural contexts. Provide clear explanations and examples."},
                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            ]
            
            try:
                # Stream response
                for chunk in chat_with_openrouter(messages_for_api, st.session_state.model_choice):
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