# Multi-Agent Framework Documentation

This directory contains a LangGraph-based multi-agent framework for log error analysis and notification.

## Architecture

The framework consists of 3 specialized agents orchestrated by LangGraph:

### Agent 1: Error Classification Agent (`error_classification_agent.py`)
- **Purpose**: Processes multiple log files, classifies errors, and aggregates issues
- **Key Features**:
  - Extracts error lines from log files
  - Classifies errors by type and severity
  - Aggregates errors across multiple files
  - Provides comprehensive analysis with key findings

### Agent 2: Solution Finding Agent (`solution_agent.py`)
- **Purpose**: Finds and ranks possible solutions for identified errors
- **Key Features**:
  - Generates top 3 solutions ranked by effectiveness
  - Provides solution metadata (effectiveness, complexity, time estimate, risk level)
  - Includes implementation steps and code examples
  - Ranks solutions intelligently

### Agent 3: Notification Agent (`notification_agent.py`)
- **Purpose**: Handles notifications to Slack and JIRA
- **Key Features**:
  - Integrates with existing `notification_agents.py`
  - Sends Slack notifications via webhook
  - Creates JIRA tickets with error details
  - Supports both individual and batch notifications

### Orchestrator (`agent_orchestrator.py`)
- **Purpose**: Coordinates the workflow using LangGraph
- **Workflow**:
  1. Error Classification → 2. Solution Finding → 3. Notification
- **State Management**: Uses TypedDict for type-safe state passing

## Usage

```python
from agents import MultiAgentOrchestrator

# Initialize orchestrator
orchestrator = MultiAgentOrchestrator(
    api_key="your_openai_api_key",
    slack_webhook="your_slack_webhook_url",  # Optional
    jira_config={  # Optional
        'server': 'https://yourcompany.atlassian.net',
        'email': 'your.email@company.com',
        'api_token': 'your_api_token',
        'project_key': 'PROJ',
        'issue_type': 'Task'
    }
)

# Run complete workflow
log_files = [
    {'filename': 'error.log', 'content': '...'},
    {'filename': 'app.log', 'content': '...'}
]

result = orchestrator.run_workflow(
    log_files=log_files,
    send_notifications=False  # Set to True to send notifications
)

# Access results
classification = result['classification_result']
solutions = result['solutions']
```

## File Structure

```
agents/
├── __init__.py                    # Package exports
├── error_classification_agent.py  # Agent 1: Error classification
├── solution_agent.py              # Agent 2: Solution finding
├── notification_agent.py          # Agent 3: Notifications
└── agent_orchestrator.py          # LangGraph orchestrator
```

## Integration with Streamlit App

The multi-agent framework is integrated into `app.py`:
- Automatically used when multiple files are uploaded
- Falls back to single-file analysis if framework unavailable
- Provides enhanced UI with aggregated results
- Shows solution metadata (effectiveness, complexity, etc.)

## Dependencies

- `langchain`: For LLM integration
- `langchain-openai`: For OpenAI API
- `langgraph`: For workflow orchestration
- `jira`: For JIRA integration (optional)
- `requests`: For Slack webhooks

