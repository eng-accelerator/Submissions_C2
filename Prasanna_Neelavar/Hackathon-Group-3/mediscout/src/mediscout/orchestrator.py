"""
LangGraph orchestrator for MediScout research workflow.

Coordinates the execution of specialized agents in a sequential pipeline.
"""

import time
from typing import Dict, Any
from loguru import logger

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

from mediscout.state import ResearchState
from mediscout.agents.validate_query import ValidateQueryAgent
from mediscout.agents.retriever import RetrieverAgent
from mediscout.agents.critical_analysis import CriticalAnalysisAgent
from mediscout.agents.report_builder import ReportBuilderAgent


class ResearchOrchestrator:
    """Orchestrates the multi-agent research workflow using LangGraph."""
    
    def __init__(self):
        """Initialize the orchestrator and all agents."""
        logger.info("Initializing Research Orchestrator")
        
        # Initialize all agents
        self.validate_agent = ValidateQueryAgent()
        self.retriever_agent = RetrieverAgent()
        self.analysis_agent = CriticalAnalysisAgent()
        self.report_agent = ReportBuilderAgent()
        
        # Build the workflow graph
        self.graph = self._build_graph()
        
        logger.info("Research Orchestrator initialized successfully")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            Compiled StateGraph
        """
        # Create the graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes (each node is an agent)
        workflow.add_node("validate_query", self.validate_agent)
        workflow.add_node("retrieve_documents", self.retriever_agent)
        workflow.add_node("analyze_documents", self.analysis_agent)
        workflow.add_node("build_report", self.report_agent)
        
        # Define the workflow edges (sequential pipeline with early exit)
        workflow.set_entry_point("validate_query")
        
        # Add conditional edge from validation - exit early if validation fails
        def check_validation(state):
            """Check if validation succeeded."""
            if state.get("current_stage") == "validation_failed":
                return END
            return "retrieve_documents"
        
        workflow.add_conditional_edges(
            "validate_query",
            check_validation,
            {
                END: END,
                "retrieve_documents": "retrieve_documents"
            }
        )
        
        workflow.add_edge("retrieve_documents", "analyze_documents")
        workflow.add_edge("analyze_documents", "build_report")
        workflow.add_edge("build_report", END)
        
        # Compile the graph
        compiled_graph = workflow.compile()
        
        logger.info("Workflow graph built successfully")
        return compiled_graph
    
    def run_research(
        self,
        research_topic: str,
        search_scope: str = "local_and_pubmed",
        config: RunnableConfig = None
    ) -> Dict[str, Any]:
        """
        Execute the complete research workflow.
        
        Args:
            research_topic: The research question/topic
            search_scope: Where to search (local_only, local_and_pubmed, pubmed_only)
            config: Optional LangChain config (for callbacks)
            
        Returns:
            Final state with research report
        """
        logger.info(f"Starting research workflow for: '{research_topic}' (scope: {search_scope})")
        start_time = time.time()
        
        # Initialize state
        initial_state: ResearchState = {
            "research_topic": research_topic,
            "search_scope": search_scope,
            "query_validation": None,
            "refined_query": None,
            "retrieval_result": None,
            "retrieved_documents": [],
            "analysis_results": [],
            "generated_hypotheses": [],
            "final_report_markdown": None,
            "current_stage": "initializing",
            "error_message": None,
            "processing_time_seconds": 0.0
        }
        
        try:
            # Run the graph
            if config:
                final_state = self.graph.invoke(initial_state, config=config)
            else:
                final_state = self.graph.invoke(initial_state)
            
            # Add processing time
            final_state["processing_time_seconds"] = time.time() - start_time
            
            logger.info(
                f"Research workflow complete in {final_state['processing_time_seconds']:.2f}s"
            )
            
            return final_state
        
        except Exception as e:
            logger.error(f"Research workflow failed: {e}")
            
            error_state = initial_state.copy()
            error_state.update({
                "error_message": str(e),
                "current_stage": "failed",
                "processing_time_seconds": time.time() - start_time,
                "final_report_markdown": self._create_error_report(research_topic, str(e))
            })
            
            return error_state
    
    def _create_error_report(self, topic: str, error: str) -> str:
        """Create an error report when workflow fails."""
        return f"""# Research Report: {topic}

## Error

The research workflow encountered an error and could not complete:

```
{error}
```

## Troubleshooting Steps

1. **Check API Keys:** Ensure your OpenRouter API key is set in the .env file
2. **Check Internet Connection:** PubMed access requires internet connectivity
3. **Check Query:** Ensure your research topic is a valid medical question
4. **Check Logs:** Review the application logs for detailed error information

## Next Steps

- Verify your configuration in the .env file
- Try a simpler or more specific research query
- Check that you have uploaded documents to the knowledge base
- Consult the documentation or support channels

---

**Generated by:** MediScout AI Research Assistant  
**Status:** Failed  
**Error Type:** Workflow Exception
"""
    
    def get_retriever(self) -> RetrieverAgent:
        """Get the retriever agent (for document ingestion)."""
        return self.retriever_agent

