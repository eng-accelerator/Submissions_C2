import streamlit as st
import json
import csv
import io
from datetime import datetime
from openai import OpenAI

# ======================================================================
# APP CONFIGURATION
# ======================================================================
st.set_page_config(page_title="Multi-Chat AI Assistant", layout="wide")

# ======================================================================
# PERSONALITY DEFINITIONS
# ======================================================================
PERSONALITIES = {
    "Professional Business Assistant": {
        "prompt": (
            "You are a Professional Business Assistant. "
            "Respond formally, clearly, and efficiently. "
            "Focus on strategy, communication, and professional problem-solving."
        ),
        "description": "Formal and efficient — great for business strategy, emails, and meetings.",
        "emoji": "💼"
    },
    "Creative Writing Helper": {
        "prompt": (
            "You are a Creative Writing Assistant. "
            "Respond with imagination and flair. "
            "Use metaphors, emotions, and artistic expression to help writers."
        ),
        "description": "Expressive and inspiring — perfect for stories, poems, and ideas.",
        "emoji": "🎨"
    },
    "Technical Expert": {
        "prompt": (
            "You are a Technical Expert. "
            "Be precise, methodical, and detail-oriented. "
            "Focus on technology, programming, and step-by-step reasoning."
        ),
        "description": "Analytical and detail-focused — ideal for code help or explanations.",
        "emoji": "🧠"
    },
    "Friendly Companion": {
        "prompt": (
            "You are a Friendly Companion. "
            "Speak warmly and empathetically. "
            "Offer casual conversation and emotional support."
        ),
        "description": "Casual and supportive — great for general chat or friendly talk.",
        "emoji": "😊"
    },
    "Custom Personality": {
        "prompt": "",
        "description": "Define your own style and expertise!",
        "emoji": "✨"
    }
}

# ======================================================================
# INITIALIZE SESSION STATE
# ======================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"
if "personality" not in st.session_state:
    st.session_state.personality = "Professional Business Assistant"
if "custom_personality_prompt" not in st.session_state:
    st.session_state.custom_personality_prompt = ""

# ======================================================================
# OPENROUTER CLIENT SETUP
# ======================================================================
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    st.error("OPENROUTER_API_KEY not found in .streamlit/secrets.toml")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    default_headers={
        "HTTP-Referer": "http://localhost:8504",
        "X-Title": "My ChatBot",
    }
)
# ======================================================================
# HELPER FUNCTIONS FOR EXPORT
# ======================================================================
def calculate_metadata(messages):
    """Compute basic chat metadata."""
    user_msgs = sum(1 for m in messages if m["role"] == "user")
    ai_msgs = sum(1 for m in messages if m["role"] == "assistant")
    total_chars = sum(len(m["content"]) for m in messages)
    avg_len = total_chars / len(messages) if messages else 0
    return {
        "export_timestamp": datetime.utcnow().isoformat() + "Z",
        "format_version": "1.0",
        "session_id": st.session_state.chat_title.replace(" ", "_"),
        "total_messages": len(messages),
        "user_messages": user_msgs,
        "assistant_messages": ai_msgs,
        "total_characters": total_chars,
        "average_message_length": round(avg_len, 2)
    }

def export_as_txt(messages, metadata):
    """Convert chat to human-readable TXT format."""
    buffer = io.StringIO()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    buffer.write(f"Chat Export - {now}\n{'='*40}\n\n")
    buffer.write("Session Information:\n")
    buffer.write(f"- Total Messages: {metadata['total_messages']}\n")
    buffer.write(f"- Export Date: {metadata['export_timestamp']}\n\n")
    buffer.write("Conversation:\n" + "-"*40 + "\n\n")

    for i, msg in enumerate(messages, start=1):
        ts = msg.get("timestamp", datetime.now().strftime("%H:%M:%S"))
        role = "You" if msg["role"] == "user" else "Assistant"
        buffer.write(f"[{ts}] {role}: {msg['content']}\n\n")
    return buffer.getvalue()

