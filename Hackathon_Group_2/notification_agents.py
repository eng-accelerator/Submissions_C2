import requests  # type: ignore[import-untyped]
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Optional JIRA import - only import if available
JIRA_AVAILABLE = False
JIRA = None

try:
    from jira import JIRA  # type: ignore[import-untyped]
    JIRA_AVAILABLE = True
except ImportError as e:
    JIRA_AVAILABLE = False
    JIRA = None
    import_error = str(e)
except Exception as e:
    # Handle any other import errors
    JIRA_AVAILABLE = False
    JIRA = None
    import_error = str(e)

class SlackNotifier:
    """Slack notification agent for error reporting"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_error_notification(
        self,
        error_type: str,
        severity: str,
        causes: List[Dict],
        selected_solution: Dict
    ) -> bool:
        """Send error notification to Slack"""
        
        # Determine color based on severity
        color_map = {
            'Critical': '#FF0000',
            'High': '#FF6B6B',
            'Medium': '#FFA500',
            'Low': '#FFD700'
        }
        color = color_map.get(severity, '#808080')
        
        # Format causes
        causes_text = ""
        for i, cause in enumerate(causes[:3], 1):  # Limit to 3 causes
            causes_text += f"• *{cause.get('title', 'Unknown')}*: {cause.get('description', '')}\n"
        
        # Format solution steps
        solution_steps = ""
        if 'steps' in selected_solution:
            for step in selected_solution['steps']:
                solution_steps += f"• {step}\n"
        
        # Create Slack message payload
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": "🔍 Log Error Analysis",
                    "fields": [
                        {
                            "title": "Error Type",
                            "value": error_type,
                            "short": True
                        },
                        {
                            "title": "Severity",
                            "value": severity,
                            "short": True
                        },
                        {
                            "title": "Possible Causes",
                            "value": causes_text or "No causes identified",
                            "short": False
                        },
                        {
                            "title": "Selected Solution",
                            "value": selected_solution.get('title', 'Unknown'),
                            "short": False
                        },
                        {
                            "title": "Solution Description",
                            "value": selected_solution.get('description', 'No description'),
                            "short": False
                        },
                        {
                            "title": "Implementation Steps",
                            "value": solution_steps or "No steps provided",
                            "short": False
                        }
                    ],
                    "footer": "Log Error Analyzer",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Slack notification error: {str(e)}")
            return False


class JIRANotifier:
    """JIRA notification agent for creating error tickets"""
    
    def __init__(self, server: str, email: str, api_token: str):
        # Re-check JIRA availability at runtime
        import sys
        try:
            from jira import JIRA as JIRAClass  # type: ignore[import-untyped]
            self.JIRAClass = JIRAClass
        except ImportError as e:
            python_path = sys.executable
            python_version = sys.version
            
            error_msg = (
                f"JIRA package is not installed in the current Python environment.\n\n"
                f"Current Python: {python_path}\n"
                f"Python version: {python_version.split()[0]}\n\n"
                f"To fix this:\n"
                f"1. Activate your virtual environment: source myenv/bin/activate\n"
                f"2. Install JIRA: pip install jira\n"
                f"3. Run Streamlit: streamlit run app.py\n\n"
                f"Original error: {str(e)}"
            )
            raise ImportError(error_msg)
        
        self.server = server
        self.email = email
        self.api_token = api_token
        self.jira = None
        self._connect()
    
    def _connect(self):
        """Establish connection to JIRA"""
        try:
            self.jira = self.JIRAClass(
                server=self.server,
                basic_auth=(self.email, self.api_token)
            )
        except Exception as e:
            raise Exception(f"Failed to connect to JIRA: {str(e)}")
    
    def test_connection(self, project_key: str = None) -> Dict[str, Any]:
        """Test JIRA connection and permissions"""
        result = {
            'success': False,
            'connection': False,
            'project_access': False,
            'create_permission': False,
            'message': '',
            'details': {}
        }
        
        try:
            # Test 1: Connection
            if not self.jira:
                self._connect()
            result['connection'] = True
            result['details']['connection'] = '✅ Connected to JIRA successfully'
            
            # Test 2: Get current user info
            try:
                current_user = self.jira.current_user()
                result['details']['user'] = f"✅ Authenticated as: {current_user}"
            except Exception as e:
                result['details']['user'] = f"⚠️ Could not get user info: {str(e)}"
            
            # Test 3: Project access (if project_key provided)
            if project_key:
                try:
                    project = self.jira.project(project_key)
                    result['project_access'] = True
                    result['details']['project'] = f"✅ Project '{project_key}' found: {project.name}"
                    
                    # Test 4: Check if user can create issues
                    try:
                        creatable_issue_types = self.jira.creatable_issue_types(project_key)
                        if creatable_issue_types:
                            result['create_permission'] = True
                            issue_type_names = [it.name for it in creatable_issue_types[:3]]
                            result['details']['permission'] = f"✅ Can create issues. Available types: {', '.join(issue_type_names)}"
                        else:
                            result['details']['permission'] = "❌ No issue types available to create"
                    except Exception as e:
                        error_str = str(e).lower()
                        if 'permission' in error_str or '401' in str(e) or '403' in str(e):
                            result['details']['permission'] = f"❌ Permission denied: {str(e)}"
                        else:
                            result['details']['permission'] = f"⚠️ Could not check permissions: {str(e)}"
                            
                except Exception as e:
                    error_str = str(e).lower()
                    if 'not found' in error_str or '404' in str(e):
                        result['details']['project'] = f"❌ Project '{project_key}' not found or not accessible"
                    elif 'permission' in error_str or '401' in str(e) or '403' in str(e):
                        result['details']['project'] = f"❌ No access to project '{project_key}': {str(e)}"
                    else:
                        result['details']['project'] = f"⚠️ Error accessing project: {str(e)}"
            
            # Determine overall success
            if result['connection'] and (not project_key or (result['project_access'] and result['create_permission'])):
                result['success'] = True
                result['message'] = '✅ JIRA connection and permissions verified successfully'
            elif result['connection'] and result['project_access']:
                result['success'] = False
                result['message'] = '⚠️ Connected but cannot create issues. Check permissions.'
            elif result['connection']:
                result['success'] = False
                result['message'] = '⚠️ Connected but project access failed'
            else:
                result['success'] = False
                result['message'] = '❌ Connection failed'
                
        except Exception as e:
            error_str = str(e).lower()
            if 'authentication' in error_str or '401' in str(e) or 'authenticated_failed' in error_str:
                result['message'] = f"❌ Authentication failed. Check your email and API token."
                result['details']['error'] = str(e)
            elif 'connection' in error_str or 'timeout' in error_str:
                result['message'] = f"❌ Connection failed. Check server URL and network."
                result['details']['error'] = str(e)
            else:
                result['message'] = f"❌ Error: {str(e)}"
                result['details']['error'] = str(e)
        
        return result
    
    def create_error_ticket(
        self,
        project_key: str,
        error_type: str,
        severity: str,
        causes: List[Dict],
        selected_solution: Dict,
        log_content: str = "",
        issue_type: str = "Task"
    ) -> Optional[Dict]:
        """Create a JIRA ticket for the error"""
        
        if not self.jira:
            raise Exception("JIRA connection not established")
        
        # Get available issue types for the project
        valid_issue_type = issue_type or "Task"
        
        try:
            # Get project metadata to find available issue types
            project = self.jira.project(project_key)
            
            # Try to get creatable issue types for this project
            try:
                # Get issue types available for this project
                creatable_issue_types = self.jira.creatable_issue_types(project_key)
                available_issue_types = [it.name for it in creatable_issue_types]
            except Exception:
                # Fallback: try to get all issue types
                try:
                    available_issue_types = [it.name for it in self.jira.issue_types()]
                except Exception:
                    available_issue_types = []
            
            # Try to find a valid issue type
            if available_issue_types:
                preferred_types = [issue_type, 'Task', 'Bug', 'Story', 'Issue', 'Incident']
                
                for preferred in preferred_types:
                    if preferred in available_issue_types:
                        valid_issue_type = preferred
                        break
                
                # If none of the preferred types match, use the first available
                if valid_issue_type not in available_issue_types:
                    valid_issue_type = available_issue_types[0]
        except Exception as e:
            # If we can't fetch issue types, use the provided one or default
            # This is fine - we'll try with the provided type and JIRA will error if invalid
            pass
        
        # Format causes
        causes_text = ""
        for i, cause in enumerate(causes, 1):
            causes_text += f"h3. Cause {i}: {cause.get('title', 'Unknown')}\n"
            causes_text += f"{cause.get('description', '')}\n\n"
        
        # Format solution
        solution_text = f"h2. Selected Solution: {selected_solution.get('title', 'Unknown')}\n\n"
        solution_text += f"{selected_solution.get('description', '')}\n\n"
        
        if 'steps' in selected_solution:
            solution_text += "h3. Implementation Steps:\n"
            for step in selected_solution['steps']:
                solution_text += f"# {step}\n"
        
        if 'code_example' in selected_solution and selected_solution['code_example']:
            solution_text += "\nh3. Code Example:\n"
            solution_text += f"{{code}}\n{selected_solution['code_example']}\n{{code}}\n"
        
        # Create issue description
        description = f"""
