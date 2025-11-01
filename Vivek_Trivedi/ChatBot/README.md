## **Role:**
You are **GPT-5 Thinking**, my senior full‑stack AI engineer and Streamlit specialist. Act as my hands-on pair‑programmer to build and polish a **ChatGPT‑like app in Streamlit** that uses **OpenRouter (OpenAI‑compatible API)**, persists multi‑chat history, and implements three challenges:
- **Challenge 1 — Translation Mode (Intermediate)**
- **Challenge 2 — Personality Selector (Beginner–Intermediate)**
- **Challenge 3 — Export Functionality (Intermediate–Advanced)**

Deliver production‑quality, well‑structured, *ready‑to‑run* code and UX with careful state management. Do all work in one reply.

---

## **Objective:**
Ship a single‑file Streamlit app **`app.py`** (plus `requirements.txt` and `.streamlit/secrets.toml` schema) that:
- Connects to **OpenRouter** via the OpenAI‑compatible SDK  
  `OpenAI(base_url="https://www.openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"], default_headers={"HTTP-Referer": "http://localhost:8501", "X-Title": "My ChatBot"})`.
- Supports **multiple conversations with persistent storage** under **`chat-history/`** (one JSON file per chat), sorted by `updated` (newest first).
- Provides a refined **left sidebar** with:
  - **➕ New chat** button.
  - **Plain, aligned chat history list** (title left, 🗑️ delete icon right, no layout jump on rename, click to select).
  - **Mode switch**: *Standard* / *Translation*.
  - **Target language selector** (for Translation Mode).
  - **Direction toggle**: *Auto/Bidirectional* vs *Source → Target*.
  - **Personality selector** with ≥4 presets + **Custom**, visible active persona badge.
  - **Export controls**: choose TXT / JSON / CSV, optional date range & role filter, download via `st.download_button`.
- Main chat area with **Streamlit Chat UI**:
  - Renders history using `st.chat_message("user"|"assistant")`.
  - `st.chat_input("Ask or paste text…")` for sending messages.
  - Streams assistant responses live; maintains context across turns and app reloads.
  - In **Translation Mode**, shows blocks: **Detected Language**, **Translation (→ target)**, **Alternatives**, **Cultural/Regional note**, **Confidence**.
- Robust error handling: **any exception text appears in a dedicated “Output / Errors” textbox** in the main area (no silent failures; do not promise background/asynchronous work).

---

## **Context:**
**Repository / Files**
- `app.py` — full Streamlit application (single file; provide complete code).
- `requirements.txt` — minimal pinned versions (Streamlit, openai, python-slugify, python-dateutil, pandas).
- `.streamlit/secrets.toml` — contains:
  ```toml
  OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"
  ```
- `chat-history/` — local folder for persistent conversations.

**Persistence Schema** (one file per chat `chat-history/<uuid>__<slug>.json`):
```json
{
  "id": "UUID",
  "title": "New chat",
  "created": "2025-10-30T12:34:56Z",
  "updated": "2025-10-30T12:35:30Z",
  "messages": [
    {"role":"system","content":"...", "ts":"2025-10-30T12:34:56Z", "tokens":0},
    {"role":"user","content":"Hi", "ts":"2025-10-30T12:35:01Z", "tokens":5},
    {"role":"assistant","content":"Hello!", "ts":"2025-10-30T12:35:03Z", "tokens":4}
  ],
  "meta": {
    "model": "openrouter/anthropic/claude-3.5-sonnet",
    "mode": "standard|translation",
    "target_language": "English",
    "last_detected_source": "French",
    "last_confidence": 0.92,
    "bidirectional": true,
    "previous_other_lang": "Spanish",
    "personality_key": "professional|creative|technical|friend|custom",
    "custom_persona": {"style":"", "expertise":"", "tone":""}
  }
}
```

**Sidebar Layout (plain list look & stable alignment)**
- Each chat row: `⦿ Title ……… 🗑️` (title left, trash on right; fixed height; no shift when entering rename mode).
- Inline rename uses a text input overlay of identical width so the row height/placement doesn’t change.

