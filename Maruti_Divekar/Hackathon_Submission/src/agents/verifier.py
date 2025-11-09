from __future__ import annotations
from typing import List, Dict, Any

class VerifierAgent:
    def __init__(self):
        pass

    def verify_claims(self, claims: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
        verified = []
        for c in claims:
            evid = c.get('evidence', [])
            if evid and evid[0].get('id') and evid[0].get('url'):  # Check both id and url exist
                c['verified'] = True
            else:
                c['verified'] = False
                reason = 'No supporting citation found' if not evid else 'Missing URL in citation'
                c.setdefault('notes', []).append(reason)
            verified.append(c)
        return verified

    def remove_unsupported(self, claims: List[Dict[str,Any]], keep_unsupported: bool = False) -> List[Dict[str,Any]]:
        if keep_unsupported:
            return claims
        return [c for c in claims if c.get('verified')]
