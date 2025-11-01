# Open router API key for using a free model , paid models
# Challenge 1: Translation Mode
# Features added:
# - Sidebar target language selection
# - Two-stage flow: detect language -> translate
# - Cultural notes and alternative translations
# - Translation history in session_state
# - Still keeps original chat history & OpenRouter streaming style (for final display)

import streamlit as st
from openai import OpenAI
import json

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="My Translation ChatBot", page_icon="🤖")

# ------------------------------------------------------------
# OPENROUTER CLIENT SETUP
# ------------------------------------------------------------
if "OPENROUTER_API_KEY" in st.secrets:
    api_key = st.secrets["OPENROUTER_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter OpenRouter API Key", type="password")

if not api_key:
    st.warning("Please enter your OpenRouter API key to continue.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    default_headers={
        "HTTP-Referer": "http://localhost:8501",  # Optional: shows on OpenRouter rankings
        "X-Title": "My ChatBot",                  # Optional: shows on OpenRouter rankings
    }
)

# ------------------------------------------------------------
# MODELS (adjust to what you have on OpenRouter)
# ------------------------------------------------------------
# detection / translation model (must support following instructions well)
DETECTION_MODEL = "openai/gpt-4o-mini"  # change if not enabled
TRANSLATION_MODEL = "openai/gpt-4o-mini"  # can be same as detection
# if those don't work for your key, try the free one you used:
# DETECTION_MODEL = "mistralai/mistral-7b-instruct:free"
# TRANSLATION_MODEL = "mistralai/mistral-7b-instruct:free"

# ------------------------------------------------------------
# SESSION STATE INIT
# ------------------------------------------------------------
# chat history (original)
if "messages" not in st.session_state:
    st.session_state.messages = []

# target language for translation (new)
if "target_language" not in st.session_state:
    st.session_state.target_language = "English"

# translation history (new)
if "translation_history" not in st.session_state:
    # each item: {
    #   "source_text": ...,
    #   "detected_language": ...,
    #   "target_language": ...,
    #   "translation": ...,
    #   "alternatives": [...],
    #   "cultural_note": ...,
    #   "confidence": ...
    # }
    st.session_state.translation_history = []

# ------------------------------------------------------------
# SIDEBAR (new UI for challenge)
# ------------------------------------------------------------
with st.sidebar:
    st.header("🌏 Translation Settings")

    target = st.selectbox(
        "Translate INTO:",
        [
            "English",
            "Spanish",
            "French",
            "German",
            "Portuguese",
            "Italian",
            "Hindi",
            "Japanese",
            "Korean",
            "Chinese (Simplified)",
        ],
        index=0,
    )
    st.session_state.target_language = target

    st.divider()
    st.subheader("📝 Translation History")
    if st.session_state.translation_history:
        for item in reversed(st.session_state.translation_history[-10:]):
            st.write(f"**Source ({item['detected_language']}):** {item['source_text']}")
            st.write(f"**→ {item['target_language']}:** {item['translation']}")
            if item.get("confidence") is not None:
                st.caption(f"Confidence: {item['confidence']:.2f}")
            if item.get("cultural_note"):
                st.caption("💡 " + item["cultural_note"])
            st.markdown("---")
    else:
        st.caption("No translations yet.")

    # Clear history
    if st.button("Clear translation history"):
        st.session_state.translation_history = []

# ------------------------------------------------------------
# APP TITLE
# ------------------------------------------------------------
st.title("🤖 My Translation ChatBot")

st.caption(
    "Type in **any language** → I will detect it → translate to "
    f"**{st.session_state.target_language}** and add cultural notes."
)

# ------------------------------------------------------------
# HELPER: detect language (first call)
# ------------------------------------------------------------
def detect_language(text: str) -> dict:
    """
    Ask the model to detect language and return a structured dict.
    We tell it to return ONLY JSON so it's easy to parse.
    """
    try:
        resp = client.chat.completions.create(
            model=DETECTION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a language detector. "
                        "Detect the language of the user's text. "
                        "Return ONLY valid JSON with fields: "
                        "language_name (string), iso_code (string), confidence (0-1), is_mixed (bool)."
                    ),
                },
                {"role": "user", "content": text},
            ],
            temperature=0,
        )
        raw = resp.choices[0].message.content.strip()
        # try to parse JSON
        data = json.loads(raw)
        return data
    except Exception as e:
        # fallback if model returns non-JSON or error
        return {
            "language_name": "Unknown",
            "iso_code": "",
            "confidence": 0.0,
            "is_mixed": False,
            "error": str(e),
        }

