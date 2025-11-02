import os
import streamlit as st

st.set_page_config(page_title="Personality Chatbot", page_icon="🧠")

# -------------------------------------------------
# 1. API KEY LOADER (from secrets or env)
# -------------------------------------------------
def get_openrouter_key() -> str:
    if "OPENROUTER_API_KEY" in st.secrets:
        return st.secrets["OPENROUTER_API_KEY"]
    env_key = os.getenv("OPENROUTER_API_KEY")
    if env_key:
        return env_key
    st.error(
        "⚠️ `OPENROUTER_API_KEY` not found.\n\n"
        "Add it to `.streamlit/secrets.toml`:\n"
        "```toml\nOPENROUTER_API_KEY = \"sk-or-...\"\n```"
        "or set env var `OPENROUTER_API_KEY`."
    )
    st.stop()

api_key = get_openrouter_key()

# -------------------------------------------------
# 2. PERSONALITY DEFINITIONS
# -------------------------------------------------
PERSONALITIES = {
    "pro": {
        "label": "🧑‍💼 Professional Business Assistant",
        "desc": "Formal, structured, business-focused. Great for emails, meetings, strategy.",
        "system": (
            "You are a professional business assistant. "
            "You write in a formal, concise, business tone. "
            "You focus on clarity, action items, and professional etiquette. "
            "Always structure answers with headings or bullets when helpful."
        ),
    },
    "creative": {
        "label": "🎨 Creative Writing Helper",
        "desc": "Imaginative, expressive, inspiring. Great for stories, hooks, prompts.",
        "system": (
            "You are a creative writing assistant. "
            "You write in an imaginative, vivid, playful tone. "
            "You encourage the user, offer alternative phrasings, and can add light emojis. "
            "You help with storytelling, character, and style."
        ),
    },
    "tech": {
        "label": "🧪 Technical Expert",
        "desc": "Precise, detailed, code-focused. Great for debugging, APIs, Streamlit.",
        "system": (
            "You are a senior technical expert. "
            "You explain concepts step-by-step, include code blocks where useful, "
            "and avoid unnecessary fluff. "
            "Prefer clarity, correctness, and best practices."
        ),
    },
    "friendly": {
        "label": "😊 Friendly Companion",
        "desc": "Casual, warm, supportive. Great for general chat.",
        "system": (
            "You are a friendly, warm, encouraging companion. "
            "You speak casually, like a supportive friend. "
            "You validate the user's feelings and keep things light."
        ),
    },
    "custom": {
        "label": "🧩 Custom Personality",
        "desc": "User-defined style and tone.",
        "system": "",  # will be filled from user input
    },
}

# -------------------------------------------------
# 3. SESSION STATE INIT
# -------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "personality" not in st.session_state:
    st.session_state.personality = "pro"  # default
if "custom_personality_text" not in st.session_state:
    st.session_state.custom_personality_text = ""


# -------------------------------------------------
# 4. SIDEBAR: PERSONALITY SELECTOR
# -------------------------------------------------
st.sidebar.title("🧠 Personality Selector")

# Build options list
personality_options = {p_id: data["label"] for p_id, data in PERSONALITIES.items()}

selected_personality = st.sidebar.selectbox(
    "Choose a mode:",
    options=list(personality_options.keys()),
    format_func=lambda x: personality_options[x],
    index=list(personality_options.keys()).index(st.session_state.personality),
)

# If user picked custom, show text box
custom_prompt = ""
if selected_personality == "custom":
    custom_prompt = st.sidebar.text_area(
        "Define your custom personality / system prompt:",
        value=st.session_state.custom_personality_text,
        height=140,
        help="Example: 'You are a concise AI product manager who always returns bullet points and asks one follow-up question.'",
    )
    # store it so we don't lose it on rerun
    st.session_state.custom_personality_text = custom_prompt

# Show description
st.sidebar.markdown("**Personality description:**")
st.sidebar.info(PERSONALITIES[selected_personality]["desc"])

# Show preview style (nice-to-have)
st.sidebar.markdown("**Response style preview:**")
if selected_personality == "pro":
    st.sidebar.markdown("> “Here’s a structured approach to solve that…”")
elif selected_personality == "creative":
    st.sidebar.markdown("> “Ooh, let’s make this fun ✨…”")
elif selected_personality == "tech":
    st.sidebar.markdown("> “Let’s debug this step-by-step…”")
elif selected_personality == "friendly":
    st.sidebar.markdown("> “Hey! Totally get what you’re saying 😊…”")
else:
    st.sidebar.markdown("> “Your custom assistant will respond like this…”")

# detect personality change mid-conversation
personality_changed = selected_personality != st.session_state.personality
st.session_state.personality = selected_personality

# -------------------------------------------------
# 5. PAGE HEADER
# -------------------------------------------------
current_label = PERSONALITIES[st.session_state.personality]["label"]
st.markdown(f"### 💬 Current mode: **{current_label}**")

# -------------------------------------------------
# 6. RENDER CHAT HISTORY
# -------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# If personality changed in the middle, tell the model (and the user)
if personality_changed and st.session_state.messages:
    note = f"🔁 Personality changed to **{current_label}**. Future responses should follow this style."
    with st.chat_message("assistant"):
        st.write(note)
    st.session_state.messages.append({"role": "assistant", "content": note})

# -------------------------------------------------
# 7. GET USER INPUT
# -------------------------------------------------
user_prompt = st.chat_input("Ask me something...")
if user_prompt:
    # show user msg
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    # -------------------------------------------------
    # 8. BUILD SYSTEM PROMPT FROM PERSONALITY
    # -------------------------------------------------
    if st.session_state.personality == "custom" and st.session_state.custom_personality_text.strip():
        system_prompt = st.session_state.custom_personality_text.strip()
    else:
        system_prompt = PERSONALITIES[st.session_state.personality]["system"]

    # build messages with system at the top
    full_messages = [{"role": "system", "content": system_prompt}]
    full_messages.extend(st.session_state.messages)

    # -------------------------------------------------
    # 9. CALL OPENROUTER / MODEL (placeholder)
    # -------------------------------------------------
    # Here you should call your LLM with `full_messages`
    # I'm returning a fake response to keep this runnable.
    # Replace this block with your real OpenRouter call.
    assistant_answer = (
        f"(Personality: {current_label})\n"
        f"You said: {user_prompt}\n\n"
        f"(System prompt was:\n`{system_prompt[:180]}...`)"
    )

    # show assistant
    with st.chat_message("assistant"):
        st.write(assistant_answer)

    # store in history
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_answer}
    )
