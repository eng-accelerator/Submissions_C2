"""
main.py
-------
Streamlit app entry for the Multi-Agent Deep Researcher UI prototype.

Important changes in this version:
- All button actions use dedicated handler functions.
- `Clear` no longer calls `st.experimental_rerun()` (which previously caused recursion).
  We use session-state flags and present non-blocking alerts instead.
- `Export` sidebar button shows an alert directing the user to the report's Download button.
- The report panel contains the actual `st.download_button` for a deterministic export flow.

Keep the same module names and data shapes as previous version to ensure backend compatibility.
"""

# To ensure without our secret key we will not be able to run the app
# rest of your app code below
from dotenv import load_dotenv
load_dotenv()
import guard

import streamlit as st
from home_ui import sidebar_controls, page_header
from components import lottie_spinner
from rag import run_research
from utils import compile_report_md

st.set_page_config(page_title="Multi-Agent Deep Researcher", layout="wide")

# Page header (kept the same place as before to preserve "core answer")
page_header()

# Initialize session_state keys used by handlers
if "results" not in st.session_state:
    st.session_state["results"] = None
if "last_action" not in st.session_state:
    st.session_state["last_action"] = None
if "alert_message" not in st.session_state:
    st.session_state["alert_message"] = None

# Lottie animation url (optional). The components loader will fallback safely if it can't fetch.
LOTTIE_URL = "https://assets5.lottiefiles.com/packages/lf20_V9t630.json"

# --- Action Handlers (clear, run, export) ---------------------------------
def handle_clear():
    """
    Handler for 'Clear Results' button.
    Important: Do NOT force an experimental rerun here. Instead, clear session data and set an alert.
    This prevents multiple scheduled event-loop callbacks (which caused recursion).
    """
    st.session_state["results"] = None
    st.session_state["last_action"] = "clear"
    st.session_state["alert_message"] = "Results cleared. You can run another research."

def handle_export_sidebar():
    """
    Handler for the sidebar 'Export' button.
    For now this simply informs the user where to export from (the Report panel contains the download).
    """
    st.session_state["last_action"] = "export_sidebar"
    st.session_state["alert_message"] = (
        "To export the compiled report, expand the 'Report Builder Agent' panel and click 'Download Report (Markdown)'."
    )

def handle_run(query: str, num_agents: int, retrieval_depth: int, model: str, temperature: float):
    """
    Handler for the 'Run Research' action. Runs the orchestrator (stubbed) and stores results.
    We display a spinner + Lottie while the background call executes.
    """
    st.session_state["last_action"] = "run"
    st.session_state["alert_message"] = f"Running research for query: '{query[:80]}'"

    # run the orchestrator (blocking for this prototype). Backend can implement async/queue later.
    results = run_research(
        query=query,
        num_agents=num_agents,
        retrieval_depth=retrieval_depth,
        model=model,
        temperature=temperature
    )
    st.session_state["results"] = results
    st.session_state["alert_message"] = "Research completed successfully."

# --- Build sidebar and react to controls -----------------------------------
controls = sidebar_controls()

# React to actions by calling handlers (do not experimental_rerun)
if controls["clear"]:
    handle_clear()

if controls["export"]:
    handle_export_sidebar()

if controls["run"]:
    q = controls["query"].strip()
    if not q:
        st.sidebar.error("Please provide a research query.")
    else:
        # Show Lottie spinner and message while running the handler
        with st.spinner("Launching agents & running research pipeline..."):
            col1, col2 = st.columns([3,7])
            with col1:
                # render spinner (components handles fallback)
                lottie_spinner(url=LOTTIE_URL, height=150, key="main_spinner")
            with col2:
                st.info("Agents running: Retriever → Analysis → Insights → Report Builder")
                handle_run(
                    query=q,
                    num_agents=controls["num_agents"],
                    retrieval_depth=controls["retrieval_depth"],
                    model=controls["model"],
                    temperature=controls["temperature"]
                )

# Show an alert banner if available (non-modal).
if st.session_state.get("alert_message"):
    st.info(st.session_state["alert_message"])

# --- Display results (same structure as before, with download support) -----
if st.session_state["results"]:
    results = st.session_state["results"]
    st.success("Research run finished — see agent outputs below.")

    # Retrieval Agent
    with st.expander("Contextual Retriever Agent (click to expand)", expanded=True):
        st.write(results["retrieval"]["summary"])
        for doc in results["retrieval"]["docs"]:
            st.markdown(f"**{doc['title']}**  \n{doc['snippet']}  \nSource: {doc['source']}")

    # Critical Analysis Agent
    with st.expander("Critical Analysis Agent"):
        st.write(results["analysis"]["analysis"])
        st.write("Contradictions:")
        for c in results["analysis"]["contradictions"]:
            st.warning(c)
        st.write("Insights:")
        for i in results["analysis"]["insights"]:
            st.write(f"- {i}")

    # Insight Generation Agent
    with st.expander("Insight Generation Agent"):
        for h in results["insights"]["hypotheses"]:
            st.write(f"- {h}  ")
        st.write(f"Confidence: {results['insights']['confidence']:.2f}")

    # Report Builder Agent (contains the actual download button)
    with st.expander("Report Builder Agent (compiled report)"):
        report_md = results["report"]["report_markdown"]
        st.markdown(report_md)

        # Provide final compiled markdown with timestamp
        final_md = compile_report_md(results)

        # The actual export/download is provided as a download_button here.
        # Sidebar export only shows an alert that points the user here.
        st.download_button(
            "Download Report (Markdown)",
            final_md,
            file_name="research_report.md",
            mime="text/markdown"
        )

# If no results, show a friendly placeholder and short instructions
if not st.session_state["results"]:
    st.write("---")
    st.header("Ready to run research")
    st.write(
        "Enter your research query and tweak model/moderation options in the sidebar. "
        "Click **Run Research** to start. Use **Clear Results** to reset the UI."
    )
