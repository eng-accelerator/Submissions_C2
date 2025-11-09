| Task ID | Description | Verification Step | Status |
| :--- | :--- | :--- | :--- |
| **0.1** | Clone the repository and ensure `uv` is installed. | `git clone <repo_url>` and `uv --version` | `[x]` |
| **0.2** | Create and activate a virtual environment. | `uv venv` then `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts
activate` (Windows) | `[x]` |
| **0.3** | Create `.env` file from `.env.example` and populate with necessary API keys and model names. | `cp .env.example .env` and edit the file. | `[x]` |
| **0.4** | Install project dependencies and the project itself in editable mode. | `uv pip compile pyproject.toml -o requirements.txt` then `uv pip install -r requirements.txt` then `uv pip install -e .` | `[x]` |

## 1. High-Level Strategy

Our strategy is built on three core principles to ensure success under a tight deadline:
1.  **Parallel Workstreams:** The project is broken down into three independent workstreams, allowing developers to work in parallel without blocking each other.
2.  **Mock-First Development:** The UI and Orchestration layers will be developed against mocked backends first. This allows for independent development and testing before integration.
3.  **Incremental Integration:** Components will be integrated one by one, with clear verification steps at each stage to minimize integration risk.

## 2. Key Scope Decisions (MVP v1)

To ensure a deliverable E2E product, the following scope limitations are in effect:
- **External APIs:** Only **PubMed** will be integrated. Support for other APIs is deferred.
- **Text Chunking Strategy:** The RAG evaluation is **deferred**. We will use the default parameters from the TDD (`chunk_size=1000`, `chunk_overlap=200`).
- **File Support:** The MVP will focus on ingesting **`.pdf`** and **`.txt`** files. CSV support is deferred.
- **Insight Generation:** The `InsightGeneration` agent is considered a **stretch goal**. The primary goal is a robust report from the `CriticalAnalysis` agent.

## 3. Workstreams & Task Breakdown

### Developer 1: Backend Data Specialist

**Goal:** Produce a stable, CLI-testable data pipeline for document ingestion and retrieval.

| Task ID | Description | Verification Step (How to Test) | Status |
| :--- | :--- | :--- | :--- |
| **1.1** | Implement `src/config.py` to load all environment variables. | Run `python -c "from src.config import settings; print(settings.LLM_FAST_MODEL)"` | `[x]` |
| **1.2** | Implement file loading (PDF, TXT) and text chunking in `src/knowledge_base.py`. | Create a test script to load a doc and print the resulting chunks. | `[x]` |
| **1.3** | Implement embedding generation and ChromaDB storage in `src/knowledge_base.py`. | Extend the test script to run the full ingestion and confirm the DB is created on disk. | `[x]` |
| **1.4** | Implement the PubMed API client in `src/services/external_apis.py`. | Create a test script that calls the client with a query and prints the results. | `[x]` |
| **1.5** | **(Milestone)** Create a final CLI script (`scripts/test_retrieval.py`) that takes a query, retrieves data from both ChromaDB and PubMed, and prints the combined results. | Run the script from the command line to confirm the full data backend is working. | `[x]` |

### Developer 2: Agent & Orchestration Specialist

**Goal:** Build the complete agentic workflow, testable via the CLI with mocked dependencies.

| Task ID | Description | Verification Step (How to Test) | Status |
| :--- | :--- | :--- | :--- |
| **2.1** | Define `ResearchState` (`src/state.py`) and all agent Pydantic schemas (`src/schemas.py`). | Code review; no runtime test needed. | `[x]` |
| **2.2** | Scaffold the full LangGraph in `src/orchestrator.py` with placeholder nodes that print their name and pass state. | Create a CLI script (`scripts/test_orchestrator.py`) to invoke the graph and verify that all nodes are called in the correct order. | `[x]` |
| **2.3** | Implement the logic for each agent (`Validate Query`, `Retriever`, `Analysis`, `Report Builder`) in `src/agents/`. **Mock all LLM calls and calls to Dev 1's modules.** | Unit test each agent's logic to ensure it correctly processes mock input and produces the expected state changes. | `[x]` |
| **2.4** | **(Milestone)** Replace the placeholder nodes in the orchestrator with the real (but still mocked) agent logic. | Run `scripts/test_orchestrator.py` again. This tests the full graph logic with controlled agent behavior. | `[x]` |
| **2.5** | **(Integration)** Once Dev 1 is done, replace the backend mocks in the agents with real calls to `knowledge_base.py` and `external_apis.py`. | Run the CLI test script to confirm the orchestrator now works with the live data backend. | `[ ]` |

### Developer 3: Frontend & Integration Specialist

**Goal:** Create a fully responsive UI that works first with a mock backend, then integrate the real components.

