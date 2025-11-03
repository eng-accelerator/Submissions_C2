import streamlit as st
from openai import OpenAI
import json
import os
from datetime import datetime
from pathlib import Path

# ----------------------------
# 🔧 Setup
# ----------------------------
st.set_page_config(page_title="Translation Assistant", page_icon="🌐", layout="wide")
st.title("🌐 Translation Assistant")

# Directory for saving translation history
CHAT_STORAGE_DIR = Path(os.getcwd()) / "translation_history"
CHAT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = CHAT_STORAGE_DIR / "history.json"

# ----------------------------
# 🧠 Helper functions
# ----------------------------

def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Failed to save history: {e}")

# ----------------------------
# 🌍 Sidebar: Target Language Selection
# ----------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    api_key = st.text_input("🔑 Enter your OpenRouter API key:", type="password")

    target_language = st.selectbox(
        "🎯 Target Language:",
        ["English", "Spanish", "French", "German", "Italian", "Hindi", "Chinese (Simplified)"]
    )

    specify_source = st.checkbox("Manually specify source language")
    forced_source = None
    if specify_source:
        forced_source = st.text_input("Source Language (English name):")

    st.divider()

    # Show recent history in sidebar
    if "translation_history" in st.session_state and st.session_state["translation_history"]:
        st.subheader("🕒 Recent Translations")
        for item in reversed(st.session_state["translation_history"][-5:]):
            st.write(f"**{item['source_lang']} → {item['target_lang']}**: {item['translation'][:40]}...")

# ----------------------------
# 🚀 Initialize session + client
# ----------------------------
if "translation_history" not in st.session_state:
    st.session_state.translation_history = load_history()

if api_key:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Translation Assistant"
        }
    )
else:
    st.warning("Please enter your OpenRouter API key in the sidebar to start translating.")
    st.stop()


# ----------------------------
# 🔒 Safe API JSON Wrapper
# ----------------------------
def safe_model_json_call(system_prompt, user_prompt, model="openai/gpt-4o-mini"):
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=False
        )
        text = resp.choices[0].message.content.strip()
        idx = text.find("{")
        json_text = text[idx:] if idx != -1 else text
        data = json.loads(json_text)
        return data
    except json.JSONDecodeError:
        st.error("⚠️ Model returned malformed JSON. Try again or simplify your text.")
    except Exception as e:
        st.error(f"❌ API error: {e}")
    return None


# ----------------------------
# 💬 Translation Function
# ----------------------------
def translate_pipeline(text):
    system_prompt = (
        "You are a professional translator. Return JSON only with keys: "
        "detected_language, translation, alternatives, cultural_note, confidence"
    )

    user_prompt = f"""
    Text: \"\"\"{text}\"\"\"

    Tasks:
    1. Detect the source language.
    2. Translate it to {target_language}.
    3. Provide up to 3 alternative translations.
    4. Add a short cultural note for idiomatic expressions or context.
    5. Include a confidence score between 0 and 1.

    Respond ONLY in JSON format:
    {{
        "detected_language": "",
        "translation": "",
        "alternatives": [],
        "cultural_note": "",
        "confidence": 0.0
    }}
    """

    data = safe_model_json_call(system_prompt, user_prompt)
    if not data:
        return

    detected = data.get("detected_language", "Unknown")
    translation = data.get("translation", "")
    confidence = data.get("confidence", 0.0)
    alternatives = data.get("alternatives", [])
    note = data.get("cultural_note", "")

    # 🧩 UI Display
    st.markdown(f"### 🔍 Detected Language: `{detected}`")
    st.markdown(f"### 🎯 Translation ({target_language}):")
    st.success(translation)

    if confidence:
        st.progress(int(confidence * 100))

    if alternatives:
        st.markdown("**🌟 Alternative Translations:**")
        for alt in alternatives:
            st.write(f"- {alt}")

    if note:
        st.markdown("**💡 Cultural Note:**")
        st.info(note)

    # Save translation to session + file
    entry = {
        "original": text,
        "translation": translation,
        "source_lang": detected,
        "target_lang": target_language,
        "alternatives": alternatives,
        "cultural_note": note,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.translation_history.append(entry)
    save_history(st.session_state.translation_history)


# ----------------------------
# 🧾 Main Chat Input
# ----------------------------
user_input = st.chat_input("Enter text to translate...")
if user_input:
    if target_language:
        with st.spinner("Translating..."):
            translate_pipeline(user_input)
    else:
        st.warning("Please select a target language first.")

# ----------------------------
# 📥 Export History
# ----------------------------
st.divider()
st.subheader("📜 Translation History")
if st.session_state.translation_history:
    for item in reversed(st.session_state.translation_history[-10:]):
        st.markdown(f"**{item['source_lang']} → {item['target_lang']}** ({item['confidence']:.2f})")
        st.write(f"🗣️ Original: {item['original']}")
        st.write(f"✅ Translation: {item['translation']}")
        if item.get("cultural_note"):
            st.caption(f"💡 {item['cultural_note']}")
        st.write("---")

    st.download_button(
        "📥 Export All Translations",
        json.dumps(st.session_state.translation_history, ensure_ascii=False, indent=2),
        file_name="translations.json"
    )
else:
    st.info("No translations yet. Try entering text above!")

