import streamlit as st  # type: ignore[import-untyped]
import os
from dotenv import load_dotenv  # type: ignore[import-untyped]
import sys
import traceback

# Add agents directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import multi-agent framework
try:
    from agents import MultiAgentOrchestrator
    MULTI_AGENT_AVAILABLE = True
except ImportError as e:
    MULTI_AGENT_AVAILABLE = False
    import_error = traceback.format_exc()
    print(f"Multi-agent framework not available: {e}")
    print(f"Import traceback: {import_error}")

# Fallback to old system
from error_analyzer import ErrorAnalyzer
from notification_agents import SlackNotifier

# Optional JIRA import
try:
    from notification_agents import JIRANotifier
    JIRA_AVAILABLE = True
except ImportError:
    JIRA_AVAILABLE = False
    JIRANotifier = None

import tempfile

# Load environment variables
# Priority: Environment variables (Railway/local) > .env file (local only)
# Railway: Environment variables are set in Railway dashboard
# Local: Falls back to .env file if environment variables are not set
env_file_used = None
is_railway = (
    os.getenv("RAILWAY_ENVIRONMENT") is not None 
    or os.getenv("RAILWAY_PROJECT_ID") is not None
    or os.getenv("RAILWAY") is not None
)

# Always try to load .env for local development (won't override existing env vars)
# This allows local dev with .env file, but Railway will use its own env vars
if not is_railway:
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path, override=False)  # Don't override existing env vars
        env_file_used = env_path
    else:
        # Try auto-detect .env file
        load_dotenv(override=False)
        env_file_used = "auto-detected" if os.path.exists('.env') else None
else:
    # Running on Railway - environment variables are already set
    env_file_used = "Railway environment variables"