# ------------------------------------------------------------
# HELPER: translate text (second call)
# ------------------------------------------------------------
def translate_with_context(source_text: str, source_lang: str, target_lang: str) -> dict:
    """
    Ask the model to translate, provide alternatives, and cultural/regional notes.
    Return structured JSON.
    """
    try:
        resp = client.chat.completions.create(
            model=TRANSLATION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional translator and cultural advisor. "
                        "Translate the user's text from the source language to the target language. "
                        "Return ONLY JSON with fields: "
                        "main_translation (string), "
                        "alternative_translations (array of strings), "
                        "cultural_note (string, optional), "
                        "tone (string, optional). "
                        "Use natural, idiomatic language, not word-for-word."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "source_language": source_lang,
                            "target_language": target_lang,
                            "text": source_text,
                        }
                    ),
                },
            ],
            temperature=0.4,
        )
        raw = resp.choices[0].message.content.strip()
        data = json.loads(raw)
        return data
    except Exception as e:
        return {
            "main_translation": "",
            "alternative_translations": [],
            "cultural_note": "",
            "error": str(e),
        }

# ------------------------------------------------------------
# DISPLAY CHAT HISTORY (original behavior)
# ------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ------------------------------------------------------------
# HANDLE USER INPUT
# ------------------------------------------------------------
if prompt := st.chat_input("Type text in ANY language, I'll translate it..."):
    # 1) Add user message to chat history (original behavior)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2) Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3) DETECT LANGUAGE (first call)
    with st.chat_message("assistant"):
        with st.spinner("🔍 Detecting language..."):
            detection = detect_language(prompt)

        source_lang = detection.get("language_name", "Unknown")
        confidence = detection.get("confidence", 0.0)
        iso_code = detection.get("iso_code", "")

        # If the user typed already in the target language, we can try to be smart
        target_lang = st.session_state.target_language
        if source_lang.lower().startswith(target_lang.lower()):
            # user typed in same language as target -> switch to English as fallback
            # (you can change this logic)
            target_lang = "English" if target_lang != "English" else "Spanish"

        # 4) TRANSLATE (second call)
        with st.spinner(f"🌐 Translating from {source_lang} → {target_lang}..."):
            translation = translate_with_context(prompt, source_lang, target_lang)

        main_translation = translation.get("main_translation", "").strip()
        alternatives = translation.get("alternative_translations", []) or []
        cultural_note = translation.get("cultural_note", "")

        # 5) RENDER STRUCTURED OUTPUT
        st.markdown(f"🔍 **Detected Language:** {source_lang}")
        st.markdown(f"📏 **Confidence:** {confidence:.2f}")
        if iso_code:
            st.markdown(f"🆔 **ISO Code:** `{iso_code}`")

        st.markdown(f"🎯 **Translation → {target_lang}:** {main_translation or '—'}")

        if alternatives:
            st.markdown("🌟 **Alternative translations:**")
            for alt in alternatives:
                st.markdown(f"- {alt}")

        if cultural_note:
            st.markdown(f"💡 **Cultural / Regional note:** {cultural_note}")

        # 6) ADD TO TRANSLATION HISTORY (for sidebar)
        st.session_state.translation_history.append(
            {
                "source_text": prompt,
                "detected_language": source_lang,
                "target_language": target_lang,
                "translation": main_translation,
                "alternatives": alternatives,
                "cultural_note": cultural_note,
                "confidence": confidence,
            }
        )

        # 7) Add assistant message to chat history (so original flow is preserved)
        #    We store a compact version here
        assistant_compact = (
            f"Detected: {source_lang} (conf {confidence:.2f})\n"
            f"Translation ({target_lang}): {main_translation}\n"
        )
        if cultural_note:
            assistant_compact += f"Cultural note: {cultural_note}"
        st.session_state.messages.append({"role": "assistant", "content": assistant_compact})
      
