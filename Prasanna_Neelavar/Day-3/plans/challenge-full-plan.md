# Plan for `full-feature-chat.py`

This document outlines the plan to merge all features from the previous challenges into a single, cohesive `full-feature-chat.py` application.

### Primary Goal

The objective is to create a single, master chat application that seamlessly integrates the distinct features from all challenges: a stateful summary, personality selection, a specialized translation mode, and multi-format exporting.

### Base File Selection

`chat-challenge-3.py` will be used as the foundational code. It is the most robust starting point because it already includes the critical feature of adding timestamps to every message and the graceful error handling for the export functions, which all other features will depend on.

---

### Step 1: Introduce a Global App Mode Switch

To resolve the conflict between the conversational "Personality Mode" and the utility-focused "Translation Mode", a global mode switch is necessary.

- **UI Control**: Add a `st.radio` or `st.toggle` to the sidebar to allow the user to select the application's primary mode: `"Conversation"` or `"Translation"`.
- **State Management**: Create a new session state variable, `st.session_state.app_mode`, initialized to `"Conversation"`.
- **Conditional Logic**: The main chat input logic (`if prompt := st.chat_input(...)`) will be wrapped in an `if/else` block that checks `st.session_state.app_mode`.
    - If the mode is `"Conversation"`, it will execute the personality-based chat logic.
    - If the mode is `"Translation"`, it will execute the two-stage, detect-and-translate logic.

### Step 2: Integrate Personality Mode (from Challenge 2)

This will be the default operational mode.

- **Copy Data**: The `PERSONALITIES` dictionary from `chat-challenge-2.py` will be copied into the new script.
- **Merge State & UI**: 
    - The `st.session_state.personality` variable will be added to the session state block.
    - The personality `selectbox` and the UI `caption` that displays the current personality will be added. The selectbox will be conditionally displayed only when `st.session_state.app_mode == "Conversation"`.
- **Merge Logic**: The core logic from Challenge 2—prepending the selected personality's system prompt to the message list before the API call—will be placed inside the `if st.session_state.app_mode == "Conversation"` block.

### Step 3: Integrate Translation Mode (from Challenge 1)

- **Merge State & UI**:
    - The `st.session_state.target_language` variable will be added.
    - The target language `selectbox` will be added to the sidebar and will be conditionally displayed only when `st.session_state.app_mode == "Translation"`.
- **Merge Logic**: The entire two-stage detection and translation logic from `chat-challenge-1.py` will be placed inside the `elif st.session_state.app_mode == "Translation"` block.

### Step 4: Consolidate and Verify

- **Session State**: All session state initializations from all files (`summary`, `personality`, `target_language`, `app_mode`, etc.) will be consolidated into a single, clean block.
- **Sidebar Organization**: The sidebar will be organized logically with clear sections for mode selection, settings (which will change dynamically based on the mode), and exporting.
- **Shared Features**: I will ensure that the universal features—like Summary and Export—function correctly regardless of which mode is active, as they all rely on the common `st.session_state.messages` structure.

### Final Application Structure

The resulting `full-feature-chat.py` will be a versatile application with a clear hierarchy:

1.  The user selects a primary **Mode** (Conversation or Translation).
2.  Based on the mode, **mode-specific settings** (Personality or Target Language) are displayed.
3.  The main chat logic executes the correct behavior based on the selected mode.
4.  **Universal features** (History, Summary, Export) are always available.
