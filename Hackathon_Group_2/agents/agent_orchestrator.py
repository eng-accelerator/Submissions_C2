"""
LangGraph-based Multi-Agent Orchestrator
Coordinates the three agents: Error Classification, Solution Finding, and Notification
"""
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import operator

from agents.error_classification_agent import ErrorClassificationAgent
from agents.solution_agent import SolutionAgent
from agents.notification_agent import NotificationAgent


class AgentState(TypedDict):
    """State shared between agents"""
    # Input
    log_files: List[Dict[str, str]]  # List of {filename, content}
    api_key: str
    
    # Error Classification Agent output
    classification_result: Optional[Dict[str, Any]]
    aggregated_errors: Optional[Dict[str, Any]]
    
    # Solution Agent output
    solutions: Optional[List[Dict[str, Any]]]
    selected_solution: Optional[Dict[str, Any]]
    
    # Notification Agent output
    notification_results: Optional[Dict[str, Any]]
    
    # Metadata
    current_step: str
    errors: List[str]


class MultiAgentOrchestrator:
    """Orchestrates the multi-agent workflow using LangGraph"""
    
    def __init__(self, api_key: str, slack_webhook: Optional[str] = None, jira_config: Optional[Dict] = None):
        self.api_key = api_key
        self.classification_agent = ErrorClassificationAgent(api_key)
        self.solution_agent = SolutionAgent(api_key)
        self.notification_agent = NotificationAgent(slack_webhook, jira_config)
        
        # Build the graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_errors", self.classify_errors_node)
        workflow.add_node("find_solutions", self.find_solutions_node)
        workflow.add_node("send_notifications", self.send_notifications_node)
        
        # Define edges
        workflow.set_entry_point("classify_errors")
        workflow.add_edge("classify_errors", "find_solutions")
        workflow.add_edge("find_solutions", "send_notifications")
        workflow.add_edge("send_notifications", END)
        
        return workflow.compile()
    
    def classify_errors_node(self, state: AgentState) -> AgentState:
        """Node 1: Error Classification Agent"""
        try:
            state["current_step"] = "classifying_errors"
            
            if not state.get("log_files"):
                state["errors"].append("No log files provided")
                return state
            
            # Process multiple log files
            result = self.classification_agent.process_multiple_logs(state["log_files"])
            
            state["classification_result"] = result
            state["aggregated_errors"] = result.get("aggregated_errors", {})
            state["current_step"] = "classification_complete"
            
        except Exception as e:
            state["errors"].append(f"Classification error: {str(e)}")
            state["current_step"] = "classification_failed"
        
        return state
    
    def find_solutions_node(self, state: AgentState) -> AgentState:
        """Node 2: Solution Finding Agent"""
        try:
            state["current_step"] = "finding_solutions"
            
            classification_result = state.get("classification_result")
            if not classification_result:
                state["errors"].append("No classification result available")
                return state
            
            # Get the primary error for solution finding
            aggregated_errors = state.get("aggregated_errors", {})
            aggregated_analysis = classification_result.get("aggregated_analysis", {})
            
            if not aggregated_errors:
                state["errors"].append("No errors found to generate solutions for")
                return state
            
            # Find top error
            top_error = max(aggregated_errors.items(), key=lambda x: x[1].get('count', 0))
            error_type = top_error[0]
            error_details = top_error[1]
            severity = error_details.get('severity', 'Medium')
            
            # Find solutions
            solutions = self.solution_agent.find_solutions(
                error_type=error_type,
                severity=severity,
                error_details=error_details,
                aggregated_analysis=aggregated_analysis
            )
            
            # Rank solutions
            solutions = self.solution_agent.rank_solutions(solutions)
            
            state["solutions"] = solutions
            state["current_step"] = "solutions_found"
            
        except Exception as e:
            state["errors"].append(f"Solution finding error: {str(e)}")
            state["current_step"] = "solution_finding_failed"
        
        return state
    
    def send_notifications_node(self, state: AgentState) -> AgentState:
        """Node 3: Notification Agent"""
        try:
            state["current_step"] = "sending_notifications"
            
            selected_solution = state.get("selected_solution")
            if not selected_solution:
                state["errors"].append("No solution selected for notification")
                state["current_step"] = "notification_skipped"
                return state
            
            classification_result = state.get("classification_result", {})
            aggregated_analysis = classification_result.get("aggregated_analysis", {})
            
            # Get error information
            aggregated_errors = state.get("aggregated_errors", {})
            if aggregated_errors:
                top_error = max(aggregated_errors.items(), key=lambda x: x[1].get('count', 0))
                error_type = top_error[0]
                error_details = top_error[1]
                severity = error_details.get('severity', 'Medium')
                
                # Extract causes from aggregated analysis
                causes = [{
                    'title': finding,
                    'description': finding
                } for finding in aggregated_analysis.get('key_findings', [])]
                
                if not causes:
                    causes = [{
                        'title': error_type,
                        'description': f"Error occurred {error_details.get('count', 0)} times"
                    }]
                
                # Get log content from first file
                log_content = ""
                if state.get("log_files"):
                    log_content = state["log_files"][0].get("content", "")[:5000]
                
                # Send notifications
                notification_results = self.notification_agent.send_notifications(
                    error_type=error_type,
                    severity=severity,
                    causes=causes,
                    selected_solution=selected_solution,
                    log_content=log_content,
                    aggregated_data=classification_result
                )
                
                state["notification_results"] = notification_results
                state["current_step"] = "notifications_sent"
            else:
                state["errors"].append("No errors to notify about")
                state["current_step"] = "notification_skipped"
        
        except Exception as e:
            state["errors"].append(f"Notification error: {str(e)}")
            state["current_step"] = "notification_failed"
        
        return state
    
    def run_workflow(
        self,
        log_files: List[Dict[str, str]],
        selected_solution: Optional[Dict[str, Any]] = None,
        send_notifications: bool = False
    ) -> Dict[str, Any]:
        """Run the complete multi-agent workflow"""
        initial_state: AgentState = {
            "log_files": log_files,
            "api_key": self.api_key,
            "classification_result": None,
            "aggregated_errors": None,
            "solutions": None,
            "selected_solution": selected_solution,
            "notification_results": None,
            "current_step": "initialized",
            "errors": []
        }
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        
        return {
            "classification_result": final_state.get("classification_result"),
            "aggregated_errors": final_state.get("aggregated_errors"),
            "solutions": final_state.get("solutions"),
            "selected_solution": final_state.get("selected_solution"),
            "notification_results": final_state.get("notification_results") if send_notifications else None,
            "current_step": final_state.get("current_step"),
            "errors": final_state.get("errors", []),
            "success": len(final_state.get("errors", [])) == 0
        }
    
    def run_classification_only(self, log_files: List[Dict[str, str]]) -> Dict[str, Any]:
        """Run only the classification agent"""
        initial_state: AgentState = {
            "log_files": log_files,
            "api_key": self.api_key,
            "classification_result": None,
            "aggregated_errors": None,
            "solutions": None,
            "selected_solution": None,
            "notification_results": None,
            "current_step": "initialized",
            "errors": []
        }
        
        # Run only classification
        state = self.classify_errors_node(initial_state)
        
        return {
            "classification_result": state.get("classification_result"),
            "aggregated_errors": state.get("aggregated_errors"),
            "current_step": state.get("current_step"),
            "errors": state.get("errors", []),
            "success": len(state.get("errors", [])) == 0
        }
    
    def run_with_selected_solution(
        self,
        log_files: List[Dict[str, str]],
        selected_solution: Dict[str, Any],
        send_notifications: bool = True
    ) -> Dict[str, Any]:
        """Run workflow with a pre-selected solution"""
        initial_state: AgentState = {
            "log_files": log_files,
            "api_key": self.api_key,
            "classification_result": None,
            "aggregated_errors": None,
            "solutions": None,
            "selected_solution": selected_solution,
            "notification_results": None,
            "current_step": "initialized",
            "errors": []
        }
        
        # Run classification
        state = self.classify_errors_node(initial_state)
        
        # Skip solution finding, go directly to notifications if requested
        if send_notifications:
            state = self.send_notifications_node(state)
        
        return {
            "classification_result": state.get("classification_result"),
            "aggregated_errors": state.get("aggregated_errors"),
            "selected_solution": state.get("selected_solution"),
            "notification_results": state.get("notification_results"),
            "current_step": state.get("current_step"),
            "errors": state.get("errors", []),
            "success": len(state.get("errors", [])) == 0
        }