**Default Model**
- Use a dependable OpenRouter model such as `openrouter/anthropic/claude-3.5-sonnet` (allow switching to others like `openrouter/openai/gpt-4.1-mini`, `openrouter/meta-llama/llama-3.1-405b-instruct`).

---

## **Instructions:**

### **Instruction 1 — Base App (Streamlit + OpenRouter + Persistence)**
1. **Init & Client**
   - `st.set_page_config(page_title="ChatGPT-like via OpenRouter", page_icon="🤖", layout="wide")`.
   - Validate `OPENROUTER_API_KEY` in `st.secrets`; fail gracefully with message in the **Output / Errors** box.
   - Ensure `chat-history/` exists.

2. **Session State Keys**
   - `chat_id` — currently open chat UUID.
   - `messages` — list of `{role, content, ts, tokens}`.
   - `meta` — dict per schema (mode, target_language, personality_key, custom persona, model, bidirectional, last_detected_source, last_confidence, previous_other_lang).
   - `all_chats` — list of `{id, title, updated, path}` for sidebar.
   - `rename_mode` (bool), `rename_value` (str), `status_text` (str).

3. **System Prompt Builder**
   - Compose three layers:
     1) **Core guardrails** (concise, accurate; show errors when asked; never claim background/asynchronous work; refuse unsafe content; preserve formatting).
     2) **Personality block**: inject style/tone/expertise from selected persona or custom fields.
     3) **Mode block**:  
        - **Standard**: act as a helpful assistant; be brief by default; show code with triple backticks; avoid purple prose.  
        - **Translation**: use the translator spec in *Instruction 2*.

4. **Chat Lifecycle**
   - **New chat**: generate UUID; default title “New chat”; seed with system message from `system_prompt`; save file; focus input.
   - **Select chat**: load file → populate `messages` & `meta` → render.
   - **Rename**: switch row to inline text input; on confirm, update `title`, rename file (`<uuid>__<new-slug>.json`), keep `id`.
   - **Delete**: confirm, remove file; if current chat deleted, open most recent or create new.

5. **Sending & Streaming**
   - On `if prompt := st.chat_input("Ask or paste text…")`:
     - Append user message to `messages` with timestamp.
     - Prepare `messages_for_api = [system_prompt, *history, user]` (optionally trim by token budget).
     - Call `client.chat.completions.create(model=meta["model"], messages=messages_for_api, stream=True)`.
     - Stream deltas into an `st.chat_message("assistant")` container; accumulate full text; capture token usage if provided.
     - Append final assistant message; update `updated`; persist file.

6. **Persistence Helpers**
   - `save_chat(state)`, `load_chat(chat_id)`, `list_chats()` (sorted by `updated`), `slugify(title)`.
   - Autosave on any mutation.

7. **Error Handling**
   - Wrap API/file ops in `try/except`; write the full traceback to `status_text` and show it in an **Output / Errors** `st.text_area` beneath the chat.

---

### **Instruction 2 — Challenge 1: Translation Mode (Auto‑Detect, Bidirectional, Notes)**
1. **Two‑Stage Pipeline for Each User Turn**
   - **Stage A — Language Detection**: Ask the model to detect language and return **strict JSON**:
     ```json
     {"language_name":"French","language_code":"fr","confidence":0.92}
     ```
     - Save `language_name` to `meta["last_detected_source"]`, `confidence` to `meta["last_confidence"]`.
   - **Stage B — Decide Direction & Translate**:
     - If **Auto/Bidirectional** and `detected_code != target_code` → translate Detected → Target.
     - If **Auto/Bidirectional** and `detected_code == target_code` → translate Target → `previous_other_lang` if available; otherwise ask the user which language they want to translate *from* (and set `previous_other_lang`).
     - If **Source → Target** fixed → always translate from detected (or selected source) → target.
   - Produce a **single assistant message** containing structured blocks:
     - **🔍 Detected Language:** `Name (code) — Confidence: 0–1 or Low/Medium/High`  
     - **🎯 Translation (→ Target):** final translation string  
     - **🌟 Alternatives:** 1–3 concise alternatives (only if meaningful)  
     - **💡 Cultural/Regional Note:** short practical context (politeness/idioms/register)
   - Also append a compact **Translation History** entry in `messages` meta for later export (e.g., `{"pair":{"from":"fr","to":"en"},"confidence":0.92,"src":"…","tgt":"…","alts":["…"]}`).

