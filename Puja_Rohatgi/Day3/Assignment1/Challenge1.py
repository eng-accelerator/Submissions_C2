import streamlit as st
from openai import OpenAI
import json

# Page config
st.set_page_config(page_title="Smart Translator", page_icon="🌐", layout="wide")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'cache' not in st.session_state:
    st.session_state.cache = {}
if 'token_count' not in st.session_state:
    st.session_state.token_count = 0
if 'api_calls' not in st.session_state:
    st.session_state.api_calls = 0

# Sidebar
with st.sidebar:
    st.title("🌐 Translator")
    
    api_key = st.text_input("OpenRouter API Key", type="password", key="api_key", 
                            help="Get free credits at openrouter.ai")
    
    st.divider()
    
    # Model selection
    model = st.selectbox(
        "Model (by cost)",
        [
            "google/gemini-flash-1.5",  # $0.075/M - Cheapest & reliable
            "google/gemini-pro-1.5",    # $1.25/M - Better quality
            "anthropic/claude-3-haiku", # $0.25/M - High quality
            "openai/gpt-3.5-turbo",     # $0.50/M - Standard
            "meta-llama/llama-3.1-8b-instruct"  # $0.06/M - Very cheap
        ]
    )
    
    target_lang = st.selectbox(
        "Target Language",
        ["English", "Spanish", "French", "German", "Italian", 
         "Portuguese", "Russian", "Japanese", "Korean", "Chinese", "Arabic", "Hindi"]
    )
    
    st.divider()
    
    # Token usage display
    st.metric("Token Usage", f"{st.session_state.token_count:,}")
    st.metric("API Calls", st.session_state.api_calls)
    st.metric("Cache Hits", len(st.session_state.cache))
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.cache = {}
        st.rerun()
    
    st.divider()
    st.caption("💡 Using OpenRouter API")
    st.caption("Get free API key: [openrouter.ai](https://openrouter.ai)")

# Main content
st.title("Translation Assistant")

if not api_key:
    st.info("👈 Enter your OpenRouter API key in the sidebar to start")
    st.markdown("""
    ### Getting Started:
    1. Visit [openrouter.ai](https://openrouter.ai)
    2. Sign up (free credits included!)
    3. Get your API key
    4. Paste it in the sidebar
    
    **Free models available!** 🎉
    """)
    st.stop()

# Initialize OpenAI client with OpenRouter base URL
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

def get_cache_key(text, target, model_name):
    """Create cache key"""
    return f"{text.lower().strip()}_{target.lower()}_{model_name}"

def translate_text(text, target_language, model_name):
    """Translate with caching and minimal tokens"""
    cache_key = get_cache_key(text, target_language, model_name)
    
    # Check cache
    if cache_key in st.session_state.cache:
        return st.session_state.cache[cache_key], True
    
    # Single optimized API call
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{
                "role": "system",
                "content": "You are a translator. Return ONLY valid JSON, no other text."
            }, {
                "role": "user",
                "content": f"""Detect language and translate to {target_language}. Return JSON:
{{"detected": "lang_name", "translation": "text", "cultural_note": "note or null", "alternative": "alt or null"}}

Text: {text}"""
            }],
            temperature=0.3,
            max_tokens=300  # Limited for cost savings
        )
        
        # Update token count
        if hasattr(response, 'usage') and response.usage:
            st.session_state.token_count += response.usage.total_tokens
        st.session_state.api_calls += 1
        
        # Parse response
        content = response.choices[0].message.content.strip()
        
        # Extract JSON if wrapped in markdown
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        result = json.loads(content)
        
        # Cache result
        st.session_state.cache[cache_key] = result
        
        return result, False
        
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON response: {str(e)}", "raw": content}, False
    except Exception as e:
        return {"error": str(e)}, False

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            data = msg["content"]
            
            if "error" in data:
                st.error(f"Error: {data['error']}")
                if "raw" in data:
                    with st.expander("See raw response"):
                        st.code(data["raw"])
            else:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**🔍 Detected:** {data['detected']}")
                with col2:
                    if msg.get("cached"):
                        st.success("⚡ Cached")
                
                st.markdown(f"**🎯 Translation ({target_lang}):**")
                st.info(f'"{data["translation"]}"')
                
                if data.get("alternative") and data["alternative"] != "null":
                    st.markdown(f"**🌟 Alternative:** {data['alternative']}")
                
                if data.get("cultural_note") and data["cultural_note"] != "null":
                    st.warning(f"💡 **Cultural Note:** {data['cultural_note']}")

# Chat input
if prompt := st.chat_input("Type text in any language..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get translation
    with st.chat_message("assistant"):
        with st.spinner("Translating..."):
            result, from_cache = translate_text(prompt, target_lang, model)
            
            # Display result
            if "error" in result:
                st.error(f"Error: {result['error']}")
                if "raw" in result:
                    with st.expander("See raw response"):
                        st.code(result["raw"])
            else:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**🔍 Detected:** {result['detected']}")
                with col2:
                    if from_cache:
                        st.success("⚡ Cached")
                
                st.markdown(f"**🎯 Translation ({target_lang}):**")
                st.info(f'"{result["translation"]}"')
                
                if result.get("alternative") and result["alternative"] != "null":
                    st.markdown(f"**🌟 Alternative:** {result['alternative']}")
                
                if result.get("cultural_note") and result["cultural_note"] != "null":
                    st.warning(f"💡 **Cultural Note:** {result['cultural_note']}")
    
    # Add assistant message
    st.session_state.messages.append({
        "role": "assistant", 
        "content": result,
        "cached": from_cache
    })
    
    st.rerun()

# Footer
st.divider()
st.caption("💡 **Token Saving:** Smart caching • Minimal prompts • Limited tokens • FREE models available!")