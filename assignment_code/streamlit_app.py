# -*- coding: utf-8 -*-
"""Streamlit UI for Multi-Agent AI Researcher"""

import streamlit as st
import time
from datetime import datetime
from typing import List, Optional

from researcher import SimpleMultiAgentResearcher


# Page configuration
st.set_page_config(
    page_title="🔬 Multi-Agent AI Researcher",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .status-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .status-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)


def initialize_researcher(api_key: str, model: str, temperature: float) -> Optional[SimpleMultiAgentResearcher]:
    """Initialize the researcher with error handling"""
    try:
        researcher = SimpleMultiAgentResearcher(
            openrouter_api_key=api_key,
            temperature=temperature,
            model=model
        )
        return researcher
    except Exception as e:
        st.error(f"❌ Error initializing researcher: {str(e)}")
        return None


def get_sample_documents() -> List[str]:
    """Return sample documents"""
    return [
        """
        Artificial Intelligence is transforming industries worldwide through advanced
        machine learning capabilities. Key applications include healthcare diagnostics,
        financial analysis, autonomous systems, and natural language processing.
        However, significant challenges remain around algorithmic bias, data privacy,
        transparency, and ethical deployment. Organizations must implement responsible
        AI practices, including bias audits, privacy safeguards, and explainability.
        """,
        """
        The future of AI development focuses on several critical areas. Natural language
        processing continues to advance with large language models showing remarkable
        capabilities. Computer vision applications are expanding in robotics and medical
        imaging. Reinforcement learning is enabling autonomous decision-making systems.
        Key research priorities include explainable AI for trust and transparency,
        federated learning for privacy-preserving collaboration, robust AI safety
        mechanisms, and regulatory frameworks to ensure responsible deployment across
        sectors like healthcare, finance, transportation, and criminal justice.
        """,
        """
        AI adoption patterns vary significantly across industries. Healthcare leads in
        diagnostic AI and drug discovery applications. Financial services use AI for
        fraud detection, risk assessment, and algorithmic trading. Manufacturing
        implements predictive maintenance and quality control. Retail leverages
        recommendation engines and inventory optimization. Transportation advances
        with autonomous vehicles and traffic management. Education explores personalized
        learning through intelligent tutoring systems. Each sector faces unique
        challenges in implementation, from data quality to regulatory compliance.
        """
    ]


