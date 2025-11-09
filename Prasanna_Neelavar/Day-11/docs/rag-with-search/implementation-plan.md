# Implementation Plan: Agentic RAG AI Application MVP

**To:** Python Developer  
**From:** Solution Architect  
**Date:** November 6, 2025  
**Subject:** Detailed Implementation Guide for MVP

---

## 1. Introduction

This document provides a detailed technical implementation plan for the Agentic RAG AI Application MVP. It is designed to be consumed by a Python developer and should be read in conjunction with the `product-requirements.md` and `architecture-mvp.md` documents. The goal is to provide a clear, step-by-step approach to building the application.

## 2. Recommended Project Structure

Start with the following modular project structure:

```
agentic-rag-app/
├── app.py                      # Main Streamlit application entry point
├── src/
│   ├── config.py               # Environment variable loading, constants
│   ├── llm_utils.py            # LLM initialization logic
│   ├── document_processor.py   # File reading, chunking, embedding, FAISS index creation
│   ├── tools.py                # Definition of agent tools (Document RAG, Tavily, Arxiv, Wikipedia)
│   ├── agents.py               # Agent creation and core agentic logic
│   └── chains.py               # Analysis Mode chains (summarization, structured output)
├── .env.example                # Template for environment variables
└── pyproject.toml              # Project metadata and dependencies (using uv)
```

## 3. Configuration Details (`src/config.py`)

This module will handle loading environment variables at application startup. Ensure you have a `.env` file (or set these directly in your execution environment) for development to test different configurations.

```python
import os

def load_env_vars():
    # Example of loading, use more robust methods for production if needed
    # For this MVP, direct os.getenv calls are acceptable
    pass

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter") # 'openrouter' or 'ollama'
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "openai/gpt-4o") # e.g., "llama3" for Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# TAVILY_API_KEY will be provided by user in UI, but could have a default here for dev
# OPENROUTER_API_KEY will be provided by user in UI

# Other constants like chunk_size, chunk_overlap can also go here.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
```

Provide a `.env.example` file:

```
# LLM Configuration (choose one)
LLM_PROVIDER=openrouter
# LLM_PROVIDER=ollama

# If OpenRouter
LLM_MODEL_NAME=openai/gpt-4o

# If Ollama
# LLM_MODEL_NAME=llama3
# OLLAMA_BASE_URL=http://localhost:11434
```

## 4. Core Function & Class Signatures

### 4.1. LLM Initialization (`src/llm_utils.py`)

```python
import os
from langchain_openai import ChatOpenAI
from src.config import LLM_PROVIDER, LLM_MODEL_NAME, OLLAMA_BASE_URL

def initialize_llm(user_openrouter_api_key: str = None) -> ChatOpenAI:
    """Initializes and returns the ChatOpenAI instance based on configuration.
    User's OpenRouter API key takes precedence if LLM_PROVIDER is openrouter.
    """
    if LLM_PROVIDER == "ollama":
        return ChatOpenAI(
            base_url=f"{OLLAMA_BASE_URL}/v1", # Ollama's OpenAI-compatible endpoint
            api_key="ollama", # Dummy API key for Ollama's OpenAI-compatible endpoint
            model_name=LLM_MODEL_NAME,
            temperature=0.7 # Example temperature
        )
    elif LLM_PROVIDER == "openrouter":
        if not user_openrouter_api_key:
            raise ValueError("OpenRouter API key is required and not provided.")
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=user_openrouter_api_key,
            model_name=LLM_MODEL_NAME,
            temperature=0.7
        )
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")

```

### 4.2. Document Processing (`src/document_processor.py`)

```python
import os
from typing import List
import streamlit as st
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from pypdf import PdfReader # Example for PDF processing
from io import BytesIO

@st.cache_resource
def get_embedding_model():
    """Loads the HuggingFace embedding model (cached)."""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_text_chunks(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_text(text)

def get_documents_from_pdf(pdf_docs: List[BytesIO]) -> List[Document]:
    # Implement logic to read PDF files and extract text
    # For MVP, focus on PDF, TXT. Extend for CSV later.
    pass

def create_vector_store(text_chunks: List[str], embeddings_model: HuggingFaceEmbeddings) -> FAISS:
    """Creates and returns a FAISS index from text chunks and an embedding model.
    This should be cached in st.session_state.
    """
    # Example: return FAISS.from_texts(texts=text_chunks, embedding=embeddings_model)
    pass
```

### 4.3. Agent Tools (`src/tools.py`)

