"""Critical Analysis Agent for in-depth content analysis."""
from __future__ import annotations
from typing import List, Dict, Any
import json
from src.utils.config import load_settings
from src.utils.llm import generate_text

SETTINGS = load_settings()

class CriticalAnalysisAgent:
    """Analyzes content for:
    - Key findings and summaries
    - Contradictions and conflicts
    - Source validation and credibility
    - Evidence strength assessment
    """
    def __init__(self, settings=None):
        self.settings = settings or SETTINGS
    
    def analyze_sources(self, passages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Quick analysis of source credibility and content. Optimized for performance."""
        analysis = {
            'summaries': [],  # Per-source key points
            'credibility': {},  # Credibility assessment
            'conflicts': [],  # Contradictions found
            'evidence': {},  # Evidence mapping
            'text': ''  # Plain-English report
        }
        
        # Skip empty results
        if not passages:
            analysis['text'] = 'No passages available for analysis.'
            return analysis
            
        # Group by source (skip empty/invalid)
        by_source = {}
        for p in passages:
            if not p.get('text', '').strip():
                continue
            source = p.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(p)
            
        # Process all sources at once
        for source, docs in by_source.items():
            # Get key points (fast)
            points = []
            for d in docs:
                text = d.get('text', '')
                sents = text.split('.')
                if sents:
                    points.append(sents[0].strip())
                    
            summary = ' '.join(points[:3])  # Take top 3 points
            analysis['summaries'].append({
                'source': source,
                'summary': summary[:500]  # Limit length
            })

            # Quick credibility check
            cred_score = self._assess_credibility(source, docs)
            analysis['credibility'][source] = {
                'score': round(cred_score, 2),
                'rationale': self._credibility_rationale(source, docs)
            }

            # Map core evidence 
            evidence = self._map_evidence(docs[:2])  # Limit to first 2 docs
            analysis['evidence'][source] = evidence

        # Find contradictions across sources
        analysis['conflicts'] = self._find_contradictions(analysis['summaries'])

    # Build a plain-English report text
        report_lines = []
        report_lines.append('Critical Analysis Report')
        report_lines.append('========================')
        for s in analysis['summaries']:
            report_lines.append(f"Source: {s['source']}")
            report_lines.append(s['summary'])
            cred = analysis['credibility'].get(s['source'], {})
            report_lines.append(f"Credibility: {cred.get('score', 'N/A')} - {cred.get('rationale','')}")
            ev = analysis['evidence'].get(s['source'], [])
            report_lines.append('Evidence:')
            for e in ev:
                report_lines.append(f" - {e.get('claim')}: {e.get('support')}")
            report_lines.append('')

        if analysis['conflicts']:
            report_lines.append('Conflicts identified:')
            for c in analysis['conflicts']:
                report_lines.append(f" - {c.get('description','')}")
        else:
            report_lines.append('No major conflicts identified across sources.')

        analysis['text'] = "\n".join(report_lines)

        # If an LLM is available, refine the plain-English analysis into
        # a concise, user-ready report in plain English.
        try:
            # Format source details for prompt
            source_details = []
            for s in analysis['summaries']:
                src = s['source']
                cred = analysis['credibility'].get(src, {})
                evid = analysis['evidence'].get(src, [])
                source_details.append(
                    f"Source: {src}\n"
                    f"Summary: {s['summary']}\n"
                    f"Credibility: {cred.get('score', 'N/A')}/1.0 - {cred.get('rationale','')}\n"
                    "Evidence:\n" +
                    '\n'.join(f"- {e.get('claim')}: {e.get('support')}" for e in evid)
                )
            
            # Format conflicts section
            conflicts_text = ''
            if analysis['conflicts']:
                conflicts_text = "Key Conflicts:\n" + '\n'.join(
                    f"- {c.get('description','')}" for c in analysis['conflicts']
                )
            else:
                conflicts_text = "No significant conflicts were identified between sources."
            
            # Build extractive summary directly from data (don't rely on LLM)
            lines = []
            
            # Structured multi-line (pointer-wise) critical analysis
            lines = []
            num_sources = len(analysis['summaries'])
            cred_scores = [score.get('score', 0) for score in analysis['credibility'].values()]
            avg_cred = sum(cred_scores) / len(cred_scores) if cred_scores else 0.5

            lines.append(f"Analyzed: {num_sources} source(s)")
            lines.append(f"Average credibility: {avg_cred:.2f}/1.0")

            # Key findings (max 2)
            top_findings = []
            for s in analysis['summaries'][:2]:
                summary = s.get('summary', '').strip()
                if summary:
                    first_sent = summary.split('.')[0].strip()
                    if first_sent:
                        top_findings.append(first_sent)
            if top_findings:
                lines.append(f"Key finding: {top_findings[0]}")
                if len(top_findings) > 1:
                    lines.append(f"Additional finding: {top_findings[1]}")

            # Credibility assessment line
            if avg_cred > 0.7:
                lines.append("Credibility assessment: High overall reliability; sources largely authoritative.")
            elif avg_cred > 0.4:
                lines.append("Credibility assessment: Moderate reliability; independent verification recommended.")
            else:
                lines.append("Credibility assessment: Low reliability; treat claims with caution and seek peer-reviewed confirmation.")

            # Conflicts line(s)
            if analysis['conflicts']:
                lines.append("Conflicts detected:")
                for c in analysis['conflicts'][:2]:
                    desc = c.get('description', '').replace('Conflicting claims: ', '')
                    lines.append(f" - {desc}")
            else:
                lines.append("Conflicts detected: None identified across analyzed sources.")

            analysis['text'] = '\n'.join(lines)
        except Exception:
            # On any LLM failure, keep the heuristic text
            pass

        return analysis
    
    def _summarize_source(self, docs: List[Dict[str, Any]]) -> str:
        """Create a focused summary of source content."""
        combined = "\n".join(d.get('text', '') for d in docs)
        prompt = (
            "As a skilled research analyst, summarize the following content in 4-5 clear sentences. "
            "Focus on key findings, methodology, and main conclusions. Use objective language and cite "
            "specific evidence when available.\n\nContent to summarize:\n" + combined
        )
        try:
            summary = generate_text(prompt, max_tokens=400)
            if summary:
                return summary
        except Exception:
            # Fall back to heuristic: first 800 chars, cleaned
            text = combined.strip().replace('\n', ' ')
            summary = (text[:800] + '...') if len(text) > 800 else text
            return f"Based on {len(docs)} analyzed passages, the key findings are: {summary}"
    
    def _assess_credibility(self, source: str, docs: List[Dict[str, Any]]) -> float:
        """Score source credibility (0-1)."""
        # Would check:
        # - Domain authority
        # - Citation count
        # - Publication date
        # - Author credentials
        s = source.lower()
        score = 0.5
        if 'nature' in s or 'jama' in s or 'nejm' in s:
            score = 0.95
        elif 'arxiv' in s or 'doi' in s or 'springer' in s:
            score = 0.85
        elif s.startswith('http') and ('blog' in s or 'medium' in s):
            score = 0.4
        elif s.startswith('file://') or s.endswith('.pdf'):
            score = 0.7
        return float(score)

    def _credibility_rationale(self, source: str, docs: List[Dict[str, Any]]) -> str:
        s = source.lower()
        if 'nature' in s or 'jama' in s or 'nejm' in s:
            return 'Peer-reviewed journal or high authority outlet.'
        if 'arxiv' in s:
            return 'Preprint archive; useful but not peer-reviewed.'
        if 'doi' in s or 'springer' in s:
            return 'Published research with DOI reference.'
        if 'medium' in s or 'blog' in s:
            return 'Informal blog; verify claims.'
        if s.startswith('file://') or s.endswith('.pdf'):
            return 'Local document or PDF; credibility depends on source metadata.'
        return 'Generic web source; verify with authoritative sources.'
    
    def _map_evidence(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and classify evidence from source."""
        evidence = []
        for doc in docs:
            text = doc.get('text', '') or ''
            # take first sentence-like piece as a representative claim
            sent = text.strip().split('. ')
            claim = sent[0][:240] if sent else ''
            support = (sent[1][:240] + '...') if len(sent) > 1 else (sent[0][:240] if sent else '')
            evidence.append({
                'claim': claim or 'No explicit claim found',
                'support': support,
                'type': 'textual'
            })
        return evidence
    
    def _find_contradictions(self, summaries: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Identify conflicting claims across sources."""
        conflicts = []
        # naive contradictions: look for opposite words across summaries
        pos_terms = ['increase', 'improve', 'positive', 'rise']
        neg_terms = ['decrease', 'reduce', 'negative', 'decline']
        for i, a in enumerate(summaries):
            for j, b in enumerate(summaries):
                if i >= j:
                    continue
                ta = a.get('summary','').lower()
                tb = b.get('summary','').lower()
                for pt in pos_terms:
                    for nt in neg_terms:
                        if pt in ta and nt in tb:
                            conflicts.append({'sources': [a.get('source'), b.get('source')], 'description': f"Conflicting claims: one source suggests '{pt}' while another suggests '{nt}'."})
        return conflicts