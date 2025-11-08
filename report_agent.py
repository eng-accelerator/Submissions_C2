import datetime
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from pathlib import Path
from config import Config  # Add this line

@dataclass
class ReportSection:
    title: str
    content: str
    level: int
    metadata: Dict[str, Any]

class ReportBuilderAgent:
    def __init__(self, output_formats: List[str] = ["markdown", "html", "pdf"]):
        self.output_formats = output_formats
        self.template_registry = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize report templates for different use cases"""
        return {
            "research_report": {
                "structure": "executive_summary,methodology,findings,insights,conclusions,recommendations",
                "style": "academic"
            },
            "executive_summary": {
                "structure": "key_findings,insights,recommendations,next_steps",
                "style": "business"
            },
            "technical_report": {
                "structure": "introduction,data_sources,methodology,analysis,results,discussion",
                "style": "technical"
            }
        }
    
    def build_comprehensive_report(self,
                                 contextual_data: Dict[str, Any],
                                 analysis_results: Dict[str, Any],
                                 insights: List[Dict[str, Any]],
                                 report_type: str = "research_report") -> Dict[str, Any]:
        """
        Build comprehensive report from all agent outputs
        
        Args:
            contextual_data: Output from Contextual Retriever Agent
            analysis_results: Output from Critical Analysis Agent
            insights: Output from Insight Generation Agent
            report_type: Type of report to generate
            
        Returns:
            Dictionary containing report in multiple formats
        """
        
        sections = []
        
        # Executive Summary
        sections.append(self._build_executive_summary(insights, analysis_results))
        
        # Methodology
        sections.append(self._build_methodology_section(contextual_data))
        
        # Key Findings
        sections.append(self._build_findings_section(analysis_results))
        
        # Insights and Hypotheses
        sections.append(self._build_insights_section(insights))
        
        # Conclusions and Recommendations
        sections.append(self._build_recommendations_section(insights, analysis_results))
        
        # Build complete report
        report = {
            "metadata": self._generate_report_metadata(report_type),
            "sections": sections,
            "formats": {}
        }
        
        # Generate different output formats
        for format_type in self.output_formats:
            report["formats"][format_type] = self._render_format(
                sections, format_type, report["metadata"]
            )
        
        return report
    
    def _build_executive_summary(self, 
                               insights: List[Dict[str, Any]],
                               analysis_results: Dict[str, Any]) -> ReportSection:
        """Build executive summary section"""
        
        key_insights = insights[:3]  # Top 3 insights
        confidence_score = analysis_results.get('overall_confidence', 0.5)
        
        content = f"""
# Executive Summary

## Key Insights
{self._format_key_insights(key_insights)}

## Overall Confidence
**Confidence Score: {confidence_score:.2f}/1.00**

## Primary Findings
- {analysis_results.get('summary', 'No summary available')}
- Contradictions resolved: {len(analysis_results.get('resolved_contradictions', []))}
- Sources validated: {analysis_results.get('sources_validated', 0)}

## Immediate Implications
{self._extract_implications(insights)}
"""
        
        return ReportSection(
            title="Executive Summary",
            content=content,
            level=1,
            metadata={"word_count": len(content.split()), "contains_key_findings": True}
        )
    
    def _build_methodology_section(self, contextual_data: Dict[str, Any]) -> ReportSection:
        """Build methodology section"""
        
        sources = contextual_data.get('sources', [])
        data_types = set()
        for source in sources:
            data_types.add(source.get('type', 'unknown'))
        
        content = f"""
# Methodology

## Data Sources
This analysis utilized {len(sources)} distinct data sources including:
- **Source Types**: {', '.join(data_types)}
- **Time Range**: {contextual_data.get('time_range', 'Not specified')}
- **Geographic Scope**: {contextual_data.get('geographic_scope', 'Global')}