2. **Translator System Prompt (use inside the system layer when mode=translation)**
   - Goals: detect source language, estimate confidence, translate to target, propose alternatives, add cultural/usage note, return clearly delimited sections.
   - Style: concise, accurate, no over‑explaining; preserve meaning, tone, register; do not hallucinate facts; mark uncertainties.
   - Output template (markdown):
     ```md
     🔍 **Detected Language:** <Name> (`<code>`) — *Confidence:* <0–1 or Low/Med/High>

     🎯 **Translation (→ <TargetName>):**
     <translated text>

     🌟 **Alternative translations (if relevant):**
     - <alt 1>
     - <alt 2>
     - <alt 3>

     💡 **Cultural / Regional note (if relevant):**
     <one short, useful note>
     ```

3. **Language Selection UI**
   - Sidebar selectbox for **Target language** (e.g., English, Spanish, French, German, Hindi, Japanese, etc.). Map to ISO codes.
   - Toggle for **Bidirectional (Auto)** vs **Source → Target**. When fixed, show a source selector.

4. **Confidence Display**
   - Show numeric confidence or a mapped label (≥0.85=High, 0.6–0.84=Medium, <0.6=Low) next to the detected language.

5. **Edge Cases**
   - Low confidence → ask user to confirm source language.
   - Non‑translatable input (code, numbers, URLs) → respond briefly and skip translation.
   - Preserve punctuation, emojis, and line breaks. Keep code blocks unchanged.

---

### **Instruction 3 — Challenge 2: Personality Selector (Presets + Custom)**
1. **Personas (at least 4 presets + Custom)**  
   - **professional** — Formal, structured, business‑focused; expertise: strategy, comms; tone: polite, efficient, results‑oriented.  
   - **creative** — Imaginative, expressive, inspiring; expertise: storytelling, content; tone: enthusiastic, artistic, encouraging.  
   - **technical** — Precise, detailed, code‑focused; expertise: programming, systems; tone: analytical, educational, step‑wise.  
   - **friend** — Casual, supportive, conversational; expertise: general chat; tone: warm, empathetic, upbeat.  
   - **custom** — User-specified `style`, `expertise`, `tone` (text inputs).

2. **Dynamic System Prompts**
   - Each persona defines its own style directives, formatting preferences, and guardrails.
   - Allow **mid‑conversation switching**; when persona changes, refresh the system prompt for subsequent turns while preserving prior history.

3. **UI & Persistence**
   - Sidebar dropdown for persona selection + short descriptions (tooltip or help text).
   - Top of main chat shows current persona badge (icon + name).  
   - Store `personality_key` and `custom_persona` in `meta` and persist per chat.

4. **Example Behavior**
   - *User:* “How do I handle a difficult client meeting?”  
     - **Professional:** numbered strategy steps, clear action items.  
     - **Creative:** metaphorical, vivid, motivational.  
     - **Technical:** root-cause analysis, checklists, structured plan.  
     - **Friend:** empathetic, conversational tips.

---

### **Instruction 4 — Challenge 3: Export Functionality (TXT / JSON / CSV)**
1. **Data Processing**
   - Convert `st.session_state.messages` into:
     - **TXT** (human‑readable transcript + metadata + stats).
     - **JSON** (structured `export_metadata`, `conversation[]`, `statistics`).
     - **CSV** (`Message_ID, Timestamp, Role, Content, Character_Count, Word_Count`).

2. **Metadata & Statistics**
   - Include: `export_timestamp`, `format_version`, `session_id`, `total_messages`, `session_duration_minutes`, `model`, `mode`, `target_language`, `personality_key`, `bidirectional`, `last_detected_source`, `last_confidence`.
   - Stats: `user_messages`, `assistant_messages`, `total_characters`, `average_message_length`.

3. **Download Interface**
   - `st.download_button` per chosen format; filenames like `chat_<slug>_<YYYYMMDD_HHMM>.txt|json|csv`.
   - Optional filters: date range and role (user/assistant/all).

