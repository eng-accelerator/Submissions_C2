from __future__ import annotations
from typing import List, Dict, Any

class AnalystAgent:
    def __init__(self):
        pass

    def summarize_sources(self, passages: List[Dict[str,Any]]) -> Dict[str,Any]:
        summaries = []
        for p in passages:
            summaries.append({'id': p['id'], 'summary': p['text'][:800], 'url': p.get('url')})
        merged = ' '.join(s['summary'] for s in summaries[:5])
        return {'summaries': summaries, 'merged': merged}

    def detect_contradictions(self, summaries: List[Dict[str,Any]]) -> List[str]:
        contradictions = []
        keywords = ['no evidence','not associated','inconclusive','contradict']
        for s in summaries:
            text = s.get('summary','').lower()
            for k in keywords:
                if k in text:
                    contradictions.append(f"{s['id']}: {k}")
        return contradictions

    def claim_evidence_map(self, merged: str, passages: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
        claims = []
        for i, sent in enumerate(merged.split('.')[:6]):
            sent = sent.strip()
            if not sent:
                continue
            support = next((p for p in passages if p['text'].lower().find(sent[:30].lower())!=-1), passages[0] if passages else {'id':'', 'url':None})
            claims.append({'claim_id': f'c{i}', 'claim': sent, 'evidence': [{'id': support['id'], 'url': support.get('url')} ]})
        return claims