## Analytical Approach
The research employed a multi-agent AI system with the following specialized components:
1. **Contextual Retriever**: Gathers and processes multi-source data
2. **Critical Analysis**: Validates sources and identifies contradictions  
3. **Insight Generation**: Develops hypotheses and identifies trends
4. **Report Builder**: Synthesizes findings into structured reports

## Validation Framework
All findings underwent rigorous validation including:
- Source credibility assessment
- Contradiction resolution
- Confidence scoring
- Reasoning chain verification
"""
        
        return ReportSection(
            title="Methodology",
            content=content,
            level=1,
            metadata={"sources_count": len(sources), "data_types": list(data_types)}
        )
    
    def _build_findings_section(self, analysis_results: Dict[str, Any]) -> ReportSection:
        """Build key findings section"""
        
        findings = analysis_results.get('key_findings', [])
        contradictions = analysis_results.get('contradictions', [])
        validations = analysis_results.get('source_validations', {})
        
        content = f"""
# Key Findings

## Primary Results
{chr(10).join(f"- {finding}" for finding in findings[:5])}

## Data Quality Assessment
- **Sources Validated**: {sum(validations.values())}/{len(validations)}
- **Contradictions Identified**: {len(contradictions)}
- **Confidence Level**: {analysis_results.get('confidence_score', 'Not calculated')}

## Notable Patterns
{self._extract_patterns(analysis_results)}
"""
        
        return ReportSection(
            title="Key Findings",
            content=content,
            level=1,
            metadata={"findings_count": len(findings), "contradictions_count": len(contradictions)}
        )
    
    def _build_insights_section(self, insights: List[Dict[str, Any]]) -> ReportSection:
        """Build insights and hypotheses section"""
        
        content = """
# Insights and Hypotheses

## Generated Insights
"""
        
        for i, insight in enumerate(insights, 1):
            content += f"""
### Insight {i}: {insight['statement']}

**Confidence**: {insight['confidence']:.2f}

**Reasoning Chain**:
{chr(10).join(f"- {step}" for step in insight['reasoning_chain'])}

**Testable Implications**:
{chr(10).join(f"- {implication}" for implication in insight['testable_implications'])}

---
"""
        
        return ReportSection(
            title="Insights and Hypotheses",
            content=content,
            level=1,
            metadata={"insights_count": len(insights), "average_confidence": sum(i['confidence'] for i in insights) / len(insights)}
        )
    
    def _build_recommendations_section(self, 
                                     insights: List[Dict[str, Any]],
                                     analysis_results: Dict[str, Any]) -> ReportSection:
        """Build conclusions and recommendations section"""
        
        content = """
# Conclusions and Recommendations

## Key Conclusions
"""
        
        # Extract conclusions from insights
        for i, insight in enumerate(insights[:3], 1):
            content += f"""
{i}. {insight['statement']} (Confidence: {insight['confidence']:.2f})
"""
        
        content += """
## Recommendations

### Immediate Actions
1. **Validate Top Hypotheses**: Prioritize testing of high-confidence insights
2. **Address Data Gaps**: Focus on areas with lower confidence scores
3. **Monitor Key Indicators**: Establish tracking for critical variables

### Strategic Considerations
- Leverage identified patterns for predictive modeling
- Address contradictions through targeted data collection
- Scale successful analytical approaches to other domains

