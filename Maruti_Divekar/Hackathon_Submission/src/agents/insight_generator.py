"""Insight Generation Agent for discovering patterns and hypotheses."""
from __future__ import annotations
from typing import List, Dict, Any
from src.utils.config import load_settings
from src.utils.llm import generate_text
from src.agents.keywords import extract_keywords, extract_topics

SETTINGS = load_settings()

class InsightGenerationAgent:
    """Generates insights by:
    - Identifying patterns and trends
    - Forming hypotheses
    - Building reasoning chains
    - Suggesting implications
    """
    def __init__(self, settings=None):
        self.settings = settings or SETTINGS
    
    def generate_insights(self, 
                        analysis: Dict[str, Any],
                        query: str,
                        constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate structured insights from analyzed content."""
        insights = {
            'patterns': [],     # Identified patterns/trends
            'hypotheses': [],   # Generated hypotheses
            'implications': [], # Potential implications
            'gaps': [],        # Knowledge gaps identified
            'chains': [],      # Reasoning chains
            'text': ''         # Plain-English insights report
        }
        
        # Extract patterns from analysis
        insights['patterns'] = self._find_patterns(analysis)
        
        # Generate hypotheses
        insights['hypotheses'] = self._generate_hypotheses(
            analysis, 
            insights['patterns']
        )
        
        # Map implications
        insights['implications'] = self._map_implications(
            insights['patterns'],
            insights['hypotheses']
        )
        
        # Identify knowledge gaps
        insights['gaps'] = self._identify_gaps(
            query,
            analysis,
            insights['hypotheses']
        )
        
        # Build reasoning chains
        insights['chains'] = self._build_reasoning_chains(
            analysis,
            insights['patterns'],
            insights['hypotheses']
        )

        # Produce a plain-English summary using the simple reporter
        base_text = self._simple_plain_report(insights)
        insights['text'] = base_text

        # Use LLM to refine into polished English if available
        try:
            # Prepare structured context for insights
            sections = []
            
            # Patterns section
            if insights.get('patterns'):
                sections.append("=== Observed Patterns ===\n" + 
                    "\n".join(f"- {p.get('description', str(p))}" for p in insights['patterns']))
            
            # Hypotheses with evidence
            if insights.get('hypotheses'):
                sections.append("=== Hypotheses & Supporting Evidence ===\n" + 
                    "\n".join(f"- {h.get('title', str(h))}: {h.get('description','')}" 
                            for h in insights['hypotheses']))
            
            # Knowledge gaps
            if insights.get('gaps'):
                sections.append("=== Knowledge Gaps & Research Needs ===\n" +
                    "\n".join(f"- {g}" for g in insights['gaps']))
            
            # Build insights summary directly from structured data
            lines = []
            
            # Add patterns section
            if insights.get('patterns'):
                lines.append("**Observed Patterns:**")
                for p in insights['patterns'][:3]:
                    desc = p.get('description', '').strip()
                    if desc:
                        lines.append(f"- {desc}")
                lines.append("")
            
            # Add hypotheses section
            if insights.get('hypotheses'):
                lines.append("**Key Hypotheses:**")
                for h in insights['hypotheses'][:3]:
                    title = h.get('title', '').strip()
                    desc = h.get('description', '').strip()
                    conf = h.get('confidence', 'medium')
                    if title:
                        lines.append(f"- **{title}** (confidence: {conf})")
                        if desc:
                            lines.append(f"  {desc}")
                lines.append("")
            
            # Add implications if present
            if insights.get('implications'):
                lines.append("**Practical Implications:**")
                for imp in insights['implications'][:3]:
                    desc = imp.get('description', '').strip()
                    if desc:
                        lines.append(f"- {desc}")
                lines.append("")
            
            # Add research gaps
            if insights.get('gaps'):
                lines.append("**Research Gaps & Recommendations:**")
                for g in insights['gaps'][:3]:
                    if isinstance(g, dict):
                        desc = g.get('description', '').strip()
                        if desc:
                            lines.append(f"- {desc}")
                    elif isinstance(g, str) and g.strip():
                        lines.append(f"- {g.strip()}")
            
            insights['text'] = '\n'.join(lines) if lines else "Insights generated from research data."
        except Exception:
            pass

        return insights

    def _simple_plain_report(self, insights: Dict[str, Any]) -> str:
        """Generate a structured plain-English report from insights data."""
        lines = ['Research Insights Summary', '=======================\n']

        # Start with key patterns section
        lines.append('Key Patterns & Trends')
        lines.append('--------------------')
        if insights.get('patterns'):
            for p in insights['patterns']:
                desc = p.get('description', str(p))
                strength = p.get('strength', 'medium')
                lines.append(f"• {desc}")
                if p.get('supporting_evidence'):
                    lines.append(f"  Evidence: {p['supporting_evidence']}")
        else:
            lines.append("No clear patterns were identified in the current research.")
        lines.append('')

        # Hypotheses with confidence levels
        lines.append('Research Hypotheses')
        lines.append('-----------------')
        if insights.get('hypotheses'):
            for h in insights['hypotheses']:
                title = h.get('title', '')
                desc = h.get('description', '')
                conf = h.get('confidence', 'Not assessed')
                lines.append(f"• {title}")
                lines.append(f"  {desc}")
                lines.append(f"  Confidence Level: {conf}")
        else:
            lines.append("No formal hypotheses were generated from the current data.")
        lines.append('')

        # Implications section (if present)
        if insights.get('implications'):
            lines.append('Practical Implications')
            lines.append('--------------------')
            for imp in insights['implications']:
                lines.append(f"• {imp.get('description', str(imp))}")
            lines.append('')

        # Knowledge gaps and next steps
        lines.append('Knowledge Gaps & Research Needs')
        lines.append('-----------------------------')
        if insights.get('gaps'):
            for g in insights['gaps']:
                lines.append(f"• {g}")
                if isinstance(g, dict) and g.get('suggested_research'):
                    lines.append(f"  Suggested: {g['suggested_research']}")
        else:
            lines.append("No critical knowledge gaps were identified.")
        lines.append('')

        return '\n'.join(lines)
    
    def _find_patterns(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract patterns and trends from analyzed content."""
        patterns = []
        
        # Get text from analysis
        text = analysis.get('text', '')
        if not text:
            summaries = analysis.get('summaries', [])
            text = ' '.join(s.get('summary', '') for s in summaries)
        
        if not text.strip():
            return patterns
        
        # Try LLM-based pattern identification
        try:
            prompt = (
                "Analyze the following research content and identify 2-3 key patterns or trends. "
                "For each pattern, provide a clear description (1-2 sentences). Format as a numbered list.\n\n"
                f"Content:\n{text[:2000]}"
            )
            llm_response = generate_text(prompt, max_tokens=300, temperature=0.3)
            
            # Parse LLM response into structured patterns
            if llm_response and len(llm_response.strip()) > 20 and not llm_response.startswith("Analyze"):
                lines = [l.strip() for l in llm_response.split('\n') if l.strip()]
                for line in lines[:3]:
                    # Remove numbering if present
                    clean_line = line.lstrip('0123456789.-) ')
                    if clean_line and len(clean_line) > 15:
                        patterns.append({
                            'description': clean_line,
                            'strength': 'medium',
                            'type': 'llm_identified'
                        })
                if patterns:
                    return patterns
        except Exception as e:
            print(f"LLM pattern extraction error: {e}")
        
        # Fallback: Extract topics and keywords
        topics = extract_topics(text)
        for topic in topics[:3]:
            patterns.append({
                'description': f"Recurring theme: {topic}",
                'strength': 'medium',
                'type': 'recurring_topic'
            })
            
        keywords = extract_keywords(text)
        if keywords and not patterns:
            patterns.append({
                'description': f"Key concepts identified: {', '.join(keywords[:5])}",
                'strength': 'medium',
                'type': 'key_terms'
            })
            
        return patterns if patterns else [{'description': 'Analysis completed successfully', 'strength': 'low', 'type': 'generic'}]
    
    def _generate_hypotheses(self,
                           analysis: Dict[str, Any],
                           patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Form hypotheses explaining observed patterns."""
        hypotheses = []
        
        if not patterns:
            return hypotheses
        
        # Try LLM-based hypothesis generation
        try:
            pattern_text = '\n'.join(f"- {p.get('description', '')}" for p in patterns[:3])
            prompt = (
                "Based on these observed patterns, generate 2-3 research hypotheses. "
                "For each hypothesis, provide a title and brief description (1-2 sentences).\n\n"
                f"Patterns:\n{pattern_text}\n\n"
                "Format: Title | Description"
            )
            llm_response = generate_text(prompt, max_tokens=300, temperature=0.4)
            
            if llm_response and len(llm_response.strip()) > 20 and not llm_response.startswith("Based on"):
                lines = [l.strip() for l in llm_response.split('\n') if l.strip() and '|' in l]
                for line in lines[:3]:
                    parts = line.split('|', 1)
                    if len(parts) == 2:
                        title = parts[0].strip().lstrip('0123456789.-) ')
                        desc = parts[1].strip()
                        if title and desc:
                            hypotheses.append({
                                'title': title,
                                'description': desc,
                                'confidence': 'medium',
                                'type': 'llm_generated'
                            })
                if hypotheses:
                    return hypotheses
        except Exception as e:
            print(f"LLM hypothesis generation error: {e}")
        
        # Fallback: Generate from patterns
        for i, pattern in enumerate(patterns[:2], 1):
            desc = pattern.get('description', '')
            hypotheses.append({
                'title': f'Hypothesis {i}: Pattern Significance',
                'description': f'The identified pattern suggests potential relationships that warrant further investigation: {desc[:100]}',
                'confidence': 'low',
                'type': 'pattern_based'
            })
        
        return hypotheses if hypotheses else [{'title': 'Further Research Needed', 'description': 'Additional data required to form testable hypotheses', 'confidence': 'low'}]
    
    def _map_implications(self,
                         patterns: List[Dict[str, Any]],
                         hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Project implications of patterns and hypotheses."""
        implications = []
        # Would use LLM to:
        # - Project future impacts
        # - Identify affected areas
        # - Assess probability
        return implications
    
    def _identify_gaps(self,
                      query: str,
                      analysis: Dict[str, Any],
                      hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find gaps in current knowledge and evidence."""
        gaps = []
        
        try:
            # First try using LLM
            return gaps
        except Exception:
            # Basic heuristic fallback
            # Check which query terms are missing from results
            query_keywords = set(extract_keywords(query.lower()))
            
            text = analysis.get('merged', '')
            if not text:
                summaries = analysis.get('summaries', [])
                text = ' '.join(s.get('summary', '') for s in summaries)
            
            result_keywords = set(extract_keywords(text.lower()))
            
            missing_terms = query_keywords - result_keywords
            if missing_terms:
                gaps.append({
                    'description': f"Limited coverage of query terms: {', '.join(missing_terms)}",
                    'suggested_research': f"Consider searching specifically for content about: {', '.join(missing_terms)}"
                })
            
            # Check confidence of hypotheses
            low_confidence = [h for h in hypotheses if h.get('confidence', '') == 'low']
            if low_confidence:
                topics = [h.get('title', '').split('of ')[-1].strip() for h in low_confidence]
                gaps.append({
                    'description': f"Limited evidence for topics: {', '.join(topics)}",
                    'suggested_research': f"Gather more data about: {', '.join(topics)}"
                })
                
            # Always suggest verification
            gaps.append({
                'description': "Results based on heuristic analysis - consider human verification",
                'suggested_research': "Review key findings with domain experts"
            })
            
            return gaps
    
    def _build_reasoning_chains(self,
                              analysis: Dict[str, Any],
                              patterns: List[Dict[str, Any]],
                              hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Construct logical chains connecting evidence to conclusions."""
        chains = []
        # Would use LLM to:
        # - Link evidence to claims
        # - Build logical steps
        # - Validate reasoning
        return chains