4. **Formatting Rules**
   - **TXT**: human timestamps, separators, preserve markdown & line breaks.  
   - **JSON**: valid JSON; machine‑readable timestamps (ISO 8601).  
   - **CSV**: proper quoting for commas/quotes/newlines.

5. **Edge Cases**
   - Empty conversation → disable export with hint.  
   - Large files → build content in memory safely; avoid excessive RAM.  
   - Always handle exceptions and surface message in **Output / Errors** textbox.

---

## **Getting Started (Implementation Order)**
1. Copy your existing workshop chatbot to this structure.  
2. Implement **Base App (Instruction 1)**: page config, client, session state, persistence helpers, sidebar history (aligned list), chat loop with streaming + errors.  
3. Add **Mode switch** + **Target language** + **Direction toggle**.  
4. Implement **Translation Mode (Instruction 2)**: two‑stage detect → translate, cultural notes, alternatives, confidence & history.  
5. Add **Personality Selector (Instruction 3)** with dynamic system prompts and mid‑chat switching.  
6. Implement **Export (Instruction 4)** with TXT → JSON → CSV progression.  
7. Final polish: stable rename UX, active persona badge, tidy status/error box, model dropdown.

---

## **Example Interactions (for QA)**

**A) Translation Mode**
- **Input:** `Bonjour, comment allez-vous ?`  
  **Output:**  
  - 🔍 Detected Language: *French (fr)* — Confidence: High (≈0.95)  
  - 🎯 Translation (English): “Hello, how are you?”  
  - 🌟 Alternative: “Hi, how are you doing?”  
  - 💡 Cultural Note: Formal register; casual is “Salut, ça va ?”.

- **Input:** `I love this weather` (Target: Spanish, Auto/Bidirectional)  
  **Output:**  
  - 🔍 Detected Language: *English (en)* — Confidence: High  
  - 🎯 Translation (Spanish): “Me encanta este clima.”  
  - 🌟 Alternative: “Adoro este tiempo.” (more emphatic)  
  - 💡 Regional Note: In Mexico you might hear “Está padrísimo el clima.”

**B) Personality Selector**
- **Professional:** Provide 4‑step structured plan, crisp action items.  
- **Creative:** Vivid metaphors, inspiring tone, playful emojis allowed.  
- **Technical:** Step‑by‑step, precise, code blocks where relevant.  
- **Friend:** Warm, encouraging, simple language.

**C) Export**
- TXT example header:
  ```text
  Chat Export — 2024‑01‑15 14:55
  ========================================
  Session Information:
  - Total Messages: 12
  - Duration: 25 minutes
  - Model: openrouter/anthropic/claude-3.5-sonnet
  - Mode: translation (bidirectional)
  - Target Language: English
  - Last Detected Source: French (0.92)
  ----------------------------------------
  [14:30:15] You: Hello! How can I help you today?
  [14:30:22] Assistant: Hello! I'm here to help you…
  ```

---

## **Success Criteria**
- ✅ Automatically detects input language and shows confidence.
- ✅ Translates accurately to the selected target language.
- ✅ Supports **bidirectional** flow and remembers the previous other language.
- ✅ Provides **cultural/regional notes** and **alternative translations** when relevant.
- ✅ Maintains multi‑chat persistent history with stable, aligned sidebar list and inline rename.
- ✅ Exports clean **TXT/JSON/CSV** with metadata and statistics; supports optional filters.
- ✅ Handles all errors gracefully and displays them in the **Output / Errors** area.
- ✅ Clear, modern UI/UX using Streamlit chat primitives.

---

## **Notes:**
- No background/asynchronous claims — all work is performed within the current request/response cycle.
- Keep outputs concise in normal chat; expand detail when explicitly asked.
- Use safe content practices; refuse disallowed content with a brief explanation and safer alternatives where relevant.
- Preserve code blocks and formatting in translations; don’t hallucinate facts; mark uncertainties.
- Sidebar **chat history** must be a simple, clean list (no misaligned icons; no shifting on rename).
- Provide the complete `app.py`, `requirements.txt`, and example `.streamlit/secrets.toml` in your reply.
