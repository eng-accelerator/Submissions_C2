# Project Plan: Agentic RAG AI Application MVP

**To:** Development Team  
**From:** Project Manager  
**Date:** November 6, 2025  
**Subject:** MVP Project Plan & Backlog

---

## 1. Project Goal

To build and deliver a functional Minimum Viable Product (MVP) of the Agentic RAG AI Application as defined in the `product-requirements.md` and guided by the `architecture-mvp.md` and `implementation-plan.md` documents.

## 2. High-Level Project Epics

This plan is broken down into five sequential epics. Each epic contains a set of high-level tasks that must be completed to close the epic.

---

### Epic 1: Project Setup & Core UI Shell

*   **Goal:** Establish the foundational structure of the application and a functional, non-interactive UI.
*   **Tasks:**
    *   [x] Create the project directory structure as outlined in the implementation plan.
    *   [x] Initialize the project with a `pyproject.toml` file, defining initial metadata.
    *   [x] Use `uv` to create and manage the virtual environment.
    *   [x] Add initial dependencies to `pyproject.toml`.
    *   [x] Build the basic Streamlit UI shell in `app.py`, including:
        *   [x] Main title.
        *   [x] Sidebar with placeholders for API keys and document uploader.
        *   [x] Radio button for mode selection ("Chat Mode" / "Analysis Mode").
        *   [x] A disabled chat input box.
    *   [x] Implement the configuration module (`src/config.py`) to handle environment variables.

---

### Epic 2: Document Processing & Vectorization

*   **Goal:** Enable users to upload documents and have them processed into a searchable vector store.
*   **Tasks:**
    *   [x] Implement file reading logic in `src/document_processor.py` to handle PDF and TXT files.
    *   [x] Implement text chunking using `RecursiveCharacterTextSplitter`.
    *   [x] Implement the embedding model loader.
    *   [x] Implement the FAISS vector store creation logic.
    *   [x] Connect the document processing pipeline to the "Process Documents" button in the Streamlit UI.
    *   [x] Store the created FAISS index in the `st.session_state`.

---

### Epic 3: Core Agentic Workflow (Chat Mode)

*   **Goal:** Implement the main agentic chat functionality.
*   **Tasks:**
    *   [x] Implement the configurable LLM initialization in `src/llm_utils.py` to support both OpenRouter and Ollama.
    *   [x] Implement the `DocumentRAGTool` in `src/tools.py`.
    *   [x] Implement wrappers for the Tavily, Arxiv, and Wikipedia tools in `src/tools.py`.
    *   [x] Implement the agent creation logic in `src/agents.py`, including the initial system prompt.
    *   [x] Integrate the agent executor into `app.py`.
    *   [x] Enable the chat input and display the agent's responses in the UI for "Chat Mode".
    *   [x] Handle chat history in the `st.session_state`.

---

### Epic 4: Analysis Mode Chains

*   **Goal:** Implement the analytical capabilities of the application.
*   **Tasks:**
    *   [x] Implement the summarization chain in `src/chains.py`.
    *   [x] Define the Pydantic models for tabular and chart data.
    *   [x] Implement the structured output chains for tables and charts using Pydantic parsers.
    *   [x] Integrate the analysis chains into `app.py`.
    *   [x] Add logic to `app.py` to call the correct chain based on the user's query in "Analysis Mode".
    *   [x] Render the results (summaries, tables, charts) in the Streamlit UI.

---

### Epic 5: Testing & Finalization

*   **Goal:** Ensure the application is stable, functional, and ready for handoff.
*   **Status:** MVP Achieved. Further refinement required.
*   **Tasks:**
    *   [x] Conduct end-to-end testing of the full user flow for both Chat and Analysis modes.
    *   [x] Refine agent prompts and chain prompts based on test results to improve accuracy and reliability.
    *   [ ] Test with different LLM providers (OpenRouter and Ollama) to ensure consistent behavior.
    *   [ ] Test edge cases (e.g., no documents uploaded, missing API keys, large files).
    *   [ ] Clean up code, add comments where necessary, and perform a final review.
    *   [x] Mark the MVP as complete.

---

## 3. MVP Backlog & Next Steps

The following items have been identified for the next phase of development to move from a functional MVP to a polished and robust application:

*   **Chat History:**
    *   Re-integrate and thoroughly debug the chat history feature.

*   **Agent & UI Feedback:**
    *   Investigate and resolve occasional UI timeout errors where the agent appears to hang.
    *   Implement a visual indicator in the UI to show the user which tool the agent is currently using (e.g., "Searching documents...", "Searching the web...").
    *   Re-implement a robust method for the agent to cite its sources (e.g., Documents, Web Search, Wikipedia) in the final answer.
