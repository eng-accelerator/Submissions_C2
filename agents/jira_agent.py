"""
JIRA Ticket Agent
Creates JIRA tickets for critical issues
"""
from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from config import Config
import logging

logger = logging.getLogger(__name__)

try:
    from jira import JIRA
    from jira.exceptions import JIRAError
    JIRA_AVAILABLE = True
except ImportError:
    JIRA_AVAILABLE = False
    logger.warning("jira not available. Install with: pip install jira")


class JiraAgent(BaseAgent):
    """Agent responsible for creating JIRA tickets"""
    
    def __init__(self, api_key: str = None):
        super().__init__(name="JIRA Agent", api_key=api_key)
        self.jira_client = self._initialize_jira()
    
    def _initialize_jira(self) -> Optional[JIRA]:
        """Initialize JIRA client"""
        if not JIRA_AVAILABLE:
            logger.warning("JIRA library not available")
            return None
        
        if not Config.has_jira_integration():
            logger.info("JIRA integration not configured (optional)")
            return None
        
        try:
            client = JIRA(
                server=Config.JIRA_URL,
                basic_auth=(Config.JIRA_EMAIL, Config.JIRA_API_TOKEN)
            )
            # Test the connection
            client.myself()
            logger.info("JIRA client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize JIRA client: {e}")
            return None
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create JIRA tickets for critical issues
        
        Args:
            input_data: Dict with 'remediations' from RemediationAgent
            
        Returns:
            Dict with ticket creation results
        """
        self.status = "processing"
        self.log_action("Starting JIRA ticket creation")
        
        try:
            remediations = input_data.get("remediations", [])
            
            # Filter for CRITICAL and ERROR severity only
            critical_issues = [
                rem for rem in remediations
                if rem["issue"]["severity"] in ["CRITICAL", "ERROR"]
            ]
            
            if not critical_issues:
                return {
                    "success": True,
                    "agent": self.name,
                    "message": "No critical issues requiring JIRA tickets",
                    "tickets_created": 0
                }
            
            tickets_created = []
            
            # Create tickets if JIRA is configured
            if self.jira_client:
                for rem in critical_issues[:5]:  # Limit to 5 tickets
                    ticket = self._create_ticket(rem)
                    if ticket:
                        tickets_created.append(ticket)
            else:
                # Simulation mode
                for rem in critical_issues[:5]:
                    tickets_created.append(self._simulate_ticket(rem))
            
            self.status = "completed"
            self.log_action(f"Created {len(tickets_created)} JIRA tickets")
            
            return {
                "success": True,
                "agent": self.name,
                "tickets_created": len(tickets_created),
                "tickets": tickets_created,
                "mode": "live" if self.jira_client else "simulation",
                "execution_log": self.execution_log
            }
            
        except Exception as e:
            self.status = "failed"
            self.log_action(f"Error: {str(e)}")
            logger.error(f"{self.name} failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def _create_ticket(self, remediation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create actual JIRA ticket"""
        try:
            issue = remediation["issue"]
            plan = remediation["remediation_plan"]
            
            # Prepare ticket fields
            summary = f"[{issue['severity']}] {issue['category'].upper()}: {issue['message'][:80]}"
            
            description = f"""*Incident Details:*
* Severity: {issue['severity']}
* Category: {issue['category']}
* Timestamp: {issue.get('timestamp', 'Unknown')}
* Message: {issue['message']}

*Remediation Plan:*
{plan}

*Additional Context:*
* Confidence: {remediation['confidence']}
* Knowledge Sources: {remediation['knowledge_sources']}

---
_This ticket was automatically created by the DevOps Incident Analysis Suite_
"""
            
            # Map severity to priority
            priority_map = {
                "CRITICAL": "Highest",
                "ERROR": "High",
                "WARNING": "Medium"
            }
            
            issue_dict = {
                'project': {'key': Config.JIRA_PROJECT_KEY},
                'summary': summary,
                'description': description,
                'issuetype': {'name': 'Bug'},
                'priority': {'name': priority_map.get(issue['severity'], 'Medium')},
                'labels': ['incident', 'automated', issue['category']]
            }
            
            new_issue = self.jira_client.create_issue(fields=issue_dict)
            
            return {
                "ticket_key": new_issue.key,
                "ticket_url": f"{Config.JIRA_URL}/browse/{new_issue.key}",
                "summary": summary,
                "priority": priority_map.get(issue['severity'], 'Medium')
            }
            
        except JIRAError as e:
            logger.error(f"JIRA API error: {e.text}")
            return None
        except Exception as e:
            logger.error(f"Failed to create JIRA ticket: {e}")
            return None
    
    def _simulate_ticket(self, remediation: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate ticket creation when JIRA is not configured"""
        issue = remediation["issue"]
        
        ticket_key = f"OPS-{abs(hash(issue['message'])) % 10000}"
        summary = f"[{issue['severity']}] {issue['category'].upper()}: {issue['message'][:80]}"
        
        return {
            "ticket_key": ticket_key,
            "ticket_url": f"https://your-jira.atlassian.net/browse/{ticket_key}",
            "summary": summary,
            "priority": "High" if issue['severity'] == "CRITICAL" else "Medium",
            "mode": "simulated"
        }

