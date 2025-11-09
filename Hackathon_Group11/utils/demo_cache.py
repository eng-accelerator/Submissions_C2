"""
Demo caching utilities for hackathon presentation
"""

import json
import os
from typing import Dict, Any, Optional

DEMO_CACHE_FILE = "demo_cache.json"


def load_demo_cache() -> Dict[str, Any]:
    """Load demo cache from file."""
    if os.path.exists(DEMO_CACHE_FILE):
        try:
            with open(DEMO_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading demo cache: {e}")
            return {}
    return {}


def save_demo_cache(cache: Dict[str, Any]):
    """Save demo cache to file."""
    try:
        with open(DEMO_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving demo cache: {e}")


def get_cached_result(query_key: str) -> Optional[Dict[str, Any]]:
    """Get cached result for a query key."""
    cache = load_demo_cache()
    return cache.get(query_key)


def cache_result(query_key: str, result: Dict[str, Any]):
    """Cache a result for a query key."""
    cache = load_demo_cache()
    cache[query_key] = result
    save_demo_cache(cache)