def export_as_json(messages, metadata):
    """Convert chat to structured JSON."""
    conversation = []
    for i, msg in enumerate(messages, start=1):
        conversation.append({
            "timestamp": msg.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "role": msg["role"],
            "content": msg["content"],
            "message_id": i,
            "character_count": len(msg["content"])
        })
    data = {"export_metadata": metadata, "conversation": conversation}
    return json.dumps(data, indent=2, ensure_ascii=False)

def export_as_csv(messages, metadata):
    """Convert chat to CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Message_ID", "Timestamp", "Role", "Content", "Character_Count", "Word_Count"])
    for i, msg in enumerate(messages, start=1):
        writer.writerow([
            i,
            msg.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            msg["role"],
            msg["content"].replace("\n", " "),
            len(msg["content"]),
            len(msg["content"].split())
        ])
    return output.getvalue()

# ======================================================================
# SIDEBAR CONTROLS
# ======================================================================
with st.sidebar:
    st.title("⚙️ Settings")

    # Personality Selector
    st.subheader("🎭 Personality")
    selected_personality = st.selectbox(
        "Choose Personality",
        options=list(PERSONALITIES.keys()),
        index=list(PERSONALITIES.keys()).index(st.session_state.personality),
    )
    if selected_personality != st.session_state.personality:
        st.session_state.personality = selected_personality
        st.rerun()

    st.markdown(f"**{PERSONALITIES[selected_personality]['emoji']} {selected_personality}**")
    st.caption(PERSONALITIES[selected_personality]["description"])

    if selected_personality == "Custom Personality":
        st.text_area(
            "Define custom personality:",
            value=st.session_state.custom_personality_prompt,
            key="custom_personality_prompt",
            placeholder="Describe tone, expertise, and style..."
        )

    st.divider()

    # Export Functionality
    st.subheader("📤 Export Conversation")
    export_format = st.radio("Select format", ["TXT", "JSON", "CSV"], horizontal=True)

    if st.button("💾 Generate Export"):
        metadata = calculate_metadata(st.session_state.messages)

        if export_format == "TXT":
            export_data = export_as_txt(st.session_state.messages, metadata)
            mime = "text/plain"
            file_name = "chat_export.txt"
        elif export_format == "JSON":
            export_data = export_as_json(st.session_state.messages, metadata)
            mime = "application/json"
            file_name = "chat_export.json"
        else:
            export_data = export_as_csv(st.session_state.messages, metadata)
            mime = "text/csv"
            file_name = "chat_export.csv"

        st.download_button(
            label=f"⬇️ Download {export_format}",
            data=export_data,
            file_name=file_name,
            mime=mime,
            use_container_width=True
        )

# ======================================================================
# MAIN CHAT AREA
# ======================================================================
st.title(f"🤖 {st.session_state.chat_title} — {PERSONALITIES[st.session_state.personality]['emoji']} {st.session_state.personality}")

# Display existing messages
for msg in st.session_state.messages:
    role_label = "🧑‍💼 You" if msg["role"] == "user" else "🤖 Assistant"
    st.chat_message(msg["role"]).markdown(f"**{role_label}:**\n\n{msg['content']}")

# Chat input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": datetime.now().strftime("%H:%M:%S")})
    st.chat_message("user").markdown(f"**You:** {prompt}")

    # Build personality system prompt
    if st.session_state.personality == "Custom Personality" and st.session_state.custom_personality_prompt.strip():
        system_prompt = st.session_state.custom_personality_prompt.strip()
    else:
        system_prompt = PERSONALITIES[st.session_state.personality]["prompt"]
    system_message = {"role": "system", "content": system_prompt}

    # Send request
    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_message, *st.session_state.messages]
        )
    reply = response.choices[0].message.content.strip()
    st.session_state.messages.append({"role": "assistant", "content": reply, "timestamp": datetime.now().strftime("%H:%M:%S")})
    st.chat_message("assistant").markdown(f"**Assistant:** {reply}")
