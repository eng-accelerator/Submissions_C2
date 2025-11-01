# Plan for Challenge 2: Personality Selector

This document outlines the plan to implement the "Personality Selector" feature in the `chat-challenge-2.py` file.

### Primary Goal

The objective is to modify the chatbot to include multiple personalities that the user can select. The bot's responses should reflect the tone, style, and expertise of the chosen personality. This will be achieved by dynamically altering the system prompt sent to the AI model based on user selection.

---

### Step 1: Define Personalities and System Prompts

- **Action**: Create a Python dictionary to act as a central repository for all available personalities and their detailed system prompts.
- **Location**: This dictionary will be defined near the top of the `chat-challenge-2.py` script for easy configuration.
- **Details**:

  - **1. Professional Business Assistant**
    - **Name**: `Professional Business Assistant`
    - **System Prompt**:
      > "You are a highly skilled business assistant. Your communication style is formal, structured, and always professional. You are an expert in business strategy, project management, and clear, effective communication. Your goal is to provide users with actionable, efficient, and results-oriented advice. When responding, use structured formats like lists or numbered steps where appropriate. Maintain a polite and methodical tone at all times."

  - **2. Creative Writing Helper**
    - **Name**: `Creative Writing Helper`
    - **System Prompt**:
      > "You are an imaginative and inspiring creative writing coach. Your expertise lies in storytelling, brainstorming, and artistic expression. Your communication style is expressive, enthusiastic, and encouraging. Use vivid language, metaphors, and an artistic tone to spark creativity in the user. Your goal is to help users overcome creative blocks, develop their ideas, and feel inspired to create."

  - **3. Technical Expert**
    - **Name**: `Technical Expert`
    - **System Prompt**:
      > "You are a precise and knowledgeable technical expert. Your specialty is programming, software architecture, and complex problem-solving. Your responses should be detailed, analytical, and methodical. When explaining technical concepts, be clear and educational. Provide code snippets, step-by-step instructions, and logical reasoning. Your primary goal is to deliver accurate, in-depth technical solutions and explanations."

  - **4. Friendly Companion**
    - **Name**: `Friendly Companion`
    - **System Prompt**:
      > "You are a warm, empathetic, and friendly companion. Your expertise is in providing supportive, casual conversation and general life advice. Your tone should always be encouraging and understanding. You are a great listener and offer a safe space for users to express themselves. Your goal is to be a positive and comforting presence."

### Step 2: Implement UI Controls and State Management

- **UI Enhancement**: Add a `st.selectbox` widget to the sidebar under the "⚙️ Settings" section. This will serve as the personality selector for the user.
- **State Management**: 
    - Create a new session state variable, `st.session_state.personality`, to track the currently selected personality.
    - Initialize this variable in the "SESSION STATE INITIALIZATION" block with a default value (e.g., "Friendly Companion").

### Step 3: Dynamic System Prompt Injection

This is the core logic change for the challenge.

- **Location**: The modification will occur within the `if prompt := st.chat_input(...)` block, just before the `client.chat.completions.create` API call.
- **Action**:
    1.  Retrieve the currently selected personality name from `st.session_state.personality`.
    2.  Use this name to look up the corresponding system prompt from the personalities dictionary defined in Step 1.
    3.  Construct a system message object: `{"role": "system", "content": system_prompt}`.
    4.  **Prepend** this system message to the list of existing messages (`st.session_state.messages`) before sending the payload to the API. This ensures the personality-defining prompt is always the first instruction the model receives.

### Step 4: Add a Visual Indicator for the Current Personality

- **Action**: To meet the requirement of showing the current personality, I will add a visual indicator in the main chat interface.
- **Location**: A `st.caption` or similar element will be placed directly below the main `st.title` to display the active personality (e.g., `Responding as: Creative Writing Helper`).

### Summary of Implementation Flow

1.  Define the personality data (names and prompts) in a dictionary.
2.  Add the necessary session state variable and the UI selector in the sidebar.
3.  Modify the API call logic to dynamically insert the correct system prompt based on the session state.
4.  Add a label to the UI to make the current state clear to the user.

This plan systematically addresses all the core requirements of the challenge by adding the necessary UI controls, managing the state, and dynamically injecting context into the AI model interaction.
