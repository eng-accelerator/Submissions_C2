# Plan for Challenge 1: Translation Mode

This document outlines the plan to implement the "Translation Mode" feature in the `chat-challenge-1.py` file, as described in the challenge brief.

### Primary Goal

The objective is to transform the single-response chatbot into a two-stage translation assistant. The application will intercept a user's prompt, process it through two sequential AI calls (first for language detection, then for translation), and return a structured, informative response.

---

### Step 1: UI Enhancement: Add Target Language Selection

- **Location**: The main sidebar (`with st.sidebar:`).
- **Action**: Introduce a `st.selectbox` widget under the "Settings" section. This will allow the user to choose their desired target language for translation.
- **State Management**: The selected language will be stored in `st.session_state.target_language`. This variable will be initialized with a default value (e.g., "English") in the "SESSION STATE INITIALIZATION" block of the script.

### Step 2: Refactor the Main Chat Logic

The core of the work will be to replace the current single-API-call logic within the `if prompt := st.chat_input(...)` block with a new two-stage process.

#### Stage 2a: Language Detection

1.  **System Prompt**: A new, highly specific system prompt will be created solely for language detection. It will instruct the model to respond with *only* the name of the language.
    - *Example Prompt*: `"You are a language detection expert. Respond with ONLY the name of the language in the user's text (e.g., 'French', 'Spanish')."`
2.  **First API Call**: A non-streaming API call will be made to the LLM using this detection prompt and the user's input.
3.  **Process & Display**: The detected language will be captured from the model's response and immediately displayed to the user (e.g., using `st.write("🔍 Detected Language: French")`).

#### Stage 2b: Translation and Context

1.  **Conditional Logic**: A check will be implemented to determine if the detected language is the same as the target language. If they match, the bot will notify the user and skip the translation step.
2.  **System Prompt**: A second, more detailed system prompt will be engineered for the translation task. This prompt will instruct the model to act as an expert translator and to structure its response with the specific prefixes from the challenge brief (`🎯 Translation:`, `💡 Cultural Note:`, `🌟 Alternative:`).
3.  **Second API Call**: Another non-streaming API call will be made using this new translation prompt, the user's input, and the `target_language` from session state.
4.  **Display Formatted Response**: The model's complete, structured response will be displayed to the user within the assistant's chat message.

### Step 3: State and History Management

- **Chat History**: The existing `st.session_state.messages` list will be used to store the conversation. The user's raw input and the final, formatted translation output from the assistant will be appended to this list, automatically fulfilling the "Translation History" requirement.
- **Persistence**: The existing `save_chat` function will continue to work as-is, saving the entire conversation history, including the structured translation results, to the JSON file.
