"""Analysis Agent for evaluating research content."""
from __future__ import annotations
from typing import List, Dict, Any
import json
from src.utils.config import load_settings
from src.utils.llm import generate_text

SETTINGS = load_settings()

class AnalysisAgent:
    """Analyzes research content for patterns and insights."""
    def __init__(self, settings=None):
        self.settings = settings or SETTINGS

    def analyze_sources(self,
                       passages: List[Dict[str, str]],
                       plan: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze a collection of research passages."""
        analysis = {
            'summaries': [],
            'evidence': {},
            'credibility': {},
            'text': ''
        }
        
        # Process each source
        for i, passage in enumerate(passages):
            src = passage.get('source', f'Source {i+1}')
            content = passage.get('text', '').strip()
            
            if not content:
                continue
            
            # Generate content summary
            summary = self._summarize_passage(content)
            if summary:
                analysis['summaries'].append({
                    'source': src,
                    'summary': summary
                })
            
            # Extract evidence points
            evidence = self._extract_evidence(content)
            if evidence:
                analysis['evidence'][src] = evidence
            
            # Assess source credibility
            cred_score = self._assess_credibility(content)
            if cred_score:
                analysis['credibility'][src] = cred_score
        
        # Generate text summary of analysis
        analysis['text'] = self._format_analysis_text(analysis)
        
        return analysis
    
    def _summarize_passage(self, text: str) -> str:
        """Create concise summary of key points."""
        try:
            response = generate_text("""Summarize the key points from this research content.
                                   Focus on findings, methodology, and evidence.
                                   Keep the summary concise (2-3 sentences max).
                                   
                                   Content to summarize:
                                   {text}
                                   """.format(text=text[:2000]))
            
            return response.strip() if response else ''
        except Exception as e:
            print(f"Error generating summary: {e}")
            return ''
    
    def _extract_evidence(self, text: str) -> List[Dict[str, str]]:
        """Extract key evidence points and supporting details."""
        evidence = []
        try:
            # Ask LLM to identify evidence points
            response = generate_text("""Extract key evidence points from this research text.
                                   For each point include:
                                   1. The main claim/finding
                                   2. Supporting evidence/methodology
                                   Format as: claim|support
                                   
                                   Text to analyze:
                                   {text}
                                   """.format(text=text[:2000]))
            
            # Parse response into evidence points
            if response:
                for line in response.split('\n'):
                    if '|' in line:
                        claim, support = line.split('|', 1)
                        evidence.append({
                            'claim': claim.strip(),
                            'support': support.strip()
                        })
                    
        except Exception as e:
            print(f"Error extracting evidence: {e}")
            
        return evidence
    
    def _assess_credibility(self, text: str) -> Dict[str, Any]:
        """Evaluate source credibility and reliability."""
        try:
            response = generate_text("""Assess the credibility of this research content.
                                   Consider:
                                   - Methodology rigor
                                   - Evidence quality
                                   - Source authority
                                   - Potential biases
                                   
                                   Provide:
                                   1. A score (1-10)
                                   2. Brief rationale
                                   Format as: score|rationale
                                   
                                   Content to assess:
                                   {text}
                                   """.format(text=text[:2000]))
            
            if response and '|' in response:
                score_str, rationale = response.split('|', 1)
                try:
                    score = float(score_str.strip())
                except ValueError:
                    score = 5.0  # Default mid-range score
                    
                return {
                    'score': score,
                    'rationale': rationale.strip()
                }
                
        except Exception as e:
            print(f"Error assessing credibility: {e}")
            
        return {'score': 5.0, 'rationale': 'Credibility assessment failed'}
    
    def _format_analysis_text(self, analysis: Dict[str, Any]) -> str:
        """Format analysis results as readable text."""
        lines = [
            "Research Analysis Results",
            "========================",
            ""
        ]
        
        # Add summaries
        if analysis.get('summaries'):
            lines.extend(["Key Points by Source:", "--------------------", ""])
            for s in analysis['summaries']:
                if isinstance(s, dict):
                    src = s.get('source', 'Unknown')
                    summary = s.get('summary', '').strip()
                    if summary:
                        lines.extend([f"{src}:", summary, ""])
        
        # Add credibility assessments
        if analysis.get('credibility'):
            lines.extend(["Source Credibility:", "-----------------", ""])
            for src, cred in analysis['credibility'].items():
                if isinstance(cred, dict):
                    score = cred.get('score', 'N/A')
                    rationale = cred.get('rationale', '')
                    if rationale:
                        lines.extend([
                            f"{src}:",
                            f"Score: {score}/10",
                            f"Rationale: {rationale}",
                            ""
                        ])
        
        # Add evidence points
        if analysis.get('evidence'):
            lines.extend(["Supporting Evidence:", "------------------", ""])
            for src, evidence in analysis['evidence'].items():
                if isinstance(evidence, list):
                    lines.append(f"\n{src}:")
                    for e in evidence:
                        if isinstance(e, dict):
                            claim = e.get('claim', '').strip()
                            support = e.get('support', '').strip()
                            if claim and support:
                                lines.extend([
                                    f"Finding: {claim}",
                                    f"Support: {support}",
                                    ""
                                ])
        
        return "\n".join(lines)