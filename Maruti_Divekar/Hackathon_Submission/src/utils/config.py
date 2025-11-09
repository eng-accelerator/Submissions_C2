from __future__ import annotations
import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any

ROOT = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(ROOT, '.env'))

def load_settings(path: str = None) -> Dict[str, Any]:
    cfg_path = path or os.path.join(ROOT, 'config', 'settings.yaml')
    if os.path.exists(cfg_path):
        with open(cfg_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    # fallback defaults
    return {
        'project': 'deep-researcher',
        'budgets': {'max_budget_usd_default': 2.0, 'max_tokens_default': 200000},
        'retrieval': {'chunk_size': 1200, 'chunk_overlap': 200, 'top_k': 8},
        'observability': {'enable_langsmith': False}
    }

def get_env(key: str, default: Any = None) -> Any:
    return os.getenv(key, default)