# Page configuration
st.set_page_config(
    page_title="Log Error Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject Tailwind CSS
st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .card {
            background: white;
            border-radius: 0.5rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            padding: 1.5rem;
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
        }
        .card-header {
            font-size: 1.25rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #1f2937;
        }
        .stButton > button {
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'selected_solution' not in st.session_state:
    st.session_state.selected_solution = None
if 'log_content' not in st.session_state:
    st.session_state.log_content = None
if 'log_files' not in st.session_state:
    st.session_state.log_files = []
if 'classification_result' not in st.session_state:
    st.session_state.classification_result = None
if 'solutions' not in st.session_state:
    st.session_state.solutions = None
if 'use_multi_agent' not in st.session_state:
    st.session_state.use_multi_agent = True
if 'slack_enabled' not in st.session_state:
    st.session_state.slack_enabled = True  # Default enabled
if 'jira_enabled' not in st.session_state:
    st.session_state.jira_enabled = True  # Default enabled
if 'notifications_sent' not in st.session_state:
    st.session_state.notifications_sent = False
if 'analysis_in_progress' not in st.session_state:
    st.session_state.analysis_in_progress = False
if 'notification_results' not in st.session_state:
    st.session_state.notification_results = None

def send_notifications(result, solution, slack_webhook, jira_config, auto_trigger=False):
    """Helper function to send notifications"""
    notification_results = {'slack': None, 'jira': None, 'all_success': False}
    
    # Get Slack webhook from environment variables (Railway) or .env (local)
    slack_webhook_env = os.getenv("SLACK_WEBHOOK_URL", "")
    slack_webhook_to_use = slack_webhook or slack_webhook_env
    
    # Get JIRA config from environment variables (Railway) or .env (local)
    jira_server_env = os.getenv("JIRA_SERVER", "")
    jira_email_env = os.getenv("JIRA_EMAIL", "")
    jira_token_env = os.getenv("JIRA_API_TOKEN", "")
    jira_project_env = os.getenv("JIRA_PROJECT_KEY", "")
    jira_issue_type_env = os.getenv("JIRA_ISSUE_TYPE", "")
    
    jira_config_to_use = jira_config or {
        'server': jira_server_env,
        'email': jira_email_env,
        'api_token': jira_token_env,
        'project_key': jira_project_env,
        'issue_type': jira_issue_type_env or "Task"
    }
    
    # Send Slack notification
    if st.session_state.slack_enabled and slack_webhook_to_use:
        try:
            notifier = SlackNotifier(slack_webhook_to_use)
            success = notifier.send_error_notification(
                error_type=result.get('error_type'),
                severity=result.get('severity'),
                causes=result.get('causes', []),
                selected_solution=solution
            )
            notification_results['slack'] = {'success': success, 'error': None if success else 'Failed to send'}
        except Exception as e:
            notification_results['slack'] = {'success': False, 'error': str(e)}
    
    # Send JIRA notification
    if st.session_state.jira_enabled and JIRA_AVAILABLE and jira_config_to_use.get('server') and jira_config_to_use.get('email') and jira_config_to_use.get('api_token') and jira_config_to_use.get('project_key'):
        try:
            notifier = JIRANotifier(
                server=jira_config_to_use['server'],
                email=jira_config_to_use['email'],
                api_token=jira_config_to_use['api_token']
            )
            ticket = notifier.create_error_ticket(
                project_key=jira_config_to_use['project_key'],
                error_type=result.get('error_type'),
                severity=result.get('severity'),
                causes=result.get('causes', []),
                selected_solution=solution,
                log_content=st.session_state.log_content[:5000] if st.session_state.log_content else "",
                issue_type=jira_config_to_use.get('issue_type', 'Task')
            )
            notification_results['jira'] = {'success': ticket is not None, 'ticket': ticket, 'error': None if ticket else 'Failed to create'}
        except Exception as e:
            notification_results['jira'] = {'success': False, 'error': str(e)}
    
    notification_results['all_success'] = (
        (not st.session_state.slack_enabled or notification_results['slack'] is None or notification_results['slack'].get('success')) and
        (not st.session_state.jira_enabled or notification_results['jira'] is None or notification_results['jira'].get('success'))
    )
    
    return notification_results

def main():
    # Get API key from environment variables (Railway) or .env (local)
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        
    # Simplified Sidebar - Collapsible Navigation
    with st.sidebar:
        st.markdown("### 📢 Notifications")
        st.session_state.slack_enabled = st.checkbox(
            "📢 Slack",
            value=st.session_state.slack_enabled,
            help="Enable Slack notifications"
        )
        st.session_state.jira_enabled = st.checkbox(
            "🎫 JIRA",
            value=st.session_state.jira_enabled,
            help="Enable JIRA ticket creation"
        )
    
    # Main Header
    st.markdown("""
    <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">🔍 Log Error Analyzer</h1>
        <p class="text-gray-600">AI-powered multi-agent framework for error analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Multi-agent framework indicator
    if MULTI_AGENT_AVAILABLE:
        st.success("✅ Multi-Agent Framework (LangGraph) Enabled")
    else:
        st.warning("⚠️ Multi-Agent Framework not available, using fallback mode")
    
    # Get credentials from environment variables (Railway) or .env (local)
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL", "")
    jira_config = {
        'server': os.getenv("JIRA_SERVER", ""),
        'email': os.getenv("JIRA_EMAIL", ""),
        'api_token': os.getenv("JIRA_API_TOKEN", ""),
        'project_key': os.getenv("JIRA_PROJECT_KEY", ""),
        'issue_type': os.getenv("JIRA_ISSUE_TYPE", "Task")
    }
    
    # 3-Column Layout
    col1, col2, col3 = st.columns(3)
    
    # Column 1: Upload & Analyze Card
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">📤 Upload & Analyze</div>
        </div>
        """, unsafe_allow_html=True)
        
        if not api_key:
            if is_railway:
                st.warning("⚠️ Please set OPENAI_API_KEY as an environment variable in Railway dashboard")
            else:
                st.warning("⚠️ Please set OPENAI_API_KEY in .env file or as an environment variable")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Choose log files",
            type=['log', 'txt', 'out', 'err', 'ndjson'],
            help="Upload one or more log files to analyze",
            key="file_uploader",
            accept_multiple_files=True
        )
        
        if uploaded_files:
            # Process files
            log_files_data = []
            total_size = 0
            total_lines = 0
            
            for uploaded_file in uploaded_files:
                log_content = uploaded_file.read().decode('utf-8', errors='ignore')
                log_files_data.append({
                    'filename': uploaded_file.name,
                    'content': log_content
                })
                total_size += len(log_content)
                total_lines += len(log_content.splitlines())
            
            st.session_state.log_files = log_files_data
            if log_files_data:
                st.session_state.log_content = log_files_data[0]['content']
            
            # File info
            st.info(f"📁 {len(uploaded_files)} file(s) | {total_size:,} chars | {total_lines:,} lines")
            
            # Analyze button
            if st.button("🔍 Analyze Errors", type="primary", use_container_width=True):
                # Debug: Log button click for Railway troubleshooting
                num_files = len(log_files_data) if uploaded_files else 0
                print(f"[DEBUG] Analyze button clicked. API key present: {bool(api_key)}, Multi-agent available: {MULTI_AGENT_AVAILABLE}, Files: {num_files}")
                try:
                    if not api_key:
                        if is_railway:
                            st.error("❌ Please set OPENAI_API_KEY as an environment variable in Railway dashboard")
                        else:
                            st.error("❌ Please set OPENAI_API_KEY in .env file or as an environment variable")
                    elif st.session_state.analysis_in_progress:
                        st.warning("⏳ Analysis already in progress...")
                    elif st.session_state.analysis_result or st.session_state.classification_result:
                        # Reset previous results if re-analyzing
                        st.session_state.analysis_result = None
                        st.session_state.classification_result = None
                        st.session_state.solutions = None
                        st.session_state.selected_solution = None
                        st.session_state.notification_results = None
                        st.session_state.notifications_sent = False
                        st.session_state.analysis_in_progress = True
                    else:
                        st.session_state.analysis_in_progress = True
                        st.session_state.notification_results = None
                        st.session_state.notifications_sent = False
                        
                        if MULTI_AGENT_AVAILABLE and st.session_state.use_multi_agent:
                            with st.spinner("🤖 Multi-Agent Analysis in progress..."):
                                try:
                                    orchestrator = MultiAgentOrchestrator(
                                        api_key=api_key,
                                        slack_webhook=slack_webhook if st.session_state.slack_enabled else None,
                                        jira_config=jira_config if st.session_state.jira_enabled else None
                                    )
                                    result = orchestrator.run_workflow(
                                        log_files=log_files_data,
                                        send_notifications=False
                                    )
                                    st.session_state.classification_result = result.get('classification_result')
                                    st.session_state.solutions = result.get('solutions')
                                    st.session_state.analysis_result = {
                                        'error_type': result.get('classification_result', {}).get('aggregated_analysis', {}).get('primary_issue_category', 'Unknown'),
                                        'severity': result.get('classification_result', {}).get('aggregated_analysis', {}).get('overall_severity', 'Medium'),
                                        'causes': [{'title': f, 'description': f} for f in result.get('classification_result', {}).get('aggregated_analysis', {}).get('key_findings', [])],
                                        'solutions': result.get('solutions', [])
                                    }
                                    st.session_state.analysis_in_progress = False
                                    st.success("✅ Analysis complete!")
                                    st.rerun()  # Rerun to update UI with results
                                except Exception as e:
                                    st.session_state.analysis_in_progress = False
                                    error_details = traceback.format_exc()
                                    st.error(f"❌ Error during multi-agent analysis: {str(e)}")
                                    with st.expander("🔍 View detailed error", expanded=False):
                                        st.code(error_details, language="python")
                                    # Log to console for Railway logs
                                    print(f"Multi-agent analysis error: {error_details}")
                        else:
                            if len(log_files_data) > 1:
                                st.warning("⚠️ Analyzing first file only (multi-agent not available)")
                            with st.spinner("🤖 Analyzing..."):
                                try:
                                    analyzer = ErrorAnalyzer(api_key)
                                    result = analyzer.analyze_errors(log_files_data[0]['content'])
                                    st.session_state.analysis_result = result
                                    st.session_state.analysis_in_progress = False
                                    st.success("✅ Analysis complete!")
                                    st.rerun()  # Rerun to update UI with results
                                except Exception as e:
                                    st.session_state.analysis_in_progress = False
                                    error_details = traceback.format_exc()
                                    st.error(f"❌ Error during analysis: {str(e)}")
                                    with st.expander("🔍 View detailed error", expanded=False):
                                        st.code(error_details, language="python")
                                    # Log to console for Railway logs
                                    print(f"Error analysis error: {error_details}")
                except Exception as outer_e:
                    # Catch any unexpected errors in the button handler
                    error_details = traceback.format_exc()
                    st.error(f"❌ Unexpected error: {str(outer_e)}")
                    with st.expander("🔍 View detailed error", expanded=False):
                        st.code(error_details, language="python")
                    print(f"Unexpected error in analyze button: {error_details}")
    
    # Column 2: Analysis Results Card
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">📊 Analysis Results</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.analysis_result is None and st.session_state.classification_result is None:
            st.info("👆 Upload and analyze files first")
        else:
            # Get result data
            if st.session_state.classification_result:
                classification_result = st.session_state.classification_result
                aggregated_analysis = classification_result.get('aggregated_analysis', {})
                result = {
                    'error_type': aggregated_analysis.get('primary_issue_category', 'Unknown'),
                    'severity': aggregated_analysis.get('overall_severity', 'Medium'),
                    'causes': [{'title': f, 'description': f} for f in aggregated_analysis.get('key_findings', [])],
                    'solutions': st.session_state.solutions or []
                }
            else:
                result = st.session_state.analysis_result
            
            # Display error info
            st.markdown(f"**Error Type:** {result.get('error_type', 'Unknown')}")
            severity = result.get('severity', 'Unknown')
            severity_badge = {
                'Critical': '🔴 Critical',
                'High': '🟠 High',
                'Medium': '🟡 Medium',
                'Low': '🟢 Low'
            }.get(severity, f'⚪ {severity}')
            st.markdown(f"**Severity:** {severity_badge}")
            
            # Solutions
            solutions = result.get('solutions', [])
            if solutions:
                st.markdown("### 💡 Solutions")
                for i, solution in enumerate(solutions):
                    with st.expander(f"Solution {i+1}: {solution.get('title', 'Unknown')}", expanded=(i==0)):
                        st.markdown(f"**{solution.get('description', '')}**")
                        if st.button("✅ Select", key=f"select_{i}", use_container_width=True):
                            st.session_state.selected_solution = solution
                            st.session_state.notifications_sent = False
                            st.session_state.notification_results = None
                            
                            # Auto-trigger notifications if enabled
                            if (st.session_state.slack_enabled or st.session_state.jira_enabled):
                                with st.spinner("📢 Sending notifications..."):
                                    notification_results = send_notifications(
                                        result, solution, slack_webhook, jira_config, auto_trigger=True
                                    )
                                    st.session_state.notification_results = notification_results
                                    st.session_state.notifications_sent = True
                            st.rerun()
            else:
                st.warning("No solutions available")
    
    # Column 3: Notifications Card
    with col3:
        st.markdown("""
        <div class="card">
            <div class="card-header">📢 Notifications</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.selected_solution is None:
            st.info("👆 Select a solution first")
        else:
            # Get result data
            if st.session_state.classification_result:
                classification_result = st.session_state.classification_result
                aggregated_analysis = classification_result.get('aggregated_analysis', {})
                result = {
                    'error_type': aggregated_analysis.get('primary_issue_category', 'Unknown'),
                    'severity': aggregated_analysis.get('overall_severity', 'Medium'),
                    'causes': [{'title': f, 'description': f} for f in aggregated_analysis.get('key_findings', [])]
                }
            else:
                result = st.session_state.analysis_result
            
            solution = st.session_state.selected_solution
            
            st.markdown(f"**Selected:** {solution.get('title', 'Unknown')}")
            
            # Display notification results from session state
            notification_results = st.session_state.notification_results
            
            if notification_results:
                st.divider()
                st.markdown("### 📊 Notification Status")
                
                # Slack status
                if st.session_state.slack_enabled:
                    if notification_results.get('slack'):
                        slack_result = notification_results['slack']
                        if slack_result.get('success'):
                            st.success("✅ **Slack:** Notification sent successfully")
                        else:
                            error_msg = slack_result.get('error', 'Unknown error')
                            st.error(f"❌ **Slack:** {error_msg}")
                    else:
                        st.info("ℹ️ **Slack:** Not attempted")
                else:
                    st.info("ℹ️ **Slack:** Disabled")
                
                # JIRA status
                if st.session_state.jira_enabled:
                    if notification_results.get('jira'):
                        jira_result = notification_results['jira']
                        if jira_result.get('success'):
                            ticket = jira_result.get('ticket', {})
                            ticket_key = ticket.get('key', 'Created') if ticket else 'Created'
                            st.success(f"✅ **JIRA:** Ticket {ticket_key} created successfully")
                            if ticket and ticket.get('url'):
                                st.markdown(f"🔗 [View Ticket]({ticket.get('url')})")
                        else:
                            error_msg = jira_result.get('error', 'Unknown error')
                            st.error(f"❌ **JIRA:** {error_msg}")
                    else:
                        st.info("ℹ️ **JIRA:** Not attempted")
                else:
                    st.info("ℹ️ **JIRA:** Disabled")
                
                # Overall status
                if notification_results.get('all_success'):
                    st.balloons()
            elif st.session_state.notifications_sent:
                st.info("💡 Notifications were sent. Check status above.")
            else:
                st.info("💡 Notifications will be sent automatically when you select a solution")
            
            # On-demand trigger button
            st.divider()
            if st.button("📢 Send Notifications Now", type="primary", use_container_width=True):
                with st.spinner("Sending notifications..."):
                    notification_results = send_notifications(
                        result, solution, slack_webhook, jira_config, auto_trigger=False
                    )
                    st.session_state.notification_results = notification_results
                    st.session_state.notifications_sent = True
                st.rerun()
            
            # Notification settings status
            st.divider()
            st.markdown("**Status:**")
            slack_status = "✅ Enabled" if st.session_state.slack_enabled else "❌ Disabled"
            jira_status = "✅ Enabled" if st.session_state.jira_enabled else "❌ Disabled"
            st.markdown(f"- Slack: {slack_status}")
            st.markdown(f"- JIRA: {jira_status}")

if __name__ == "__main__":
    main()
