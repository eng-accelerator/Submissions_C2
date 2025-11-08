import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM Configuration - CHANGE THESE BASED ON YOUR LLM PROVIDER
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # Options: openai, anthropic, local
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Model Configuration
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")
    
    # API Configuration
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    # Output Configuration
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./reports")
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI")
        elif cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic")