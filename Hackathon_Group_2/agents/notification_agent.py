"""
Agent 3: Notification Agent
Handles notifications to JIRA and Slack using existing notification_agents.py
"""
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path to import notification_agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from notification_agents import SlackNotifier, JIRANotifier
    JIRA_AVAILABLE = True
except ImportError:
    JIRA_AVAILABLE = False
    JIRANotifier = None
    SlackNotifier = None


class NotificationAgent:
    """Agent responsible for sending notifications to Slack and JIRA"""
    
    def __init__(self, slack_webhook: Optional[str] = None, jira_config: Optional[Dict] = None):
        self.slack_webhook = slack_webhook
        self.jira_config = jira_config or {}
        self.slack_notifier = None
        self.jira_notifier = None
        
        # Initialize Slack notifier if webhook provided
        if slack_webhook and SlackNotifier:
            try:
                self.slack_notifier = SlackNotifier(slack_webhook)
            except Exception as e:
                print(f"Failed to initialize Slack notifier: {str(e)}")
        
        # Initialize JIRA notifier if config provided
        if jira_config and JIRA_AVAILABLE and JIRANotifier:
            try:
                if all(k in jira_config for k in ['server', 'email', 'api_token']):
                    self.jira_notifier = JIRANotifier(
                        server=jira_config['server'],
                        email=jira_config['email'],
                        api_token=jira_config['api_token']
                    )
            except Exception as e:
                print(f"Failed to initialize JIRA notifier: {str(e)}")
    
    def send_slack_notification(
        self,
        error_type: str,
        severity: str,
        causes: List[Dict],
        selected_solution: Dict,
        aggregated_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Send notification to Slack"""
        if not self.slack_notifier:
            return {
                'success': False,
                'error': 'Slack notifier not initialized. Provide SLACK_WEBHOOK_URL.'
            }
        
        try:
            success = self.slack_notifier.send_error_notification(
                error_type=error_type,
                severity=severity,
                causes=causes,
                selected_solution=selected_solution
            )
            
            return {
                'success': success,
                'platform': 'Slack',
                'message': 'Notification sent successfully' if success else 'Failed to send notification'
            }
        except Exception as e:
            return {
                'success': False,
                'platform': 'Slack',
                'error': str(e)
            }
    
    def create_jira_ticket(
        self,
        error_type: str,
        severity: str,
        causes: List[Dict],
        selected_solution: Dict,
        log_content: str = "",
        aggregated_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create JIRA ticket"""
        if not self.jira_notifier:
            return {
                'success': False,
                'error': 'JIRA notifier not initialized. Provide JIRA configuration.'
            }
        
        project_key = self.jira_config.get('project_key')
        if not project_key:
            return {
                'success': False,
                'error': 'JIRA project key not provided.'
            }
        
        try:
            issue_type = self.jira_config.get('issue_type', 'Task')
            
            ticket = self.jira_notifier.create_error_ticket(
                project_key=project_key,
                error_type=error_type,
                severity=severity,
                causes=causes,
                selected_solution=selected_solution,
                log_content=log_content,
                issue_type=issue_type
            )
            
            if ticket:
                return {
                    'success': True,
                    'platform': 'JIRA',
                    'ticket_key': ticket.get('key'),
                    'ticket_url': ticket.get('url', ticket.get('self', '')),
                    'message': f"Ticket {ticket.get('key')} created successfully"
                }
            else:
                return {
                    'success': False,
                    'platform': 'JIRA',
                    'error': 'Failed to create ticket'
                }
        except Exception as e:
            return {
                'success': False,
                'platform': 'JIRA',
                'error': str(e)
            }
    
    def send_notifications(
        self,
        error_type: str,
        severity: str,
        causes: List[Dict],
        selected_solution: Dict,
        log_content: str = "",
        aggregated_data: Optional[Dict] = None,
        send_slack: bool = True,
        send_jira: bool = True
    ) -> Dict[str, Any]:
        """Send notifications to both Slack and JIRA"""
        results = {
            'slack': None,
            'jira': None,
            'all_success': False
        }
        
        if send_slack:
            results['slack'] = self.send_slack_notification(
                error_type=error_type,
                severity=severity,
                causes=causes,
                selected_solution=selected_solution,
                aggregated_data=aggregated_data
            )
        
        if send_jira:
            results['jira'] = self.create_jira_ticket(
                error_type=error_type,
                severity=severity,
                causes=causes,
                selected_solution=selected_solution,
                log_content=log_content,
                aggregated_data=aggregated_data
            )
        
        results['all_success'] = (
            (not send_slack or results['slack'] and results['slack'].get('success', False)) and
            (not send_jira or results['jira'] and results['jira'].get('success', False))
        )
        
        return results

