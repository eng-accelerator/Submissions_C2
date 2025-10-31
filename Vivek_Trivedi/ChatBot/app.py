import os
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
import re
import csv
import html
try:
    from slugify import slugify  # from python-slugify
except Exception:
    def slugify(text: str) -> str:
        s = re.sub(r"\s+", "-", text.strip().lower())
        s = re.sub(r"[^a-z0-9\-]+", "", s)
        return s or "chat"
try:
    from dateutil import parser as dtparser
except Exception:
    class _DTParser:
        @staticmethod
        def isoparse(s: str):
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
    dtparser = _DTParser()
try:
    import pandas as pd
except Exception:
    pd = None
# Note: we import the OpenAI client below as _Client for compatibility

apptitle = "Lets Talk"
# === PART 1: Bootstrap ===
st.set_page_config(page_title=apptitle, page_icon="🤖", layout="wide")

APP_TITLE = apptitle
HISTORY_DIR = "chat-history"
DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"
MODEL_OPTIONS = [
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4o-mini",
    "meta-llama/llama-3.1-405b-instruct",
]

# Languages
LANG_MAP = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Japanese": "ja",
    "Chinese (Simplified)": "zh",
    "Portuguese": "pt",
    "Italian": "it",
    "Korean": "ko",
    "Russian": "ru",
}
CODE_TO_NAME = {v: k for k, v in LANG_MAP.items()}

def utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def ensure_dirs():
    os.makedirs(HISTORY_DIR, exist_ok=True)

def file_slug(title: str) -> str:
    s = slugify(title or "New chat")
    return s or "chat"

def chat_filepath(chat_id: str, title: str) -> str:
    return os.path.join(HISTORY_DIR, f"{chat_id}__{file_slug(title)}.json")