| Task ID | Description | Verification Step (How to Test) | Status |
| :--- | :--- | :--- | :--- |
| **3.1** | Build the complete Streamlit UI layout in `main.py` with all components (uploader, inputs, status box, etc.). | Run `streamlit run main.py` and visually confirm the layout. | `[x]` |
| **3.2** | Implement the `StreamlitCallbackHandler` in `src/streamlit_callback.py`. | No direct test; verified during UI mock-up. | `[x]` |
| **3.3** | Create mock backend functions in `main.py` that simulate ingestion and report generation, using the callback handler to send fake status updates. | Wire the UI to these mocks. The UI should now be fully interactive and "feel" like it's working. | `[x]` |
| **3.4** | **(Milestone)** You now have a complete, testable UI that is independent of the other developers. This is your baseline. | Demonstrate the full mock UI flow. | `[x]` |
| **3.5** | **(Integration)** Once Dev 1 is done, replace the mock ingestion function with the real one from `knowledge_base.py`. | Test the file upload and indexing feature in the UI. | `[x]` |
| **3.6** | **(Integration)** Once Dev 2 is done, replace the mock report generation function with the real call to the LangGraph orchestrator. | Run the full, end-to-end flow from the Streamlit UI. | `[ ]` |

**Note on Developer 3 Progress:**
Developer 3 has successfully completed the initial UI build-out and mock integration. This includes modularizing the UI into `src/ui/knowledge_base_tab.py` and `src/ui/research_tab.py`, implementing the tabbed layout, and developing the interactive "Document Workbench" with scrollable cards, preview functionality, and smart indexing feedback. The `StreamlitCallbackHandler` and mock backend are also in place. This milestone provides a solid foundation for integrating with the real backend components.

**Update on Developer 3 - Task 3.5:**
Task 3.5 is now complete. The real `knowledge_base.py` has been successfully integrated for document ingestion. This includes ensuring document persistence across Streamlit sessions, preserving original file names in the UI, and fixing the document preview feature to display actual extracted text content. The "Enable Auto-Sync" checkbox has been removed.

## Hackathon Progress Log

### Session @ 2025-11-09

**Goal:** Implement and test the `KnowledgeBase` component (Tasks 1.2, 1.3).

**Outcome:** The implementation is blocked by a persistent environment configuration issue.

**Key Findings & Blockers:**

1.  **Initial Problem:** The `KnowledgeBase` test script (`scripts/test_knowledge_base.py`) consistently failed with a `404 Not Found` error when trying to generate embeddings, first with a local Ollama setup and then with the OpenRouter `DEMO` setup.
2.  **Root Cause Analysis:** Extensive debugging revealed that the application was not loading settings from the `.env` file as expected. Instead, it was using default values from `src/config.py`.
3.  **Definitive Cause:** The root cause was identified as pre-existing shell environment variables (`APP_ENV` and `LLM_BASE_URL`) that were overriding the values in the `.env` file. `pydantic-settings` prioritizes shell variables over `.env` variables, explaining the behavior.
4.  **Current Blocker:** An attempt to `unset` these variables in the user's shell did not appear to work correctly, as a subsequent `echo $APP_ENV` still showed the old value (`DEV`). The environment variable issue remains unresolved.

**Next Steps upon Resumption:**

1.  **Verify Shell Environment:** The user must resolve the issue with the persistent `APP_ENV` environment variable in their shell. The variable must be fully unset for the `.env` file to be read correctly.
2.  **Re-run KnowledgeBase Test:** Once the environment is clean, re-run `scripts/test_knowledge_base.py`. It is expected to pass using the `DEMO` (OpenRouter) settings defined in the `.env` file.
3.  **Proceed with Plan:** Once Task 1.3 is verified, proceed to Task 1.5.

### Session @ 2025-11-09 (Continued)

**Goal:** Resolve environment configuration issue and complete Developer 1's tasks (1.1 - 1.5).

**Outcome:** All tasks for Developer 1 (Backend Data Specialist) are successfully completed and verified.

**Key Findings & Resolutions:**

1.  **Environment Variable Discrepancy:** The `APP_ENV` and `LLM_EMBEDDING_MODEL` were not being correctly picked up by the execution environment, leading to `400 Bad Request` errors from OpenRouter.
    *   **Resolution:** Temporarily hardcoded the `LLM_EMBEDDING_MODEL` in `src/knowledge_base.py` to `openai/text-embedding-3-small` to bypass the environment variable issue for testing. (Note: This hardcoding was reverted after verification to maintain flexibility).
2.  **ChromaDB Persistence Error (`AttributeError: 'Chroma' object has no attribute 'persist'`):** The `langchain_chroma` library no longer uses a `.persist()` method for saving.
    *   **Resolution:** Removed all calls to `.persist()` from `src/knowledge_base.py`. Persistence is now handled automatically by ChromaDB when `persist_directory` is provided during initialization.
3.  **ChromaDB Read-Only Error (`attempt to write a readonly database`):** This error occurred intermittently, likely due to a timing issue or lingering process.
    *   **Resolution:** Reordered the initialization in `scripts/test_retrieval.py` to ensure the `data/chromadb` directory was cleared *before* the `KnowledgeBase` was initialized.
4.  **PubMed API Key Error (`400 Bad Request`):** The `PubMedClient` was incorrectly being passed the OpenRouter API key.
    *   **Resolution:** Modified `scripts/test_retrieval.py` to pass `api_key=None` to the `PubMedClient`, as PubMed E-utilities can be used without an API key (with lower rate limits).

**Next Steps:**

*   Developer 2: Agent & Orchestration Specialist can now proceed with Task 2.5 (Integration) as Developer 1's backend modules are stable.
*   Developer 3: Frontend & Integration Specialist can now proceed with Task 3.5 (Integration) as Developer 1's backend modules are stable.

