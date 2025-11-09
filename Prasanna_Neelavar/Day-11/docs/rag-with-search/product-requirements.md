# Product Requirements: Agentic RAG AI Application

## 1. Introduction

This document outlines the product requirements for a Langchain-based Retrieval-Augmented Generation (RAG) AI application with a Streamlit front end. The application will provide a chat interface for users to interact with their documents and perform analysis.

## 2. Functional Requirements

### 2.1. File Upload

*   The application shall allow users to upload documents of the following types: PDF, CSV, and TXT.
*   The user shall be able to upload one or more files.
*   The application shall support drag-and-drop functionality for file uploads.
*   The application shall provide a "Browse files" button for file selection.
*   The maximum file size for each uploaded file shall be 200MB.
*   The file upload is optional for the user to start a query.

### 2.2. Chat Mode

*   When in "Chat Mode," the application shall provide a standard chat interface for users to enter their queries.
*   The system shall employ an agentic workflow to intelligently determine the best tool for a given query.
*   Based on the query's intent, the agent will automatically route the request to the most appropriate tool:
    *   **Document RAG:** For questions that can be answered from the content of the uploaded documents.
    *   **Web Search (Tavily):** For general knowledge questions or when the answer is not in the documents.
    *   **Academic Search (Arxiv):** For queries related to academic papers, research, or scientific topics.
*   The system shall be able to handle queries even if no documents are uploaded by relying on web and academic search tools.
*   If multiple documents are uploaded, the Document RAG tool shall search across all of them.

### 2.3. Analysis Mode

*   The user shall be able to select "Analysis Mode" from a dropdown in the main interface.
*   When in this mode, user queries will be interpreted as instructions to perform analysis on the content of the uploaded document(s).
*   The analysis capabilities shall include:
    *   **Summarization:** The user can ask for a summary of the document(s).
    *   **Tabular Analysis:** The user can ask for specific data to be extracted and presented in a table.
    *   **Chart Generation:** The user can ask for data to be visualized in a chart.

### 2.4. Source Citation

*   The application shall display the source of the information provided in the answer.
*   For answers from uploaded documents, the source shall be labeled as "PDF Documents" or similar.
*   For answers from web searches, the source shall be labeled as "Web Search (Tavily)".
*   For answers from Arxiv, the source shall be a direct link to the Arxiv paper.
*   The application shall provide a "View Sources" or "View Source Documents" dropdown to show the source links.

## 3. Non-Functional Requirements

### 3.1. Technology Stack

*   **Front-end:** Streamlit
*   **Back-end:** Langchain, Python
*   **Vector Store:** FAISS
*   **LLM:** Any LLM accessible via OpenRouter and the OpenAI Langchain SDK.

### 3.2. API Keys

*   The application shall require users to enter their API keys for OpenRouter and Tavily in the sidebar.
*   The entered keys shall be managed as session-level environment variables and will only persist for the current session.
*   The application shall not store user-provided API keys permanently.
*   The API key input fields shall mask the entered keys for security.

### 3.3. Chat History

*   The chat history shall be maintained only for the current session.
*   If the user refreshes the page, the chat history will be cleared.

## 4. Front-End Requirements

### 4.1. Main Interface

*   The main interface shall have a title: "Agentic RAG with Tavily + GPT-4 (OpenRouter) + HuggingFace Embeddings".
*   A file upload section with drag-and-drop functionality and a "Browse files" button.
*   A mode selection dropdown allowing the user to switch between **Chat Mode** and **Analysis Mode**.
*   A text area for users to enter their queries with a "Run Query" button.
*   If the user attempts to run a query without providing API keys, the application shall display a clear and helpful message prompting the user to enter them.
*   A sidebar with the following sections:
    *   **API Keys:** Input fields for "OpenRouter API Key" and "Tavily API Key".
    *   **Query Examples:** A section with example queries and their expected sources.
    *   **Available Tools (Informational):** An informational list of the agent's capabilities, such as "PDF RAG", "Wikipedia", "ArXiv", and "Web Search". This is not a selection menu.

### 4.2. File Upload and Query Response

*   After a file is uploaded, a confirmation message shall be displayed (e.g., "1 PDF(s) uploaded and indexed for retrieval!").
*   The uploaded file shall be listed with its name and size, and an option to remove it.
*   When a query is being processed, a loading indicator shall be displayed (e.g., "Searching external sources...").
*   The response shall be displayed in a text block with the source clearly labeled.

### 4.3. ArXiv Search

*   When a query for an academic paper is made, the system shall display a loading indicator.
*   The results shall be presented as a numbered list of research papers with their titles and descriptions.
*   The "View Sources" dropdown shall be expanded to show the direct links to the ArXiv papers.
