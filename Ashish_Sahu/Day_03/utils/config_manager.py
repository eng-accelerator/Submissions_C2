import json
import os
from typing import Dict, Any

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": "",
        "mini_model": "openai/gpt-4o-mini",
        "thinking_model": "openai/o1-mini",
        "multimodal_model": "openai/gpt-4o"
    },
    "ollama": {
        "endpoint": "http://localhost:11434",
        "mini_model": "llama3.2:3b",
        "thinking_model": "llama3.2:70b",
        "multimodal_model": "llava"
    },
    "settings": {
        "temperature": 0.7,
        "max_tokens": 2000,
        "custom_instructions": "",
        "provider": "openrouter",
        "mode": "mini"
    }
}

def load_config() -> Dict[str, Any]:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return {**DEFAULT_CONFIG, **config}
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> bool:
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_active_model(config: Dict[str, Any], has_files: bool) -> str:
    provider = config['settings']['provider']
    mode = config['settings']['mode']

    if has_files or mode == 'multimodal':
        model_key = 'multimodal_model'
    elif mode == 'thinking':
        model_key = 'thinking_model'
    else:
        model_key = 'mini_model'

    return config[provider][model_key]

def get_provider_config(config: Dict[str, Any]) -> Dict[str, Any]:
    provider = config['settings']['provider']
    return config[provider]
