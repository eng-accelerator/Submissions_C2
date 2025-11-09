"""
Critical Analysis Agent for MediScout.

Performs deep analysis of retrieved documents, extracting key information
and identifying contradictions.
"""

from typing import Dict, Any, List
from loguru import logger

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from mediscout.config import get_settings
from mediscout.schemas import Document, AnalysisResult
from mediscout.state import ResearchState


ANALYSIS_PROMPT = """Quick analysis of this medical document:

**Title:** {title}
**Content:** {content}

JSON response:
{{
    "summary": "brief 1-2 sentence summary",
    "key_findings": ["finding 1", "finding 2"],
    "reliability_score": 0.0-1.0,
    "limitations": ["main limitation"]
}}

Be concise.
"""


class CriticalAnalysisAgent:
    """Agent for critical analysis of medical documents."""
    
    def __init__(self):
        """Initialize the analysis agent."""
        self.settings = get_settings()
        
        # Use the configured model from settings (works with your OpenRouter account)
        # This avoids issues with free model availability
        
        # Initialize LLM with OpenRouter
        self.llm = ChatOpenAI(
            model=self.settings.openrouter_model,
            temperature=0.0,
            max_tokens=1000,  # Reduced for speed
            timeout=10,  # Aggressive timeout
            api_key=self.settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        self.prompt = ChatPromptTemplate.from_template(ANALYSIS_PROMPT)
        self.parser = JsonOutputParser()
        
        self.chain = self.prompt | self.llm | self.parser
        
        logger.info("Critical Analysis Agent initialized")
    
    def __call__(self, state: ResearchState) -> Dict[str, Any]:
        """
        Analyze all retrieved documents.
        
        Args:
            state: Current research state
            
        Returns:
            Updated state with analysis results
        """
        documents = state.get("retrieved_documents", [])
        
        if not documents:
            logger.warning("No documents to analyze")
            return {
                "analysis_results": [],
                "current_stage": "analysis_complete"
            }
        
        logger.info(f"Analyzing {len(documents)} documents")
        
        analysis_results = []
        
        for i, doc in enumerate(documents, 1):
            logger.info(f"Analyzing document {i}/{len(documents)}: {doc.title[:50]}...")
            
            try:
                result = self._analyze_document(doc)
                analysis_results.append(result)
                logger.info(f"Analysis complete for document {i}")
            
            except Exception as e:
                logger.error(f"Failed to analyze document {doc.id}: {e}")
                # Add a minimal result
                analysis_results.append(
                    AnalysisResult(
                        document_id=doc.id,
                        summary=doc.content[:500] + "...",
                        key_findings=["Analysis failed - content truncated"],
                        reliability_score=0.3
                    )
                )
        
        logger.info(f"Analysis complete: {len(analysis_results)} documents analyzed")
        
        return {
            "analysis_results": analysis_results,
            "current_stage": "analysis_complete"
        }
    
    def _analyze_document(self, doc: Document) -> AnalysisResult:
        """
        Analyze a single document.
        
        Args:
            doc: Document to analyze
            
        Returns:
            AnalysisResult with structured information
        """
        # Truncate content if too long (keep first 2000 words)
        content = doc.content
        words = content.split()
        if len(words) > 2000:
            content = " ".join(words[:2000]) + "... [truncated]"
        
        try:
            # Run analysis chain
            result = self.chain.invoke({
                "title": doc.title,
                "source": doc.source,
                "content": content
            })
            
            # Convert to AnalysisResult
            analysis = AnalysisResult(
                document_id=doc.id,
                summary=result.get("summary", "No summary available"),
                study_design=result.get("study_design"),
                key_findings=result.get("key_findings", []),
                patient_population=result.get("patient_population"),
                intervention=result.get("intervention"),
                outcomes=result.get("outcomes", []),
                statistical_significance=result.get("statistical_significance"),
                reliability_score=float(result.get("reliability_score", 0.5)),
                contradictions=result.get("contradictions", []),
                limitations=result.get("limitations", [])
            )
            
            return analysis
        
        except Exception as e:
            logger.error(f"LLM analysis failed for {doc.id}: {e}")
            # Fallback: create basic analysis
            return AnalysisResult(
                document_id=doc.id,
                summary=content[:500] + "...",
                key_findings=["Full analysis unavailable"],
                reliability_score=0.3
            )
    
    def identify_contradictions(self, analyses: List[AnalysisResult]) -> List[str]:
        """
        Identify contradictions across multiple analyses.
        
        Args:
            analyses: List of analysis results
            
        Returns:
            List of identified contradictions
        """
        contradictions = []
        
        for analysis in analyses:
            if analysis.contradictions:
                contradictions.extend(analysis.contradictions)
        
        return list(set(contradictions))  # Remove duplicates

