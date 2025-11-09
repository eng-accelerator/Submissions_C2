# MVP Architecture: Agentic RAG AI Application

**To:** Development Team  
**From:** Solution Architect  
**Date:** November 6, 2025  
**Subject:** MVP Technical Architecture and Design

---

## 1. Introduction

This document outlines the technical architecture for the Minimum Viable Product (MVP) of the Agentic RAG AI Application. The design is derived directly from the approved `product-requirements.md` and is intended to provide a clear blueprint for implementation.

The primary goal of this architecture is to enable rapid development of the core features while establishing a foundation that can be evolved in the future.

## 2. Configuration

The application will be configured via environment variables to allow for flexibility during development and deployment.

*   `LLM_PROVIDER`: Determines the LLM provider. Set to `openrouter` (default) or `ollama`.
*   `LLM_MODEL_NAME`: The specific model to use (e.g., `openai/gpt-4o` for OpenRouter, `gpt-oss:20b` for Ollama).
*   `OLLAMA_BASE_URL`: The base URL for the Ollama server, required if `LLM_PROVIDER=ollama` (e.g., `http://localhost:11434`). Note: The Langchain `ChatOllama` integration uses a different API; we will use Ollama's OpenAI-compatible endpoint for consistency, which is typically at the `/v1` path.
*   The user will still provide their `OPENROUTER_API_KEY` and `TAVILY_API_KEY` through the UI, which will be held in the session state.

## 3. High-Level Architecture

The MVP will be a self-contained application running on a single server process, orchestrated by Streamlit. All user-specific data (API keys, documents, chat history) will be managed within the user's session state and will not be persisted.

### Text-Based Diagram

```
+--------------------------------------------------------------------------------------------+
|                                      Streamlit Server                                      |
|                                                                                            |
| +----------------------+             +---------------------------------------------------+ |
| |                      |             |                                                   | |
| |    Frontend UI       | <-----------> |           Backend Logic (Python)                  | |
| | (Streamlit Widgets)  |             |                                                   | |
| |                      |             | +-----------------------------------------------+ | |
| +----------------------+             | |         st.session_state (Per User)             | | |
|                                      | | - API Keys (OpenRouter, Tavily)               | | |
|                                      | | - Chat History                                | | |
|                                      | | - FAISS Vector Index (in-memory)              | | |
|                                      | +-----------------------------------------------+ | |
|                                      |                                                   | |
|                                      | +-----------------------------------------------+ | |
|                                      | |      Langchain Agent & Chains                 | | |
|                                      | +------------------+----------------------------+ | |
|                                      |                    |                            | | |
| +------------------------------------+--------------------+----------------------------+ | |
| |                                    |                    |                            | | |
| | [Tool: Document RAG]---------------+                    |                            | | |
| |                                                         |                            | | |
| | [Tool: Web Search (Tavily)]-----------------------------+                            | | |
| |                                                                                      | | |
| | [Tool: Academic Search (Arxiv)]------------------------------------------------------+ | |
| |                                                                                        | |
| +----------------------------------------------------------------------------------------+ |
+--------------------------------------------------------------------------------------------+
       |                            |                           |                      |
       |                            |                           |                      |
       v                            v                           v                      v
[FAISS Index]  [LLM Provider (Configurable: OpenRouter/Ollama)]   [Tavily API]           [Arxiv API]
(in-memory)
```

## 4. Component Breakdown

### 4.1. Frontend (Streamlit)

*   **Responsibilities:**
    *   Render all UI components as specified in the PRD (sidebar, file uploader, chat interface, mode selector).
    *   Capture user inputs (queries, API keys, uploaded files).
    *   Manage application state via `st.session_state`.
    *   Display outputs from the backend, including chat responses, sources, and analysis (tables/charts).

### 4.2. Backend Logic (Python/Langchain)

This logic will be implemented directly within the Streamlit application script.

*   **File Processing Workflow:**
    1.  **On File Upload:** When a user uploads files, they will be processed immediately.
    2.  **Content Extraction:** Use libraries like `PyPDF2` or `pdfplumber` for PDFs and standard file handling for TXT/CSV.
    3.  **Text Chunking:** Use Langchain's `RecursiveCharacterTextSplitter` to break documents into smaller, semantically meaningful chunks.
    4.  **Embedding Generation:** Use a sentence-transformer model from HuggingFace (e.g., `all-MiniLM-L6-v2`) via Langchain's `HuggingFaceEmbeddings` class to create vector embeddings for each chunk.
    5.  **In-Memory Indexing:** Create a FAISS vector index from the embeddings and chunks. The FAISS index object will be stored directly in `st.session_state` to make it available for the rest of the session.

*   **Core Logic Workflow:**
    1.  **Initialization:** At the start of a user query, initialize all necessary components (LLM, tools) using the API keys stored in `st.session_state`.
    2.  **Mode Selection:** The application logic will branch based on the mode selected in the UI dropdown.

### 4.3. Agent & Chains

*   **Chat Mode (Agentic Workflow):**
    *   **LLM Initialization (Configurable):** The `ChatOpenAI` object will be initialized based on the `LLM_PROVIDER` environment variable.
        *   If `LLM_PROVIDER` is `ollama`, initialize `ChatOpenAI` with `base_url` set to the `OLLAMA_BASE_URL` and `api_key` set to a non-empty string (e.g., "ollama").
        *   If `LLM_PROVIDER` is `openrouter`, initialize `ChatOpenAI` with the default OpenRouter base URL and the `api_key` from the user's session state.
        *   The `model_name` will be set from the `LLM_MODEL_NAME` environment variable in both cases.
    *   **Tools Definition:**
        *   `document_rag_tool`: A custom tool that queries the FAISS index stored in `st.session_state`.
        *   `tavily_search_tool`: A pre-built Langchain tool (`TavilySearchResults`) initialized with the user's Tavily API key.
        *   `arxiv_tool`: The pre-built Langchain `ArxivQueryRun` tool.
        *   `wikipedia_tool`: The pre-built Langchain `WikipediaQueryRun` tool for factual lookups.
    *   **Agent Executor:** Use a modern Langchain agent constructor (e.g., `create_react_agent` with `AgentExecutor`) to combine the LLM and the tools. The agent's system prompt is critical and must be engineered to effectively route between the document tool for personal data questions and the other tools for external knowledge.

*   **Analysis Mode (Chain-based Workflow):**
    *   When this mode is selected, the user's query will be passed to a dedicated Langchain chain, not the agent.
    *   **Implementation:** Use a `load_summarize_chain` or a similar chain that can process the full content of the uploaded documents.
    *   **For Structured Output (Tables/Charts):** The chain's prompt must explicitly instruct the LLM to return a JSON object. Use a `PydanticOutputParser` to ensure the LLM output is valid and can be safely passed to a rendering function (e.g., `st.table` or `st.altair_chart`).

## 5. MVP Limitations

This architecture is designed for the MVP and has the following known limitations:

*   **No Persistence:** All data (chat history, uploaded documents) is lost on session termination or page refresh.
*   **Scalability:** The application is limited to a single server process. Concurrency is limited by the server's memory, especially due to the in-memory FAISS index.
*   **Re-computation:** Documents are re-processed and re-indexed in every new session.

These trade-offs are acceptable for the MVP but should be addressed in future production-grade versions with a more robust architecture (e.g., persistent vector DB, separate backend service, user authentication).