## Next Steps
1. Conduct controlled experiments to test generated hypotheses
2. Expand data sources to improve confidence scores
3. Implement monitoring system for ongoing validation
"""
        
        return ReportSection(
            title="Conclusions and Recommendations",
            content=content,
            level=1,
            metadata={"recommendations_count": 6, "next_steps": 3}
        )
    
    def _format_key_insights(self, insights: List[Dict[str, Any]]) -> str:
        """Format key insights for executive summary"""
        formatted = ""
        for i, insight in enumerate(insights, 1):
            formatted += f"{i}. {insight['statement']} (Confidence: {insight['confidence']:.2f})\n"
        return formatted
    
    def _extract_implications(self, insights: List[Dict[str, Any]]) -> str:
        """Extract implications from insights"""
        implications = set()
        for insight in insights:
            for implication in insight.get('testable_implications', []):
                implications.add(implication)
        
        return chr(10).join(f"- {imp}" for imp in list(implications)[:5])
    
    def _extract_patterns(self, analysis_results: Dict[str, Any]) -> str:
        """Extract patterns from analysis results"""
        patterns = analysis_results.get('patterns', [])
        if not patterns:
            return "No specific patterns identified in the current analysis."
        
        return chr(10).join(f"- {pattern}" for pattern in patterns[:3])
    
    def _generate_report_metadata(self, report_type: str) -> Dict[str, Any]:
        """Generate report metadata"""
        return {
            "report_id": f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.datetime.now().isoformat(),
            "report_type": report_type,
            "version": "1.0",
            "agents_used": ["contextual_retriever", "critical_analysis", "insight_generation", "report_builder"]
        }
    
    def _render_format(self, 
                      sections: List[ReportSection], 
                      format_type: str,
                      metadata: Dict[str, Any]) -> str:
        """Render report in specified format"""
        
        if format_type == "markdown":
            return self._render_markdown(sections, metadata)
        elif format_type == "html":
            return self._render_html(sections, metadata)
        elif format_type == "pdf":
            return self._render_pdf_ready(sections, metadata)
        else:
            return self._render_markdown(sections, metadata)
    
    def _render_markdown(self, sections: List[ReportSection], metadata: Dict[str, Any]) -> str:
        """Render report as Markdown"""
        markdown = f"""# AI Research Report\n\n"""
        markdown += f"**Report ID**: {metadata['report_id']}  \n"
        markdown += f"**Generated**: {metadata['generated_at']}  \n"
        markdown += f"**Type**: {metadata['report_type']}  \n\n"
        
        for section in sections:
            markdown += f"{section.content}\n\n"
        
        return markdown
    
    def _render_html(self, sections: List[ReportSection], metadata: Dict[str, Any]) -> str:
        """Render report as HTML"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Research Report - {metadata['report_id']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 1px solid #bdc3c7; padding-bottom: 10px; }}
        h3 {{ color: #7f8c8d; }}
        .metadata {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 30px; }}
    </style>
</head>
<body>
    <h1>AI Research Report</h1>
    <div class="metadata">
        <strong>Report ID:</strong> {metadata['report_id']}<br>
        <strong>Generated:</strong> {metadata['generated_at']}<br>
        <strong>Type:</strong> {metadata['report_type']}
    </div>
"""
        
        for section in sections:
            # Convert markdown to simple HTML
            section_html = section.content.replace('# ', '<h1>').replace('\n#', '\n<h1>')
            section_html = section_html.replace('## ', '<h2>').replace('\n##', '\n<h2>')
            section_html = section_html.replace('### ', '<h3>').replace('\n###', '\n<h3>')
            section_html = section_html.replace('\n- ', '\n<li>').replace('\n\n', '</li>\n</ul>\n')
            section_html = section_html.replace('**', '<strong>').replace('**', '</strong>')
            
            html += f'<div class="section">{section_html}</div>\n'
        
        html += "</body></html>"
        return html
    
    def _render_pdf_ready(self, sections: List[ReportSection], metadata: Dict[str, Any]) -> str:
        """Render report in PDF-ready format (simplified)"""
        return self._render_markdown(sections, metadata)  # Can be converted to PDF using libraries like WeasyPrint
    
    def save_report(self, report: Dict[str, Any], output_dir: str = "./reports"):
        """Save report to files in multiple formats"""
        Path(output_dir).mkdir(exist_ok=True)
        
        base_filename = f"{output_dir}/{report['metadata']['report_id']}"
        
        for format_type, content in report['formats'].items():
            filename = f"{base_filename}.{format_type}"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Saved {format_type.upper()} report: {filename}")
        
        # Save metadata separately
        with open(f"{base_filename}_metadata.json", 'w') as f:
            json.dump(report['metadata'], f, indent=2)