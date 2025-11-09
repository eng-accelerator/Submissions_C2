"""
Notification Agent
Pushes solutions directly to Slack channels
"""
from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from config import Config
import logging

logger = logging.getLogger(__name__)

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    logger.warning("slack-sdk not available. Install with: pip install slack-sdk")


class NotificationAgent(BaseAgent):
    """Agent responsible for sending notifications to Slack"""
    
    def __init__(self, api_key: str = None):
        super().__init__(name="Notification Agent", api_key=api_key)
        self.slack_client = self._initialize_slack()
    
    def _initialize_slack(self) -> Optional[WebClient]:
        """Initialize Slack client"""
        if not SLACK_AVAILABLE:
            logger.warning("Slack SDK not available")
            return None
        
        if not Config.has_slack_integration():
            logger.info("Slack integration not configured (optional)")
            return None
        
        try:
            client = WebClient(token=Config.SLACK_BOT_TOKEN)
            # Test the connection
            client.auth_test()
            logger.info("Slack client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Slack client: {e}")
            return None
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send notifications to Slack
        
        Args:
            input_data: Dict with 'remediations' from RemediationAgent
            
        Returns:
            Dict with notification results
        """
        self.status = "processing"
        self.log_action("Starting notification dispatch")
        
        try:
            remediations = input_data.get("remediations", [])
            summary = input_data.get("summary", "Incident analysis completed")
            
            if not remediations:
                return {
                    "success": True,
                    "agent": self.name,
                    "message": "No remediations to notify",
                    "notifications_sent": 0
                }
            
            # Format notification message
            message = self._format_slack_message(remediations, summary)
            
            # Send to Slack if configured
            if self.slack_client and Config.SLACK_CHANNEL_ID:
                try:
                    response = self.slack_client.chat_postMessage(
                        channel=Config.SLACK_CHANNEL_ID,
                        blocks=message["blocks"],
                        text=message["fallback_text"]
                    )
                    
                    self.status = "completed"
                    self.log_action(f"Sent notification to Slack (ts: {response['ts']})")
                    
                    return {
                        "success": True,
                        "agent": self.name,
                        "notifications_sent": 1,
                        "slack_ts": response["ts"],
                        "channel": Config.SLACK_CHANNEL_ID,
                        "message_preview": message["fallback_text"][:200],
                        "execution_log": self.execution_log
                    }
                    
                except SlackApiError as e:
                    logger.error(f"Slack API error: {e.response['error']}")
                    raise
            else:
                # Simulation mode
                self.status = "completed"
                self.log_action("Notification prepared (Slack not configured)")
                
                return {
                    "success": True,
                    "agent": self.name,
                    "notifications_sent": 0,
                    "mode": "simulation",
                    "message_preview": message["fallback_text"][:500],
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
    
    def _format_slack_message(self, remediations: list, summary: str) -> Dict[str, Any]:
        """Format message for Slack with rich blocks"""
        
        # Create fallback text
        fallback_text = f"🚨 DevOps Incident Alert\n\n{summary}\n\nFound {len(remediations)} issues requiring attention."
        
        # Create Slack blocks for rich formatting
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 DevOps Incident Alert",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:*\n{summary}"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add remediation details (limit to 5 for Slack)
        for i, rem in enumerate(remediations[:5], 1):
            issue = rem["issue"]
            plan = rem["remediation_plan"]
            
            # Truncate if too long
            if len(plan) > 500:
                plan = plan[:500] + "..."
            
            severity_emoji = {
                "CRITICAL": "🔴",
                "ERROR": "🟠",
                "WARNING": "🟡"
            }.get(issue["severity"], "⚪")
            
            blocks.extend([
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{severity_emoji} *Issue #{i}: {issue['category'].upper()}*\n```{issue['message'][:150]}```"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Remediation Plan:*\n{plan}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Confidence: {rem['confidence']} | Sources: {rem['knowledge_sources']}"
                        }
                    ]
                }
            ])
            
            if i < len(remediations):
                blocks.append({"type": "divider"})
        
        # Add footer
        if len(remediations) > 5:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"_Showing 5 of {len(remediations)} total issues. Check the dashboard for complete details._"
                    }
                ]
            })
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🔗 *View full analysis in the DevOps Incident Suite dashboard*"
            }
        })
        
        return {
            "blocks": blocks,
            "fallback_text": fallback_text
        }

