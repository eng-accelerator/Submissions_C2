# UI/UX Notes from Screen Prototypes

## Screen 1: Main Interface

*   **Title:** Agentic RAG with Tavily + GPT-4 (OpenRouter) + HuggingFace Embeddings
*   **File Upload:**
    *   Drag and drop functionality.
    *   "Browse files" button.
    *   Supports PDF files.
    *   File size limit of 200MB per file.
    *   The upload is optional.
*   **Query Input:**
    *   A text area for users to enter their queries.
    *   "Run Query" button.
*   **API Keys:**
    *   Input fields for "OpenRouter API Key" and "Tavily API Key".
    *   The keys are masked for security.
*   **Query Examples:**
    *   Provides examples of how the system chooses the best source based on the query.
        *   "Who is Einstein?" -> Wikipedia
        *   "Latest research on quantum computing" -> ArXiv
        *   "Today's weather" -> Web Search
        *   Questions about uploaded PDFs -> RAG first, then fallback
*   **Available Tools:**
    *   PDF RAG (your documents)
    *   Wikipedia (encyclopedic info)
    *   ArXiv (academic papers)
    *   Web Search (current info)
*   **Deployment:**
    *   A "Deploy" button is visible in the top right corner.

## Screen 2: Web Search Response

*   **File Upload Success:**
    *   After uploading a file (e.g., "Langchain.pdf"), a confirmation message is displayed: "1 PDF(s) uploaded and indexed for retrieval!".
    *   The uploaded file is listed with its name and size.
    *   There is an "x" button to remove the uploaded file.
*   **Query and Response:**
    *   The user has entered the query "What is langchain?".
    *   The system first searches the uploaded PDFs. A message indicates this: "No relevant information found in uploaded PDFs. Searching external sources...".
    *   The system then falls back to a web search.
    *   The response is displayed with the source clearly labeled: "Source: Web Search (Tavily)".
    *   The response itself is a text block.
*   **Source Citation:**
    *   There is a "View Sources" dropdown below the response, which is collapsed by default.

## Screen 3: ArXiv Search

*   **Query for Academic Paper:**
    *   The user has entered the query "Latest research on quantum computing".
    *   The system is searching for the information. A spinning wheel and the message "Searching external sources..." are displayed.
    *   Based on the "Query Examples" in the sidebar, the system should use ArXiv for this query.

## Screen 4: ArXiv Search Results

*   **ArXiv Search Results:**
    *   The screen displays the results for the query "Latest research on quantum computing".
    *   The results are presented as a numbered list of research papers.
    *   Each item in the list includes the title of the paper and a brief description.
*   **Source Citation:**
    *   The "View Sources" dropdown is now expanded, revealing a list of "Information Sources".
    *   The sources are direct links to ArXiv papers (e.g., `http://arxiv.org/abs/2308.10513v1`).

## Screen 5: Response from Uploaded PDF

*   **Query against Uploaded PDF:**
    *   The user has uploaded a file named "GTM Tempo.pdf".
    *   The user has entered the query "What is Tempo?".
    *   The system has found the answer within the uploaded PDF.
*   **Response from PDF:**
    *   The answer is displayed with the source clearly labeled: "Source: PDF Documents".
    *   The title of the response section is "Answer from Uploaded PDFs".
*   **Source Citation:**
    *   There is a "View Source Documents" dropdown below the response, which is collapsed by default.
