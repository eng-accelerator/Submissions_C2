from __future__ import annotations
import json
import os
import logging
from typing import Any, Dict
from .config import get_env

REDACT_KEYS = get_env('REDACT_KEYS', 'true').lower() in ('1','true','yes')

class JSONLogger:
    def __init__(self, name: str = 'deep-researcher'):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _redact(self, d: Dict[str, Any]) -> Dict[str, Any]:
        if not REDACT_KEYS:
            return d
        out = {}
        for k, v in d.items():
            if 'key' in k.lower() or 'token' in k.lower() or 'secret' in k.lower():
                out[k] = '[REDACTED]'
            else:
                out[k] = v
        return out

    def info(self, **kwargs):
        print(json.dumps(self._redact(kwargs), ensure_ascii=False))
