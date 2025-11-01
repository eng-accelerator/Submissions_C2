# Streamlit AI Chat Application

This repository contains a full-featured AI chat application built with Streamlit. The project evolves from a basic prototype to a multi-mode application through a series of distinct challenges, demonstrating various techniques for building sophisticated AI-powered apps.

## Final Features

- **Multi-Mode Operation**: Switch between a conversational assistant and a specialized translator.
- **AI Personalities**: In Conversation Mode, choose from multiple AI personas (e.g., Friendly, Technical, Business) that change the bot's tone and expertise.
- **Translation Service**: In Translation Mode, the app automatically detects the input language and translates it to a user-selected target language, providing cultural context.
- **Persistent Chat History**: Conversations are automatically saved and can be reloaded, managed, and deleted through the sidebar.
- **Stateful Summarization**: Generate and view a concise summary of the current conversation.
- **Multi-Format Export**: Download the current chat history as a TXT, JSON, or CSV file, complete with metadata and statistics.
- **Light/Dark Mode**: Toggle between light and dark themes.

---

### Project Evolution

The application was built iteratively, with each major step saved as a separate source file to document the development process.

1.  **`src/chat.py` - The Functional Baseline**: This file established the core pattern for a functional, streaming chatbot with a real connection to a language model. It served as the foundation for subsequent challenges.

2.  **`src/chat-challenge-1.py` - Translation Mode**: The first challenge transformed the bot into a translation utility. This was achieved by implementing a two-stage AI pipeline: a first call to detect the language and a second call to perform the translation with cultural context.

3.  **`src/chat-challenge-2.py` - Personality Selector**: The second challenge focused on dynamic system prompts. A `PERSONALITIES` dictionary was created, and the application was modified to prepend a specific system prompt to the AI call based on the user's selection, allowing the bot to adopt different personas.

4.  **`src/chat-challenge-3.py` - Export Functionality**: The third challenge added a comprehensive, multi-format export feature. This involved writing data transformation functions to convert the chat history into TXT, JSON, and CSV formats. A critical part of this challenge was augmenting the data model to include a timestamp for every message and gracefully handling older chat files that lacked this information.

5.  **`src/full-feature-chat.py` - The Final Application**: This file merges all the features from the previous steps into a single, cohesive application. It introduces a primary **Mode Switch** ("Conversation" vs. "Translation") to manage the conflicting chat behaviors and conditionally displays the relevant UI controls for each mode.

### Planning Process

The project's inception was guided by a visual design mock-up, available at `docs/0_screenshot-input.png`. This image was systematically analyzed to deconstruct its components and infer the necessary features. This analysis led to the creation of the initial Product Requirements Document (`docs/1_prd.md`), which translated the visual design into a structured list of technical and functional requirements. This PRD served as the foundational blueprint for the project.

Furthermore, each subsequent challenge was preceded by its own detailed implementation plan, which can be found in the `docs/plans/` directory. This approach ensured that every feature was thoughtfully designed and integrated.


---

## Getting Started

Follow these instructions to set up and run the application on your local machine.

### Prerequisites

- Python 3.8+
- `uv` - A fast Python package installer and resolver. If you don't have it, you can install it with `pip install uv`.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd streamlit-chat
```

### 2. Set Up The Virtual Environment

Using `uv` is recommended for its speed.

```bash
# Create the virtual environment
uv venv

# Activate the environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

All required packages are listed in the `pyproject.toml` file.

```bash
# Install the dependencies
uv pip install -e .
```

### 4. Configure API Secrets

The application needs API credentials to connect to a language model. A template is provided.

1.  **Create the secrets file**: Make a copy of the example file and place it in the `.streamlit` directory.

    ```bash
    cp secrets.example.toml .streamlit/secrets.toml
    ```

2.  **Edit the secrets file**: Open `.streamlit/secrets.toml` and configure it for your setup. 

    - **`USE_HOST`**: Set this to either `"openrouter"` or `"ollama"` depending on which service you want to use.
    - **`[openrouter]`**: If using OpenRouter, paste your API key into the `API_KEY` field.
    - **`[ollama]`**: If using a local Ollama server, ensure the `BASE_URL` is correct (the default is usually fine) and set `MODEL_NAME` to the local model you wish to use.

### 5. Run the Application

Once the setup is complete, you can run the full-featured application.

```bash
streamlit run src/full-feature-chat.py
```

Navigate to the URL provided by Streamlit (usually `http://localhost:8501`) in your browser to use the app.
