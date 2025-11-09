"""
LLM Configuration Utility
Handles OpenRouter API setup for all agents
Optimized model selection based on agent cognitive load requirements
"""

import os
import logging
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# OpenRouter API endpoint
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_KEY")

# Optimized model configurations (OpenRouter format)
# Based on cognitive load analysis: match model capability to task requirements
# Format: provider/model-name (not openrouter/provider/model-name)
# Note: Model names may vary - check https://openrouter.ai/models for exact names
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "anthropic/claude-3-5-sonnet")
RETRIEVER_MODEL = os.getenv("RETRIEVER_MODEL", "openai/gpt-4o-mini")  # Fast, cheap (fetch URLs)
ANALYZER_MODEL = os.getenv("ANALYZER_MODEL", "anthropic/claude-3-5-sonnet")  # Strong reasoning (find patterns)
INSIGHT_MODEL = os.getenv("INSIGHT_MODEL", "openai/gpt-4o")  # Creative pattern matching (hypotheses)
REPORT_MODEL = os.getenv("REPORT_MODEL", "anthropic/claude-3-5-haiku")  # Fast formatting (output)

# Temperature configurations (task-specific)
TEMPERATURES = {
    "retriever": float(os.getenv("RETRIEVER_TEMPERATURE", "0.1")),   # Low: consistent formatting
    "analyzer": float(os.getenv("ANALYZER_TEMPERATURE", "0.5")),     # Medium: balanced reasoning
    "insight": float(os.getenv("INSIGHT_TEMPERATURE", "0.7")),       # High: creative pattern matching
    "report": float(os.getenv("REPORT_TEMPERATURE", "0.2")),         # Low: consistent formatting
}


def create_llm(model: str = None, temperature: float = 0.3, base_url: str = None, max_tokens: int = None) -> ChatOpenAI:
    """
    Create a ChatOpenAI instance configured for OpenRouter.
    Works with both OpenAI and Anthropic models through OpenRouter's unified API.
    
    Args:
        model: Model name (OpenRouter format, e.g., "openai/gpt-4o-mini")
        temperature: Temperature setting
        base_url: Optional custom base URL (defaults to OpenRouter)
        max_tokens: Optional max tokens for response
        
    Returns:
        ChatOpenAI instance or None if API key not configured
    """
    api_key = OPENROUTER_API_KEY
    
    # Validate API key
    if not api_key or api_key == "your_openrouter_key_here":
        logger.warning("OPEN_ROUTER_KEY not found. LLM will not be available.")
        logger.warning("Please set OPEN_ROUTER_KEY in your .env file. Get your key from: https://openrouter.ai/keys")
        return None
    
    # Clean API key (remove quotes and whitespace)
    api_key = api_key.strip().strip('"').strip("'")
    
    # Validate API key format (OpenRouter keys start with 'sk-or-')
    if not api_key.startswith('sk-or-'):
        logger.warning(f"OPEN_ROUTER_KEY format appears invalid. OpenRouter keys should start with 'sk-or-'")
        logger.warning(f"Current key starts with: {api_key[:10]}...")
        logger.warning("Please verify your API key at: https://openrouter.ai/keys")
        # Continue anyway in case format changes
    
    # Use provided model or default
    model_name = model or DEFAULT_MODEL
    
    # Use OpenRouter base URL if not specified
    base_url = base_url or OPENROUTER_BASE_URL
    
    try:
        llm_kwargs = {
            "model": model_name,
            "temperature": temperature,
            "openai_api_key": api_key,
            "openai_api_base": base_url,
            "default_headers": {
                "HTTP-Referer": "https://github.com/yourusername/multi-agent-researcher",  # Optional
                "X-Title": "Multi-Agent AI Deep Researcher"  # Optional
            }
        }
        
        if max_tokens:
            llm_kwargs["max_tokens"] = max_tokens
        
        llm = ChatOpenAI(**llm_kwargs)
        logger.info(f"LLM initialized with model: {model_name} (temperature: {temperature})")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        logger.error("Please check:")
        logger.error("1. OPEN_ROUTER_KEY is set correctly in .env file")
        logger.error("2. API key is valid and active at https://openrouter.ai/keys")
        logger.error("3. API key has sufficient credits")
        return None


def create_retriever_llm() -> ChatOpenAI:
    """Create LLM for Retriever agent (GPT-4o Mini - fast, cheap)."""
    return create_llm(
        model=RETRIEVER_MODEL,
        temperature=TEMPERATURES["retriever"]
    )


def create_analyzer_llm() -> ChatOpenAI:
    """Create LLM for Analyzer agent (Claude 3.5 Sonnet - strong reasoning)."""
    return create_llm(
        model=ANALYZER_MODEL,
        temperature=TEMPERATURES["analyzer"],
        max_tokens=2000
    )


def create_insight_llm() -> ChatOpenAI:
    """Create LLM for Insight agent (GPT-4o - creative pattern matching)."""
    return create_llm(
        model=INSIGHT_MODEL,
        temperature=TEMPERATURES["insight"],
        max_tokens=1500
    )


def create_report_llm() -> ChatOpenAI:
    """Create LLM for Report agent (Claude 3.5 Haiku - fast formatting)."""
    return create_llm(
        model=REPORT_MODEL,
        temperature=TEMPERATURES["report"],
        max_tokens=4000
    )


def is_llm_available() -> bool:
    """Check if LLM is available (API key configured)."""
    return OPENROUTER_API_KEY is not None and OPENROUTER_API_KEY != "your_openrouter_key_here"

