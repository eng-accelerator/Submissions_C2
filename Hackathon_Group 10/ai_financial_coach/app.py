# app.py
# Main Dashboard - AI Financial Coach
# Guest mode (test user) by default, optional sign in/sign up

import streamlit as st
from core.transaction_store import TransactionStore
from core.knowledge_store import FinancialKnowledgeStore
from core.transaction_parser import BankStatementParser
import plotly.graph_objects as go
from datetime import datetime
import hashlib

# Guest mode configuration
GUEST_MODE_ENABLED = True
GUEST_USER = {
    'username': 'guest_user',
    'email': 'guest@aifinancialcoach.com',
    'country': 'India',
    'employment_status': 'Guest',
    'is_guest': True
}

st.set_page_config(
    page_title="AI Financial Coach",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== AUTHENTICATION ====================

def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_session_state():
    """Initialize session state variables."""
    # Get current session ID
    current_session = get_session_id()
    
    # Check if this is a new browser session
    if current_session and '_last_session_id' not in st.session_state:
        # New session detected - clear guest data
        clear_guest_data_from_db()
        st.session_state._last_session_id = current_session
    
    # Check if user is already authenticated
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        return
    
    # GUEST MODE: Auto-login as guest if enabled
    if GUEST_MODE_ENABLED:
        st.session_state.authenticated = True
        st.session_state.username = GUEST_USER['username']
        st.session_state.user_profile = GUEST_USER.copy()
        st.session_state.is_guest = True
        
        # Initialize transaction store
        if 'transaction_store' not in st.session_state:
            try:
                st.session_state.transaction_store = TransactionStore(
                    connection_string="sqlite:///./financial_data.db"
                )
            except Exception as e:
                print(f"Error initializing transaction store: {e}")
        
        # Ensure guest user exists in database
        if 'transaction_store' in st.session_state:
            user_id = st.session_state.transaction_store.get_user_id(
                GUEST_USER['username']
            )
            
            if not user_id:
                # Create guest user in database
                user_id = st.session_state.transaction_store.add_user(
                    username=GUEST_USER['username'],
                    email=GUEST_USER['email'],
                    country=GUEST_USER['country']
                )
                print(f"✅ Created guest user with ID: {user_id}")
            else:
                print(f"✅ Guest user exists with ID: {user_id}")
        
        return
    
    # Initialize other session state variables
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'users_db' not in st.session_state:
        st.session_state.users_db = {}
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    if 'is_guest' not in st.session_state:
        st.session_state.is_guest = False

def show_login_dialog():
    """Show login dialog in sidebar."""
    with st.sidebar:
        st.divider()
        
        if st.session_state.get('is_guest', False):
            st.info("👤 **You're using Guest Mode**\n\nSign in to save your data permanently!")
            
            with st.expander("🔐 Sign In / Sign Up", expanded=False):
                tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
                
                with tab1:
                    with st.form("signin_form_sidebar"):
                        username = st.text_input("Username")
                        password = st.text_input("Password", type="password")
                        submit = st.form_submit_button("Sign In", use_container_width=True)
                        
                        if submit:
                            if username in st.session_state.users_db:
                                if st.session_state.users_db[username]['password'] == hash_password(password):
                                    # Switch from guest to real user
                                    st.session_state.authenticated = True
                                    st.session_state.username = username
                                    st.session_state.user_profile = st.session_state.users_db[username]
                                    st.session_state.is_guest = False
                                    st.success("✅ Signed in successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Invalid password")
                            else:
                                st.error("❌ User not found")
                
                with tab2:
                    with st.form("signup_form_sidebar"):
                        new_username = st.text_input("Username", key="signup_username")
                        new_email = st.text_input("Email", key="signup_email")
                        new_password = st.text_input("Password", type="password", key="signup_password")
                        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
                        
                        country = st.selectbox("Country", ["India", "Poland"])
                        employment = st.selectbox("Employment", ["Salaried", "Self-Employed", "Business", "Student", "Retired"])
                        
                        submit = st.form_submit_button("Sign Up", use_container_width=True)
                        
                        if submit:
                            if new_password != confirm_password:
                                st.error("❌ Passwords don't match")
                            elif new_username in st.session_state.users_db:
                                st.error("❌ Username already exists")
                            elif len(new_password) < 6:
                                st.error("❌ Password must be at least 6 characters")
                            else:
                                # Create new user
                                st.session_state.users_db[new_username] = {
                                    'password': hash_password(new_password),
                                    'email': new_email,
                                    'country': country,
                                    'employment_status': employment,
                                    'created_at': datetime.now().isoformat()
                                }
                                
                                # Create user in database
                                if 'transaction_store' in st.session_state:
                                    st.session_state.transaction_store.add_user(
                                        username=new_username,
                                        email=new_email,
                                        country=country
                                    )
                                
                                # Auto sign in
                                st.session_state.authenticated = True
                                st.session_state.username = new_username
                                st.session_state.user_profile = st.session_state.users_db[new_username]
                                st.session_state.is_guest = False
                                
                                st.success("✅ Account created! Signed in.")
                                st.rerun()

# ==================== SIDEBAR ====================

def render_sidebar():
    """Render sidebar with user info and actions."""
    with st.sidebar:
        st.title("👤 User Profile")
        
        if st.session_state.get('is_guest', False):
            st.warning("**Guest User** 👤")
            st.caption("Using temporary session")
            st.caption("🌍 India")
        else:
            st.write(f"**{st.session_state.username}**")
            st.write(f"🌍 {st.session_state.user_profile.get('country', 'India')}")
            st.write(f"💼 {st.session_state.user_profile.get('employment_status', 'Salaried')}")
        
        st.divider()
        
        # Upload Section
        st.header("📂 Upload Transactions")
        
        if st.session_state.get('is_guest', False):
            st.caption("⚠️ Guest mode - data is temporary")
        else:
            st.caption("Upload bank statements (PDF, Excel, CSV)")
        
        uploaded_files = st.file_uploader(
            "Drag and drop files here",
            type=['pdf', 'xlsx', 'csv'],
            accept_multiple_files=True,
            key="transaction_upload",
            help="Upload your bank statements for analysis"
        )
        
        if uploaded_files:
            st.success(f"✓ {len(uploaded_files)} file(s) selected")
            
            if st.button("🚀 Process & Store", type="primary", use_container_width=True):
                process_transactions(uploaded_files)
        
        # Statistics
        if 'transaction_store' in st.session_state:
            try:
                stats = get_transaction_stats()
                st.metric("📄 Transactions", stats['count'])
                if stats.get('date_range'):
                    st.caption(f"📅 {stats['date_range']}")
            except:
                pass
        
        st.divider()
        
        # Quick Actions
        st.header("🎯 Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 AI Coach", use_container_width=True):
                st.switch_page("pages/AI_Financial_Planner.py")
        with col2:
            if st.button("📚 Knowledge", use_container_width=True):
                st.switch_page("pages/Knowledge_Base.py")
        
        st.divider()
        
        # Show login option for guest users, logout for authenticated users
        show_login_dialog()
        
        # Sign out button
        if st.session_state.get('is_guest', False):
            if st.button("🔄 Clear Guest Data", use_container_width=True):
                clear_user_data()
                st.success("✅ Guest data cleared!")
                st.rerun()
        else:
            if st.button("🚪 Sign Out", use_container_width=True):
                # Clear user data
                clear_user_data()
                # Switch back to guest mode
                st.session_state.clear()
                st.rerun()

# ==================== MAIN DASHBOARD ====================

def generate_and_download_report():
    """Generate comprehensive Excel report for download."""
    from core.report_generator import FinancialReportGenerator
    
    try:
        # Get user data
        user_id = st.session_state.transaction_store.get_user_id(st.session_state.username)
        
        if not user_id:
            st.error("User not found in database")
            return
        
        # Gather all data
        summary = st.session_state.transaction_store.get_financial_summary(user_id)
        categories = st.session_state.transaction_store.get_category_totals(user_id)
        monthly_trend = st.session_state.transaction_store.get_monthly_trend(user_id, months=12)
        
        # User data
        user_data = {
            'username': st.session_state.username,
            'email': st.session_state.user_profile.get('email', 'N/A'),
            'country': st.session_state.user_profile.get('country', 'India')
        }
        
        # Transaction summary
        transaction_summary = {
            'total_income': summary.get('total_income', 0),
            'total_expenses': summary.get('total_expenses', 0),
            'savings': summary.get('savings', 0),
            'savings_rate': summary.get('savings_rate', 0),
            'transaction_count': summary.get('transaction_count', 0),
            'date_range': f"{summary.get('start_date', 'N/A')} to {summary.get('end_date', 'N/A')}"
        }
        
        # Generate report
        generator = FinancialReportGenerator()
        
        with st.spinner("📊 Generating comprehensive report..."):
            excel_file = generator.generate_comprehensive_report(
                user_data=user_data,
                transaction_summary=transaction_summary,
                categories=categories,
                monthly_trend=monthly_trend,
                goals=None,  # TODO: Add goals when available
                investment_options=None  # TODO: Add investment options when available
            )
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Financial_Report_{st.session_state.username}_{timestamp}.xlsx"
        
        return excel_file, filename
    
    except Exception as e:
        st.error(f"Error generating report: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None, None
    
def render_dashboard():
    """Render main financial dashboard."""
    
    st.title("🏦 AI Financial Coach")
    st.subheader("Your Personal Money Advisor with AI-Powered Analysis")
    
    # Show guest mode banner
    if st.session_state.get('is_guest', False):
        st.info("👋 **Welcome to Guest Mode!** You're exploring the app with a temporary account. Sign in to save your data permanently.", icon="ℹ️")
    
    # Initialize connections
    if 'transaction_store' not in st.session_state:
        try:
            st.session_state.transaction_store = TransactionStore(
                connection_string="sqlite:///./financial_data.db"
            )
        except Exception as e:
            st.error(f"Database connection error: {e}")
            return
    
    # Calculate metrics
    try:
        metrics = calculate_financial_metrics()
    except Exception as e:
        st.warning("No transaction data yet. Please upload bank statements using the sidebar.")
        st.info("👈 Use the sidebar to upload your bank statements")
        
        # Show empty metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Income", "₹0", delta="No data", delta_color="inverse")
        with col2:
            st.metric("💸 Expenses", "₹0", delta="No data", delta_color="normal")
        with col3:
            st.metric("💎 Savings", "₹0", delta="No data", delta_color="inverse")
        with col4:
            st.metric("📊 Health Score", "0/100", delta="Poor", delta_color="inverse")
        
        st.divider()
        
        # Show action buttons even without data
        st.subheader("🎯 What would you like to do?")
        
        col1, col2, col3 = st.columns(3)
             
        with col1:
            if st.button("💬 Ask AI Coach", use_container_width=True, type="primary"):
                st.switch_page("pages/AI_Financial_Planner.py")
        
        with col2:
            if st.button("🎯 Create New Goal", use_container_width=True):
                st.switch_page("pages/Create_Goal.py")
        
        with col3:
            if st.button("🎯 Download reports", use_container_width=True):
                st.info("💡 Coming soon: Goal tracking")
        return
    
    # [Rest of your dashboard code stays the same - metrics display, charts, etc.]
    # ... (keeping all your existing dashboard rendering code)
    
    # Determine if we have actual data
    has_data = metrics['income'] > 0 or metrics['expenses'] > 0
    
    # Get change values
    income_change = metrics.get('income_change', 0)
    expense_change = metrics.get('expense_change', 0)
    savings_change = metrics.get('savings_change', 0)
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not has_data:
            delta_txt = "No data"
            delta_color = "inverse"
        elif income_change == 0:
            delta_txt = "0.0% vs last month"
            delta_color = "off"
        else:
            delta_txt = f"{income_change:.1f}% vs last month"
            delta_color = "normal" if income_change > 0 else "inverse"
        
        st.metric("💰 Income", f"₹{metrics['income']:,.0f}", delta=delta_txt, delta_color=delta_color)
    
    with col2:
        if not has_data:
            delta_txt = "No data"
            delta_color = "normal"
        elif expense_change == 0:
            delta_txt = "0.0% vs last month"
            delta_color = "off"
        elif expense_change > 0:
            delta_txt = f"{expense_change:.1f}% vs last month"
            delta_color = "inverse"
        else:
            delta_txt = f"{expense_change:.1f}% vs last month"
            delta_color = "normal"
        
        st.metric("💸 Expenses", f"₹{metrics['expenses']:,.0f}", delta=delta_txt, delta_color=delta_color)
    
    with col3:
        if not has_data:
            delta_txt = "No data"
            delta_color = "inverse"
        elif metrics['savings'] <= 0:
            delta_txt = "Overspending!" if metrics['savings'] < 0 else "Zero savings"
            delta_color = "inverse"
        elif savings_change == 0:
            delta_txt = "0.0% vs last month"
            delta_color = "off"
        else:
            delta_txt = f"{savings_change:.1f}% vs last month"
            delta_color = "normal" if savings_change > 0 else "inverse"
        
        st.metric("💎 Savings", f"₹{metrics['savings']:,.0f}", delta=delta_txt, delta_color=delta_color)
    
    with col4:
        health_score = metrics['health_score']
        
        if health_score == 0:
            health_status = "No data"
            delta_color = "inverse"
        elif health_score >= 70:
            health_status = "Good"
            delta_color = "normal"
        elif health_score >= 50:
            health_status = "Fair"
            delta_color = "off"
        else:
            health_status = "Poor"
            delta_color = "inverse"
        
        st.metric("📊 Health Score", f"{health_score}/100", delta=health_status, delta_color=delta_color)
    
    if metrics.get('latest_balance'):
        st.caption(f"💰 Account Balance: ₹{metrics['latest_balance']:,.2f} (as of {metrics.get('balance_date', 'N/A')})")
    
    st.caption(f"📅 Data from {metrics.get('date_range', 'N/A')}")
    
    st.divider()
    
    # Spending Breakdown Chart
    st.subheader("📊 Spending Breakdown")
    
    if metrics['category_breakdown'] and len(metrics['category_breakdown']) > 0:
        categories = [cat['category'].replace('_', ' ').title() for cat in metrics['category_breakdown'][:10]]
        amounts = [float(cat['amount']) for cat in metrics['category_breakdown'][:10]]
        
        total = sum(amounts)
        percentages = [(amt/total*100) if total > 0 else 0 for amt in amounts]
        
        fig = go.Figure(go.Bar(
            x=amounts, y=categories, orientation='h',
            marker=dict(color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                               '#DFE6E9', '#74B9FF', '#A29BFE', '#FD79A8', '#FDCB6E'][:len(categories)]),
            text=[f"₹{amt:,.0f} ({pct:.1f}%)" for amt, pct in zip(amounts, percentages)],
            textposition='auto',
        ))
        
        fig.update_layout(
            height=400, margin=dict(l=20, r=20, t=20, b=20),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title="Amount (₹)", gridcolor='rgba(128,128,128,0.2)'),
            yaxis=dict(title="Category"), font=dict(size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expense data to display yet")
    
    # Transaction Modes
    st.subheader("💳 Transaction Modes")
    
    if metrics['mode_breakdown'] and len(metrics['mode_breakdown']) > 0:
        mode_cols = st.columns(min(4, len(metrics['mode_breakdown'])))
        
        for idx, mode_data in enumerate(metrics['mode_breakdown'][:4]):
            with mode_cols[idx]:
                mode = mode_data['mode'].upper() if mode_data['mode'] else 'OTHER'
                count = mode_data['count']
                total_txns = metrics['transaction_count']
                percentage = (count / total_txns * 100) if total_txns > 0 else 0
                
                st.metric(label=mode, value=count, delta=f"{percentage:.1f}%")
    
    st.divider()
    
    # Action Buttons
    st.subheader("🎯 What would you like to do?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Detailed Reports", use_container_width=True):
            st.info("💡 Coming soon: Detailed financial reports")
    
    with col2:
        if st.button("💬 Ask AI Coach", use_container_width=True, type="primary"):
            st.switch_page("pages/AI_Financial_Planner.py")
      
    with col3:
        if st.button("🎯 Create New Goal", use_container_width=True):
            st.switch_page("pages/Create_Goal.py")

# ==================== HELPER FUNCTIONS ====================

def calculate_financial_metrics():
    """Calculate metrics from database."""
    user_id = st.session_state.transaction_store.get_user_id(st.session_state.username)
    
    if not user_id:
        user_id = st.session_state.transaction_store.add_user(
            username=st.session_state.username,
            email=st.session_state.user_profile.get('email', ''),
            country=st.session_state.user_profile.get('country', 'India')
        )
    
    summary = st.session_state.transaction_store.get_financial_summary(user_id)
    savings_rate = summary.get('savings_rate', 0)
    health_score = calculate_health_score(savings_rate)
    
    return {
        'income': float(summary.get('total_income', 0)),
        'expenses': float(summary.get('total_expenses', 0)),
        'savings': float(summary.get('savings', 0)),
        'savings_rate': savings_rate,
        'health_score': health_score,
        'category_breakdown': summary.get('category_breakdown', []),
        'mode_breakdown': summary.get('mode_breakdown', []),
        'transaction_count': summary.get('transaction_count', 0),
        'date_range': f"{summary.get('start_date', 'N/A')} to {summary.get('end_date', 'N/A')}",
        'latest_balance': summary.get('latest_balance'),
        'balance_date': summary.get('balance_date'),
        'income_change': 0,
        'expense_change': 0,
        'savings_change': 0
    }

def calculate_health_score(savings_rate):
    """Calculate financial health score."""
    if savings_rate >= 50: return 100
    elif savings_rate >= 30: return 80
    elif savings_rate >= 20: return 70
    elif savings_rate >= 10: return 60
    elif savings_rate > 0: return 40
    else: return 0

def process_transactions(files):
    """Process uploaded transaction files."""
    parser = BankStatementParser()
    user_id = st.session_state.transaction_store.get_user_id(st.session_state.username)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_transactions = 0
    
    for idx, file in enumerate(files):
        status_text.text(f"Processing {file.name}...")
        
        try:
            transactions = parser.parse_to_dict(file)
            
            if transactions:
                st.session_state.transaction_store.bulk_insert_transactions(user_id, transactions)
                total_transactions += len(transactions)
            
            progress_bar.progress((idx + 1) / len(files))
        
        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
    
    status_text.success(f"✅ Processed {len(files)} file(s) - {total_transactions} transactions!")
    st.balloons()
    
    import time
    time.sleep(2)
    st.rerun()

def get_transaction_stats():
    """Get transaction statistics."""
    user_id = st.session_state.transaction_store.get_user_id(st.session_state.username)
    
    if not user_id:
        return {'count': 0}
    
    summary = st.session_state.transaction_store.get_financial_summary(user_id)
    
    return {
        'count': summary.get('transaction_count', 0),
        'date_range': f"{summary.get('start_date', '')} to {summary.get('end_date', '')}" if summary.get('start_date') else None
    }

def clear_user_data():
    """Clear transaction data for current user."""
    if 'transaction_store' in st.session_state and st.session_state.username:
        try:
            user_id = st.session_state.transaction_store.get_user_id(st.session_state.username)
            
            if user_id:
                cursor = st.session_state.transaction_store.conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
                st.session_state.transaction_store.conn.commit()
        except Exception as e:
            print(f"Error clearing transactions: {e}")

# ==================== MAIN ====================

def clear_guest_data_from_db():
    """Clear guest user transactions from database."""
    try:
        temp_store = TransactionStore(connection_string="sqlite:///./financial_data.db")
        guest_user_id = temp_store.get_user_id('guest_user')
        
        if guest_user_id:
            cursor = temp_store.conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE user_id = ?", (guest_user_id,))
            temp_store.conn.commit()
            print("✅ Cleared guest user data for new session")
        
        temp_store.close()
    except Exception as e:
        print(f"⚠️ Error clearing guest data: {e}")

def get_session_id():
    """Get unique session ID from Streamlit."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx:
            return ctx.session_id
    except:
        pass
    return None

def main():
    """Main application entry point."""
    init_session_state()
    
    if not st.session_state.authenticated:
        # This shouldn't happen with guest mode, but just in case
        st.error("Authentication error. Please refresh the page.")
    else:
        render_sidebar()
        render_dashboard()

if __name__ == "__main__":
    main()