import os

# Load environment variables (python-dotenv is typically used for this)
# For Streamlit, os.getenv works directly if variables are set in the environment
# or if .streamlit/secrets.toml is used.

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter") # 'openrouter' or 'ollama'
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "openai/gpt-4o") # e.g., "llama3" for Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Other constants
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
