"""
LangGraph state management for MediScout workflow.

Defines the state schema that flows through the agent pipeline.
"""

from typing import List, Optional, TypedDict, Annotated
import operator
from mediscout.schemas import (
    Document,
    AnalysisResult,
    Hypothesis,
    QueryValidation,
    RetrievalResult
)


class ResearchState(TypedDict):
    """
    State object that flows through the LangGraph workflow.
    
    Uses TypedDict for type safety and Annotated for reducer functions.
    """
    
    # Input
    research_topic: str  # Original user query
    search_scope: Optional[str]  # Search scope: local_only, local_and_pubmed, pubmed_only
    
    # Query Validation
    query_validation: Optional[QueryValidation]  # Result of query validation
    refined_query: Optional[str]  # Improved query after validation
    
    # Retrieval
    retrieval_result: Optional[RetrievalResult]  # Combined retrieval results
    retrieved_documents: Annotated[List[Document], operator.add]  # All retrieved docs
    
    # Analysis
    analysis_results: Annotated[List[AnalysisResult], operator.add]  # Per-document analysis
    
    # Insights (optional for MVP)
    generated_hypotheses: Annotated[List[Hypothesis], operator.add]  # Novel hypotheses
    
    # Report
    final_report_markdown: Optional[str]  # Generated report in Markdown
    
    # Metadata
    current_stage: str  # Current workflow stage for UI
    error_message: Optional[str]  # Error details if any
    processing_time_seconds: float  # Total processing time

