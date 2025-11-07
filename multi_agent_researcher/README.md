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


Initial Prompt:
Act as a team of experts from generative AI, Streamlit and Python experts
Do, refer all the relevant resources and documentation as we want a fully working and  documented result. Think test properly and provide solution. 

We have been given an assignment on our AI completion hackathon and I have been given a responsibility to mainly work on the frontend part of the assignment. We are team of 5 members. 
Though I have team but I might work on the whole complete solution.


I do want full working solution consider following points:

1. I want it to be developed on streamlit - Complete python code fully customisable and documented so that we can do proper changes later on
2. I want user input, buttons, result of the deep research with a collapsible panel, Gen AI modulators like temperature, selecting models etc, loading indicators etc.. 
3. Want I want to develop after first draft - Three theme toggles Dark, white, neon | Different loading indicators may be we will use Lottie animations | Export to files etc |  Post to Linkedin social media | Various animations very cool and sobers (These points I need on the second draft once we make our first phase of UI ready and fully working wrt UI)
4. Make sure right now we fully focus on UI creation only
5. Do create different files like main.py | homeUI.py | rag classes file different | langchai lang graph files if required different so all the backend processing happening should have proper different modular files - This initial structure with fully working UI, I will be sharing with the whole team on git so that they can continue working on there part, I am sharing transcripts of our first meeting and small draft of task provided to our team.

Task:
 Multi-Agent AI Deep Researcher
What it demonstrates:
An AI-powered research assistant for multi-hop, multi-source investigations. The system spins up specialized agents that:
Contextual Retriever Agent – Pulls data from research papers, news articles, reports, and APIs.
Critical Analysis Agent – Summarizes findings, highlights contradictions, and validates sources.
Insight Generation Agent – Suggests hypotheses or trends using reasoning chains.
Report Builder Agent – Compiles all insights into a structured report
Any more agents you want to add
Why it's ideal:
Showcases agent collaboration, retrieval-augmented reasoning, and long-context synthesis.
You can use frameworks like LangChain/Langgraph, LlamaIndex, etc to build this.




Transcript:
Project: Multi-Agent AI Deep Researcher
Hackathon Team Formation & Task Allocation
 
Team Roles
Manish - Front-End Lead (UI/UX)
•⁠  ⁠Design and implement web-based user interface aesthetically.
•⁠  ⁠Integrate dynamic elements like progress indicators and collapsible analysis panels.
 
Thomas - VectorDB, SQLite and RAG
•⁠  ⁠Implement local FAISS vector store for knowledge retrieval.
•⁠  ⁠Design the RAG pipeline connecting document retrievers and embeddings to LangChain/LangGraph agents.
•⁠  ⁠Build the SQLite layer for persistent metadata (queries, agent states, cached insights).
•⁠  ⁠Collaborate with Kalyan on data flow and retrieval orchestration.
•⁠  ⁠Deliver functional retrieval and ranking logic for first release
•⁠  ⁠Create the logic flow diagram of our AI app process
o	As first pass
o	Everyone to review and augment as deemed fit
 
Kalyan - Tools, LangChain/LangGraph, Orchestration and Indexing with LlamaIndex
•⁠  ⁠Lead backend orchestration of agents using LangChain/LangGraph.
•⁠  ⁠Integrate LlamaIndex for document ingestion and contextual indexing.
•⁠  ⁠Develop the orchestration logic that manages agent collaboration, dependencies, and error handling.
•⁠  ⁠Work with Thomas to integrate RAG into the orchestration layer
•⁠  ⁠Validate state transitions in LangGraph and debug agent logic.

 
Mamta - Nodes
•⁠  ⁠Define and implement agent nodes for:
o	Contextual Retriever Agent
o	Critical Analysis Agent
o	Insight Generation Agent
o	Report Builder Agent
o	And any additional needed to successfully run Deep Research
•⁠  ⁠Manage prompt design, data flow between nodes, and ensure each returns structured outputs.
 
Monalisa - Presentation and Demo
•⁠  ⁠Create a PowerPoint deck presenting:
o	Objective, architecture, workflow, agent roles and output
o	Screenshots or live demo visuals
•⁠  ⁠Record a video demo using the mentor-specified tool (showing workflow and app usage).
•⁠  ⁠Ensure final pitch materials are ready before submission.
 
Timeline
•	 By the end of Friday Evening class:
o	Thomas & Kalyan draft system flow diagram (architecture + agent interactions).
o	Team reviews whether to include Human-in-the-Loop feedback during evaluation phase.
o	Manish finalizes UI skeleton.
•⁠  ⁠Saturday, Nov 8 (2 PM IST):
o	First working release due — integrated agents, functioning RAG pipeline, and basic Streamlit UI.
o	Dry-run internal demo for feedback.
•⁠  ⁠Post-2 PM:
o	Polish UI/UX, refine prompts, finalize slides, and record video demo.
•⁠  ⁠Saturday Mid-night IST:
o	Finalize the code
o	Integrate with Front End GUI
 
Flow Design Discussion
•⁠  ⁠Thomas & Kalyan will take first pass at designing the flow diagram:
o	Define agent data paths and message passing.
o	Determine if “Human-in-the-Loop” validation occurs between analysis and insight generation.
o	Present for team review and refinement.


Last promt:
Before we proceed further which we will do indeed after my query: Can you create a proper flow diagram which I can copy paste which will consist each and every step of this assignment like - User will input - Step 1.... what will happen - Step 2 what will happen etc... 

After this we will again come to our actual code to do further things... 