def list_chats() -> List[Dict[str, Any]]:
    ensure_dirs()
    rows: List[Dict[str, Any]] = []
    for name in os.listdir(HISTORY_DIR):
        if not name.endswith(".json"):
            continue
        path = os.path.join(HISTORY_DIR, name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            rows.append({
                "id": data.get("id"),
                "title": data.get("title", "New chat"),
                "created": data.get("created", ""),
                "path": path,
            })
        except Exception:
            continue
    # Stable ordering bound to creation time only (newest first).
    # Do NOT re-order on rename or message updates.
    rows.sort(key=lambda r: (r.get("created", ""), r.get("id") or ""), reverse=True)
    return rows

def load_chat_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_chat_path_by_id(chat_id: str) -> Optional[str]:
    for it in list_chats():
        if it.get("id") == chat_id:
            return it.get("path")
    return None

def load_chat(chat_id: str) -> Optional[Dict[str, Any]]:
    p = find_chat_path_by_id(chat_id)
    if not p:
        return None
    try:
        return load_chat_file(p)
    except Exception as e:
        set_status_text(e)
        return None

def save_chat(state: Dict[str, Any]) -> None:
    ensure_dirs()
    chat_id = state.get("id") or str(uuid.uuid4())
    title = state.get("title") or "New chat"
    path = chat_filepath(chat_id, title)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        set_status_text(e)

def rename_chat_file(old_id: str, new_title: str) -> Optional[str]:
    old_path = find_chat_path_by_id(old_id)
    if not old_path:
        return None
    new_path = chat_filepath(old_id, new_title)
    try:
        with open(old_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["title"] = new_title
        with open(new_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if os.path.abspath(new_path) != os.path.abspath(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass
        return new_path
    except Exception as e:
        set_status_text(e)
        return None

def delete_chat(chat_id: str) -> None:
    p = find_chat_path_by_id(chat_id)
    if p and os.path.exists(p):
        try:
            os.remove(p)
        except Exception as e:
            set_status_text(e)

def set_status_text(exc: Exception | str):
    msg = f"{type(exc).__name__}: {exc}" if isinstance(exc, Exception) else str(exc)
    st.session_state["status_text"] = (st.session_state.get("status_text", "").strip() + "\n" + msg).strip()

def init_state():
    ensure_dirs()
    st.session_state.setdefault("chat_id", None)
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("meta", {
        "model": DEFAULT_MODEL,
        "mode": "standard",
        "target_language": "English",
        "last_detected_source": None,
        "last_confidence": None,
        "bidirectional": True,
        "previous_other_lang": None,
        "personality_key": "professional",
        "custom_persona": {"style": "", "expertise": "", "tone": ""},
    })
    st.session_state.setdefault("all_chats", list_chats())
    st.session_state.setdefault("rename_mode", False)
    st.session_state.setdefault("rename_value", "")
    st.session_state.setdefault("status_text", "")
    st.session_state.setdefault("source_language_fixed", None)
    st.session_state.setdefault("mode_radio", st.session_state["meta"].get("mode", "standard"))
    # Inline title edit state for main header
    st.session_state.setdefault("edit_title_mode", False)
    st.session_state.setdefault("title_edit_input", "")
    # Inline editing states
    st.session_state.setdefault("edit_title_mode", False)
    st.session_state.setdefault("edit_message_index", None)
    st.session_state.setdefault("edit_message_buffer", "")

# === PART 2: Personas and prompts ===
PERSONAS = {
    "professional": {"label": "Professional", "icon": "💼", "desc": "Formal, structured, business-focused.", "style": "You are formal, concise, and business-oriented. Provide numbered steps and clear action items."},
    "creative": {"label": "Creative", "icon": "🎨", "desc": "Imaginative, expressive, inspiring.", "style": "You are imaginative and expressive. Use vivid examples and an encouraging tone. Emojis allowed sparingly."},
    "technical": {"label": "Technical", "icon": "🧠", "desc": "Precise, detailed, code-focused.", "style": "You are precise and analytical. Provide step-by-step explanations and fenced code blocks when needed."},
    "friend": {"label": "Friend", "icon": "🤝", "desc": "Casual, supportive, conversational.", "style": "You are warm, empathetic, and practical, with simple language."},
    "custom": {"label": "Custom", "icon": "✨", "desc": "User-defined style/tone/expertise.", "style": ""},
}

def persona_block(meta: Dict[str, Any]) -> str:
    key = meta.get("personality_key", "professional")
    if key == "custom":
        c = meta.get("custom_persona", {}) or {}
        return "\n".join([
            "Persona: Custom.",
            f"Style: {c.get('style') or 'unspecified'}.",
            f"Expertise: {c.get('expertise') or 'unspecified'}.",
            f"Tone: {c.get('tone') or 'neutral'}.",
        ])
    p = PERSONAS.get(key, PERSONAS["professional"])
    return f"Persona: {p['label']}. {p['style']}"

def core_guardrails_block() -> str:
    return (
        "You are a careful, concise assistant. Be accurate and do not hallucinate."
        " Show errors verbatim when asked. Never claim background/asynchronous work."
        " Refuse unsafe content briefly with safer alternatives. Preserve formatting and code blocks."
    )

def translator_block(meta: Dict[str, Any]) -> str:
    target_name = meta.get("target_language", "English")
    return (
        "You are a professional translator. Detect source language and translate to the target.\n"
        "Goals: detect language, estimate confidence, translate, propose 1-3 alternatives, add a short cultural/usage note."
        " Preserve meaning, tone, register, line breaks, punctuation; keep code blocks unchanged.\n"
        "Output template (markdown):\n"
        "🔍 **Detected Language:** <Name> (`<code>`) — *Confidence:* <0–1 or Low/Med/High>\n\n"
        f"🎯 **Translation (→ {target_name}):**\n<translated text>\n\n"
        "🌟 **Alternative translations (if relevant):**\n- <alt 1>\n- <alt 2>\n- <alt 3>\n\n"
        "💡 **Cultural / Regional note (if relevant):**\n<one short, useful note>\n"
    )

def build_system_prompt(meta: Dict[str, Any]) -> str:
    parts = [core_guardrails_block(), persona_block(meta)]
    if meta.get("mode", "standard") == "translation":
        parts.append(translator_block(meta))
    else:
        parts.append("You are a helpful assistant. Be brief by default. Use triple backticks for code. Avoid purple prose.")
    return "\n\n".join(parts)

# === PART 3: Client and API helpers ===
try:
    from openai import OpenAI as _Client
except Exception:
    _Client = None

def get_client() -> Optional[_Client]:
    try:
        api_key = st.secrets.get("OPENROUTER_API_KEY")
    except Exception:
        api_key = None
    if not api_key:
        set_status_text("Missing OPENROUTER_API_KEY in st.secrets.")
        return None
    if _Client is None:
        set_status_text("openai package not available.")
        return None
    try:
        return _Client(
            base_url="https://www.openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={"HTTP-Referer": "http://localhost:8501", "X-Title": "My ChatBot"},
        )
    except Exception as e:
        set_status_text(e)
        return None

def to_api_messages(system_prompt: str, history: List[Dict[str, Any]], user_content: Optional[str] = None) -> List[Dict[str, str]]:
    msgs: List[Dict[str, str]] = []
    if system_prompt:
        msgs.append({"role": "system", "content": system_prompt})
    # Avoid duplicating prior system prompts; we already injected the fresh system_prompt above.
    for m in history:
        r = m.get("role")
        if r in ("user", "assistant"):
            msgs.append({"role": r, "content": m.get("content", "")})
    if user_content is not None:
        msgs.append({"role": "user", "content": user_content})
    return msgs

def _extract_delta_text(chunk: Any) -> Optional[str]:
    try:
        choice = chunk.choices[0]
        delta = getattr(choice, "delta", None)
        if isinstance(delta, dict):
            return delta.get("content")
        return getattr(delta, "content", None)
    except Exception:
        return None


def stream_completion(client: _Client, model: str, messages: List[Dict[str, str]]) -> str:
    full = ""
    try:
        stream = client.chat.completions.create(model=model, messages=messages, stream=True)
        chat_ctx = None
        area = None
        for chunk in stream:
            delta_text = _extract_delta_text(chunk)
            if delta_text:
                if chat_ctx is None:
                    # Create the assistant bubble only on first token to avoid empty bubbles
                    chat_ctx = st.chat_message("assistant")
                    area = chat_ctx.empty()
                full += delta_text
                if area is not None:
                    area.markdown(full)
    except Exception as e:
        set_status_text(e)
    # Fallback: if nothing streamed (SDK/compat quirk), do a non-stream call
    if not full:
        try:
            resp = client.chat.completions.create(model=model, messages=messages, stream=False)
            full = getattr(resp.choices[0].message, "content", "") or ""
            if full:
                with st.chat_message("assistant"):
                    st.markdown(full)
        except Exception as e:
            set_status_text(e)
            return ""
    return full


# -----------------------------
# Summarizer helpers
# -----------------------------
def _truncate_by_chars(msgs: List[Dict[str, str]], max_chars: int = 16000) -> List[Dict[str, str]]:
    total = sum(len(m.get("content", "")) for m in msgs)
    if total <= max_chars:
        return msgs
    out: List[Dict[str, str]] = []
    running = 0
    # Keep the last messages, ensure we keep the initial system
    sys = [m for m in msgs if m.get("role") == "system"]
    rest = [m for m in msgs if m.get("role") != "system"]
    # Start with the latest ones
    rest_rev = list(reversed(rest))
    chosen_rev: List[Dict[str, str]] = []
    for m in rest_rev:
        c = len(m.get("content", ""))
        if running + c > max_chars:
            break
        chosen_rev.append(m)
        running += c
    # Rebuild ordered: system first, then chronologically for chosen
    chosen = list(reversed(chosen_rev))
    out.extend(sys[:1])
    out.extend(chosen)
    return out


def build_summary_messages(client_meta: Dict[str, Any], user_prompt: str) -> List[Dict[str, str]]:
    # Use current persona/mode by default
    system_prompt = build_system_prompt(client_meta)
    # Include full conversation (system + user + assistant)
    msgs: List[Dict[str, str]] = []
    if system_prompt:
        msgs.append({"role": "system", "content": system_prompt})
    for m in st.session_state.get("messages", []):
        role = m.get("role")
        if role in ("system", "user", "assistant"):
            msgs.append({"role": role, "content": m.get("content", "")})
    # Append summarizer instruction + user prompt
    final_user = (
        "Summarize the entire conversation so far. Follow the current persona and mode unless this prompt says otherwise.\n"
        f"User request: {user_prompt}"
    )
    msgs.append({"role": "user", "content": final_user})
    return _truncate_by_chars(msgs)

def non_stream_completion(client: _Client, model: str, messages: List[Dict[str, str]]) -> str:
    try:
        resp = client.chat.completions.create(model=model, messages=messages, stream=False)
        return resp.choices[0].message.content or ""
    except Exception as e:
        set_status_text(e)
        return ""

def main():
    init_state()
    ensure_current_chat()
    client = get_client()

    # Sidebar
    # Compact sidebar list look: smaller buttons and icons
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] .stButton > button { padding: 4px 6px !important; font-size: 0.9rem !important; text-align: left !important; }
        [data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,0.06) !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    sidebar_history_latest()
    sidebar_controls()
    if st.session_state.get("show_delete_modal") and st.session_state.get("delete_chat_id"):
        open_delete_dialog()

    st.title(APP_TITLE)
    render_chat_area(client)

    errors = (st.session_state.get("status_text", "") or "").strip()
    if errors:
        with st.expander("Output / Errors", expanded=True):
            st.text_area("", value=errors, height=150)

    # Perform deferred rerun only after rendering to avoid interrupting first turns
    if st.session_state.get("do_rerun"):
        st.session_state["do_rerun"] = False
        st.rerun()

# MAIN CALL MOVED TO END

# === PART 4: Translation + UI wiring ===

def confidence_label(conf: Optional[float]) -> str:
    if conf is None:
        return "Unknown"
    if conf >= 0.85:
        return f"High ({conf:.2f})"
    if conf >= 0.60:
        return f"Medium ({conf:.2f})"
    return f"Low ({conf:.2f})"

def looks_untranslatable(text: str) -> bool:
    t = text.strip()
    if not t:
        return True
    if t.startswith("http://") or t.startswith("https://"):
        return True
    if t.isnumeric():
        return True
    if "```" in t:
        return True
    letters = sum(ch.isalpha() for ch in t)
    return (letters / max(len(t), 1)) < 0.2

def detect_language(client: Any, model: str, text: str) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    sys = (
        "You detect the language of the user's message. Respond with strict JSON only:"
        " {\"language_name\":<Name>,\"language_code\":<ISO 639-1>,\"confidence\":<0..1>}"
    )
    msgs = [{"role": "system", "content": sys}, {"role": "user", "content": text}]
    out = non_stream_completion(client, st.session_state.meta.get("model", DEFAULT_MODEL), msgs).strip()
    if out.startswith("```") or out.lower().startswith("```json"):
        out = out.strip("`\n ")
        if out.lower().startswith("json"):
            out = out[4:].strip()
    try:
        data = json.loads(out)
        return data.get("language_name"), data.get("language_code"), float(data.get("confidence")) if data.get("confidence") is not None else None
    except Exception:
        return None, None, None

def translate_message(client: Any, meta: Dict[str, Any], user_text: str,
                      detected_name: Optional[str], detected_code: Optional[str]) -> Tuple[str, Dict[str, Any]]:
    target_name = meta.get("target_language", "English")
    target_code = LANG_MAP.get(target_name, "en")
    bidirectional = meta.get("bidirectional", True)
    previous_other = meta.get("previous_other_lang")
    source_fixed = st.session_state.get("source_language_fixed")

    src_code = detected_code or None
    src_name = detected_name or CODE_TO_NAME.get(src_code or "", "Unknown")
    if not bidirectional and source_fixed:
        src_code = LANG_MAP.get(source_fixed, "en")
        src_name = source_fixed

    direction = {"from": src_code or "", "to": target_code}

    if bidirectional and src_code == target_code:
        if previous_other:
            prev_code = LANG_MAP.get(previous_other, None)
            direction = {"from": target_code, "to": prev_code or target_code}
        else:
            prompt = (
                f"🔍 **Detected Language:** {src_name} (`{src_code}`) — *Confidence:* {confidence_label(meta.get('last_confidence'))}\n\n"
                "Detected language matches target. Choose the other language in the sidebar to enable bidirectional translation."
            )
            return prompt, {"pair": {"from": src_code or "", "to": target_code}, "src": user_text, "tgt": "", "alts": []}

    if looks_untranslatable(user_text):
        md = (
            f"🔍 **Detected Language:** {src_name} (`{src_code}`) — *Confidence:* {confidence_label(meta.get('last_confidence'))}\n\n"
            f"🎯 **Translation (→ {CODE_TO_NAME.get(direction['to'], target_name)}):**\n"
            "Content appears non-translatable (code, URL, or numbers). Skipping translation.\n\n"
            "💡 **Cultural / Regional note (if relevant):**\nNone"
        )
        return md, {"pair": direction, "src": user_text, "tgt": "", "alts": []}

    system_prompt = build_system_prompt({**meta, "mode": "translation", "target_language": CODE_TO_NAME.get(direction['to'], target_name)})
    user_instructions = f"Translate from `{direction['from']}` to `{direction['to']}`.\nText:\n{user_text}"
    msgs = to_api_messages(system_prompt, [], user_instructions)
    content = stream_completion(client, meta.get("model", DEFAULT_MODEL), msgs)
    alts: List[str] = []
    for line in content.splitlines():
        s = line.strip()
        if s.startswith("- "):
            alts.append(s[2:].strip())
    return content, {"pair": direction, "src": user_text, "tgt": content, "alts": alts}

def new_chat(meta_override: Optional[Dict[str, Any]] = None) -> str:
    chat_id = str(uuid.uuid4())
    created = utcnow_iso()
    meta = st.session_state.get("meta", {}).copy()
    if meta_override:
        meta.update(meta_override)
    system_prompt = build_system_prompt(meta)
    # Generate a unique default title to avoid multiple identical 'New chat' labels
    def _generate_title() -> str:
        base = "New chat"
        titles = {c.get("title") for c in list_chats()}
        if base not in titles:
            return base
        i = 2
        while f"{base} {i}" in titles:
            i += 1
        return f"{base} {i}"
    default_title = _generate_title()
    state = {
        "id": chat_id,
        "title": default_title,
        "created": created,
        "updated": created,
        "messages": [{"role": "system", "content": system_prompt, "ts": created, "tokens": 0}],
        "meta": meta,
    }
    save_chat(state)
    st.session_state.chat_id = chat_id
    st.session_state.messages = state["messages"]
    st.session_state.meta = meta
    st.session_state.all_chats = list_chats()
    return chat_id

def open_chat(chat_id: str):
    data = load_chat(chat_id)
    if not data:
        return
    st.session_state.chat_id = chat_id
    # Drop any historical empty assistant messages
    def _clean(msgs: List[Dict[str, Any]]):
        return [m for m in msgs if not (m.get("role") == "assistant" and not (m.get("content") or "").strip())]
    st.session_state.messages = _clean(data.get("messages", []))
    st.session_state.meta = data.get("meta", st.session_state.get("meta", {}))
    st.session_state.all_chats = list_chats()
    # Keep the mode radio in sync with persisted meta so refresh reflects the saved mode
    try:
        st.session_state["mode_radio"] = st.session_state.meta.get("mode", "standard")
    except Exception:
        pass
    # Reset transient header title override and inline edit flags when switching chats
    try:
        if "current_title_override" in st.session_state:
            st.session_state.pop("current_title_override", None)
        st.session_state["edit_title_mode"] = False
        st.session_state["_title_edit_initialized"] = False
        st.session_state["title_edit_input"] = ""
    except Exception:
        pass

def persist_current():
    cid = st.session_state.get("chat_id")
    if not cid:
        return
    p = find_chat_path_by_id(cid)
    if not p:
        return
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Clean out any empty assistant messages before persisting
        msgs = st.session_state.get("messages", [])
        msgs = [m for m in msgs if not (m.get("role") == "assistant" and not (m.get("content") or "").strip())]
        data["messages"] = msgs
        data["meta"] = st.session_state.get("meta", {})
        data["updated"] = utcnow_iso()
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        st.session_state.all_chats = list_chats()
    except Exception as e:
        set_status_text(e)

def persona_badge(meta: Dict[str, Any]):
    key = meta.get("personality_key", "professional")
    p = PERSONAS.get(key, PERSONAS["professional"])
    st.markdown(f"{p['icon']} **Persona:** {p['label']}")

def handle_rename_confirm(cid: str):
    new_title = st.session_state.get(f"rename_input_{cid}", "").strip() or "New chat"
    rename_chat_file(cid, new_title)
    st.session_state.rename_mode = False
    st.session_state.rename_value = ""
    st.session_state.all_chats = list_chats()
    # Clear transient title override when switching chats
    if "current_title_override" in st.session_state:
        st.session_state.pop("current_title_override", None)
    st.session_state["do_rerun"] = True

def handle_title_save():
    """Save chat title from the header inline editor on Enter.
    Keeps display text as typed (capped at 80 chars), sanitizes only for filename.
    """
    import streamlit as st
    try:
        cid = st.session_state.get("chat_id")
        if not cid:
            return
        new_title = (st.session_state.get("title_edit_input", "") or "").strip() or "New chat"
        if len(new_title) > 80:
            new_title = new_title[:80]
        rename_chat_file(cid, new_title)
        st.session_state["current_title_override"] = new_title
        st.session_state.all_chats = list_chats()
    except Exception as e:
        set_status_text(e)
    finally:
        st.session_state["edit_title_mode"] = False
    st.session_state["do_rerun"] = True

def sidebar_controls():
    st.sidebar.subheader("Mode")
    # Mode + inline Translation settings
    mode = st.sidebar.radio("", ["standard", "translation"], horizontal=True, key="mode_radio")
    st.session_state.meta["mode"] = mode
    # Persist immediately so refresh keeps the selected mode
    try:
        persist_current()
    except Exception:
        pass

    if mode == "translation":
        # Show language selection directly under the mode toggle
        tgt = st.sidebar.selectbox(
            "Target language",
            list(LANG_MAP.keys()),
            index=list(LANG_MAP.keys()).index(st.session_state.meta.get("target_language", "English"))
            if st.session_state.meta.get("target_language", "English") in LANG_MAP else 0,
            key="tgt_lang",
        )
        st.session_state.meta["target_language"] = tgt
        direction = st.sidebar.radio(
            "Direction",
            ["Auto/Bidirectional", "Source → Target"],
            index=0 if st.session_state.meta.get("bidirectional", True) else 1,
            key="direction_radio_inline",
        )
        st.session_state.meta["bidirectional"] = (direction == "Auto/Bidirectional")
        if direction == "Source → Target":
            st.session_state.source_language_fixed = st.sidebar.selectbox("Source language", list(LANG_MAP.keys()), key="src_lang_fixed")
        else:
            st.session_state.source_language_fixed = None
        try:
            persist_current()
        except Exception:
            pass

    # Divider after Mode section
    st.sidebar.divider()

    st.sidebar.subheader("Model")
    model_val = st.sidebar.text_input(
        "Model ID",
        value=st.session_state.meta.get("model", DEFAULT_MODEL),
        placeholder="e.g., anthropic/claude-3.5-sonnet",
        help="Paste any valid OpenRouter model ID (see openrouter.ai/models)",
    )
    def _valid_model(s: str) -> bool:
        if not s or any(ch.isspace() for ch in s):
            return False
        # require vendor/name pattern
        return "/" in s and all(len(part) > 0 for part in s.split("/"))

    if model_val:
        model_val = model_val.strip()
        st.session_state.meta["model"] = model_val
        if not _valid_model(model_val):
            st.sidebar.warning("Model looks invalid. Use vendor/name, no spaces.")
    try:
        persist_current()
    except Exception:
        pass

    # Divider after Model section
    st.sidebar.divider()

    # (Removed duplicate Translation Settings block below Mode)

    st.sidebar.subheader("Personality")
    persona_keys = list(PERSONAS.keys())
    pkey = st.sidebar.selectbox("Persona", persona_keys, index=persona_keys.index(st.session_state.meta.get("personality_key", "professional")))
    st.session_state.meta["personality_key"] = pkey
    if pkey == "custom":
        cp = st.session_state.meta.get("custom_persona", {})
        cp["style"] = st.sidebar.text_input("Custom style", cp.get("style", ""))
        cp["expertise"] = st.sidebar.text_input("Custom expertise", cp.get("expertise", ""))
        cp["tone"] = st.sidebar.text_input("Custom tone", cp.get("tone", ""))
        st.session_state.meta["custom_persona"] = cp
    try:
        persist_current()
    except Exception:
        pass

    # Divider after Personality section
    st.sidebar.divider()

    # Export controls
    st.sidebar.subheader("Export")
    role_filter = st.sidebar.selectbox("Role filter", ["all", "user", "assistant"])
    date_range = st.sidebar.date_input("Date range (optional)", [])
    start_dt: Optional[datetime] = None
    end_dt: Optional[datetime] = None
    if isinstance(date_range, list) and len(date_range) == 2:
        start_dt = datetime.combine(date_range[0], datetime.min.time(), tzinfo=timezone.utc)
        end_dt = datetime.combine(date_range[1], datetime.max.time(), tzinfo=timezone.utc)
    if st.session_state.get("chat_id"):
        path = find_chat_path_by_id(st.session_state.chat_id)
        if path and os.path.exists(path):
            try:
                chat = load_chat_file(path)
                msgs = filter_messages_by_date_role(chat.get("messages", []), start_dt, end_dt, role_filter)
                if len([m for m in msgs if m.get("role") in ("user", "assistant")]) == 0:
                    st.sidebar.info("No messages to export with current filters.")
                else:
                    slug = slugify(chat.get("title", "chat")) or "chat"
                    ts = datetime.now().strftime("%Y%m%d_%H%M")
                    try:
                        st.sidebar.download_button("Download TXT", to_txt_export(chat, msgs).encode("utf-8"), file_name=f"chat_{slug}_{ts}.txt", mime="text/plain")
                    except Exception as e:
                        set_status_text(e)
                    try:
                        st.sidebar.download_button("Download JSON", to_json_export(chat, msgs).encode("utf-8"), file_name=f"chat_{slug}_{ts}.json", mime="application/json")
                    except Exception as e:
                        set_status_text(e)
                    try:
                        st.sidebar.download_button("Download CSV", to_csv_export(msgs).encode("utf-8"), file_name=f"chat_{slug}_{ts}.csv", mime="text/csv")
                    except Exception as e:
                        set_status_text(e)
            except Exception as e:
                set_status_text(e)
    # Divider after Export section
    st.sidebar.divider()

def filter_messages_by_date_role(messages: List[Dict[str, Any]], start: Optional[datetime], end: Optional[datetime], role: str) -> List[Dict[str, Any]]:
    def in_range(ts: str) -> bool:
        try:
            t = dtparser.isoparse(ts)
        except Exception:
            return True
        if start and t < start:
            return False
        if end and t > end:
            return False
        return True
    out: List[Dict[str, Any]] = []
    for m in messages:
        r = m.get("role")
        if role != "all" and r != role:
            continue
        if in_range(m.get("ts", utcnow_iso())):
            out.append(m)
    return out

def export_stats(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    user_msgs = [m for m in messages if m.get("role") == "user"]
    asst_msgs = [m for m in messages if m.get("role") == "assistant"]
    total_chars = sum(len((m.get("content") or "")) for m in messages)
    avg_len = total_chars / max(len(messages), 1)
    return {"user_messages": len(user_msgs), "assistant_messages": len(asst_msgs), "total_characters": total_chars, "average_message_length": round(avg_len, 2)}

def build_export_metadata(chat: Dict[str, Any]) -> Dict[str, Any]:
    meta = chat.get("meta", {})
    created = chat.get("created")
    updated = chat.get("updated")
    dur_min = None
    try:
        if created and updated:
            dur = dtparser.isoparse(updated) - dtparser.isoparse(created)
            dur_min = round(dur.total_seconds() / 60.0, 2)
    except Exception:
        dur_min = None
    return {
        "export_timestamp": utcnow_iso(),
        "format_version": "1.0",
        "session_id": chat.get("id"),
        "total_messages": len(chat.get("messages", [])),
        "session_duration_minutes": dur_min,
        "model": meta.get("model"),
        "mode": meta.get("mode"),
        "target_language": meta.get("target_language"),
        "personality_key": meta.get("personality_key"),
        "bidirectional": meta.get("bidirectional"),
        "last_detected_source": meta.get("last_detected_source"),
        "last_confidence": meta.get("last_confidence"),
    }

def to_txt_export(chat: Dict[str, Any], messages: List[Dict[str, Any]]) -> str:
    meta = build_export_metadata(chat)
    header = [
        f"Chat Export — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 39,
        "Session Information:",
        f"- Total Messages: {meta['total_messages']}",
        f"- Duration: {meta['session_duration_minutes']} minutes",
        f"- Model: {meta['model']}",
        f"- Mode: {meta['mode']}",
        f"- Target Language: {meta['target_language']}",
        f"- Last Detected Source: {meta['last_detected_source']} ({meta['last_confidence']})",
        "-" * 40,
    ]
    lines = ["\n".join(header)]
    for m in messages:
        ts = m.get("ts", "")
        try:
            hts = datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%H:%M:%S")
        except Exception:
            hts = ts
        who = "You" if m.get("role") == "user" else ("Assistant" if m.get("role") == "assistant" else "System")
        content = m.get("content") or ""
        lines.append(f"[{hts}] {who}: {content}")
    return "\n".join(lines)

def to_json_export(chat: Dict[str, Any], messages: List[Dict[str, Any]]) -> str:
    data = {"export_metadata": build_export_metadata(chat), "conversation": messages, "statistics": export_stats(messages)}
    return json.dumps(data, ensure_ascii=False, indent=2)

def to_csv_export(messages: List[Dict[str, Any]]) -> str:
    headers = ["Message_ID", "Timestamp", "Role", "Content", "Character_Count", "Word_Count"]
    if pd is not None:
        rows = []
        for i, m in enumerate(messages, start=1):
            content = m.get("content") or ""
            rows.append({
                "Message_ID": i,
                "Timestamp": m.get("ts", ""),
                "Role": m.get("role", ""),
                "Content": content,
                "Character_Count": len(content),
                "Word_Count": len(content.split()),
            })
        df = pd.DataFrame(rows, columns=headers)
        return df.to_csv(index=False)
    # Fallback without pandas
    from io import StringIO
    buf = StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(headers)
    for i, m in enumerate(messages, start=1):
        content = m.get("content") or ""
        writer.writerow([i, m.get("ts", ""), m.get("role", ""), content, len(content), len(content.split())])
    return buf.getvalue()

def ensure_current_chat():
    if st.session_state.get("chat_id") is None:
        lst = list_chats()
        if lst:
            open_chat(lst[0]["id"])
        else:
            new_chat()

# Global delete confirmation dialog
try:
    from streamlit.runtime.scriptrunner import add_script_run_ctx  # noqa: F401
    DIALOG_AVAILABLE = True
except Exception:
    DIALOG_AVAILABLE = True  # Streamlit >=1.25 has st.dialog

@st.dialog("Confirm deletion")
def open_delete_dialog():
    cid = st.session_state.get("delete_chat_id")
    if not cid:
        st.write("No chat selected.")
        return
    # Find title for display
    title = None
    for it in st.session_state.get("all_chats", []):
        if it.get("id") == cid:
            title = it.get("title")
            break
    st.warning(f"This will permanently delete: {title or cid}")
    c1, c2 = st.columns(2)
    if c1.button("Delete permanently", type="primary"):
        delete_chat(cid)
        # Clear selection and refresh chat list
        st.session_state["delete_chat_id"] = None
        st.session_state["show_delete_modal"] = False
        newlist = list_chats()
        st.session_state.all_chats = newlist
        # If the current chat was deleted, open most recent or create new
        if st.session_state.get("chat_id") == cid:
            if newlist:
                open_chat(newlist[0]["id"])
            else:
                new_chat()
        # Close dialog and refresh UI immediately
        st.rerun()
    if c2.button("Cancel"):
        st.session_state["delete_chat_id"] = None
        st.session_state["show_delete_modal"] = False
        st.rerun()

def render_chat_area(client: Any):
    meta = st.session_state.get("meta", {})
    # Show current chat title prominently
    try:
        chat_title = None
        cid = st.session_state.get("chat_id")
        if cid:
            p = find_chat_path_by_id(cid)
            if p and os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    chat_title = (json.load(f) or {}).get("title")
        # Prefer transient override if present (immediate UI update after rename)
        chat_title = st.session_state.get("current_title_override", chat_title)
        # Inline title editor with pencil toggle and live counter
        col_title, col_btn = st.columns([0.88, 0.12])
        with col_title:
            if st.session_state.get("edit_title_mode"):
                # Preload current title into input if first time entering edit mode
                if not st.session_state.get("_title_edit_initialized"):
                    st.session_state["title_edit_input"] = chat_title or "New chat"
                    st.session_state["_title_edit_initialized"] = True
                val = st.text_input(
                    label="Rename chat",
                    key="title_edit_input",
                    max_chars=80,
                    label_visibility="collapsed",
                    placeholder="Enter chat title (max 80 chars)",
                    on_change=handle_title_save,
                )
                # Live character counter
                try:
                    count = len(val or "")
                except Exception:
                    count = 0
                counter_style = "color:#f87171;" if count > 80 else "opacity:0.75;"
                st.markdown(f"<div style='{counter_style} font-size:0.8rem;'>{count}/80</div>", unsafe_allow_html=True)
            else:
                if chat_title:
                    st.subheader(chat_title)
                else:
                    st.subheader("New chat")
        with col_btn:
            if st.button("✎", key="toggle_edit_title"):
                # Toggle edit mode; second click cancels without saving
                editing = st.session_state.get("edit_title_mode", False)
                st.session_state["edit_title_mode"] = not editing
                # Reset initializer so input value is refreshed when opening
                if not editing:
                    st.session_state["_title_edit_initialized"] = False
    except Exception as e:
        set_status_text(e)
    persona_badge(meta)
    # Summarizer panel (available throughout; collapsed by default)
    with st.expander("Summarize your chat", expanded=False):
        sprompt = st.text_area(
            "",
            key="summarizer_prompt",
            height=60,
            placeholder="e.g., Summarize key decisions and action items",
            label_visibility="collapsed",
        )
        # Place the Summarize button directly under the input, with a right-side spinner area
        _btn_col, _spin_col = st.columns([0.2, 0.8])
        with _btn_col:
            gen = st.button("Summarize", use_container_width=True, key="summarize_btn")

        # Output area (fixed height, scrollable) using a placeholder so we can replace content
        output_box = st.empty()

        # Show the latest saved summary (if any) below the button
        last_summary = None
        for m in reversed(st.session_state.get("messages", [])):
            if m.get("is_summary"):
                last_summary = m.get("content")
                break
        if last_summary:
            safe = html.escape(last_summary)
            output_box.markdown(
                f'<div style="height:50vw; overflow-y:auto; border:1px solid rgba(255,255,255,0.1); '
                f'border-radius:6px; padding:12px; background:rgba(255,255,255,0.02);">'
                f'<pre style="white-space:pre-wrap; word-break:break-word; margin:0;">{safe}</pre></div>',
                unsafe_allow_html=True,
            )

        if gen:
            if not client:
                st.warning("No API client configured. Check API key in secrets.")
            else:
                try:
                    model = meta.get("model", DEFAULT_MODEL)
                    if not model or (" " in model) or ("/" not in model):
                        st.warning("Please provide a valid model ID in the sidebar (vendor/name).")
                    else:
                        msgs = build_summary_messages(meta, sprompt or "")
                        # Show spinner on the right of the button row
                        with _spin_col:
                            with st.spinner("Summarizing…"):
                                summary_text = non_stream_completion(client, model, msgs)
                        if summary_text:
                            # Replace any previous summary in UI and state; keep only the latest
                            safe = html.escape(summary_text)
                            output_box.empty()
                            output_box.markdown(
                                f'<div style="height:50vw; overflow-y:auto; border:1px solid rgba(255,255,255,0.1); '
                                f'border-radius:6px; padding:12px; background:rgba(255,255,255,0.02);">'
                                f'<pre style="white-space:pre-wrap; word-break:break-word; margin:0;">{safe}</pre></div>',
                                unsafe_allow_html=True,
                            )
                            # Save as assistant message (flagged), but do not render in main chat loop
                            st.session_state.messages = [m for m in st.session_state.messages if not m.get("is_summary")]
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": summary_text,
                                "ts": utcnow_iso(),
                                "tokens": 0,
                                "is_summary": True,
                            })
                            persist_current()
                        else:
                            st.info("No summary text returned. Try a different prompt or check errors.")
                except Exception as e:
                    set_status_text(e)

    st.divider()
    for m in st.session_state.get("messages", []):
        if m.get("role") in ("user", "assistant"):
            if m.get("is_summary"):
                # Do not clutter main chat with summary entries; they are visible in the panel and exports
                continue
            content_to_show = m.get("content", "")
            # Skip rendering blank assistant bubbles
            if m.get("role") == "assistant" and not (content_to_show or "").strip():
                continue
            with st.chat_message(m.get("role")):
                st.markdown(content_to_show)
    prompt = st.chat_input("Ask or paste text…")
    if not prompt:
        return
    now = utcnow_iso()
    st.session_state.messages.append({"role": "user", "content": prompt, "ts": now, "tokens": 0})
    persist_current()
    # Render the just-submitted user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    # Auto-rename chat to first user message preview if still default title
    try:
        cid = st.session_state.get("chat_id")
        if cid:
            path = find_chat_path_by_id(cid)
            if path and os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                current_title = (data or {}).get("title", "")
                if current_title and current_title.lower().startswith("new chat"):
                    first_line = prompt.strip().splitlines()[0]
                    preview = first_line.strip()
                    if len(preview) > 40:
                        preview = preview[:40].rstrip() + "…"
                    if preview:
                        rename_chat_file(cid, preview)
                        st.session_state["current_title_override"] = preview
                        st.session_state.all_chats = list_chats()
                        # Schedule a rerun at end of this cycle so sidebar reflects new title now
                        st.session_state["do_rerun"] = True
    except Exception as e:
        set_status_text(e)
    if not client:
        st.warning("No API client configured. Check API key in secrets.")
        return
    try:
        model = meta.get("model", DEFAULT_MODEL)
        # Validate model id before API call
        if not model or (" " in model) or ("/" not in model):
            st.warning("Please provide a valid model ID in the sidebar (vendor/name).")
            return
        if meta.get("mode") == "translation":
            with st.spinner("Detecting language…"):
                name, code, conf = detect_language(client, model, prompt)
            st.session_state.meta["last_detected_source"] = name
            st.session_state.meta["last_confidence"] = conf
            persist_current()
            with st.spinner("Translating…"):
                content, tmeta = translate_message(client, st.session_state.meta, prompt, name, code)
            st.session_state.messages.append({"role": "assistant", "content": content, "ts": utcnow_iso(), "tokens": 0, "translation_meta": tmeta})
            pair = tmeta.get("pair", {})
            src = pair.get("from")
            tgt = pair.get("to")
            if src and tgt and src != tgt:
                target_code = LANG_MAP.get(meta.get("target_language", "English"), "en")
                other = src if src != target_code else tgt
                st.session_state.meta["previous_other_lang"] = CODE_TO_NAME.get(other, other)
            persist_current()
        else:
            system_prompt = build_system_prompt(meta)
            msgs = to_api_messages(system_prompt, st.session_state.messages[:-1], prompt)
            with st.spinner("Thinking…"):
                content = stream_completion(client, model, msgs)
            if content and content.strip():
                st.session_state.messages.append({"role": "assistant", "content": content, "ts": utcnow_iso(), "tokens": 0})
                persist_current()
            else:
                st.warning("The model returned no text. Check model ID and errors panel.")
    except Exception as e:
        set_status_text(e)

# Move main call to the end so all functions are defined first
def sidebar_history_latest():
    st.sidebar.subheader("Chats")
    st.sidebar.markdown(
        """
        <style>
        #chat-list { height: 30vh; overflow-y: auto; padding-right: 4px; }
        #new-chat { margin-bottom: 6px; }
        #chat-list .stTextInput input{ background: transparent; border: 1px solid transparent; padding: 2px 4px; }
        #chat-list .stTextInput input:focus{ border: 1px solid rgba(255,255,255,0.25); background: rgba(255,255,255,0.03); }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button("+ New chat", key="new_chat_btn_clean", use_container_width=True):
        new_chat()
        st.session_state["do_rerun"] = True
    st.sidebar.caption("Chat History")
    chats = list_chats()
    st.session_state.all_chats = chats
    current_id = st.session_state.get("chat_id")
    chat_list = st.sidebar.container()
    def select_chat(cid: str):
        for it in chats:
            key = f"sel_{it.get('id')}"
            if key in st.session_state:
                st.session_state[key] = (it.get('id') == cid)
        open_chat(cid)
        st.session_state["do_rerun"] = True
    with chat_list:
        for item in chats:
            cid = item.get("id")
            title = item.get("title") or "Untitled"
            row = st.container()
            col_sel, col_title, col_del = row.columns([0.12, 0.73, 0.15])
            col_sel.checkbox(
                label="",
                value=(current_id == cid),
                key=f"sel_{cid}",
                label_visibility="collapsed",
                on_change=lambda cid=cid: select_chat(cid),
            )
            new_title = col_title.text_input(
                label="",
                value=title,
                key=f"title_inline_{cid}",
                label_visibility="collapsed",
                placeholder="Title",
                help="Click to rename; selection stays unchanged",
            )
            if new_title.strip() and new_title != title:
                st.session_state[f"rename_input_{cid}"] = new_title
                handle_rename_confirm(cid)
            if col_del.button("🗑️", key=f"del_inline_{cid}"):
                st.session_state["delete_chat_id"] = cid
                st.session_state["show_delete_modal"] = True
                # dialog handled centrally via show_delete_modal



if __name__ == "__main__":
    main()