h2. Error Analysis Summary

*Error Type:* {error_type}
*Severity:* {severity}

h2. Possible Causes

{causes_text}

{solution_text}

h2. Log Content (Preview)

{{code}}
{log_content[:2000] if log_content else 'No log content provided'}
{{code}}

---
*Generated by Log Error Analyzer on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Map severity to JIRA priority
        priority_map = {
            'Critical': 'Highest',
            'High': 'High',
            'Medium': 'Medium',
            'Low': 'Low'
        }
        priority = priority_map.get(severity, 'Medium')
        
        # Create issue
        try:
            issue_dict = {
                'project': {'key': project_key},
                'summary': f'[Log Error] {error_type} - {severity}',
                'description': description,
                'issuetype': {'name': valid_issue_type},
                'priority': {'name': priority}
            }
            
            issue = self.jira.create_issue(fields=issue_dict)
            
            return {
                'key': issue.key,
                'id': issue.id,
                'self': issue.self,
                'url': f"{self.server}/browse/{issue.key}"
            }
        except Exception as e:
            error_str = str(e)
            error_lower = error_str.lower()
            
            # Check for permission errors
            if '401' in error_str or 'permission' in error_lower or 'authenticated_failed' in error_lower:
                raise Exception(
                    f"JIRA Permission Error: You do not have permission to create issues in project '{project_key}'.\n\n"
                    f"To fix this:\n"
                    f"1. Verify your JIRA email ({self.email}) has access to project '{project_key}'\n"
                    f"2. Check that your API token has the correct permissions\n"
                    f"3. Contact your JIRA administrator to grant 'Create Issues' permission for project '{project_key}'\n"
                    f"4. Verify the project key is correct\n\n"
                    f"Original error: {error_str}"
                )
            elif '403' in error_str or 'forbidden' in error_lower:
                raise Exception(
                    f"JIRA Access Forbidden: Access denied to project '{project_key}'.\n\n"
                    f"To fix this:\n"
                    f"1. Verify you have access to project '{project_key}'\n"
                    f"2. Check your JIRA permissions for this project\n"
                    f"3. Contact your JIRA administrator if needed\n\n"
                    f"Original error: {error_str}"
                )
            elif '404' in error_str or 'not found' in error_lower:
                raise Exception(
                    f"JIRA Project Not Found: Project '{project_key}' does not exist or is not accessible.\n\n"
                    f"To fix this:\n"
                    f"1. Verify the project key '{project_key}' is correct\n"
                    f"2. Check that the project exists in your JIRA instance\n"
                    f"3. Verify you have access to this project\n\n"
                    f"Original error: {error_str}"
                )
            else:
                raise Exception(f"Failed to create JIRA ticket: {error_str}")
    
    def add_comment(self, issue_key: str, comment: str) -> bool:
        """Add a comment to an existing JIRA issue"""
        try:
            issue = self.jira.issue(issue_key)
            self.jira.add_comment(issue, comment)
            return True
        except Exception as e:
            print(f"Failed to add comment: {str(e)}")
            return False

