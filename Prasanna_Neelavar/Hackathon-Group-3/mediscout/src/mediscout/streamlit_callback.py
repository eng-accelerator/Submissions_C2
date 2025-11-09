"""
Streamlit callback handler for LangChain/LangGraph.

Provides real-time updates to Streamlit UI during agent execution with progress bar.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain_core.callbacks.base import BaseCallbackHandler
from loguru import logger
import streamlit as st


class StreamlitCallbackHandler(BaseCallbackHandler):
    """Callback handler with progress bar and storytelling."""
    
    # Stage definitions with progress and storytelling
    STAGES = {
        "ValidateQueryAgent": {
            "name": "🔍 Validating Query",
            "description": "Analyzing your research question for medical relevance...",
            "progress": 15
        },
        "RetrieverAgent": {
            "name": "⛏️ Deep Mining Knowledge",
            "description": "Excavating insights from medical databases and literature...",
            "progress": 40
        },
        "CriticalAnalysisAgent": {
            "name": "🧬 Critical Analysis",
            "description": "Synthesizing evidence and extracting key findings...",
            "progress": 70
        },
        "ReportBuilderAgent": {
            "name": "📊 Compiling Report",
            "description": "Generating comprehensive medical research report...",
            "progress": 95
        }
    }
    
    def __init__(self, progress_container):
        """
        Initialize the callback handler with progress bar.
        
        Args:
            progress_container: Streamlit container for progress updates
        """
        super().__init__()
        self.progress_container = progress_container
        self.current_stage = None
        self.progress_bar = None
        self.status_text = None
        self.detail_text = None
        self.substep_text = None
        
        # Initialize progress UI
        if self.progress_container:
            with self.progress_container:
                self.progress_bar = st.progress(0, text="Initializing...")
                self.status_text = st.empty()
                self.detail_text = st.empty()
                self.substep_text = st.empty()
    
    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when a chain starts."""
        chain_name = serialized.get("name", "Unknown")
        
        if chain_name in self.STAGES:
            self.current_stage = chain_name
            self._update_progress()
            logger.info(f"Started: {chain_name}")
    
    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when a chain ends."""
        if self.current_stage:
            logger.info(f"Completed: {self.current_stage}")
            
            # Mark stage as complete
            if self.current_stage == "ReportBuilderAgent":
                self._complete()
    
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when LLM starts."""
        self._update_substep("🤖 AI model processing...")
    
    def on_llm_end(
        self,
        response: Any,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when LLM ends."""
        self._update_substep("✅ AI analysis complete")
    
    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when a tool starts."""
        tool_name = serialized.get("name", "tool")
        self._update_substep(f"🔧 {tool_name}...")
    
    def on_error(
        self,
        error: Exception,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when an error occurs."""
        logger.error(f"Error: {error}")
        if self.status_text:
            self.status_text.error(f"❌ Error: {str(error)[:150]}")
    
    def _update_progress(self):
        """Update the progress bar and status with storytelling."""
        if not self.progress_container or not self.current_stage:
            return
        
        stage_info = self.STAGES.get(self.current_stage)
        if not stage_info:
            return
        
        # Update progress bar with label
        if self.progress_bar:
            self.progress_bar.progress(
                stage_info["progress"],
                text=stage_info["name"]
            )
        
        # Update status with storytelling
        if self.status_text:
            self.status_text.markdown(f"**{stage_info['name']}**")
        
        if self.detail_text:
            self.detail_text.caption(stage_info['description'])
    
    def _update_substep(self, message: str):
        """Update substep information."""
        if self.substep_text:
            self.substep_text.caption(f"  {message}")
    
    def _complete(self):
        """Mark the entire process as complete."""
        if self.progress_bar:
            self.progress_bar.progress(100, text="✨ Complete!")
        
        if self.status_text:
            self.status_text.markdown("**✨ Research Analysis Complete**")
        
        if self.detail_text:
            self.detail_text.caption("Your comprehensive report is ready!")
        
        if self.substep_text:
            self.substep_text.empty()
