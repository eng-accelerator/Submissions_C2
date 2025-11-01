import os
import json
import csv
import uuid
import time
import datetime as dt
from pathlib import Path
from typing import Dict, List, Generator, Any

import requests
import streamlit as st

# =============================
# ---- Config & Constants  ----
# =============================
APP_TITLE = "Multi-Chat Assistant"
DATA_DIR = Path("./chats")
INDEX_FILE = DATA_DIR / "index.json"
DEFAULT_MODEL = "openai/gpt-4o-mini:free"
DEFAULT_SUMMARY_MODEL = "openai/gpt-4o-mini:free"
REQUEST_TIMEOUT = 60

PERSONAS = {
    "General": "You are a helpful, concise assistant. Prefer short, clear answers.",
    "Teacher": "You are a calm teacher. Explain simply, add brief examples when helpful.",
    "Coach": "You are an encouraging coach. Give actionable, stepwise advice.",
    "Analyst": "You are a precise analyst. Be structured and avoid fluff.",
}

TRANSLATE_TO = [
    "English", "Hindi", "Spanish", "French", "German", "Chinese", "Arabic",
]

SUGGESTED_MODELS = {
    "OpenAI • GPT-4o mini (free)": "openai/gpt-4o-mini:free",
    "Meta • Llama-3.1-8B Instruct (free)": "meta-llama/llama-3.1-8b-instruct:free",
    "Mistral • Mistral-7B Instruct (free)": "mistralai/mistral-7b-instruct:free",
}

DEFAULT_TITLES = {"New Chat", "Untitled", ""}

# =============================
# ---- File I/O Utilities  ----
# =============================

def ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        INDEX_FILE.write_text(json.dumps({"chats": []}, indent=2), encoding="utf-8")


def read_index() -> Dict[str, Any]:
    ensure_store()
    try:
        idx = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        if not isinstance(idx, dict) or "chats" not in idx:
            return {"chats": []}
        return idx
    except Exception:
        return {"chats": []}


def write_index(index: Dict[str, Any]) -> None:
    ensure_store()
    INDEX_FILE.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")


def chat_file(chat_id: str) -> Path:
    return DATA_DIR / f"{chat_id}.json"


def create_chat(title: str = "New Chat") -> str:
    chat_id = uuid.uuid4().hex[:8]
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    doc = {
        "id": chat_id,
        "title": title or "New Chat",
        "created": now,
        "updated": now,
        "persona": "General",
        "model": DEFAULT_MODEL,
        "messages": [],
        "summaries": {"key_points": "", "action_items": ""},
    }
    chat_file(chat_id).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    index = read_index()
    index["chats"].insert(0, {"id": chat_id, "title": doc["title"], "updated": now})
    write_index(index)
    return chat_id


