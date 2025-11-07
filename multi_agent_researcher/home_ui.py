"""
home_ui.py
----------
Holds functions to build the top-level page header and side-bar controls.

Why:
- Keeps all Streamlit widget creation in one place so the main file can focus on orchestration.
- Exposes `sidebar_controls()` which returns a plain dict of control values (pure data).
- Exposes `page_header()` for consistent header rendering.
"""

import streamlit as st
import base64

# Embedded small lightbulb SVG as a data URI to avoid remote image failures.
_LIGHTBULB_SVG_DATA_URI = (
    "data:image/svg+xml;utf8,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='64' height='64'%3E"
    "%3Cpath fill='%23f5c542' d='M9 21h6v-1a2 2 0 0 0-2-2H11a2 2 0 0 0-2 2v1z'/%3E"
    "%3Cpath fill='%23f5c542' d='M12 2a7 7 0 0 0-4 12.9V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.1A7 7 0 0 0 12 2z'/%3E"
    "%3C/svg%3E"
)

def sidebar_controls():
    """
    Renders the sidebar controls and returns their values in a dictionary.
    Important: this function only creates widgets and returns plain data (no side-effects).
    """
    st.sidebar.title("Multi-Agent Research Controls")
    query = st.sidebar.text_area("Research Query", value="Impact of quantum computing on cryptography", height=80)
    model = st.sidebar.selectbox("Model", ["local-mock", "gpt-4o", "gpt-4", "openai/gpt-4"], index=0)
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    max_tokens = st.sidebar.slider("Max tokens", 256, 4096, 1024, step=256)
    num_agents = st.sidebar.selectbox("Number of agents to run", [1,2,3,4,5], index=4)
    retrieval_depth = st.sidebar.slider("Retrieval depth (docs per query)", 1, 10, 3)
    # Buttons return True only on the event that triggers them.
    run_button = st.sidebar.button("Run Research", key="run_research")
    clear_button = st.sidebar.button("Clear Results", key="clear_results")
    export_button = st.sidebar.button("Export Request (sidebar)", key="export_sidebar")

    return {
        "query": query,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "num_agents": num_agents,
        "retrieval_depth": retrieval_depth,
        "run": run_button,
        "clear": clear_button,
        "export": export_button
    }

def page_header():
    """
    Renders a consistent page header (logo + title).
    Uses an embedded SVG (data URI) to avoid external image failures.
    """
    col1, col2 = st.columns([9,1])
    with col1:
        st.title("Multi-Agent AI Deep Researcher — UI Prototype")
        st.markdown("A modular Streamlit frontend for multi-agent RAG research (UI-only, stubs in place).")
    with col2:
        # Use embedded svg image (safe) to avoid 3rd-party fetch issues.
        st.image(_LIGHTBULB_SVG_DATA_URI, width=48)
