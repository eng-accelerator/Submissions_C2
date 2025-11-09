# config.py
# Configuration file for AI Financial Coach

import os
from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).parent

# Database Configuration
DATABASE_CONFIG = {
    # Default: SQLite (for demo/development)
    'connection_string': os.getenv(
        'DATABASE_URL', 
        f'sqlite:///{PROJECT_ROOT}/financial_data.db'
    ),
    
    # For production, use PostgreSQL:
    # 'connection_string': 'postgresql://user:password@localhost:5432/financedb'
}

# Vector Database Configuration
VECTOR_DB_PATH = PROJECT_ROOT / "knowledge_db"

# API Keys (set in environment variables or .streamlit/secrets.toml)
API_KEYS = {
    'openai': os.getenv('OPENAI_API_KEY', ''),
    'tavily': os.getenv('TAVILY_API_KEY', ''),  # Optional: for web search
}

# File Upload Limits
UPLOAD_LIMITS = {
    'max_file_size_mb': 20,
    'allowed_extensions': {
        'transactions': ['.csv', '.xlsx', '.xls', '.pdf'],
        'knowledge': ['.pdf']
    }
}

# Financial Settings
FINANCIAL_CONFIG = {
    'currencies': {
        'India': 'INR',
        'United States': 'USD',
        'United Kingdom': 'GBP',
        'Singapore': 'SGD',
        'UAE': 'AED'
    },
    'default_country': 'India',
    'default_currency': 'INR'
}

# LLM Configuration
LLM_CONFIG = {
    'model': 'gpt-4o-mini',
    'temperature': 0.3,
    'max_tokens': 2000
}

# Embedding Configuration
EMBEDDING_CONFIG = {
    'model': 'text-embedding-3-small',
    'chunk_size': 1000,
    'chunk_overlap': 200
}