def load_chat(chat_id: str) -> Dict[str, Any]:
    try:
        doc = json.loads(chat_file(chat_id).read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            return {}
        doc.setdefault("title", "New Chat")
        doc.setdefault("messages", [])
        doc.setdefault("persona", "General")
        doc.setdefault("model", DEFAULT_MODEL)
        doc.setdefault("summaries", {"key_points": "", "action_items": ""})
        return doc
    except Exception:
        return {}


def save_chat(doc: Dict[str, Any]) -> None:
    if not doc:
        return
    doc["updated"] = dt.datetime.now(dt.timezone.utc).isoformat()
    chat_file(doc["id"]).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    index = read_index()
    found = False
    for row in index["chats"]:
        if row["id"] == doc["id"]:
            row["title"] = doc.get("title") or row.get("title") or "New Chat"
            row["updated"] = doc["updated"]
            found = True
            break
    if not found:
        index["chats"].insert(0, {"id": doc["id"], "title": doc.get("title","New Chat"), "updated": doc["updated"]})
    write_index(index)


def delete_chat(chat_id: str) -> None:
    try:
        chat_file(chat_id).unlink(missing_ok=True)
    except Exception:
        pass
    index = read_index()
    index["chats"] = [c for c in index["chats"] if c["id"] != chat_id]
    write_index(index)

# =============================
# ---- OpenRouter Key Guard ---
# =============================

def _get_api_key() -> str:
    key = ""
    try:
        key = st.secrets.get("OPENROUTER_API_KEY", "")
    except Exception:
        pass
    if not key:
        key = os.getenv("OPENROUTER_API_KEY", "")
    return (key or "").strip()

def _require_api_key_or_stop():
    key = _get_api_key()
    if not key:
        st.error(
            "OpenRouter API key not found. Add `OPENROUTER_API_KEY` to `.streamlit/secrets.toml` "
            "or set it as an environment variable, then restart the app."
        )
        st.stop()

# =============================
# ---- OpenRouter Client  -----
# =============================

def openrouter_headers() -> Dict[str, str]:
    key = _get_api_key()  # validated via _require_api_key_or_stop() in main()
    referer = os.getenv("STREAMLIT_REFERER", "http://localhost:8501")

    def ascii_only(s: str) -> str:
        try:
            return s.encode("ascii", "ignore").decode("ascii")
        except Exception:
            return ""

    return {
        "Authorization": f"Bearer {key}",
        "HTTP-Referer": referer,
        "X-Title": ascii_only(APP_TITLE),
        "Content-Type": "application/json",
        "Accept": "text/event-stream, application/json",
    }


def stream_chat_completion(messages: List[Dict[str, str]], model: str) -> Generator[str, None, None]:
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {"model": model, "messages": messages, "stream": True}
    # Read SSE as raw bytes and UTF-8 decode manually to avoid mojibake
    with requests.post(url, headers=openrouter_headers(), json=payload, stream=True, timeout=REQUEST_TIMEOUT) as r:
        r.raise_for_status()
        for raw in r.iter_lines(chunk_size=8192):
            if not raw:
                continue
            raw = raw.strip()
            if raw.startswith(b":"):  # heartbeat/comment
                continue
            if not raw.startswith(b"data:"):
                continue
            data = raw.split(b":", 1)[1].strip()
            if data == b"[DONE]":
                break
            try:
                obj = json.loads(data.decode("utf-8"))
                delta = obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if delta:
                    yield delta
            except Exception:
                continue


def non_stream_completion(messages: List[Dict[str, str]], model: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {"model": model, "messages": messages}
    r = requests.post(url, headers=openrouter_headers(), json=payload, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    r.encoding = "utf-8"
    data = r.json()
    return data["choices"][0]["message"]["content"]

# =============================
# ---- AI Helper Functions ----
# =============================

def persona_system(persona: str) -> str:
    return PERSONAS.get(persona, PERSONAS["General"])

# --- Translation mode helpers (single-call JSON with cultural context) ---

def translate_with_context(text: str, target_language: str, model: str) -> Dict[str, str]:
    """Ask model to detect language and provide translation + notes in strict JSON."""
    sys = {
        "role": "system",
        "content": (
            "You are an expert translator. First detect the input language. "
            f"Translate naturally into {target_language}. Provide helpful cultural notes. "
            "Return ONLY compact JSON with keys: detected_language, translation, cultural_note, alternative, regional_note. "
            "Use one short sentence each for cultural_note and regional_note."
        ),
    }
    user = {"role": "user", "content": text[:4000]}
    raw = non_stream_completion([sys, user], model).strip()

    # Robust JSON extraction
    def _coerce_json(s: str) -> Dict[str, str]:
        try:
            return json.loads(s)
        except Exception:
            try:
                start = s.find("{")
                end = s.rfind("}")
                if start != -1 and end != -1:
                    return json.loads(s[start:end+1])
            except Exception:
                pass
        return {}

    data = _coerce_json(raw)
    return {
        "detected_language": str(data.get("detected_language", "")).strip() or "Unknown",
        "translation": str(data.get("translation", "")).strip() or "",
        "cultural_note": str(data.get("cultural_note", "")).strip(),
        "alternative": str(data.get("alternative", "")).strip(),
        "regional_note": str(data.get("regional_note", "")).strip(),
    }

def render_translation_block(res: Dict[str, str], target_language: str) -> str:
    # Emojis for visual consistency
    det = res.get("detected_language", "Unknown")
    trn = res.get("translation", "")
    cul = res.get("cultural_note", "")
    alt = res.get("alternative", "")
    reg = res.get("regional_note", "")

    parts = [
        f"🔵 **Detected Language:** {det}",
        f"🎯 **Translation ({target_language}):** {json.dumps(trn, ensure_ascii=False)}",
    ]
    if cul: parts.append(f"💡 **Cultural Note:** {cul}")
    if alt: parts.append(f"✨ **Alternative:** {json.dumps(alt, ensure_ascii=False)}")
    if reg: parts.append(f"🌍 **Regional Note:** {reg}")
    return "\n\n".join(parts)

def detect_language(text: str, model: str) -> str:
    sys_msg = {
        "role": "system",
        "content": "Detect the language name for the given text. Reply with only the language name.",
    }
    user_msg = {"role": "user", "content": text[:2000]}
    try:
        out = non_stream_completion([sys_msg, user_msg], model)
        return out.strip().split("\n")[0]
    except Exception:
        return "Unknown"


def translate_text(text: str, target_language: str, model: str) -> str:
    sys_msg = {
        "role": "system",
        "content": f"You translate to {target_language}. Keep meaning and tone; be natural.",
    }
    user_msg = {"role": "user", "content": text}
    return non_stream_completion([sys_msg, user_msg], model)


def summarize_conversation(messages: List[Dict[str, str]], model: str) -> Dict[str, str]:
    sys_msg = {
        "role": "system",
        "content": "Summarize the conversation into two parts: 1) Key Points (bulleted, <=6 bullets), 2) Action Items (numbered, <=5 items). Return as JSON with keys key_points and action_items.",
    }
    convo_text = []
    for m in messages[-12:]:
        who = "User" if m["role"] == "user" else "Assistant"
        convo_text.append(f"{who}: {m['content']}")
    user_msg = {"role": "user", "content": "\n".join(convo_text)[:6000]}
    try:
        raw = non_stream_completion([sys_msg, user_msg], model)
        j = json.loads(raw)
        return {"key_points": j.get("key_points", ""), "action_items": j.get("action_items", "")}
    except Exception:
        return {"key_points": "", "action_items": ""}

# ---------- Auto Title Helpers ----------

def _simple_title_from_first_user(messages: List[Dict[str, str]]) -> str:
    text = ""
    for m in messages:
        if m.get("role") == "user" and m.get("content", "").strip():
            text = m["content"].strip()
            break
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    if len(text) > 60:
        text = text[:57].rstrip() + "…"
    return " ".join(w.capitalize() for w in text.split())

def _model_title_from_history(messages: List[Dict[str, str]], model: str) -> str:
    if not messages:
        return ""
    sys = {"role": "system",
           "content": "Create a concise 3-7 word Title Case title for this conversation. No quotes."}
    convo = []
    for m in messages[-16:]:
        role = m.get("role", "user")
        content = m.get("content", "")
        if not content:
            continue
        convo.append({"role": role, "content": content[:2000]})
    try:
        title = non_stream_completion([sys] + convo, model).strip().replace("\n", " ")
        if len(title) > 60:
            title = title[:57].rstrip() + "…"
        return title
    except Exception:
        return ""

def maybe_auto_title(chat_doc: Dict[str, Any]) -> None:
    current = (chat_doc.get("title") or "").strip()
    if current in DEFAULT_TITLES:
        roles = [m.get("role") for m in chat_doc.get("messages", [])]
        has_user = "user" in roles
        has_assistant = "assistant" in roles
        title = ""
        if has_user and has_assistant:
            title = _model_title_from_history(chat_doc["messages"], chat_doc.get("model", DEFAULT_MODEL))
        if not title:
            title = _simple_title_from_first_user(chat_doc.get("messages", []))
        if title and title not in DEFAULT_TITLES:
            chat_doc["title"] = title
            save_chat(chat_doc)

# =============================
# ---- Export Helpers ---------
# =============================

def export_txt(doc: Dict[str, Any]) -> str:
    lines = [
        f"Title: {doc.get('title','')}",
        f"Persona: {doc.get('persona','')}",
        "",
        "Conversation:",
    ]
    for m in doc.get("messages", []):
        who = "User" if m["role"] == "user" else "Assistant"
        lines.append(f"[{who}] {m.get('content','')}")
    return "\n".join(lines)


def export_json(doc: Dict[str, Any]) -> str:
    return json.dumps(doc, indent=2, ensure_ascii=False)


def export_csv(doc: Dict[str, Any]) -> str:
    from io import StringIO
    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(["role", "content", "timestamp"])
    for m in doc.get("messages", []):
        writer.writerow([m.get("role",""), m.get("content",""), doc.get("updated","")])
    return buf.getvalue()

# =============================
# ---- Theming (Dark/Light) ---
# =============================
DARK_CSS = """
<style>
:root { --bg: #0f1116; --panel: #161a23; --text: #e8e8e8; --muted:#9aa1ac; --accent:#4f8cff;
        --row-bd: rgba(255,255,255,0.06); --row-hv: rgba(79,140,255,0.10); }
html, body, [data-testid="stAppViewContainer"] { background-color: var(--bg) !important; }
section[data-testid="stSidebar"] { background-color: var(--panel) !important; }
* { color: var(--text) !important; }
.block-container { padding-top: 1.5rem; }

/* Plain-list radio styling for Chat History */
section[data-testid="stSidebar"] [role="radiogroup"] > label {
  display: flex !important;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 10px;
  margin: 4px 0;
  border: 1px solid var(--row-bd);
}
section[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
  background: var(--row-hv);
}
</style>
"""

LIGHT_CSS = """
<style>
:root { --bg: #ffffff; --panel:#f7f7f9; --text:#111; --muted:#444; --accent:#1f6feb;
        --row-bd: rgba(0,0,0,0.07); --row-hv: rgba(31,110,235,0.08); }
section[data-testid="stSidebar"] { background-color: var(--panel) !important; }
.block-container { padding-top: 1.5rem; }

/* Plain-list radio styling for Chat History */
section[data-testid="stSidebar"] [role="radiogroup"] > label {
  display: flex !important;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 10px;
  margin: 4px 0;
  border: 1px solid var(--row-bd);
}
section[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
  background: var(--row-hv);
}
</style>
"""

# =============================
# ---- Streamlit UI ----------
# =============================

def init_session():
    ensure_store()
    if "chat_id" not in st.session_state:
        idx = read_index()
        st.session_state.chat_id = idx["chats"][0]["id"] if idx["chats"] else create_chat("New Chat")
    if "start_ts" not in st.session_state:
        st.session_state.start_ts = time.time()
    # Default theme: Light
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"
    if "rename_mode" not in st.session_state:
        st.session_state.rename_mode = False
    if "rename_val" not in st.session_state:
        st.session_state.rename_val = ""


def sidebar(chat_doc: Dict[str, Any]):
    st.sidebar.title("Conversations")
    if st.sidebar.button("➕ New Chat", use_container_width=True):
        st.session_state.chat_id = create_chat("New Chat")
        st.rerun()

    st.sidebar.subheader("Chat History")
    idx = read_index()
    ids = [row["id"] for row in idx["chats"]]
    labels = {row["id"]: (row["title"] or row["id"]) for row in idx["chats"]}
    if st.session_state.chat_id not in ids and ids:
        st.session_state.chat_id = ids[0]

    selected_id = st.sidebar.radio(
        "Your chats",
        options=ids,
        index=ids.index(st.session_state.chat_id) if ids else 0,
        format_func=lambda cid: labels.get(cid, cid),
        label_visibility="collapsed",
    )
    if selected_id and selected_id != st.session_state.chat_id:
        st.session_state.chat_id = selected_id
        st.rerun()

    cA, cB = st.sidebar.columns(2, gap="small")
    with cA:
        if st.button("📝 Rename", use_container_width=True):
            st.session_state.rename_mode = True
            st.session_state.rename_val = labels.get(st.session_state.chat_id, "")
            st.rerun()
    with cB:
        if st.button("🗑️ Delete", use_container_width=True):
            delete_chat(st.session_state.chat_id)
            new_idx = read_index()
            if new_idx["chats"]:
                st.session_state.chat_id = new_idx["chats"][0]["id"]
            else:
                st.session_state.chat_id = create_chat("New Chat")
            st.rerun()

    if st.session_state.rename_mode:
        new_name = st.sidebar.text_input("New title", value=st.session_state.rename_val)
        c1, c2 = st.sidebar.columns(2)
        with c1:
            if st.button("Save"):
                doc = load_chat(st.session_state.chat_id) or {}
                if doc and new_name.strip():
                    doc["title"] = new_name.strip()
                    save_chat(doc)
                st.session_state.rename_mode = False
                st.rerun()
        with c2:
            if st.button("Cancel"):
                st.session_state.rename_mode = False
                st.rerun()

    st.sidebar.divider()

    # Persona
    persona_names = list(PERSONAS.keys())
    try:
        sel_index = persona_names.index(chat_doc.get("persona", "General"))
    except ValueError:
        sel_index = 0
    chat_doc["persona"] = st.sidebar.selectbox("Persona", persona_names, index=sel_index)

    # Model selector with safe suggestions + optional custom override
    st.sidebar.subheader("Model")
    suggested_label = None
    current_model = chat_doc.get("model", DEFAULT_MODEL)
    for label, mid in SUGGESTED_MODELS.items():
        if mid == current_model:
            suggested_label = label
            break
    label_list = list(SUGGESTED_MODELS.keys())
    if suggested_label is None:
        suggested_label = label_list[0]
    chosen_label = st.sidebar.selectbox("Suggested", label_list, index=label_list.index(suggested_label))
    suggested_model = SUGGESTED_MODELS[chosen_label]
    custom_model = st.sidebar.text_input(
        "Custom model ID (optional)",
        value=current_model if current_model not in SUGGESTED_MODELS.values() else "",
        placeholder="e.g., openai/gpt-4o-mini:free",
        help="Leave blank to use the suggested model above.",
    )
    final_model = custom_model.strip() or suggested_model
    if final_model != current_model:
        chat_doc["model"] = final_model
        save_chat(chat_doc)

    # Translation mode
    st.sidebar.subheader("Translation Mode")
    use_translate = st.sidebar.toggle("Enable translation", value=False)
    target_lang = st.sidebar.selectbox("Target language", TRANSLATE_TO, index=0)

    # Theme toggle (with fallback)
    try:
        theme = st.sidebar.segmented_control("Theme", ["Light", "Dark"], selection_mode="single", default=st.session_state.theme)
    except Exception:
        theme = st.sidebar.radio("Theme", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1)
    st.session_state.theme = theme

    # Session stats
    st.sidebar.subheader("Session Stats")
    elapsed = int(time.time() - st.session_state.start_ts)
    st.sidebar.write(f"Duration: {elapsed//60}m {elapsed%60}s")

    # Exports
    st.sidebar.subheader("Export")
    st.sidebar.download_button("Export TXT", export_txt(chat_doc), file_name=f"{chat_doc.get('title','New Chat')}.txt")
    st.sidebar.download_button("Export JSON", export_json(chat_doc), file_name=f"{chat_doc.get('title','New Chat')}.json")
    st.sidebar.download_button("Export CSV", export_csv(chat_doc), file_name=f"{chat_doc.get('title','New Chat')}.csv")

    return use_translate, target_lang


def main_panel(chat_doc: Dict[str, Any], use_translate: bool, target_lang: str):
    st.markdown(LIGHT_CSS if st.session_state.theme == "Light" else DARK_CSS, unsafe_allow_html=True)

    cols = st.columns([0.8, 0.2])
    with cols[0]:
        st.title(APP_TITLE)
        st.caption(f"Chat: **{chat_doc.get('title', 'New Chat')}**")
    with cols[1]:
        if st.button("🧹 Clear messages", use_container_width=True):
            chat_doc["messages"] = []
            save_chat(chat_doc)
            st.rerun()

    for m in chat_doc.get("messages", []):
        with st.chat_message("assistant" if m["role"]=="assistant" else "user"):
            st.markdown(m.get("content", ""))

    if prompt := st.chat_input("Type your message…"):
        # always store the user message
        chat_doc["messages"].append({"role": "user", "content": prompt})
        save_chat(chat_doc)

        if use_translate:
            # Translation mode: show structured block for the user's input
            with st.chat_message("assistant"):
                placeholder = st.empty()
                try:
                    res = translate_with_context(prompt, target_lang, chat_doc.get("model", DEFAULT_MODEL))
                    out_text = render_translation_block(res, target_language=target_lang)
                except Exception as e:
                    out_text = f"❌ Error (translation): {e}"
                placeholder.markdown(out_text)
        else:
            # Regular chat mode with streaming
            sys = {"role": "system", "content": persona_system(chat_doc.get("persona","General"))}
            messages = [sys] + chat_doc["messages"]
            with st.chat_message("assistant"):
                placeholder = st.empty()
                out_text = ""
                try:
                    for chunk in stream_chat_completion(messages, chat_doc.get("model", DEFAULT_MODEL)):
                        out_text += chunk
                        placeholder.markdown(out_text)
                except Exception as e:
                    out_text = f"❌ Error: {e}"
                    placeholder.markdown(out_text)

        chat_doc["messages"].append({"role": "assistant", "content": out_text})
        save_chat(chat_doc)
        maybe_auto_title(chat_doc)

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("🧠 Summarize conversation"):
        with st.status("Summarizing…"):
            res = summarize_conversation(chat_doc["messages"], DEFAULT_SUMMARY_MODEL)
        chat_doc["summaries"] = res
        save_chat(chat_doc)
    with c2.expander("Summaries", expanded=False):
        st.markdown("**Key Points**\n\n" + (chat_doc.get("summaries",{}).get("key_points","") or "_No summary yet._"))
        st.markdown("**Action Items**\n\n" + (chat_doc.get("summaries",{}).get("action_items","") or "_No action items yet._"))

# =============================
# ---- Lightweight Self Tests -
# =============================

def _run_self_tests():
    assert persona_system("Unknown") == PERSONAS["General"]
    assert persona_system("Analyst").startswith("You are a precise analyst")

    sample = {
        "title": "T",
        "persona": "General",
        "messages": [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
        ],
        "updated": "2020-01-01T00:00:00Z",
    }
    txt = export_txt(sample)
    assert "Title: T" in txt
    assert "[User] Hi" in txt and "[Assistant] Hello" in txt
    assert "\n" in txt
    joined = "\n".join(["A", "B", "C"])
    assert joined == "A\nB\nC"
    csv_out = export_csv(sample)
    assert csv_out.splitlines()[0].startswith("role,content,timestamp")

# =============================
# ---- Entry Point ------------
# =============================

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="💬", layout="wide")
    _require_api_key_or_stop()

    init_session()
    doc = load_chat(st.session_state.chat_id)
    if not doc:
        st.session_state.chat_id = create_chat("New Chat")
        doc = load_chat(st.session_state.chat_id)
    use_translate, target_lang = sidebar(doc)
    main_panel(doc, use_translate, target_lang)

if os.getenv("RUN_SELF_TESTS") == "1":
    _run_self_tests()

if __name__ == "__main__":
    main()
