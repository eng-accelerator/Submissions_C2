# agents/llm_client.py

import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet")


def llm_chat(system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str | None:
    """
    Generic chat completion wrapper.

    - No markdown stripping
    - No code-specific assumptions
    - Returns the model's raw text content (or None on failure)

    Callers are responsible for interpreting/cleaning the output.
    """
    if not OPENROUTER_API_KEY:
        return None

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": LLM_MODEL,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        choice = data.get("choices", [{}])[0]
        return choice.get("message", {}).get("content", "")
    except Exception:
        return None
