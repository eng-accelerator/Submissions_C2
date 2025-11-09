"""
LangGraph Orchestration Coordinator
Manages the multi-agent workflow.
"""

import logging
from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
from agents.retriever import ContextualRetrieverAgent
from agents.enrichment import DataEnrichmentAgent
from agents.analyzer import CriticalAnalysisAgent
from agents.insight_generator import InsightGenerationAgent
from agents.report_builder import ReportBuilderAgent

logger = logging.getLogger(__name__)


class ResearchState(TypedDict):
    """State schema for the research workflow."""
    query: str
    sources: Dict[str, Any]
    analysis: Dict[str, Any]
    insights: Dict[str, Any]
    report: str
    error: str


class ResearchWorkflow:
    """Orchestrates the multi-agent research workflow using LangGraph."""
    
    def __init__(self):
        """Initialize agents and build workflow graph."""
        logger.info("Initializing Research Workflow")
        
        # Initialize agents
        self.retriever = ContextualRetrieverAgent()
        self.enricher = DataEnrichmentAgent()
        self.analyzer = CriticalAnalysisAgent()
        self.insight_generator = InsightGenerationAgent()
        self.report_builder = ReportBuilderAgent()
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        
        logger.info("Research Workflow initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        # Create state graph
        graph = StateGraph(ResearchState)
        
        # Add nodes (agents)
        graph.add_node("retriever", self._retriever_node)
        graph.add_node("enricher", self._enricher_node)
        graph.add_node("analyzer", self._analyzer_node)
        graph.add_node("insight_generator", self._insight_generator_node)
        graph.add_node("report_builder", self._report_builder_node)
        
        # Define edges (linear flow)
        graph.set_entry_point("retriever")
        graph.add_edge("retriever", "enricher")
        graph.add_edge("enricher", "analyzer")
        graph.add_edge("analyzer", "insight_generator")
        graph.add_edge("insight_generator", "report_builder")
        graph.add_edge("report_builder", END)
        
        # Compile workflow
        return graph.compile()
    
    def _retriever_node(self, state: ResearchState) -> ResearchState:
        """Retriever agent node."""
        try:
            logger.info(f"Workflow: Running Retriever for query: {state['query']}")
            sources = self.retriever.retrieve(state["query"])
            state["sources"] = sources
            logger.info("Workflow: Retriever completed")
        except Exception as e:
            logger.error(f"Retriever node failed: {e}")
            state["error"] = f"Retrieval failed: {str(e)}"
            state["sources"] = {"web": [], "papers": [], "news": [], "query": state["query"]}
        return state
    
    def _enricher_node(self, state: ResearchState) -> ResearchState:
        """Enrichment agent node."""
        try:
            logger.info("Workflow: Running Enricher")
            enriched_sources = self.enricher.enrich_sources(state["sources"])
            state["sources"] = enriched_sources
            logger.info("Workflow: Enricher completed")
        except Exception as e:
            logger.error(f"Enricher node failed: {e}")
            # Continue with original sources if enrichment fails
            logger.warning("Continuing with original sources (enrichment failed)")
        return state
    
    def _analyzer_node(self, state: ResearchState) -> ResearchState:
        """Analyzer agent node."""
        try:
            logger.info("Workflow: Running Analyzer")
            analysis = self.analyzer.analyze(state["sources"])
            state["analysis"] = analysis
            logger.info("Workflow: Analyzer completed")
        except Exception as e:
            logger.error(f"Analyzer node failed: {e}")
            state["error"] = f"Analysis failed: {str(e)}"
            state["analysis"] = {
                "summary": [],
                "contradictions": [],
                "credibility": [],
                "key_claims": []
            }
        return state
    
    def _insight_generator_node(self, state: ResearchState) -> ResearchState:
        """Insight generator agent node."""
        try:
            logger.info("Workflow: Running Insight Generator")
            insights = self.insight_generator.generate(
                state["analysis"],
                state["query"]
            )
            state["insights"] = insights
            logger.info("Workflow: Insight Generator completed")
        except Exception as e:
            logger.error(f"Insight generator node failed: {e}")
            state["error"] = f"Insight generation failed: {str(e)}"
            state["insights"] = {
                "insights": [],
                "hypotheses": [],
                "trends": [],
                "reasoning_chains": []
            }
        return state
    
    def _report_builder_node(self, state: ResearchState) -> ResearchState:
        """Report builder agent node."""
        try:
            logger.info("Workflow: Running Report Builder")
            report = self.report_builder.compile(
                state["query"],
                state["sources"],
                state["analysis"],
                state["insights"]
            )
            state["report"] = report
            logger.info("Workflow: Report Builder completed")
        except Exception as e:
            logger.error(f"Report builder node failed: {e}")
            state["error"] = f"Report building failed: {str(e)}"
            state["report"] = f"# Error\n\nFailed to generate report: {str(e)}"
        return state
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Execute the research workflow.
        
        Args:
            query: Research query
            
        Returns:
            Complete research results with sources, analysis, insights, and report
        """
        logger.info(f"Starting research workflow for query: {query}")
        
        initial_state: ResearchState = {
            "query": query,
            "sources": {},
            "analysis": {},
            "insights": {},
            "report": "",
            "error": ""
        }
        
        try:
            result = self.workflow.invoke(initial_state)
            logger.info("Research workflow completed successfully")
            return result
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            initial_state["error"] = str(e)
            initial_state["report"] = f"# Error\n\nWorkflow failed: {str(e)}"
            return initial_state

