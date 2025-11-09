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
    """Generates structured research reports."""
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
        
        # Build report sections with fallbacks
        sections = {
            'executive_summary': self._build_executive_summary(query, analysis, insights),
            'methodology': self._describe_methodology(plan),
            'key_findings': self._organize_findings(analysis, insights),
            'evidence': self._compile_evidence(analysis),
            'recommendations': self._generate_recommendations(insights)
        }
        
        # Write Markdown report
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._render_markdown(query, sections))
        
        return {'md_path': md_path}
    
    def _build_executive_summary(self,
                               query: str,
                               analysis: Dict[str, Any],
                               insights: Dict[str, Any]) -> str:
        """Create concise executive summary."""
        lines = [
            "Executive Summary",
            "================",
            "",
            f"Research Query: {query}",
            "",
            "Key Findings:",
        ]
        
        # Add findings from analysis
        if analysis and isinstance(analysis.get('summaries'), list):
            for s in analysis['summaries'][:3]:
                if isinstance(s, dict) and s.get('summary'):
                    lines.append(f"- {s['summary']}")
        
        # Add insights if available
        if insights:
            if insights.get('patterns'):
                lines.extend(["", "Key Patterns:"])
                for p in insights['patterns'][:3]:
                    if isinstance(p, dict) and p.get('description'):
                        lines.append(f"- {p['description']}")
            
            if insights.get('hypotheses'):
                lines.extend(["", "Key Hypotheses:"])
                for h in insights['hypotheses'][:3]:
                    if isinstance(h, dict) and h.get('description'):
                        lines.append(f"- {h['description']}")
        
        return "\n".join(lines)
    
    def _describe_methodology(self, plan: Dict[str, Any]) -> str:
        """Document research methodology."""
        lines = [
            "Research Methodology",
            "====================",
            "",
            "1. Document Processing:",
            "   - Extracted text from uploaded documents",
            "   - Indexed content for semantic search",
            "",
            "2. Information Retrieval:",
            "   - Used semantic search to find relevant passages",
            "   - Retrieved additional context from trusted web sources",
            "",
            "3. Analysis Pipeline:",
            "   - Critical analysis of source credibility and content",
            "   - Pattern identification across sources",
            "   - Evidence strength assessment"
        ]
        return "\n".join(lines)
    
    def _organize_findings(self,
                         analysis: Dict[str, Any],
                         insights: Dict[str, Any]) -> str:
        """Structure and organize key findings."""
        lines = [
            "Key Findings",
            "============",
            ""
        ]
        
        # Add source summaries
        if analysis and isinstance(analysis.get('summaries'), list):
            for i, s in enumerate(analysis['summaries'][:5], 1):
                if isinstance(s, dict):
                    src = s.get('source', 'Source ' + str(i))
                    summary = s.get('summary', '').strip()
                    if summary:
                        lines.extend([
                            f"Finding {i}: {src}",
                            "-" * (len(f"Finding {i}: {src}")),
                            summary,
                            ""
                        ])
        
        # Add patterns as findings
        if insights and isinstance(insights.get('patterns'), list):
            lines.extend(["Identified Patterns", "-----------------", ""])
            for p in insights['patterns'][:3]:
                if isinstance(p, dict) and p.get('description'):
                    lines.extend([p['description'], ""])
        
        return "\n".join(lines)
    
    def _compile_evidence(self, analysis: Dict[str, Any]) -> str:
        """Compile and organize supporting evidence."""
        lines = [
            "Supporting Evidence",
            "==================",
            ""
        ]
        
        # Add evidence from analysis
        if analysis:
            # Add credibility assessments
            if isinstance(analysis.get('credibility'), dict):
                lines.extend(["Source Credibility", "-----------------", ""])
                for src, cred in analysis['credibility'].items():
                    if isinstance(cred, dict):
                        score = cred.get('score', 'N/A')
                        rationale = cred.get('rationale', '')
                        if rationale:
                            lines.extend([
                                f"* {src}:",
                                f"  Score: {score}",
                                f"  {rationale}",
                                ""
                            ])
            
            # Add key evidence points
            if isinstance(analysis.get('evidence'), dict):
                lines.extend(["Key Evidence", "------------", ""])
                for src, evidence in analysis['evidence'].items():
                    if isinstance(evidence, list):
                        for e in evidence:
                            if isinstance(e, dict):
                                claim = e.get('claim', '').strip()
                                support = e.get('support', '').strip()
                                if claim and support:
                                    lines.extend([
                                        f"Source: {src}",
                                        f"Claim: {claim}",
                                        f"Support: {support}",
                                        ""
                                    ])
        
        return "\n".join(lines)
    
    def _generate_recommendations(self, insights: Dict[str, Any]) -> str:
        """Generate actionable recommendations."""
        lines = [
            "Recommendations",
            "===============",
            ""
        ]
        
        # Convert implications to recommendations
        if insights and isinstance(insights.get('implications'), list):
            for i, imp in enumerate(insights['implications'][:5], 1):
                if isinstance(imp, dict):
                    desc = imp.get('description', '').strip()
                    if desc:
                        lines.extend([
                            f"{i}. {desc}",
                            ""
                        ])
        
        # Add research gaps as recommendations
        if insights and isinstance(insights.get('gaps'), list):
            lines.extend(["Research Gaps to Address", "---------------------", ""])
            for gap in insights['gaps']:
                if isinstance(gap, dict):
                    desc = gap.get('description', '').strip()
                    sugg = gap.get('suggested_research', '').strip()
                    if desc or sugg:
                        lines.extend([
                            f"* Gap: {desc}",
                            f"  Suggestion: {sugg}",
                            ""
                        ])
        
        # Fallback if no recommendations
        if len(lines) <= 3:
            lines.extend([
                "1. Gather additional sources to verify findings",
                "2. Consider expert validation of key conclusions",
                "3. Monitor for updates in rapidly evolving areas"
            ])
        
        return "\n".join(lines)
    
    def _render_markdown(self, query: str, sections: Dict[str, str]) -> str:
        """Render report sections as Markdown."""
        lines = [
            "# Research Report",
            "",
            f"**Query:** {query}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## " + sections['executive_summary'],
            "",
            "## " + sections['methodology'],
            "",
            "## " + sections['key_findings'],
            "",
            "## " + sections['evidence'],
            "",
            "## " + sections['recommendations']
        ]
        
        return "\n".join(lines)