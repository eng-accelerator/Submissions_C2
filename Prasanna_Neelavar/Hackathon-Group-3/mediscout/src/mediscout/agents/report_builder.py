"""
Report Builder Agent for MediScout.

Compiles analysis results into a structured Markdown research report.
"""

from typing import Dict, Any
from datetime import datetime
from loguru import logger

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from mediscout.config import get_settings
from mediscout.schemas import AnalysisResult, Report
from mediscout.state import ResearchState


REPORT_PROMPT = """Create a brief medical research report in Markdown:

**Topic:** {topic}

**Analysis:** {analysis_summary}

Include:
# Summary
- Key findings (2-3 sentences)

## Main Results  
- Bullet points from sources

## Sources
- List source titles

Keep it concise and evidence-based.
"""


class ReportBuilderAgent:
    """Agent for building structured research reports."""
    
    def __init__(self):
        """Initialize the report builder agent."""
        self.settings = get_settings()
        
        # Use the configured model from settings (works with your OpenRouter account)
        # This avoids issues with free model availability
        
        # Initialize LLM with OpenRouter
        self.llm = ChatOpenAI(
            model=self.settings.openrouter_model,
            temperature=0.3,  # Slightly higher for better writing
            max_tokens=2000,  # Reduced for speed
            timeout=10,  # Aggressive timeout
            api_key=self.settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        self.prompt = ChatPromptTemplate.from_template(REPORT_PROMPT)
        
        self.chain = self.prompt | self.llm
        
        logger.info("Report Builder Agent initialized")
    
    def __call__(self, state: ResearchState) -> Dict[str, Any]:
        """
        Build the final research report.
        
        Args:
            state: Current research state
            
        Returns:
            Updated state with final report
        """
        topic = state["research_topic"]
        analysis_results = state.get("analysis_results", [])
        retrieved_docs = state.get("retrieved_documents", [])
        
        if not analysis_results:
            logger.warning("No analysis results to compile into report")
            return {
                "final_report_markdown": self._create_empty_report(topic),
                "current_stage": "report_complete"
            }
        
        logger.info(f"Building report for {len(analysis_results)} analyzed documents")
        
        try:
            # Prepare analysis summary
            analysis_summary = self._format_analysis_for_prompt(
                analysis_results,
                retrieved_docs
            )
            
            # Generate report
            result = self.chain.invoke({
                "topic": topic,
                "analysis_summary": analysis_summary
            })
            
            report_markdown = result.content
            
            # Add metadata footer
            report_markdown += self._create_footer(len(analysis_results))
            
            logger.info("Report generation complete")
            
            return {
                "final_report_markdown": report_markdown,
                "current_stage": "report_complete"
            }
        
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {
                "final_report_markdown": self._create_fallback_report(
                    topic, analysis_results, retrieved_docs
                ),
                "current_stage": "report_complete",
                "error_message": f"Report generation partially failed: {e}"
            }
    
    def _format_analysis_for_prompt(
        self,
        analyses: list[AnalysisResult],
        documents: list
    ) -> str:
        """Format analysis results for the LLM prompt."""
        lines = []
        
        for i, analysis in enumerate(analyses, 1):
            doc_id = analysis.document_id
            doc = next((d for d in documents if d.id == doc_id), None)
            
            lines.append(f"\n### Document {i}: {doc.title if doc else 'Unknown'}")
            lines.append(f"**ID:** {doc_id}")
            lines.append(f"**Source:** {doc.source if doc else 'unknown'}")
            lines.append(f"**Summary:** {analysis.summary}")
            
            if analysis.study_design:
                lines.append(f"**Study Design:** {analysis.study_design}")
            
            if analysis.key_findings:
                lines.append(f"**Key Findings:** {', '.join(analysis.key_findings)}")
            
            if analysis.outcomes:
                lines.append(f"**Outcomes:** {', '.join(analysis.outcomes)}")
            
            if analysis.statistical_significance:
                lines.append(f"**Statistics:** {analysis.statistical_significance}")
            
            lines.append(f"**Reliability:** {analysis.reliability_score:.2f}/1.0")
            
            if analysis.contradictions:
                lines.append(f"**Contradictions:** {'; '.join(analysis.contradictions)}")
            
            if analysis.limitations:
                lines.append(f"**Limitations:** {'; '.join(analysis.limitations)}")
        
        return "\n".join(lines)
    
    def _create_footer(self, doc_count: int) -> str:
        """Create report footer with metadata."""
        return f"""

---

## Report Metadata

- **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Documents Analyzed:** {doc_count}
- **Generated by:** MediScout AI Research Assistant
- **Version:** 0.1.0 (MVP)

---

## Disclaimer

This report is generated by an AI system for research and informational purposes only. It should not be used for clinical decision-making or as a substitute for professional medical advice. All findings should be validated by qualified medical professionals. The system may contain errors or omissions. Always consult primary sources and domain experts before acting on this information.
"""
    
    def _create_empty_report(self, topic: str) -> str:
        """Create a report when no results are available."""
        return f"""# Research Report: {topic}

## Executive Summary

No documents were found or analyzed for this research topic. Please try:
- Uploading relevant documents to the knowledge base
- Refining your search query
- Checking your internet connection for PubMed access

## Next Steps

1. Upload PDF or TXT documents related to your research topic
2. Ensure your query includes specific medical terms
3. Try broader or alternative search terms

{self._create_footer(0)}
"""
    
    def _create_fallback_report(
        self,
        topic: str,
        analyses: list,
        documents: list
    ) -> str:
        """Create a basic report when AI generation fails."""
        report = f"""# Research Report: {topic}

## Executive Summary

Analysis completed for {len(analyses)} documents. Detailed report generation encountered an error. Below is a summary of analyzed sources.

## Analyzed Documents

"""
        
        for i, analysis in enumerate(analyses, 1):
            doc = next((d for d in documents if d.id == analysis.document_id), None)
            
            report += f"""
### {i}. {doc.title if doc else 'Unknown Document'}

**Source:** {doc.source if doc else 'unknown'}  
**Summary:** {analysis.summary}

**Key Findings:**
"""
            for finding in analysis.key_findings:
                report += f"- {finding}\n"
            
            report += "\n"
        
        report += self._create_footer(len(analyses))
        
        return report