```python
from typing import Any, Dict, List, Optional
from langchain.tools import BaseTool
from langchain_community.vectorstores import FAISS
from langchain_community.tools.tavily_research import TavilySearchResults
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_core.callbacks import CallbackManagerForToolRun

class DocumentRAGTool(BaseTool):
    name: str = "document_rag_tool"
    description: str = "Useful for answering questions directly from the uploaded documents. Prioritize this tool for specific document-related queries."
    vectorstore: FAISS

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool synchronously."""
        docs = self.vectorstore.similarity_search(query)
        # For MVP, return concatenated content. Refine with LLM-based summarization of docs later.
        return "\n\n".join([doc.page_content for doc in docs]) if docs else "No relevant documents found."

def get_all_tools(faiss_index: FAISS, tavily_api_key: str) -> List[BaseTool]:
    """Initializes and returns all tools for the agent."""
    tavily_tool = TavilySearchResults(api_key=tavily_api_key, max_results=5)
    arxiv_tool = ArxivQueryRun(api_wrapper=ArxivAPIWrapper(top_k_results=3, doc_content_chars_max=4000))
    wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=4000))
    doc_rag_tool = DocumentRAGTool(vectorstore=faiss_index)

    # Ensure tools are returned in a format compatible with Langchain agents
    return [doc_rag_tool, tavily_tool, arxiv_tool, wikipedia_tool]
```

### 4.4. Agent (`src/agents.py`)

```python
from typing import List
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent, Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable # For generic agent type

# Example agent system prompt. This will require iteration and prompt engineering.
DEFAULT_AGENT_SYSTEM_PROMPT = """
    You are an advanced AI assistant. Your role is to answer user questions accurately and comprehensively. You have access to specialized tools to help you.

    **Instructions:**
    1.  **Understand the User's Intent:** Carefully read the user's query and determine what information they are seeking.
    2.  **Select the Best Tool(s):** Choose the tool(s) that are most likely to provide the necessary information.
        *   Use `document_rag_tool` for questions that are highly likely to be answerable from the *uploaded user documents*.
        *   Use `web_search_tool` (Tavily) for general knowledge, current events, or when `document_rag_tool` is unlikely to have the answer.
        *   Use `wikipedia_tool` for specific factual inquiries about entities, places, or well-established topics.
        *   Use `arxiv_tool` for questions related to scientific papers, research, or complex academic concepts.
    3.  **Execute Tool(s):** Call the selected tool(s) with appropriate input parameters derived from the user's query.
    4.  **Synthesize and Respond:** Once you have the information from the tools, synthesize it into a clear, concise, and accurate answer for the user.
    5.  **Cite Sources:** Always indicate which tool(s) were used to generate the answer (e.g., "(Source: Documents)", "(Source: Web Search)", "(Source: Arxiv)", "(Source: Wikipedia)").

    You have access to the following tools:
    {tools}

    Begin! Remember to speak in a polite and helpful tone.
    """

def create_rag_agent(llm: ChatOpenAI, tools: List[Tool]) -> Runnable:
    """Creates and returns the Langchain agent for Chat Mode."""
    # Agent requires a prompt and tools
    prompt = ChatPromptTemplate.from_messages([
        ("system", DEFAULT_AGENT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Use create_react_agent (or similar) to construct the agent
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True, # Set to False in production
        handle_parsing_errors=True # Good for MVP
    )
    return agent_executor

```

### 4.5. Analysis Chains (`src/chains.py`)

```python
from typing import List, Any, Literal
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from langchain_core.documents import Document

# Data models for structured output in Analysis Mode
class TabularData(BaseModel):
    columns: List[str] = Field(description="List of column headers.")
    data: List[List[Any]] = Field(description="Rows of data, each an array matching column order.")

class ChartData(BaseModel):
    chart_type: Literal["bar", "line", "pie"] = Field(description="Type of chart to generate.")
    title: str = Field(description="Title of the chart, summarizing the data.")
    x_axis_label: str = Field(description="Label for the X-axis (e.g., 'Category', 'Date').")
    y_axis_label: str = Field(description="Label for the Y-axis (e.g., 'Value', 'Count').")
    data: List[dict] = Field(description="Data points for the chart. Each dictionary represents a single point with keys matching axis labels, e.g., [{'Category': 'A', 'Value': 10}, ...].")

def create_summarization_chain(llm: ChatOpenAI) -> LLMChain:
    """Creates a chain for summarizing documents."""
    # For MVP, a simple StuffDocumentsChain is sufficient
    prompt_template = """Write a concise summary of the following:
    {text}
    CONCISE SUMMARY:"""
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
    return load_summarize_chain(llm, chain_type="stuff", prompt=prompt)

def create_tabular_chain(llm: ChatOpenAI) -> LLMChain:
    """Creates a chain for extracting tabular data from documents."""
    parser = PydanticOutputParser(pydantic_object=TabularData)
    prompt = PromptTemplate(
        template="""Extract structured tabular data based on the following documents and query.\n{format_instructions}\nDocuments: {documents}\nQuery: {query}""",
        input_variables=["documents", "query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    return LLMChain(llm=llm, prompt=prompt, output_parser=parser)

def create_chart_chain(llm: ChatOpenAI) -> LLMChain:
    """Creates a chain for generating chart data from documents."""
    parser = PydanticOutputParser(pydantic_object=ChartData)
    prompt = PromptTemplate(
        template="""Generate data for a chart based on the following documents and query.\nSpecify chart type, title, axis labels, and data points.\n{format_instructions}\nDocuments: {documents}\nQuery: {query}""",
        input_variables=["documents", "query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    return LLMChain(llm=llm, prompt=prompt, output_parser=parser)

```

