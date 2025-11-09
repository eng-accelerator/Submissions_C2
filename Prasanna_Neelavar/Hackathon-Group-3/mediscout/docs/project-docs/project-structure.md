# Project Structure & Setup Guide

> This document outlines the proposed directory structure, dependency management, and configuration strategy for the Multi-agent AI Deep Researcher project.

---

## 1. Project Directory Structure

The project will follow a standard `src` layout to keep application code separate from project configuration files.

```
/AI-Accelerator-C2-Hackathon-Group-3/
├── .gitignore
├── .env
├── .env.example
├── main.py
├── pyproject.toml
├── README.md
├── docs/
│   └── ...
├── data/
│   └── chromadb/  # Persisted ChromaDB data will be stored here
└── src/
    ├── __init__.py
    ├── config.py          # Handles environment variables and DEV/DEMO switching
    ├── knowledge_base.py  # Manages file ingestion and the ChromaDB vector store
    ├── orchestrator.py    # Defines the LangGraph state and graph
    ├── agents/
    │   ├── __init__.py
    │   ├── base_agent.py      # Abstract base class for all agents
    │   ├── retriever_agent.py
    │   ├── analysis_agent.py
    │   ├── insight_agent.py
    │   └── report_agent.py
    └── services/
        ├── __init__.py
        └── external_apis.py # Clients for PubMed, openFDA, ClinicalTrials.gov, and Google Scholar
```

- **`main.py`**: The entry point for the Streamlit application.
- **`pyproject.toml`**: Defines project metadata and dependencies for `uv`.
- **`.env` / `.env.example`**: Manages environment variables and secrets.
- **`data/`**: A directory for all persistent data, such as the vector store. This directory should be added to `.gitignore`.
- **`src/config.py`**: A crucial file for managing settings. It will read from `.env` and expose configuration variables to the rest ofthe application.
- **`src/` subdirectories**: Code is organized by function: `agents` for agent logic, `services` for external API clients, etc.

## 2. Dependency Management with `uv`

We will use `uv` as our package manager for its speed. All dependencies will be listed in the `pyproject.toml` file.

### Required Libraries (`pyproject.toml`)

```toml
[project]
name = "multi-agent-ai-deep-researcher"
version = "0.1.0"
dependencies = [
    # Core Frameworks
    "streamlit",
    "langgraph",
    "langchain",
    "langchain_openai",
    "langchain_community",

    # Vector Store & Data Handling
    "chromadb",
    "pypdf",
    "unstructured[local-inference]", # For robust document parsing

    # Configuration & API Clients
    "python-dotenv",
    "httpx", # Modern async-capable HTTP client
    "openai", # For OpenAI SDK compatibility with OpenRouter/Ollama
    "ollama",
    "fastapi",
    "uvicorn",
    "nomic"
]
```

## 3. Environment & Configuration (`DEV` vs. `DEMO`)

To seamlessly switch between local models (DEV) and managed models (DEMO), we will use a combination of an environment variable and a configuration script.

### a. Environment File (`.env.example`)

Create a `.env.example` file in the root directory. Users will copy this to `.env` and fill in their secrets.

```ini
# The API key for OpenRouter or another managed service.
# Not required for local Ollama-only development.
OPENROUTER_API_KEY="your_openrouter_api_key_here"

# The active environment. Can be "DEV" or "DEMO".
# DEV: Uses local Ollama instance.
# DEMO: Uses OpenRouter API.
APP_ENV="DEV"
```

### b. Configuration Logic (`src/config.py`)

This script will be the single source of truth for all configurations. It will read the `.env` file and set up the appropriate LLM client based on the `APP_ENV` variable.

```python
# src/config.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# --- General Settings ---
APP_ENV = os.getenv("APP_ENV", "DEV") # Default to DEV if not set

# --- LLM Client Configuration ---
class LLMClient:
    def __init__(self):
        self.client = None
        self.embedding_model = ""
        self.fast_model = ""
        self.heavy_model = ""
        self._configure_client()

    def _configure_client(self):
        if APP_ENV == "DEMO":
            # Configuration for DEMO using OpenRouter
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY")
            )
            self.embedding_model = "nomic-ai/nomic-embed-text-v1.5"
            self.fast_model = "mistralai/mistral-7b-instruct"
            self.heavy_model = "openai/gpt-4o"
            print("Running in DEMO mode. Using OpenRouter.")

        elif APP_ENV == "DEV":
            # Configuration for DEV using local Ollama
            self.client = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama" # Required placeholder
            )
            # Make sure you have pulled these models with `ollama pull <model_name>`
            self.embedding_model = "nomic-embed-text"
            self.fast_model = "mistral"
            self.heavy_model = "llama3"
            print("Running in DEV mode. Using local Ollama.")
        else:
            raise ValueError(f"Invalid APP_ENV: {APP_ENV}. Must be 'DEV' or 'DEMO'.")

# Instantiate a single, shared client configuration
llm_config = LLMClient()

# --- Expose the configured client and model names ---
llm_client = llm_config.client
EMBEDDING_MODEL = llm_config.embedding_model
FAST_MODEL = llm_config.fast_model
HEAVY_MODEL = llm_config.heavy_model

# Example of how to use in another file:
# from src.config import llm_client, FAST_MODEL
# response = llm_client.chat.completions.create(model=FAST_MODEL, ...)
```

## 4. Installation Command

With `uv` installed and the `pyproject.toml` file in place, you can install all required dependencies with a single command from the project root:

```bash
uv pip install -e .
```
*The `-e .` flag installs the project in "editable" mode, which is best practice for development as it makes your `src` directory available on the Python path.*
