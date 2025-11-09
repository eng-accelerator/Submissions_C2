"""
Report Builder Agent
Compiles all insights into a structured report.
"""

import logging
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_config import create_report_llm, REPORT_MODEL, TEMPERATURES

logger = logging.getLogger(__name__)


class ReportBuilderAgent:
    """Compiles research findings into a structured markdown report."""
    
    def __init__(self, model: str = None, temperature: float = None):
        """Initialize the report builder agent with LLM via OpenRouter.
        
        Uses Claude 3.5 Haiku for fast, consistent formatting.
        Default temperature: 0.2 (low creativity, consistent formatting).
        """
        # Use optimized report LLM with Claude 3.5 Haiku
        if model or temperature is not None:
            from utils.llm_config import create_llm
            self.llm = create_llm(
                model=model or REPORT_MODEL,
                temperature=temperature if temperature is not None else TEMPERATURES["report"],
                max_tokens=4000
            )
        else:
            self.llm = create_report_llm()
        if not self.llm:
            logger.warning("OpenRouter API key not found. Report will use template.")
    
    def compile(self, query: str, sources: Dict[str, Any], 
                analysis: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """
        Compile all research components into a structured report.
        
        Args:
            query: Original research query
            sources: Retrieved sources
            analysis: Analysis results
            insights: Generated insights
            
        Returns:
            Formatted markdown report
        """
        logger.info("Report Builder: Compiling final report")
        
        if not self.llm:
            return self._template_report(query, sources, analysis, insights)
        
        # Format all data for prompt
        report_data = self._format_report_data(query, sources, analysis, insights)
        
        # Create report generation prompt
        prompt = ChatPromptTemplate.from_template("""
You are a professional research report writer. Create a comprehensive, well-structured research report based on the following information:

{report_data}

Generate a professional markdown report with the following structure:

# Research Report: [Query]

## Executive Summary
A concise 2-3 paragraph summary of the key findings.

## Key Findings
Bullet points of the most important discoveries.

## Source Analysis
Summary of sources analyzed, including credibility assessments.

## Contradictions & Validation
Discussion of any contradictory information and how it was validated.

## Insights & Recommendations
Synthesized insights, hypotheses, and trends identified.

## Sources Cited
List of all sources with URLs in proper citation format. Format sources as markdown links: [Title](URL)

Make the report professional, clear, and well-formatted in markdown.
""")
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({"report_data": report_data})
            
            report = response.content if hasattr(response, 'content') else str(response)
            
            logger.info("Report Builder: Report compilation complete")
            
            return report
        
        except Exception as e:
            logger.error(f"Report compilation failed: {e}")
            return self._template_report(query, sources, analysis, insights)
    
    def _format_report_data(self, query: str, sources: Dict[str, Any],
                           analysis: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """Format all data for the report generation prompt."""
        formatted = [f"RESEARCH QUERY: {query}\n"]
        
        # Sources
        formatted.append("SOURCES:")
        if sources.get("web"):
            formatted.append("Web Sources:")
            for web in sources["web"]:
                formatted.append(f"- {web.get('title', 'No title')}: {web.get('url', 'No URL')}")
        
        if sources.get("papers"):
            formatted.append("Research Papers:")
            for paper in sources["papers"]:
                formatted.append(f"- {paper.get('title', 'No title')}: {paper.get('url', 'No URL')}")
        
        if sources.get("news"):
            formatted.append("News Sources:")
            for news in sources["news"]:
                formatted.append(f"- {news.get('title', 'No title')}: {news.get('url', 'No URL')}")
        
        formatted.append("\n")
        
        # Analysis
        formatted.append("ANALYSIS:")
        if analysis.get("summary"):
            formatted.append("Summary:")
            for point in analysis["summary"]:
                formatted.append(f"- {point}")
        
        if analysis.get("contradictions"):
            formatted.append("Contradictions:")
            for contradiction in analysis["contradictions"]:
                formatted.append(f"- {contradiction}")
        
        if analysis.get("credibility"):
            formatted.append("Credibility Assessment:")
            for cred in analysis["credibility"]:
                formatted.append(f"- {cred}")
        
        formatted.append("\n")
        
        # Insights
        formatted.append("INSIGHTS:")
        if insights.get("insights"):
            formatted.append("Key Insights:")
            for insight in insights["insights"]:
                formatted.append(f"- {insight}")
        
        if insights.get("hypotheses"):
            formatted.append("Hypotheses:")
            for hypothesis in insights["hypotheses"]:
                formatted.append(f"- {hypothesis}")
        
        if insights.get("trends"):
            formatted.append("Trends:")
            for trend in insights["trends"]:
                formatted.append(f"- {trend}")
        
        if insights.get("reasoning_chains"):
            formatted.append("Reasoning Chains:")
            for chain in insights["reasoning_chains"]:
                formatted.append(f"- {chain}")
        
        return "\n".join(formatted)
    
    def _template_report(self, query: str, sources: Dict[str, Any],
                        analysis: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """Generate report using template if LLM is not available."""
        report = f"# Research Report: {query}\n\n"
        
        report += "## Executive Summary\n\n"
        report += "This report synthesizes findings from multiple sources including web articles, research papers, and news sources. "
        report += "The analysis identifies key trends, contradictions, and insights relevant to the research query.\n\n"
        
        report += "## Key Findings\n\n"
        if analysis.get("summary"):
            for point in analysis["summary"]:
                report += f"- {point}\n"
        report += "\n"
        
        report += "## Source Analysis\n\n"
        if analysis.get("credibility"):
            report += "### Credibility Assessment\n\n"
            for cred in analysis["credibility"]:
                report += f"- {cred}\n"
        report += "\n"
        
        report += "## Contradictions & Validation\n\n"
        if analysis.get("contradictions"):
            for contradiction in analysis["contradictions"]:
                report += f"- {contradiction}\n"
        else:
            report += "No significant contradictions identified across sources.\n"
        report += "\n"
        
        report += "## Insights & Recommendations\n\n"
        if insights.get("insights"):
            report += "### Key Insights\n\n"
            for insight in insights["insights"]:
                report += f"- {insight}\n"
            report += "\n"
        
        if insights.get("hypotheses"):
            report += "### Hypotheses\n\n"
            for hypothesis in insights["hypotheses"]:
                report += f"- {hypothesis}\n"
            report += "\n"
        
        if insights.get("trends"):
            report += "### Trends\n\n"
            for trend in insights["trends"]:
                report += f"- {trend}\n"
            report += "\n"
        
        report += "## Sources Cited\n\n"
        all_sources = []
        if sources.get("web"):
            all_sources.extend([(s.get("title", "No title"), s.get("url", "")) for s in sources["web"]])
        if sources.get("papers"):
            all_sources.extend([(s.get("title", "No title"), s.get("url", "")) for s in sources["papers"]])
        if sources.get("news"):
            all_sources.extend([(s.get("title", "No title"), s.get("url", "")) for s in sources["news"]])
        
        for i, (title, url) in enumerate(all_sources, 1):
            if url:
                # Create markdown link: [Title](URL)
                report += f"{i}. [{title}]({url})\n"
            else:
                report += f"{i}. {title}\n"
            report += "\n"
        
        return report

