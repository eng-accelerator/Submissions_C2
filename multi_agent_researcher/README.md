# ai-accelerator-C2
# Hackathon - assignment

Project structure:
multi_agent_researcher/
├─ main.py
├─ home_ui.py
├─ components.py
├─ agents_stub.py
├─ rag.py
├─ utils.py
├─ requirements.txt
└─ README.md

# Multi-Agent Deep Researcher — Streamlit UI (Phase 1, updated)

## Key fixes in this version
- Fixed Clear button (no recursion; uses session state).
- Export sidebar button now shows an alert directing users to the Report panel where a proper Download button exists.
- Added action handler functions for Run / Clear / Export to keep code modular.
- Replaced external lightbulb URL with embedded SVG data URI to avoid broken image fetches.
- Documented all files and functions.

## Quickstart
1. Create venv and install:
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2. Run:
streamlit run main.py


## Integration notes for backend team
- Replace `rag.run_research` internals with the actual orchestrator.
- Keep the returned dict keys exactly as: `retrieval`, `analysis`, `insights`, `report`.
- The UI expects `report['report_markdown']` for the final markdown content.

## Troubleshooting
- If buttons appear unresponsive: confirm no long-blocking network call is placed in the main UI thread (move to an async/job queue).
- Avoid using `st.experimental_rerun()` inside handlers — this version removed such calls to fix the RecursionError you saw.


## Notes & Next steps (phase 2)
Planned UI enhancements (phase 2):
- Theme toggles: Dark / Light / Neon (use `st.set_page_config` + custom CSS)
- Multiple loading indicators (Lottie + progress bar)
- Export to PDF, PPTX
- Post compiled report to LinkedIn (requires OAuth + LinkedIn API)
- Animations and nicer UX polish

## References
- Streamlit docs: https://docs.streamlit.io/ ... :contentReference[oaicite:6]{index=6}
- streamlit-lottie: https://github.com/andfanilo/streamlit-lottie :contentReference[oaicite:7]{index=7}
- LangChain / LangGraph docs: https://docs.langchain.com/ ... :contentReference[oaicite:8]{index=8}
- LlamaIndex docs: https://developers.llamaindex.ai/ ... :contentReference[oaicite:9]{index=9}
- FAISS docs: https://faiss.ai/ ... :contentReference[oaicite:10]{index=10}

Testing plan (so we can demo Saturday 2 PM)
Install requirements and run streamlit run main.py.
Enter a query, tweak temperature/model, click Run Research.
Inspect collapsible agent outputs. Try Download Report (Markdown) to verify file contents.

Ask backend teammates to:
Replace agents_stub calls inside rag.run_research with real orchestration calls (LangGraph or LangChain flows).
Ensure returned dict keys match expected names.
Integration notes & pointers for backend teammates

Thomas (FAISS & SQLite layer): create a microservice function retrieve_docs(query, depth) returning a list of docs: {title, snippet, source, embedding_meta}. The UI will expect retrieval["docs"].
FAISS docs & quickstart: 
faiss.ai
+1

Kalyan (LangChain / LangGraph orchestration): return final structured dict with retrieval, analysis, insights, report. Use streaming to update UI later.
LangChain overview & LangGraph: 
LangChain Docs
+1

Mamta (nodes / prompts): ensure each node outputs a small JSON structure (easy to display).
Testing: the UI works with stubs now; replacing rag.run_research with real async/external calls might block Streamlit. For long-running tasks, expose an async/queue API or background job (e.g., actor model or store state in DB and poll). Later we can integrate durable LangGraph execution.