"""
Configuration management for Multi-Agent DevOps Incident Suite
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration for the application"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    LOGS_DIR = BASE_DIR / "uploaded_logs"
    KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
    VECTOR_STORE_DIR = BASE_DIR / "vector_stores"
    
    # API Keys - OpenRouter
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    USE_OPENROUTER = os.getenv("USE_OPENROUTER", "true").lower() == "true"
    
    # Fallback to OpenAI if needed
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "")
    JIRA_URL = os.getenv("JIRA_URL", "")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
    JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "OPS")
    
    # LangSmith
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "devops-incident-suite")
    
    # Model Settings
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
    MAX_TOKENS = 2000
    
    # Embedding Settings
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 5
    
    # Agent Settings
    MAX_AGENT_ITERATIONS = 5
    AGENT_TIMEOUT = 120  # seconds
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)
        cls.VECTOR_STORE_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate_api_key(cls, key: Optional[str] = None) -> bool:
        """Validate API key (OpenRouter or OpenAI)"""
        if cls.USE_OPENROUTER:
            key = key or cls.OPENROUTER_API_KEY
            return bool(key and len(key) > 20 and key.startswith("sk-"))
        else:
            key = key or cls.OPENAI_API_KEY
            return bool(key and len(key) > 20 and key.startswith("sk-"))
    
    @classmethod
    def get_api_key(cls) -> str:
        """Get the active API key"""
        if cls.USE_OPENROUTER:
            return cls.OPENROUTER_API_KEY
        return cls.OPENAI_API_KEY
    
    @classmethod
    def get_model_name(cls) -> str:
        """Get the active model name"""
        if cls.USE_OPENROUTER:
            return cls.OPENROUTER_MODEL
        return cls.DEFAULT_MODEL
    
    @classmethod
    def has_slack_integration(cls) -> bool:
        """Check if Slack is configured"""
        return bool(cls.SLACK_BOT_TOKEN and cls.SLACK_CHANNEL_ID)
    
    @classmethod
    def has_jira_integration(cls) -> bool:
        """Check if JIRA is configured"""
        return bool(cls.JIRA_URL and cls.JIRA_EMAIL and cls.JIRA_API_TOKEN)

# Initialize directories on import
Config.ensure_directories()

