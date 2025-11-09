"""Insights Generator Agent for extracting research insights."""
from __future__ import annotations
from typing import List, Dict, Any
import json
from src.utils.config import load_settings
from src.utils.llm import generate_text

SETTINGS = load_settings()

class InsightsGeneratorAgent:
    """Generates insights from analyzed research content."""
    def __init__(self, settings=None):
        self.settings = settings or SETTINGS

    def generate_insights(self,
                        analysis: Dict[str, Any],
                        query: str) -> Dict[str, Any]:
        """Generate insights from analyzed content."""
        insights = {
            'patterns': [],
            'hypotheses': [],
            'implications': [],
            'gaps': [],
            'text': ''
        }
        
        # Extract source data
        summaries = []
        evidence = {}
        if isinstance(analysis, dict):
            summaries = analysis.get('summaries', [])
            evidence = analysis.get('evidence', {})
        
        # Identify patterns
        patterns = self._identify_patterns(summaries, evidence)
        if patterns:
            insights['patterns'] = patterns
            
        # Generate hypotheses
        hypotheses = self._generate_hypotheses(patterns, query)
        if hypotheses:
            insights['hypotheses'] = hypotheses
            
        # Identify implications
        implications = self._extract_implications(patterns, hypotheses)
        if implications:
            insights['implications'] = implications
            
        # Find research gaps
        gaps = self._identify_gaps(summaries, evidence, query)
        if gaps:
            insights['gaps'] = gaps
        
        # Format insights as text
        insights['text'] = self._format_insights_text(insights)
        
        return insights
    
    def _identify_patterns(self,
                          summaries: List[Dict[str, str]],
                          evidence: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, Any]]:
        """Identify patterns across research sources."""
        # Combine relevant text for pattern analysis
        analysis_text = []
        
        # Add summaries
        for s in summaries:
            if isinstance(s, dict) and s.get('summary'):
                analysis_text.append(s['summary'])
                
        # Add evidence points
        for src_evidence in evidence.values():
            if isinstance(src_evidence, list):
                for e in src_evidence:
                    if isinstance(e, dict):
                        claim = e.get('claim', '')
                        support = e.get('support', '')
                        if claim:
                            analysis_text.append(claim)
                        if support:
                            analysis_text.append(support)
        
        if not analysis_text:
            return []
            
        # Ask LLM to identify patterns
        try:
            text_input = "\n".join(analysis_text)
            response = generate_text("""Identify key patterns, trends, or commonalities across these research findings.
                                   For each pattern include:
                                   1. A clear description
                                   2. The strength/confidence (High/Medium/Low)
                                   3. Supporting examples
                                   Format as: description|strength|examples
                                   
                                   Research content:
                                   {text}
                                   """.format(text=text_input[:2000]))
            
            patterns = []
            if response:
                for line in response.split('\n'):
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            patterns.append({
                                'description': parts[0].strip(),
                                'strength': parts[1].strip(),
                                'examples': parts[2].strip()
                            })
                            
            return patterns
            
        except Exception as e:
            print(f"Error identifying patterns: {e}")
            return []
    
    def _generate_hypotheses(self,
                           patterns: List[Dict[str, Any]],
                           query: str) -> List[Dict[str, str]]:
        """Generate hypotheses based on identified patterns."""
        if not patterns:
            return []
            
        try:
            # Format patterns for LLM input
            pattern_text = "\n".join(
                f"Pattern: {p.get('description', '')}\n"
                f"Strength: {p.get('strength', '')}\n"
                f"Examples: {p.get('examples', '')}\n"
                for p in patterns if isinstance(p, dict)
            )
            
            response = generate_text("""Generate research hypotheses based on these patterns and the original query.
                                   For each hypothesis include:
                                   1. The hypothesis statement
                                   2. Supporting rationale
                                   Format as: hypothesis|rationale
                                   
                                   Research Query: {query}
                                   
                                   Patterns:
                                   {patterns}
                                   """.format(query=query, patterns=pattern_text))
            
            hypotheses = []
            if response:
                for line in response.split('\n'):
                    if '|' in line:
                        hypothesis, rationale = line.split('|', 1)
                        hypotheses.append({
                            'description': hypothesis.strip(),
                            'rationale': rationale.strip()
                        })
                        
            return hypotheses
            
        except Exception as e:
            print(f"Error generating hypotheses: {e}")
            return []
    
    def _extract_implications(self,
                            patterns: List[Dict[str, Any]],
                            hypotheses: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Extract key implications from patterns and hypotheses."""
        implications = []
        
        try:
            # Format input for LLM
            input_text = []
            
            if patterns:
                input_text.append("Patterns:")
                for p in patterns:
                    if isinstance(p, dict):
                        desc = p.get('description', '')
                        if desc:
                            input_text.append(f"- {desc}")
                
            if hypotheses:
                input_text.append("\nHypotheses:")
                for h in hypotheses:
                    if isinstance(h, dict):
                        desc = h.get('description', '')
                        if desc:
                            input_text.append(f"- {desc}")
            
            if not input_text:
                return []
                
            response = generate_text("""Extract key implications or actionable insights from these research findings.
                                   Each implication should include:
                                   1. The implication/insight
                                   2. Suggested actions/next steps
                                   Format as: implication|actions
                                   
                                   Research Findings:
                                   {text}
                                   """.format(text="\n".join(input_text)))
            
            if response:
                for line in response.split('\n'):
                    if '|' in line:
                        insight, actions = line.split('|', 1)
                        implications.append({
                            'description': insight.strip(),
                            'actions': actions.strip()
                        })
                        
        except Exception as e:
            print(f"Error extracting implications: {e}")
            
        return implications
    
    def _identify_gaps(self,
                      summaries: List[Dict[str, str]],
                      evidence: Dict[str, List[Dict[str, str]]],
                      query: str) -> List[Dict[str, str]]:
        """Identify gaps in the research."""
        # Combine research content
        content = []
        
        # Add summaries
        for s in summaries:
            if isinstance(s, dict) and s.get('summary'):
                content.append(s['summary'])
                
        # Add evidence
        for src_evidence in evidence.values():
            if isinstance(src_evidence, list):
                for e in src_evidence:
                    if isinstance(e, dict):
                        claim = e.get('claim', '')
                        if claim:
                            content.append(claim)
        
        if not content:
            return []
            
        try:
            text_input = "\n".join(content)
            response = generate_text("""Identify gaps or areas needing more research in relation to the query.
                                   For each gap include:
                                   1. Description of the gap/limitation
                                   2. Suggested additional research
                                   Format as: gap|suggestion
                                   
                                   Query: {query}
                                   
                                   Current Research:
                                   {text}
                                   """.format(query=query, text=text_input[:2000]))
            
            gaps = []
            if response:
                for line in response.split('\n'):
                    if '|' in line:
                        gap, suggestion = line.split('|', 1)
                        gaps.append({
                            'description': gap.strip(),
                            'suggested_research': suggestion.strip()
                        })
                        
            return gaps
            
        except Exception as e:
            print(f"Error identifying gaps: {e}")
            return []
    
    def _format_insights_text(self, insights: Dict[str, Any]) -> str:
        """Format insights as readable text."""
        lines = [
            "Research Insights",
            "================",
            ""
        ]
        
        # Add patterns
        if insights.get('patterns'):
            lines.extend(["Identified Patterns:", "-----------------", ""])
            for p in insights['patterns']:
                if isinstance(p, dict):
                    desc = p.get('description', '')
                    strength = p.get('strength', '')
                    examples = p.get('examples', '')
                    if desc:
                        lines.extend([
                            f"Pattern: {desc}",
                            f"Strength: {strength}",
                            f"Examples: {examples}",
                            ""
                        ])
        
        # Add hypotheses
        if insights.get('hypotheses'):
            lines.extend(["Research Hypotheses:", "------------------", ""])
            for h in insights['hypotheses']:
                if isinstance(h, dict):
                    desc = h.get('description', '')
                    rationale = h.get('rationale', '')
                    if desc:
                        lines.extend([
                            f"Hypothesis: {desc}",
                            f"Rationale: {rationale}",
                            ""
                        ])
        
        # Add implications
        if insights.get('implications'):
            lines.extend(["Key Implications:", "---------------", ""])
            for i in insights['implications']:
                if isinstance(i, dict):
                    desc = i.get('description', '')
                    actions = i.get('actions', '')
                    if desc:
                        lines.extend([
                            f"Implication: {desc}",
                            f"Suggested Actions: {actions}",
                            ""
                        ])
        
        # Add research gaps
        if insights.get('gaps'):
            lines.extend(["Research Gaps:", "-------------", ""])
            for g in insights['gaps']:
                if isinstance(g, dict):
                    desc = g.get('description', '')
                    suggestion = g.get('suggested_research', '')
                    if desc:
                        lines.extend([
                            f"Gap: {desc}",
                            f"Suggested Research: {suggestion}",
                            ""
                        ])
        
        return "\n".join(lines)