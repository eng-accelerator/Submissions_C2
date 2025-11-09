"""
LangGraph Orchestrator
Manages workflow between all agents
"""
from typing import Dict, Any, TypedDict, Annotated
from typing_extensions import TypedDict
import operator
from langgraph.graph import StateGraph, END
from agents import (
    LogReaderAgent,
    RemediationAgent,
    NotificationAgent,
    JiraAgent,
    CookbookAgent,
    RCAAgent
)
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IncidentState(TypedDict):
    """State that flows through the agent graph"""
    logs: str
    log_analysis: Dict[str, Any]
    issues_found: list
    remediations: list
    notifications: Dict[str, Any]
    jira_tickets: Dict[str, Any]
    cookbook: Dict[str, Any]
    rca_report: Dict[str, Any]
    summary: str
    error: str
    agent_logs: Annotated[list, operator.add]


class IncidentOrchestrator:
    """Orchestrates multi-agent workflow using LangGraph"""
    
    def __init__(self, api_key: str = None, progress_callback=None):
        self.api_key = api_key
        self.progress_callback = progress_callback
        
        # Initialize all agents
        self.log_reader = LogReaderAgent(api_key)
        self.remediation = RemediationAgent(api_key)
        self.notification = NotificationAgent(api_key)
        self.jira = JiraAgent(api_key)
        self.cookbook = CookbookAgent(api_key)
        self.rca = RCAAgent(api_key)
        
        # Build the graph
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create workflow graph
        workflow = StateGraph(IncidentState)
        
        # Add nodes for each agent
        workflow.add_node("log_reader", self._log_reader_node)
        workflow.add_node("remediation", self._remediation_node)
        workflow.add_node("rca", self._rca_node)
        workflow.add_node("notification", self._notification_node)
        workflow.add_node("jira", self._jira_node)
        workflow.add_node("cookbook", self._cookbook_node)
        
        # Define the flow
        workflow.set_entry_point("log_reader")
        
        # Sequential flow through agents
        workflow.add_edge("log_reader", "remediation")
        workflow.add_edge("remediation", "rca")
        workflow.add_edge("rca", "notification")
        workflow.add_edge("notification", "jira")
        workflow.add_edge("jira", "cookbook")
        workflow.add_edge("cookbook", END)
        
        return workflow.compile()
    
    async def _log_reader_node(self, state: IncidentState) -> Dict[str, Any]:
        """Execute Log Reader Agent"""
        logger.info("🔍 Executing Log Reader Agent...")
        
        # Notify start if callback exists
        if self.progress_callback:
            await self.progress_callback("log_reader", "processing", "Parsing and classifying log entries...")
        
        try:
            result = await self.log_reader.execute({"logs": state["logs"]})
            
            # Notify completion
            if self.progress_callback:
                await self.progress_callback("log_reader", "completed", 
                    f"Analyzed {result.get('total_entries', 0)} log entries, found {len(result.get('issues_found', []))} issues")
            
            return {
                "log_analysis": result,
                "issues_found": result.get("issues_found", []),
                "summary": result.get("summary", ""),
                "agent_logs": [{
                    "agent": "Log Reader",
                    "status": "completed",
                    "details": f"Analyzed {result.get('total_entries', 0)} log entries, found {len(result.get('issues_found', []))} issues"
                }]
            }
        except Exception as e:
            logger.error(f"Log Reader failed: {e}")
            if self.progress_callback:
                await self.progress_callback("log_reader", "failed", str(e))
            return {
                "error": str(e),
                "agent_logs": [{"agent": "Log Reader", "status": "failed", "error": str(e)}]
            }
    
    async def _remediation_node(self, state: IncidentState) -> Dict[str, Any]:
        """Execute Remediation Agent"""
        logger.info("💊 Executing Remediation Agent...")
        
        if self.progress_callback:
            await self.progress_callback("remediation", "processing", "Finding solutions using RAG knowledge base...")
        
        try:
            result = await self.remediation.execute({
                "issues_found": state["issues_found"]
            })
            
            if self.progress_callback:
                await self.progress_callback("remediation", "completed", 
                    f"Generated {len(result.get('remediations', []))} remediation plans")
            
            return {
                "remediations": result.get("remediations", []),
                "agent_logs": [{
                    "agent": "Remediation",
                    "status": "completed",
                    "details": f"Generated {len(result.get('remediations', []))} remediation plans"
                }]
            }
        except Exception as e:
            logger.error(f"Remediation failed: {e}")
            if self.progress_callback:
                await self.progress_callback("remediation", "failed", str(e))
            return {
                "remediations": [],
                "agent_logs": [{"agent": "Remediation", "status": "failed", "error": str(e)}]
            }
    
    async def _notification_node(self, state: IncidentState) -> Dict[str, Any]:
        """Execute Notification Agent"""
        logger.info("📢 Executing Notification Agent...")
        
        if self.progress_callback:
            await self.progress_callback("notification", "processing", "Sending notifications to Slack...")
        
        try:
            result = await self.notification.execute({
                "remediations": state["remediations"],
                "summary": state["summary"]
            })
            
            if self.progress_callback:
                await self.progress_callback("notification", "completed", 
                    f"Sent {result.get('notifications_sent', 0)} notifications")
            
            return {
                "notifications": result,
                "agent_logs": [{
                    "agent": "Notification",
                    "status": "completed",
                    "details": f"Sent {result.get('notifications_sent', 0)} notifications"
                }]
            }
        except Exception as e:
            logger.error(f"Notification failed: {e}")
            if self.progress_callback:
                await self.progress_callback("notification", "failed", str(e))
            return {
                "notifications": {},
                "agent_logs": [{"agent": "Notification", "status": "failed", "error": str(e)}]
            }
    
    async def _jira_node(self, state: IncidentState) -> Dict[str, Any]:
        """Execute JIRA Agent"""
        logger.info("🎫 Executing JIRA Agent...")
        
        if self.progress_callback:
            await self.progress_callback("jira", "processing", "Creating JIRA tickets for critical issues...")
        
        try:
            result = await self.jira.execute({
                "remediations": state["remediations"]
            })
            
            if self.progress_callback:
                await self.progress_callback("jira", "completed", 
                    f"Created {result.get('tickets_created', 0)} tickets")
            
            return {
                "jira_tickets": result,
                "agent_logs": [{
                    "agent": "JIRA",
                    "status": "completed",
                    "details": f"Created {result.get('tickets_created', 0)} tickets"
                }]
            }
        except Exception as e:
            logger.error(f"JIRA failed: {e}")
            if self.progress_callback:
                await self.progress_callback("jira", "failed", str(e))
            return {
                "jira_tickets": {},
                "agent_logs": [{"agent": "JIRA", "status": "failed", "error": str(e)}]
            }
    
    async def _rca_node(self, state: IncidentState) -> Dict[str, Any]:
        """Execute RCA Agent"""
        logger.info("🔬 Executing RCA Agent...")
        
        if self.progress_callback:
            await self.progress_callback("rca", "processing", "Performing root cause analysis...")
        
        try:
            result = await self.rca.execute({
                "issues_found": state["issues_found"],
                "remediations": state["remediations"],
                "log_analysis": state["log_analysis"]
            })
            
            if self.progress_callback:
                await self.progress_callback("rca", "completed", "Root Cause Analysis completed")
            
            return {
                "rca_report": result.get("rca_report", {}),
                "agent_logs": [{
                    "agent": "RCA",
                    "status": "completed",
                    "details": "Root Cause Analysis completed"
                }]
            }
        except Exception as e:
            logger.error(f"RCA failed: {e}")
            if self.progress_callback:
                await self.progress_callback("rca", "failed", str(e))
            return {
                "rca_report": {},
                "agent_logs": [{"agent": "RCA", "status": "failed", "error": str(e)}]
            }
    
    async def _cookbook_node(self, state: IncidentState) -> Dict[str, Any]:
        """Execute Cookbook Agent"""
        logger.info("📚 Executing Cookbook Agent...")
        
        if self.progress_callback:
            await self.progress_callback("cookbook", "processing", "Generating incident playbook...")
        
        try:
            result = await self.cookbook.execute({
                "remediations": state["remediations"],
                "summary": state["summary"]
            })
            
            if self.progress_callback:
                await self.progress_callback("cookbook", "completed", "Incident playbook created")
            
            return {
                "cookbook": result.get("cookbook", {}),
                "agent_logs": [{
                    "agent": "Cookbook",
                    "status": "completed",
                    "details": "Incident playbook created"
                }]
            }
        except Exception as e:
            logger.error(f"Cookbook failed: {e}")
            if self.progress_callback:
                await self.progress_callback("cookbook", "failed", str(e))
            return {
                "cookbook": {},
                "agent_logs": [{"agent": "Cookbook", "status": "failed", "error": str(e)}]
            }
    
    async def process_incident(self, logs: str) -> Dict[str, Any]:
        """
        Process incident through all agents
        
        Args:
            logs: Raw log text
            
        Returns:
            Complete incident analysis with all agent results
        """
        logger.info("🚀 Starting incident analysis orchestration...")
        
        # Initialize state
        initial_state = {
            "logs": logs,
            "log_analysis": {},
            "issues_found": [],
            "remediations": [],
            "notifications": {},
            "jira_tickets": {},
            "cookbook": {},
            "rca_report": {},
            "summary": "",
            "error": "",
            "agent_logs": []
        }
        
        try:
            # Execute the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            logger.info("✅ Incident analysis completed successfully")
            
            return {
                "success": True,
                "state": final_state,
                "agent_timeline": final_state.get("agent_logs", [])
            }
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "state": initial_state
            }
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get status of all agents"""
        return {
            "log_reader": self.log_reader.status,
            "remediation": self.remediation.status,
            "rca": self.rca.status,
            "notification": self.notification.status,
            "jira": self.jira.status,
            "cookbook": self.cookbook.status
        }
    
    def reset_agents(self):
        """Reset all agents to initial state"""
        for agent in [self.log_reader, self.remediation, self.rca, self.notification, self.jira, self.cookbook]:
            agent.reset()
        logger.info("All agents reset")


# Convenience function for standalone use
async def analyze_logs(logs: str, api_key: str = None) -> Dict[str, Any]:
    """
    Analyze logs using the orchestrator
    
    Args:
        logs: Raw log text
        api_key: OpenAI API key
        
    Returns:
        Analysis results
    """
    orchestrator = IncidentOrchestrator(api_key)
    result = await orchestrator.process_incident(logs)
    return result

