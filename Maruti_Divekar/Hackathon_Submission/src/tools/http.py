from __future__ import annotations
import requests
from typing import Any, Dict

def get_json(url: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None, json: Dict[str, Any] = None, timeout: int = 10, method: str = "GET"):
    try:
        if method == "GET":
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        else:
            resp = requests.post(url, params=params, json=json, headers=headers, timeout=timeout)
        resp.raise_for_status()
        try:
            return resp.json()
        except Exception:
            return {'text': resp.text}
    except requests.exceptions.RequestException as e:
        # Return error info instead of raising to keep callers robust
        return {'error': str(e), 'status_code': getattr(e.response, 'status_code', None)}
