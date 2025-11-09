# pages/1_📚_Knowledge_Base.py
# Manage financial knowledge base - manual upload or AI crawler
# SHARED knowledge base across all users

import streamlit as st
from core.knowledge_store import FinancialKnowledgeStore
from core.knowledge_crawler import FinancialKnowledgeCrawler
import os

st.set_page_config(
    page_title="Knowledge Base - AI Financial Coach",
    page_icon="📚",
    layout="wide"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in first")
    st.switch_page("app.py")
    st.stop()

st.title("📚 Financial Knowledge Base")
st.subheader("Upload documents or let AI crawl financial information")

# Initialize SHARED knowledge store
if 'knowledge_store' not in st.session_state:
    try:
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("openai_api_key")
        base_url = os.getenv("OPENAI_BASE_URL") or st.secrets.get("openai_base_url")
        
        # Use "shared" as user_id for shared knowledge base
        st.session_state.knowledge_store = FinancialKnowledgeStore(
            user_id="shared",
            api_key=api_key,
            base_url=base_url
        )
    except Exception as e:
        st.error(f"Failed to initialize knowledge store: {e}")
        st.stop()

# Tab layout
tab1, tab2 = st.tabs(["📤 Manual Upload", "📊 Statistics"])

# ==================== TAB 1: MANUAL UPLOAD ====================
with tab1:
    st.header("Upload Financial Documents")
    
    st.info("📌 **Note:** Uploaded documents are shared across all users!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        doc_type = st.selectbox(
            "Document Type",
            ["Tax Documents", "Investment Statements", "Insurance Policies", 
             "Loan Agreements", "Financial Articles"]
        )
        
        uploaded_files = st.file_uploader(
            "Upload PDF documents",
            type=['pdf'],
            accept_multiple_files=True,
            key="knowledge_upload"
        )
        
        if uploaded_files:
            st.success(f"✓ {len(uploaded_files)} file(s) selected")
            
            # Additional metadata
            metadata = {}
            
            if doc_type == "Tax Documents":
                col_a, col_b = st.columns(2)
                with col_a:
                    metadata['region'] = st.selectbox("Region", ["India", "Poland"])
            
            elif doc_type == "Insurance Policies":
                metadata['policy_type'] = st.selectbox(
                    "Policy Type",
                    ["Term Life", "Health Insurance", "Vehicle Insurance", "Other"]
                )
                metadata['region'] = st.selectbox("Region", ["India", "USA", "UK", "Singapore", "UAE"])
            
            elif doc_type == "Loan Agreements":
                metadata['loan_type'] = st.selectbox(
                    "Loan Type",
                    ["Home Loan", "Personal Loan", "Education Loan", "Vehicle Loan", "Other"]
                )
                metadata['region'] = st.selectbox("Region", ["India", "Poland"])
            
            else:
                metadata['region'] = st.selectbox("Region", ["Global", "Poland"])
            
            if st.button("📥 Upload to Knowledge Base", type="primary"):
                with st.spinner("Processing documents..."):
                    progress_bar = st.progress(0)
                    
                    for idx, file in enumerate(uploaded_files):
                        try:
                            if doc_type == "Tax Documents":
                                st.session_state.knowledge_store.add_tax_document(
                                    file, file.name, metadata.get('region', 'India')
                                )
                            elif doc_type == "Insurance Policies":
                                st.session_state.knowledge_store.add_insurance_policy(
                                    file, file.name, metadata.get('policy_type', 'Other'),
                                    metadata.get('region', 'India')
                                )
                            elif doc_type == "Loan Agreements":
                                st.session_state.knowledge_store.add_loan_agreement(
                                    file, file.name, metadata.get('loan_type', 'Other'),
                                    metadata.get('region', 'India')
                                )
                            else:
                                st.session_state.knowledge_store.add_investment_guide(
                                    file, file.name, metadata.get('region', 'Global')
                                )
                            
                            progress_bar.progress((idx + 1) / len(uploaded_files))
                        
                        except Exception as e:
                            st.error(f"Error processing {file.name}: {e}")
                
                st.success(f"✅ Uploaded {len(uploaded_files)} document(s) to SHARED knowledge base")
                st.balloons()
    
    with col2:
        st.info("""
        **📝 Guidelines:**
        
        - PDF format only
        - Max 20MB per file
        - Clear, readable text
        
        **Shared Storage:**
        - Available to all users
        - Helps everyone learn
        - Reduces redundancy
        """)


# ==================== TAB 3: STATISTICS ====================
with tab2:
    st.header("📊 Knowledge Base Statistics")
    
    try:
        stats = st.session_state.knowledge_store.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Total Documents", stats['total_documents'])
        with col2:
            st.metric("📋 Tax Documents", stats['categories']['tax_documents'])
        with col3:
            st.metric("📈 Investment Guides", stats['categories']['investment_guides'])
        with col4:
            st.metric("🏥 Insurance Policies", stats['categories']['insurance_policies'])
        
        col5, col6, col7 = st.columns(3)
        with col5:
            st.metric("💰 Loan Agreements", stats['categories']['loan_agreements'])
        with col6:
            st.metric("📰 Articles", stats['categories']['articles'])
        
        st.divider()
        
        # Regional breakdown
        st.subheader("🌍 Knowledge by Region")
        
        if stats['by_region']:
            for region, count in stats['by_region'].items():
                st.write(f"**{region}:** {count} documents")
        else:
            st.info("No regional data yet")
        
        st.divider()
        
        # Document breakdown
        st.subheader("📚 Document Breakdown")
        
        for category, count in stats['categories'].items():
            if count > 0:
                with st.expander(f"{category.replace('_', ' ').title()} ({count})"):
                    st.write(f"✓ {count} documents in this category")
                    st.caption("Shared across all users")
    
    except Exception as e:
        st.error(f"Error loading statistics: {e}")

# Back button
st.divider()
if st.button("← Back to Dashboard"):
    st.switch_page("app.py")