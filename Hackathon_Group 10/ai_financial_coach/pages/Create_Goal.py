# pages/Create_Goal.py
# Goal creation with investment recommendations

import streamlit as st
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import json

st.set_page_config(
    page_title="Create Goal - AI Financial Coach",
    page_icon="🎯",
    layout="wide"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in first")
    st.switch_page("app.py")
    st.stop()

st.title("🎯 Create New Financial Goal")
st.subheader("Set your goal and get personalized investment recommendations")

# Initialize session state for goal creation
if 'new_goal_data' not in st.session_state:
    st.session_state.new_goal_data = None

if 'investment_recommendations' not in st.session_state:
    st.session_state.investment_recommendations = None

# Two-step process: 1. Define Goal, 2. Get Investment Options
tabs = st.tabs(["📝 Define Goal", "💰 Investment Options"])

# ==================== TAB 1: DEFINE GOAL ====================
with tabs[0]:
    st.markdown("### Tell us about your financial goal")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Goal Details Form
        with st.form("goal_creation_form"):
            st.markdown("#### Goal Details")
            
            goal_name = st.text_input(
                "Goal Name *",
                placeholder="e.g., Emergency Fund, Car Purchase, Vacation",
                help="Give your goal a meaningful name"
            )
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                target_amount = st.number_input(
                    "Target Amount (₹) *",
                    min_value=1000.0,
                    max_value=100000000.0,
                    value=100000.0,
                    step=10000.0,
                    help="How much money do you need?"
                )
            
            with col_b:
                current_balance = st.number_input(
                    "Current Savings (₹)",
                    min_value=0.0,
                    max_value=target_amount,
                    value=0.0,
                    step=5000.0,
                    help="How much have you saved already?"
                )
            
            st.markdown("#### Timeline")
            
            goal_type = st.radio(
                "When do you need this money?",
                ["Specific Date", "Time Period (Months)", "Flexible"],
                horizontal=True
            )
            
            due_date = None
            time_horizon_months = None
            
            if goal_type == "Specific Date":
                due_date = st.date_input(
                    "Target Date",
                    min_value=date.today(),
                    value=date.today() + timedelta(days=365)
                )
                # Calculate months from today to due date
                months_diff = (due_date.year - date.today().year) * 12 + (due_date.month - date.today().month)
                time_horizon_months = max(1, months_diff)
                st.caption(f"📅 That's approximately **{time_horizon_months} months** from now")
            
            elif goal_type == "Time Period (Months)":
                time_horizon_months = st.slider(
                    "Time Horizon (Months)",
                    min_value=3,
                    max_value=360,
                    value=24,
                    step=3,
                    help="How many months until you need this money?"
                )
                # Calculate approximate due date
                due_date = date.today() + relativedelta(months=time_horizon_months)
                st.caption(f"📅 Target date: **{due_date.strftime('%B %Y')}**")
            
            else:  # Flexible
                time_horizon_months = st.slider(
                    "Approximate Timeline (Months)",
                    min_value=12,
                    max_value=360,
                    value=60,
                    step=6,
                    help="Rough estimate for planning purposes"
                )
                st.caption("🔄 Timeline is flexible - we'll optimize for best returns")
            
            st.markdown("#### Investment Preferences")
            
            risk_tolerance = st.select_slider(
                "Risk Tolerance",
                options=["conservative", "balanced", "aggressive"],
                value="balanced",
                help="How comfortable are you with market volatility?"
            )
            
            # Risk tolerance explanation
            risk_info = {
                "conservative": "🛡️ Safety first - Minimize risk, accept lower returns",
                "balanced": "⚖️ Moderate approach - Balance growth and stability",
                "aggressive": "🚀 Growth focused - Accept higher risk for potentially higher returns"
            }
            st.info(risk_info[risk_tolerance])
            
            # Calculate required monthly contribution
            shortfall = max(0, target_amount - current_balance)
            if time_horizon_months and time_horizon_months > 0:
                required_monthly = shortfall / time_horizon_months
                st.markdown("---")
                st.markdown("#### 💡 Quick Estimate")
                st.metric(
                    "Required Monthly Contribution",
                    f"₹{required_monthly:,.0f}",
                    help="This is a simple calculation without considering returns"
                )
                st.caption("*Actual amount may be lower with investment returns")
            
            # Form submission
            submitted = st.form_submit_button(
                "🎯 Get Investment Recommendations",
                type="primary",
                use_container_width=True
            )
            
            if submitted:
                if not goal_name:
                    st.error("Please provide a goal name")
                elif not time_horizon_months:
                    st.error("Please specify a timeline")
                else:
                    # Store goal data
                    st.session_state.new_goal_data = {
                        'goal_name': goal_name,
                        'target_amount': target_amount,
                        'current_balance': current_balance,
                        'time_horizon_months': time_horizon_months,
                        'due_date': due_date,
                        'risk_tolerance': risk_tolerance,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    # Calculate monthly contribution estimate
                    monthly_estimate = required_monthly if time_horizon_months > 0 else 0
                    
                    # Get investment recommendations
                    with st.spinner("🤖 Analyzing your goal and generating investment strategy..."):
                        try:
                            from core.investment_options_agent import (
                                InvestmentOptionsAgent,
                                InvestmentOptionsInput
                            )
                            
                            # Initialize agent
                            openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("openai_api_key")
                            openai_base_url = os.getenv("OPENAI_BASE_URL") or st.secrets.get("openai_base_url")
                            
                            agent = InvestmentOptionsAgent(
                                openai_api_key=openai_api_key,
                                base_url=openai_base_url
                            )
                            
                            # Create input
                            investment_input = InvestmentOptionsInput(
                                goal_id=f"goal_{datetime.now().timestamp()}",
                                goal_name=goal_name,
                                target_amount=target_amount,
                                current_balance=current_balance,
                                monthly_contribution=monthly_estimate,
                                time_horizon_months=time_horizon_months,
                                due_date=due_date,
                                risk_tolerance=risk_tolerance
                            )
                            
                            # Get recommendations
                            strategy = agent.recommend(investment_input)
                            
                            st.session_state.investment_recommendations = strategy.model_dump()
                            
                            st.success("✅ Investment strategy generated!")
                            st.info("👉 Switch to the **Investment Options** tab to see recommendations")
                            
                        except Exception as e:
                            st.error(f"Error generating recommendations: {e}")
                            import traceback
                            st.error(traceback.format_exc())
    
    with col2:
        # Goal Examples
        st.markdown("### 💡 Goal Examples")
        
        example_goals = [
            {
                "name": "Emergency Fund",
                "amount": "₹1,50,000",
                "timeline": "6 months",
                "risk": "Conservative"
            },
            {
                "name": "Car Purchase",
                "amount": "₹8,00,000",
                "timeline": "2 years",
                "risk": "Balanced"
            },
            {
                "name": "House Down Payment",
                "amount": "₹20,00,000",
                "timeline": "5 years",
                "risk": "Aggressive"
            },
            {
                "name": "Retirement Fund",
                "amount": "₹1,00,00,000",
                "timeline": "20 years",
                "risk": "Aggressive"
            }
        ]
        
        for example in example_goals:
            with st.expander(f"🎯 {example['name']}"):
                st.write(f"**Target:** {example['amount']}")
                st.write(f"**Timeline:** {example['timeline']}")
                st.write(f"**Risk:** {example['risk']}")

# ==================== TAB 2: INVESTMENT OPTIONS ====================
with tabs[1]:
    if not st.session_state.investment_recommendations:
        st.info("👈 Please create a goal first to see investment recommendations")
    else:
        strategy = st.session_state.investment_recommendations
        goal_data = st.session_state.new_goal_data
        
        st.markdown("### 📊 Investment Strategy for Your Goal")
        
        # Goal Summary
        st.markdown(f"#### 🎯 {strategy['goal_name']}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Target Amount", f"₹{strategy['target_amount']:,.0f}")
        with col2:
            st.metric("Current Balance", f"₹{strategy['current_balance']:,.0f}")
        with col3:
            st.metric("Time Horizon", f"{strategy['time_horizon_months']} months")
        with col4:
            st.metric("Expected Return", f"{strategy['overall_expected_return']*100:.1f}%")
        
        st.divider()
        
        # Risk Assessment
        st.markdown("#### 🎲 Risk Assessment")
        st.info(strategy['risk_assessment'])
        
        st.divider()
        
        # Investment Recommendations
        st.markdown("#### 💰 Recommended Investment Mix")
        
        if strategy['recommended_options']:
            # Create allocation pie chart
            import plotly.graph_objects as go
            
            labels = [opt['name'] for opt in strategy['recommended_options']]
            values = [opt['allocation_percentage'] for opt in strategy['recommended_options']]
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.3,
                textinfo='label+percent',
                textposition='outside'
            )])
            
            fig.update_layout(
                title="Asset Allocation",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            # Detailed Investment Options
            st.markdown("#### 📋 Investment Details")
            
            for idx, option in enumerate(strategy['recommended_options'], 1):
                with st.expander(
                    f"**{idx}. {option['name']}** - {option['allocation_percentage']:.0f}% allocation",
                    expanded=True
                ):
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("Expected Return", f"{option['expected_return_annual']*100:.1f}%")
                    with col_b:
                        st.metric("Risk Level", option['risk_category'].replace('_', ' ').title())
                    with col_c:
                        st.metric("Liquidity", f"{option['liquidity_days']} days")
                    
                    st.markdown(f"**💡 Why this option:** {option['rationale']}")
                    
                    if option['min_investment'] > 0:
                        st.caption(f"💵 Minimum Investment: ₹{option['min_investment']:,.0f}")
                    
                    if option['lock_in_period_months']:
                        st.warning(f"🔒 Lock-in Period: {option['lock_in_period_months']} months")
                    
                    if option['tax_benefits']:
                        st.success(f"💰 Tax Benefits: {option['tax_benefits']}")
            
            st.divider()
            
            # Action Plan
            st.markdown("#### 🚀 Action Plan")
            
            st.markdown(f"**Rebalancing:** {strategy['rebalancing_frequency']}")
            
            st.markdown("**📝 Notes:**")
            for note in strategy['notes']:
                st.write(f"- {note}")
            
            st.divider()
            
            # Save Goal Button
            col_save, col_reset = st.columns(2)
            
            with col_save:
                if st.button("💾 Save This Goal", type="primary", use_container_width=True):
                    # TODO: Save to database/savings strategy agent
                    st.success("✅ Goal saved! You can now track it from the dashboard")
                    st.balloons()
            
            with col_reset:
                if st.button("🔄 Create Another Goal", use_container_width=True):
                    st.session_state.new_goal_data = None
                    st.session_state.investment_recommendations = None
                    st.rerun()

# Back button
st.divider()
if st.button("← Back to Dashboard"):
    st.switch_page("app.py")