import os
from langchain_openai import ChatOpenAI
from src.config import LLM_PROVIDER, LLM_MODEL_NAME, OLLAMA_BASE_URL

def initialize_llm(user_openrouter_api_key: str = None) -> ChatOpenAI:
    """Initializes and returns the ChatOpenAI instance based on configuration.
    User's OpenRouter API key takes precedence if LLM_PROVIDER is openrouter.
    """
    if LLM_PROVIDER == "ollama":
        return ChatOpenAI(
            base_url=f"{OLLAMA_BASE_URL}/v1", # Ollama's OpenAI-compatible endpoint
            api_key="ollama", # Dummy API key for Ollama's OpenAI-compatible endpoint
            model_name=LLM_MODEL_NAME,
            temperature=0.7 # Example temperature
        )
    elif LLM_PROVIDER == "openrouter":
        if not user_openrouter_api_key:
            raise ValueError("OpenRouter API key is required and not provided.")
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=user_openrouter_api_key,
            model_name=LLM_MODEL_NAME,
            temperature=0.7
        )
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")
