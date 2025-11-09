# pages/AI_Financial_Planner.py
# Chat with AI Financial Advisor

import streamlit as st
from core.financial_planner_agent import FinancialPlannerAgent
from core.transaction_store import TransactionStore
from core.knowledge_store import FinancialKnowledgeStore
import os

st.set_page_config(
    page_title="AI Financial Planner - AI Financial Coach",
    page_icon="🤖",
    layout="wide"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in first")
    st.switch_page("app.py")
    st.stop()

st.title("🤖 AI Financial Planner")
st.subheader("Your Multi-Agent Financial Advisory System")

# ========================================
# DEBUG INFO (Remove after testing)
# ========================================
with st.expander("🔍 Debug Info", expanded=False):
    st.write("**Session State Check:**")
    st.write(f"- Username: {st.session_state.get('username', 'NOT SET')}")
    st.write(f"- Is Guest: {st.session_state.get('is_guest', 'NOT SET')}")
    
    if 'transaction_store' in st.session_state:
        st.write("- Transaction Store: ✅ EXISTS")
        
        try:
            user_id = st.session_state.transaction_store.get_user_id(st.session_state.username)
            st.write(f"- User ID in DB: {user_id}")
            
            if user_id:
                summary = st.session_state.transaction_store.get_financial_summary(user_id)
                st.write(f"- Transaction Count: {summary.get('transaction_count', 0)}")
                st.write(f"- Total Income: ₹{summary.get('total_income', 0):,.0f}")
                st.write(f"- Total Expenses: ₹{summary.get('total_expenses', 0):,.0f}")
        except Exception as e:
            st.write(f"- Database Error: {e}")
    else:
        st.write("- Transaction Store: ❌ NOT FOUND")
    
    if 'financial_planner_agent' in st.session_state:
        st.write("- Financial Planner Agent: ✅ EXISTS")
        
        # Check if agent's transaction store is the same instance
        if st.session_state.financial_planner_agent.transaction_store is st.session_state.transaction_store:
            st.write("- Agent using SAME transaction store: ✅")
        else:
            st.write("- Agent using DIFFERENT transaction store: ❌ BUG!")
    else:
        st.write("- Financial Planner Agent: ❌ NOT FOUND")

# ========================================
# INITIALIZE COMPONENTS
# ========================================
if 'financial_planner_agent' not in st.session_state:
    try:
        # Get API keys
        openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("openai_api_key")
        openai_base_url = os.getenv("OPENAI_BASE_URL") or st.secrets.get("openai_base_url")
        tavily_api_key = os.getenv("TAVILY_API_KEY") or st.secrets.get("tavily_api_key")
        
        # CRITICAL: Reuse the transaction_store from session state
        if 'transaction_store' not in st.session_state:
            st.error("❌ Transaction store not initialized. Please go back to the dashboard first.")
            if st.button("← Go to Dashboard"):
                st.switch_page("app.py")
            st.stop()
        
        # Use the EXISTING transaction store from session
        transaction_store = st.session_state.transaction_store
        
        # Verify user exists in database
        user_id = transaction_store.get_user_id(st.session_state.username)
        if not user_id:
            st.warning("⚠️ User not found in database. Creating user...")
            user_id = transaction_store.add_user(
                username=st.session_state.username,
                email=st.session_state.user_profile.get('email', f"{st.session_state.username}@example.com"),
                country=st.session_state.user_profile.get('country', 'India')
            )
            st.success(f"✅ Created user with ID: {user_id}")
        
        # Check if user has transactions
        summary = transaction_store.get_financial_summary(user_id)
        txn_count = summary.get('transaction_count', 0)
        
        if txn_count == 0:
            st.warning("⚠️ No transaction data found!")
            st.info("""
            **Please upload your bank statements first:**
            
            1. Go back to the Dashboard (← button below)
            2. Use the sidebar to upload bank statements
            3. Come back here to chat with the AI Coach
            """)
            if st.button("← Go to Dashboard"):
                st.switch_page("app.py")
            st.stop()
        else:
            st.success(f"✅ Found {txn_count} transactions for analysis")
        
        # Initialize knowledge store
        knowledge_store = FinancialKnowledgeStore(
            user_id="shared",
            api_key=openai_api_key,
            base_url=openai_base_url
        )
        
        # Initialize agent with EXISTING transaction store
        st.session_state.financial_planner_agent = FinancialPlannerAgent(
            transaction_store=transaction_store,  # Use existing store!
            knowledge_store=knowledge_store,
            openai_api_key=openai_api_key,
            base_url=openai_base_url,
            tavily_api_key=tavily_api_key
        )
        
        st.success("✅ AI Financial Planner initialized successfully!")
        
    except Exception as e:
        st.error(f"Failed to initialize AI Financial Planner: {e}")
        import traceback
        st.error(traceback.format_exc())
        st.stop()

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
st.markdown("---")
st.subheader("💬 Conversation")

# Chat container
chat_container = st.container()

with chat_container:
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            with st.chat_message("user"):
                st.write(message['content'])
        else:
            with st.chat_message("assistant"):
                st.write(message['content'])
                
                # Display reasoning if available
                if 'reasoning' in message:
                    with st.expander("🔍 View Agent Reasoning"):
                        for step in message['reasoning']:
                            st.write(f"**{step['agent']}:** {step['action']}")
                
                # ========================================
                # 📊 DISPLAY VISUALIZATIONS (CHAT HISTORY)
                # ========================================
                if 'visualizations' in message and message['visualizations']:
                    st.markdown("---")
                    st.subheader("📊 Visual Analysis")
                    
                    for chart_idx, chart in enumerate(message['visualizations']):
                        chart_type = chart.get('type')
                        chart_title = chart.get('title', 'Chart')
                        chart_data = chart.get('data', {})
                        
                        # Generate unique key for each chart
                        chart_key = f"history_chart_{st.session_state.chat_history.index(message)}_{chart_idx}"
        
                        if chart_type == 'line':
                            import plotly.graph_objects as go
                            
                            fig = go.Figure()
                            
                            for dataset in chart_data.get('datasets', []):
                                fig.add_trace(go.Scatter(
                                    x=chart_data.get('labels', []),
                                    y=dataset.get('data', []),
                                    mode='lines+markers',
                                    name=dataset.get('label', ''),
                                    line=dict(color=dataset.get('borderColor', '')),
                                ))
                            
                            fig.update_layout(
                                title=chart_title,
                                xaxis_title="Period",
                                yaxis_title="Amount (₹)",
                                height=400,
                                hovermode='x unified'
                            )
                            
                            st.plotly_chart(fig, use_container_width=True, key=chart_key)
                        
                        elif chart_type == 'pie':
                            import plotly.graph_objects as go
                            
                            dataset = chart_data.get('datasets', [{}])[0]
                            
                            fig = go.Figure(data=[go.Pie(
                                labels=chart_data.get('labels', []),
                                values=dataset.get('data', []),
                                hole=0.3,
                                textinfo='label+percent',
                                textposition='outside'
                            )])
                            
                            fig.update_layout(
                                title=chart_title,
                                height=500,
                                showlegend=True
                            )
                            
                            st.plotly_chart(fig, use_container_width=True, key=chart_key)
                        
                        elif chart_type == 'bar':
                            import plotly.graph_objects as go
                            
                            dataset = chart_data.get('datasets', [{}])[0]
                            
                            if chart.get('options', {}).get('indexAxis') == 'y':
                                fig = go.Figure(data=[go.Bar(
                                    y=chart_data.get('labels', []),
                                    x=dataset.get('data', []),
                                    orientation='h',
                                    marker_color=dataset.get('backgroundColor', 'rgba(255, 99, 132, 0.6)'),
                                    text=dataset.get('data', []),
                                    texttemplate='₹%{text:,.0f}',
                                    textposition='outside'
                                )])
                                
                                fig.update_layout(
                                    title=chart_title,
                                    xaxis_title="Amount (₹)",
                                    yaxis_title="Category",
                                    height=400
                                )
                            else:
                                fig = go.Figure(data=[go.Bar(
                                    x=chart_data.get('labels', []),
                                    y=dataset.get('data', []),
                                    marker_color=dataset.get('backgroundColor', 'rgba(75, 192, 192, 0.6)'),
                                    text=dataset.get('data', []),
                                    texttemplate='%{text:.1f}%',
                                    textposition='outside'
                                )])
                                
                                fig.update_layout(
                                    title=chart_title,
                                    xaxis_title="Period",
                                    yaxis_title=dataset.get('label', 'Value'),
                                    height=400
                                )
                            
                            st.plotly_chart(fig, use_container_width=True, key=chart_key)
                
                # Display knowledge source indicator
                if 'knowledge_source' in message:
                    if message['knowledge_source'] == 'web_search':
                        st.info("🌐 This response includes real-time information from web search")
                    elif message['knowledge_source'] == 'knowledge_base':
                        st.info("📚 This response uses information from the knowledge base")

# Chat input section
st.markdown("---")

# Example queries
with st.expander("💡 Example Questions"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Spending Analysis:**
        - Analyze my spending patterns
        - Where is my money going?
        - Show me my expense breakdown
        - What are my top spending categories?
        
        **📈 Financial Insights:**
        - How can I save more money?
        - Analyze my savings rate
        - Show me my financial trends
        """)
    
    with col2:
        st.markdown("""
        **💰 Tax & Investment:**
        - How can I save tax?
        - Best investment options for me
        - Should I invest in mutual funds?
        
        **⏰ Time-based Queries:**
        - Show me October 2023 summary
        - Analyze last 6 months
        - Compare Q1 vs Q2
        """)

# Chat input
user_query = st.chat_input("Ask your financial question...")

if user_query:
    # Add user message to chat history
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_query
    })
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_query)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                # Get response from agent
                result = st.session_state.financial_planner_agent.chat(
                    query=user_query,
                    user_id=st.session_state.username
                )
                
                # Display response
                st.write(result['response'])
                
                # Display reasoning
                if result.get('reasoning'):
                    with st.expander("🔍 View Agent Reasoning"):
                        for step in result['reasoning']:
                            st.write(f"**{step['agent']}:** {step['action']}")
                
                # ========================================
                # 📊 DISPLAY VISUALIZATIONS (NEW MESSAGES)
                # ========================================
                if result.get('visualizations'):
                    st.markdown("---")
                    st.subheader("📊 Visual Analysis")
                    
                    for chart in result['visualizations']:
                        chart_type = chart.get('type')
                        chart_title = chart.get('title', 'Chart')
                        chart_data = chart.get('data', {})
                        
                        if chart_type == 'line':
                            import plotly.graph_objects as go
                            
                            fig = go.Figure()
                            
                            for dataset in chart_data.get('datasets', []):
                                fig.add_trace(go.Scatter(
                                    x=chart_data.get('labels', []),
                                    y=dataset.get('data', []),
                                    mode='lines+markers',
                                    name=dataset.get('label', ''),
                                    line=dict(color=dataset.get('borderColor', '')),
                                ))
                            
                            fig.update_layout(
                                title=chart_title,
                                xaxis_title="Period",
                                yaxis_title="Amount (₹)",
                                height=400,
                                hovermode='x unified'
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        elif chart_type == 'pie':
                            import plotly.graph_objects as go
                            
                            dataset = chart_data.get('datasets', [{}])[0]
                            
                            fig = go.Figure(data=[go.Pie(
                                labels=chart_data.get('labels', []),
                                values=dataset.get('data', []),
                                hole=0.3,
                                textinfo='label+percent',
                                textposition='outside'
                            )])
                            
                            fig.update_layout(
                                title=chart_title,
                                height=500,
                                showlegend=True
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        elif chart_type == 'bar':
                            import plotly.graph_objects as go
                            
                            dataset = chart_data.get('datasets', [{}])[0]
                            
                            if chart.get('options', {}).get('indexAxis') == 'y':
                                fig = go.Figure(data=[go.Bar(
                                    y=chart_data.get('labels', []),
                                    x=dataset.get('data', []),
                                    orientation='h',
                                    marker_color=dataset.get('backgroundColor', 'rgba(255, 99, 132, 0.6)'),
                                    text=dataset.get('data', []),
                                    texttemplate='₹%{text:,.0f}',
                                    textposition='outside'
                                )])
                                
                                fig.update_layout(
                                    title=chart_title,
                                    xaxis_title="Amount (₹)",
                                    yaxis_title="Category",
                                    height=400
                                )
                            else:
                                fig = go.Figure(data=[go.Bar(
                                    x=chart_data.get('labels', []),
                                    y=dataset.get('data', []),
                                    marker_color=dataset.get('backgroundColor', 'rgba(75, 192, 192, 0.6)'),
                                    text=dataset.get('data', []),
                                    texttemplate='%{text:.1f}%',
                                    textposition='outside'
                                )])
                                
                                fig.update_layout(
                                    title=chart_title,
                                    xaxis_title="Period",
                                    yaxis_title=dataset.get('label', 'Value'),
                                    height=400
                                )
                            
                            st.plotly_chart(fig, use_container_width=True)
                
                # Display knowledge source
                if result.get('knowledge_source') == 'web_search':
                    st.info("🌐 This response includes real-time information from web search")
                elif result.get('knowledge_source') == 'knowledge_base':
                    st.info("📚 This response uses information from the knowledge base")
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': result['response'],
                    'reasoning': result.get('reasoning', []),
                    'visualizations': result.get('visualizations', []),
                    'knowledge_source': result.get('knowledge_source')
                })
                
            except Exception as e:
                st.error(f"Error: {e}")
                import traceback
                st.error(traceback.format_exc())

# Sidebar with options
with st.sidebar:
    st.header("💬 Chat Options")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    st.divider()
    
    st.info("""
    **🤖 Multi-Agent System:**
    
    1. **Query Understanding** - Analyzes your question
    2. **Data Retrieval** - Fetches your financial data
    3. **Knowledge Search** - Searches knowledge base or web
    4. **Visualization** - Generates charts (when applicable)
    5. **Analysis** - Provides insights & recommendations
    
    **💡 Features:**
    - Natural language queries
    - Time-based analysis
    - Visual charts & graphs
    - Web search fallback (Tavily)
    - Personalized advice
    """)

# Back button
st.divider()
if st.button("← Back to Dashboard"):
    st.switch_page("app.py")