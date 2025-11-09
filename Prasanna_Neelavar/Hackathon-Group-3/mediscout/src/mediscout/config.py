"""
Configuration management for MediScout.

Uses Pydantic Settings for type-safe environment variable handling.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Loads from .env file if present, otherwise uses defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ========================================================================
    # LLM Provider (OpenRouter)
    # ========================================================================
    openrouter_api_key: Optional[str] = Field(default=None, description="OpenRouter API key")
    openrouter_model: str = Field(
        default="meta-llama/llama-3.1-70b-instruct:free",
        description="Default LLM model to use",
    )
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=4000, ge=100, le=100000)
    llm_timeout_seconds: int = Field(default=15, ge=5, le=300)  # REDUCED for speed

    # ========================================================================
    # LangSmith (Optional tracing)
    # ========================================================================
    langsmith_api_key: Optional[str] = None
    langsmith_project: str = "mediscout-dev"
    langsmith_tracing: bool = False

    # ========================================================================
    # Vector Database (ChromaDB)
    # ========================================================================
    chroma_persist_dir: Path = Field(default=Path("./data/chroma"))
    chroma_collection_name: str = "mediscout_docs"

    # ========================================================================
    # Embedding Model (Local)
    # ========================================================================
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"  # or 'cuda'
    embedding_batch_size: int = Field(default=32, ge=1, le=256)
    embedding_dimension: int = 384  # For all-MiniLM-L6-v2

    # ========================================================================
    # External APIs
    # ========================================================================
    # PubMed
    pubmed_email: str = Field(
        default="user@example.com", description="Required by NCBI for API access"
    )
    pubmed_max_results: int = Field(default=10, ge=1, le=100)

    # ClinicalTrials.gov
    clinicaltrials_max_results: int = Field(default=5, ge=1, le=50)

    # Google Scholar (Optional)
    serpapi_key: Optional[str] = None
    serpapi_max_results: int = Field(default=5, ge=1, le=20)

    # ========================================================================
    # Logging
    # ========================================================================
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    log_file: Optional[Path] = Field(default=Path("./logs/mediscout.log"))

    # ========================================================================
    # Document Processing
    # ========================================================================
    chunk_size: int = Field(default=1000, ge=100, le=2000)  # INCREASED for fewer chunks
    chunk_overlap: int = Field(default=150, ge=0, le=500)
    max_document_size_mb: int = Field(default=50, ge=1, le=500)

    # ========================================================================
    # RAG Settings
    # ========================================================================
    top_k_results: int = Field(default=5, ge=1, le=100)  # REDUCED for faster search
    similarity_threshold: float = Field(default=0.3, ge=0.0, le=1.0)  # LOWERED for more results
    rerank_enabled: bool = True

    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap(cls, v: int, info: any) -> int:
        """Ensure chunk_overlap is less than chunk_size."""
        if "chunk_size" in info.data and v >= info.data["chunk_size"]:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return v

    @field_validator("chroma_persist_dir", "log_file")
    @classmethod
    def create_directories(cls, v: Optional[Path]) -> Optional[Path]:
        """Create directories if they don't exist."""
        if v is not None:
            v.parent.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def has_openrouter_key(self) -> bool:
        """Check if OpenRouter API key is configured."""
        return self.openrouter_api_key is not None and len(self.openrouter_api_key) > 0

    @property
    def has_langsmith_key(self) -> bool:
        """Check if LangSmith API key is configured."""
        return self.langsmith_api_key is not None and len(self.langsmith_api_key) > 0

    @property
    def langsmith_enabled(self) -> bool:
        """Check if LangSmith tracing is enabled and configured."""
        return self.langsmith_tracing and self.has_langsmith_key


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings (singleton pattern).

    Returns:
        Settings instance loaded from environment.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset settings (useful for testing)."""
    global _settings
    _settings = None