## 5. Main Application Flow (`app.py`)

```python
import streamlit as st
from io import BytesIO
from typing import List

from src.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.llm_utils import initialize_llm
from src.document_processor import get_embedding_model, get_text_chunks, get_documents_from_pdf, create_vector_store
from src.tools import get_all_tools
from src.agents import create_rag_agent
from src.chains import create_summarization_chain, create_tabular_chain, create_chart_chain, TabularData, ChartData

# --- Streamlit Session State Initialization ---
if "chat_history" not in st.session_state: st.session_state["chat_history"] = [] # Chat Mode
if "conversation_mode" not in st.session_state: st.session_state["conversation_mode"] = "Chat Mode" # "Chat Mode" or "Analysis Mode"
if "faiss_index" not in st.session_state: st.session_state["faiss_index"] = None
if "openrouter_api_key" not in st.session_state: st.session_state["openrouter_api_key"] = ""
if "tavily_api_key" not in st.session_state: st.session_state["tavily_api_key"] = ""

# --- UI Layout ---
st.set_page_config(page_title="Agentic RAG with Tavily + GPT-4 (OpenRouter) + HuggingFace Embeddings", layout="wide")
st.title("Agentic RAG with Tavily + GPT-4 (OpenRouter) + HuggingFace Embeddings")

# Sidebar
with st.sidebar:
    st.subheader("API Keys")
    st.session_state["openrouter_api_key"] = st.text_input("OpenRouter API Key", type="password", value=st.session_state["openrouter_api_key"])
    st.session_state["tavily_api_key"] = st.text_input("Tavily API Key", type="password", value=st.session_state["tavily_api_key"])

    st.subheader("Document Upload")
    uploaded_files: List[BytesIO] = st.file_uploader("Upload PDFs, TXT, CSV", type=["pdf", "txt", "csv"], accept_multiple_files=True)
    
    if uploaded_files and st.button("Process Documents"): # Add a button to explicitly process
        with st.spinner("Processing documents..."):
            raw_documents = get_documents_from_pdf(uploaded_files) # Need to handle multiple types
            text_chunks = get_text_chunks([doc.page_content for doc in raw_documents], CHUNK_SIZE, CHUNK_OVERLAP)
            embeddings_model = get_embedding_model()
            st.session_state["faiss_index"] = create_vector_store(text_chunks, embeddings_model)
            st.success(f"{len(uploaded_files)}"document(s) uploaded and indexed!")

    st.subheader("Available Tools (Informational)")
    st.write("- PDF RAG (for uploaded documents)")
    st.write("- Web Search (Tavily)")
    st.write("- Academic Search (Arxiv)")
    st.write("- Wikipedia Search")

# Conversation Mode Selector (Main Area)
st.session_state["conversation_mode"] = st.radio(
    "Select Mode:",
    ("Chat Mode", "Analysis Mode"),
    horizontal=True
)

# Display chat history or analysis results
placeholder = st.empty()
with placeholder.container():
    if st.session_state["conversation_mode"] == "Chat Mode":
        for i, message in enumerate(st.session_state["chat_history"]):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    else: # Analysis Mode display
        st.info("Analysis results will appear here. Enter your query below.")

# User Input and Query Processing
user_query = st.chat_input("Ask a question or request analysis...")

if user_query:
    # Add user query to chat history for Chat Mode
    if st.session_state["conversation_mode"] == "Chat Mode":
        st.session_state["chat_history"].append({"role": "user", "content": user_query})
        with st.chat_message("user"): st.markdown(user_query)

    api_key_status = True
    if not st.session_state["openrouter_api_key"]:
        st.error("OpenRouter API Key is required. Please enter it in the sidebar.")
        api_key_status = False
    if not st.session_state["tavily_api_key"]:
        st.warning("Tavily API Key is missing. Web search may not function.")

    if api_key_status:
        with st.spinner("Processing request..."):
            try:
                llm = initialize_llm(st.session_state["openrouter_api_key"])

                if st.session_state["conversation_mode"] == "Chat Mode":
                    tools = get_all_tools(st.session_state["faiss_index"], st.session_state["tavily_api_key"])
                    agent_executor = create_rag_agent(llm, tools)
                    response = agent_executor.invoke({
                        "input": user_query,
                        "chat_history": [msg for msg_obj in st.session_state["chat_history"] for msg in msg_obj.values()]
                    })
                    agent_response_content = response["output"]
                    st.session_state["chat_history"].append({"role": "assistant", "content": agent_response_content})
                    with st.chat_message("assistant"): st.markdown(agent_response_content)

                elif st.session_state["conversation_mode"] == "Analysis Mode":
                    if st.session_state["faiss_index"] is None:
                        st.warning("Please upload and process documents before using Analysis Mode.")
                    else:
                        # Documents for analysis chains (assume we can retrieve all content from FAISS for simple docs)
                        # In a real app, you'd feed the original document content.
                        # For MVP, extract content from FAISS for 'stuff' chain.
                        all_docs_content = " ".join([doc.page_content for doc in st.session_state["faiss_index"].docstore._dict.values()])
                        analysis_docs = [Document(page_content=all_docs_content, metadata={"source": "Uploaded Documents"})]

                        if "summarize" in user_query.lower():
                            summary_chain = create_summarization_chain(llm)
                            analysis_result = summary_chain.invoke({"input_documents": analysis_docs})
                            st.subheader("Document Summary:")
                            st.write(analysis_result["output_text"])
                        elif "table" in user_query.lower() or "tabular" in user_query.lower():
                            tabular_chain = create_tabular_chain(llm)
                            try:
                                tabular_data: TabularData = tabular_chain.invoke({"documents": analysis_docs, "query": user_query})
                                st.subheader("Tabular Analysis:")
                                if tabular_data.columns and tabular_data.data:
                                    import pandas as pd
                                    df = pd.DataFrame(tabular_data.data, columns=tabular_data.columns)
                                    st.dataframe(df)
                                else:
                                    st.write("No tabular data could be extracted.")
                            except Exception as e:
                                st.error(f"Failed to extract tabular data: {e}")
                        elif "chart" in user_query.lower() or "graph" in user_query.lower():
                            chart_chain = create_chart_chain(llm)
                            try:
                                chart_data: ChartData = chart_chain.invoke({"documents": analysis_docs, "query": user_query})
                                st.subheader("Chart Analysis:")
                                if chart_data.data:
                                    import pandas as pd
                                    import altair as alt # Assuming Altair for charting

                                    df = pd.DataFrame(chart_data.data)
                                    
                                    # Basic Altair Charting (needs refinement)
                                    if chart_data.chart_type == "bar":
                                        chart = alt.Chart(df).mark_bar().encode(x=chart_data.x_axis_label, y=chart_data.y_axis_label, tooltip=[chart_data.x_axis_label, chart_data.y_axis_label]).properties(title=chart_data.title)
                                    elif chart_data.chart_type == "line":
                                        chart = alt.Chart(df).mark_line().encode(x=chart_data.x_axis_label, y=chart_data.y_axis_label, tooltip=[chart_data.x_axis_label, chart_data.y_axis_label]).properties(title=chart_data.title)
                                    elif chart_data.chart_type == "pie": # Pie charts are tricky with Altair from generic data
                                        st.warning("Pie chart rendering is not fully implemented for generic data. Displaying table instead.")
                                        st.dataframe(df)
                                        chart = None # Avoid error
                                    
                                    if chart:
                                        st.altair_chart(chart, use_container_width=True)
                                else:
                                    st.write("No chart data could be generated.")
                            except Exception as e:
                                st.error(f"Failed to generate chart data: {e}")
                        else:
                            st.info("Please specify 'summarize', 'table', or 'chart' in your analysis query.")

            except Exception as e:
                st.error(f"An error occurred: {e}")

```

## 6. Python Dependencies (`pyproject.toml`)

```
streamlit
langchain
langchain-community
langchain-openai
faiss-cpu
pypdf
tavily-python
arxiv
sentence-transformers # For HuggingFaceEmbeddings
python-dotenv # For loading .env files
pandas # For tabular data display
altair # For charting
```

## 7. Known Limitations (MVP Focus)

Reiterating from the architecture document, this MVP design assumes:

*   **No Persistence:** All data (chat history, uploaded documents, API keys) is lost on session termination, browser refresh, or application restart.
*   **Scalability:** The application is designed for single-user, single-session desktop use initially. Concurrency is limited by the server's memory, especially due to the in-memory FAISS index.
*   **Re-computation:** Documents are re-processed and re-indexed whenever new files are uploaded or a session is reset. This will incur latency.

These limitations are acceptable for the MVP but will require substantial architectural changes for production deployment, including persistent storage, a dedicated backend service, and potentially a distributed vector store.