def main():
    # Header
    st.markdown('<h1 class="main-header">🔬 Multi-Agent AI Researcher</h1>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            help="Get your API key from https://openrouter.ai/keys",
            value=st.session_state.get("api_key", "")
        )
        st.session_state["api_key"] = api_key

        # Model selection
        st.subheader("🤖 Model Selection")
        model_options = {
            "Claude Sonnet 4 (Best balance)": "anthropic/claude-sonnet-4-20250514",
            "GPT-4o (Fast)": "openai/gpt-4o",
            "Llama 3.1 70B (Budget)": "meta-llama/llama-3.1-70b-instruct"
        }
        selected_model_name = st.selectbox(
            "Choose Model",
            options=list(model_options.keys()),
            index=0
        )
        selected_model = model_options[selected_model_name]

        # Temperature slider
        st.subheader("🌡️ Settings")
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Higher values make output more creative, lower values more focused"
        )

        # Max iterations
        max_iterations = st.slider(
            "Max Iterations",
            min_value=1,
            max_value=5,
            value=2,
            help="Maximum number of validation iterations"
        )

        st.markdown("---")
        st.markdown("### 📚 Document Management")
        
        # Document input options
        doc_option = st.radio(
            "Document Source",
            ["Use Sample Documents", "Upload Text Documents", "Paste Documents"],
            index=0
        )

        documents = []
        if doc_option == "Use Sample Documents":
            documents = get_sample_documents()
            st.info(f"✅ {len(documents)} sample documents loaded")
        elif doc_option == "Upload Text Documents":
            uploaded_files = st.file_uploader(
                "Upload text files",
                type=["txt"],
                accept_multiple_files=True
            )
            if uploaded_files:
                for file in uploaded_files:
                    content = file.read().decode("utf-8")
                    documents.append(content)
                st.success(f"✅ {len(documents)} document(s) uploaded")
        elif doc_option == "Paste Documents":
            doc_text = st.text_area(
                "Paste document text (one per line or separated by blank lines)",
                height=200
            )
            if doc_text:
                # Split by double newlines or treat as single document
                if "\n\n" in doc_text:
                    documents = [doc.strip() for doc in doc_text.split("\n\n") if doc.strip()]
                else:
                    documents = [doc_text.strip()]
                st.success(f"✅ {len(documents)} document(s) loaded")

    # Main content area
    if not api_key:
        st.warning("⚠️ Please enter your OpenRouter API key in the sidebar to begin.")
        st.info("💡 Get your API key from [OpenRouter](https://openrouter.ai/keys)")
        return

    # Initialize researcher
    if "researcher" not in st.session_state or st.session_state.get("api_key") != api_key:
        with st.spinner("🔄 Initializing researcher..."):
            researcher = initialize_researcher(api_key, selected_model, temperature)
            if researcher:
                st.session_state["researcher"] = researcher
                st.session_state["model"] = selected_model
                st.session_state["documents"] = documents
            else:
                return
    else:
        researcher = st.session_state["researcher"]
        # Update documents if changed
        if documents:
            researcher.load_documents(documents)
            st.session_state["documents"] = documents

    # Research query input
    st.subheader("🔍 Research Query")
    query = st.text_area(
        "Enter your research question",
        height=100,
        placeholder="e.g., What are the key challenges and opportunities in AI deployment across healthcare?"
    )

    # Research button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        research_button = st.button("🚀 Start Research", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🔄 Clear Results", use_container_width=True)

    if clear_button:
        if "results" in st.session_state:
            del st.session_state["results"]
        st.rerun()

    # Execute research
    if research_button and query:
        if not query.strip():
            st.error("❌ Please enter a research question.")
            return

        # Load documents
        if documents:
            researcher.load_documents(documents)

        # Display progress
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.text("🔄 Starting research workflow...")
            progress_bar.progress(10)

            # Create placeholder for results
            results_placeholder = st.empty()

            # Execute research
            with st.spinner("🔬 Research in progress... This may take 30-60 seconds"):
                results = researcher.research(
                    query=query,
                    temperature=temperature,
                    max_iterations=max_iterations
                )

            progress_bar.progress(100)
            status_text.text("✅ Research complete!")
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()

            # Store results in session state
            st.session_state["results"] = results

        except Exception as e:
            st.error(f"❌ Error during research: {str(e)}")
            st.info("💡 Troubleshooting tips:")
            st.markdown("""
            - Check that your API key is valid
            - Ensure you have credits at https://openrouter.ai/credits
            - Try a different model
            - Check your internet connection
            """)
            return

    # Display results
    if "results" in st.session_state:
        results = st.session_state["results"]

        # Status metrics
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_color = "🟢" if results["validation_passed"] else "🟡"
            status_text = "VALIDATED" if results["validation_passed"] else "NEEDS REVIEW"
            st.metric("Status", f"{status_color} {status_text}")
        
        with col2:
            st.metric("Iterations", results["iterations"])
        
        with col3:
            st.metric("Total Time", f"{results['total_time']:.1f}s")
        
        with col4:
            st.metric("Insights", len(results["insights"]))

        # Research Report
        st.markdown("---")
        st.subheader("📄 Research Report")
        st.markdown(results["report"])

        # Key Insights
        st.markdown("---")
        st.subheader("💡 Key Insights")
        for i, insight in enumerate(results["insights"], 1):
            st.markdown(f"**{i}.** {insight}")

        # Validation Feedback
        st.markdown("---")
        st.subheader("✅ Validation Feedback")
        if results["validation_passed"]:
            st.success(results["validation_feedback"])
        else:
            st.warning(results["validation_feedback"])

        # Performance Metrics
        with st.expander("⚡ Performance Metrics"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Processing Times:**")
                for agent, duration in results["processing_time"].items():
                    st.write(f"- {agent.capitalize()}: {duration:.2f}s")
            
            with col2:
                st.write("**Critical Analysis:**")
                st.text_area("", results["analysis"], height=200, disabled=True, label_visibility="collapsed")

        # Download button
        st.markdown("---")
        st.subheader("💾 Download Results")
        
        # Generate report text
        report_text = f"""
RESEARCH REPORT
{'='*60}

Query: {results['query']}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: {'VALIDATED ✓' if results['validation_passed'] else 'NEEDS REVIEW'}
Iterations: {results['iterations']}
Total Time: {results['total_time']:.1f}s

{'='*60}
RESEARCH REPORT
{'='*60}

{results['report']}

{'='*60}
KEY INSIGHTS
{'='*60}

"""
        for i, insight in enumerate(results['insights'], 1):
            report_text += f"{i}. {insight}\n"

        report_text += f"""

{'='*60}
VALIDATION FEEDBACK
{'='*60}

{results['validation_feedback']}

{'='*60}
PERFORMANCE METRICS
{'='*60}

"""
        for agent, duration in results['processing_time'].items():
            report_text += f"{agent.capitalize()}: {duration:.2f}s\n"

        # Download button
        st.download_button(
            label="📥 Download Report as TXT",
            data=report_text,
            file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )


if __name__ == "__main__":
    main()

