"""Report Builder Agent for generating structured research reports."""
from __future__ import annotations
from typing import List, Dict, Any
import json
import os
from datetime import datetime
from src.utils.config import load_settings
from src.utils.llm import generate_text

SETTINGS = load_settings()

class ReportBuilderAgent:
    """Generates structured research reports with:
    - Executive summary
    - Methodology
    - Key findings
    - Evidence and citations
    - Visual elements
    - Recommendations
    """
    def __init__(self, settings=None):
        self.settings = settings or SETTINGS
    
    def build_report(self,
                    query: str,
                    plan: Dict[str, Any],
                    analysis: Dict[str, Any],
                    insights: Dict[str, Any],
                    output_dir: str = './outputs') -> Dict[str, str]:
        """Generate comprehensive research report."""
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"report_{timestamp}"
        md_path = os.path.join(output_dir, f"{base_name}.md")
        json_path = os.path.join(output_dir, f"{base_name}.json")
        
        # Build report sections
        sections = {
            'executive_summary': self._build_executive_summary(query, analysis, insights),
            'methodology': self._describe_methodology(plan),
            'findings': self._organize_findings(analysis, insights),
            'evidence': self._compile_evidence(analysis),
            'recommendations': self._generate_recommendations(insights),
            'appendix': self._build_appendix(analysis, insights)
        }
        
        # Write Markdown report
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._render_markdown(query, sections))
        
        # Write JSON data
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'sections': sections,
                'metadata': {
                    'sources': len(analysis.get('summaries', [])),
                    'insights': len(insights.get('patterns', [])) + len(insights.get('hypotheses', []))
                }
            }, f, indent=2)
        
        return {
            'md_path': md_path,
            'json_path': json_path
        }
    
    def _build_executive_summary(self,
                               query: str,
                               analysis: Dict[str, Any],
                               insights: Dict[str, Any]) -> str:
        """Create concise executive summary."""
        
        # Try LLM-based summary first
        try:
            analysis_text = analysis.get('text', '').strip()
            insights_text = insights.get('text', '').strip()
            sources_count = len(analysis.get('summaries', []))
            
            prompt = (
                f"Write a concise executive summary (4-6 sentences) for this research report.\n\n"
                f"Research Question: {query}\n"
                f"Sources Analyzed: {sources_count}\n\n"
                f"Analysis Findings:\n{analysis_text[:1000]}\n\n"
                f"Key Insights:\n{insights_text[:1000]}\n\n"
                "Focus on: (1) Main findings, (2) Key insights, (3) Reliability assessment, (4) Actionable recommendations."
            )
            
            llm_summary = generate_text(prompt, max_tokens=400, temperature=0.3)
            
            # Check if we got a real summary (not the prompt back)
            if llm_summary and len(llm_summary.strip()) > 50 and not llm_summary.startswith("Write a concise"):
                return llm_summary.strip()
        except Exception as e:
            print(f"LLM executive summary error: {e}")
        
        # Fallback: Build structured summary
        lines = []
        lines.append(f"This research investigated: **{query}**")
        lines.append(f"Based on analysis of **{len(analysis.get('summaries', []))} sources**, key findings include:")
        lines.append("")
        
        # Extract key points from analysis
        analysis_text = analysis.get('text', '').strip()
        if analysis_text:
            # Extract first few bullet points or sentences
            if '**Key Findings:**' in analysis_text:
                findings_section = analysis_text.split('**Key Findings:**')[1].split('**')[0]
                lines.append(findings_section.strip()[:500])
            else:
                lines.append(analysis_text[:300])
        
        lines.append("")
        
        # Add credibility note
        cred_scores = [score.get('score', 0) for score in analysis.get('credibility', {}).values()]
        if cred_scores:
            avg_cred = sum(cred_scores) / len(cred_scores)
            if avg_cred > 0.7:
                lines.append("Sources demonstrate high credibility from authoritative outlets.")
            elif avg_cred > 0.4:
                lines.append("Sources show moderate credibility; cross-referencing recommended.")
            else:
                lines.append("Source credibility requires verification with established authorities.")
        
        return '\n'.join(lines)
    
    def _describe_methodology(self, plan: Dict[str, Any]) -> str:
        """Document research methodology."""
        lines = []
        lines.append("**Search Strategy:** Multi-source retrieval combining document analysis and web search")
        lines.append("**Source Selection:** Relevance-based ranking with credibility assessment")
        lines.append("**Analysis Methods:** Critical source analysis with pattern identification")
        lines.append("**Validation:** Cross-reference verification and conflict detection")
        return '\n'.join(lines)
    
    def _organize_findings(self,
                         analysis: Dict[str, Any],
                         insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Structure and organize key findings."""
        findings = []
        # Create findings from analysis summaries
        summaries = analysis.get('summaries', []) or []
        for i, s in enumerate(summaries[:6], 1):
            findings.append({
                'title': f"Finding from source {i}",
                'description': s.get('summary', '')
            })

        # If insights contain strong patterns, add them as high-level findings
        for p in (insights.get('patterns', []) or [])[:3]:
            findings.insert(0, {
                'title': p.get('type', 'Pattern'),
                'description': p.get('description', '')
            })

        # Add hypotheses as potential findings with caveats
        for h in (insights.get('hypotheses', []) or [])[:3]:
            findings.append({
                'title': h.get('title', 'Hypothesis'),
                'description': f"{h.get('description','')} (confidence: {h.get('confidence','unknown')})"
            })

        return findings
    
    def _compile_evidence(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compile and organize supporting evidence."""
        evidence = {}
        for s in analysis.get('summaries', []) or []:
            src = s.get('source', 'unknown')
            summary = s.get('summary', '')
            evidence[src] = {
                'summary': summary,
                'notes': 'Auto-extracted evidence summary'
            }
        return evidence
    
    def _generate_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations."""
        recommendations = []
        # Derive simple recommendations from implications/hypotheses
        for i, imp in enumerate((insights.get('implications', []) or [])[:5], 1):
            recommendations.append({
                'title': imp.get('description', f'Recommendation {i}'),
                'impact': imp.get('impact', 'Medium'),
                'effort': imp.get('effort', 'Medium')
            })

        # If no implications present, turn hypotheses into recommended follow-ups
        if not recommendations:
            for i, h in enumerate((insights.get('hypotheses', []) or [])[:5], 1):
                recommendations.append({
                    'title': f"Investigate: {h.get('title','')}",
                    'impact': 'Unknown',
                    'effort': 'Low'
                })

        return recommendations
    
    def _build_appendix(self,
                       analysis: Dict[str, Any],
                       insights: Dict[str, Any]) -> Dict[str, Any]:
        """Compile detailed appendix materials."""
        appendix = {}
        appendix['summaries'] = analysis.get('summaries', [])
        appendix['raw_analysis_text'] = analysis.get('text', '')
        appendix['insights'] = insights
        return appendix
    
    def _render_markdown(self, query: str, sections: Dict[str, Any]) -> str:
        """Render report sections as Markdown."""
        md = []
        
        # Title and metadata
        md.extend([
            "# Research Report\n",
            f"**Query:** {query}\n",
            f"**Generated:** {datetime.now().isoformat()}\n\n"
        ])
        
        # Executive Summary
        md.extend([
            "## Executive Summary\n",
            sections['executive_summary'],
            "\n"
        ])
        
        # Methodology
        md.extend([
            "## Methodology\n",
            sections['methodology'],
            "\n"
        ])
        
        # Findings
        md.append("## Key Findings\n")
        for i, finding in enumerate(sections['findings'], 1):
            md.extend([
                f"### {i}. {finding.get('title', 'Finding')}\n",
                finding.get('description', ''),
                "\n"
            ])
        
        # Evidence and Citations
        md.append("## Evidence and Citations\n")
        for source, evidence in sections['evidence'].items():
            md.extend([
                f"### Source: {source}\n",
                evidence.get('summary', ''),
                "\n"
            ])
        
        # Recommendations
        md.append("## Recommendations\n")
        for i, rec in enumerate(sections['recommendations'], 1):
            md.extend([
                f"{i}. {rec.get('title', 'Recommendation')}\n",
                f"   - Impact: {rec.get('impact', 'Unknown')}\n",
                f"   - Effort: {rec.get('effort', 'Unknown')}\n",
                "\n"
            ])
        
        # Appendix section removed as per user requirement
        
        return "\n".join(md)