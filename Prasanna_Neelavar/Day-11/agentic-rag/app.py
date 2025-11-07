import streamlit as st
import os
import pandas as pd
from io import BytesIO
from typing import List
from langchain_core.documents import Document

# Import configuration and utility functions
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, LLM_PROVIDER, LLM_MODEL_NAME, OLLAMA_BASE_URL
from src.llm_utils import initialize_llm
from src.document_processor import get_embedding_model, get_text_chunks, get_text_from_uploaded_files, create_vector_store
from src.tools import get_all_tools
from src.agents import create_rag_agent
from src.chains import create_summarization_chain, create_tabular_chain, create_chart_chain, TabularData, ChartData

def format_chat_history(chat_history: List[dict]) -> str:
    """Formats the chat history into a string."""
    buffer = ""
    for message in chat_history:
        if message["role"] == "user":
            buffer += "Human: " + message["content"] + "\n"
        elif message["role"] == "assistant":
            buffer += "AI: " + message["content"] + "\n"
    return buffer


# --- Streamlit Session State Initialization ---
if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "conversation_mode" not in st.session_state: st.session_state["conversation_mode"] = "Chat Mode"
if "faiss_index" not in st.session_state: st.session_state["faiss_index"] = None
if "openrouter_api_key" not in st.session_state: st.session_state["openrouter_api_key"] = ""
if "tavily_api_key" not in st.session_state: st.session_state["tavily_api_key"] = ""

# --- UI Layout ---
st.set_page_config(page_title="Agentic RAG with Tavily + GPT-4 (OpenRouter) + HuggingFace Embeddings", layout="wide")
st.title("Agentic RAG with Tavily + GPT-4 (OpenRouter) + HuggingFace Embeddings")

# Sidebar
with st.sidebar:
    # API Keys input section (Sidebar)
    st.subheader("⚙️ Configuration:")
    with st.expander("🔑 API Keys"):
        st.session_state["openrouter_api_key"] = st.text_input("OpenRouter API Key", type="password", value=st.session_state["openrouter_api_key"])
        st.session_state["tavily_api_key"] = st.text_input("Tavily API Key", type="password", value=st.session_state["tavily_api_key"])

    mode_label = f"{'💬' if st.session_state['conversation_mode'] == 'Chat Mode' else '📈'} Mode:"
    with st.expander(mode_label):
        # Conversation Mode Selector (Sidebar)
        st.session_state["conversation_mode"] = st.radio(
            "Select Mode:",
            ("Chat Mode", "Analysis Mode"),
            horizontal=True
        )

    # Documents Upload & Process section (Sidebar)
    st.subheader("🗒️ Document Upload:")
    uploaded_files: List[BytesIO] = st.file_uploader("Upload PDFs, TXT, CSV", type=["pdf", "txt", "csv"], accept_multiple_files=True)
    
    if uploaded_files and st.button("Process Documents"): # Add a button to explicitly process
        with st.spinner("Processing documents..."):
            raw_documents = get_text_from_uploaded_files(uploaded_files)
            if raw_documents:
                text_chunks = get_text_chunks(raw_documents, CHUNK_SIZE, CHUNK_OVERLAP)
                embeddings_model = get_embedding_model()
                st.session_state["faiss_index"] = create_vector_store(text_chunks, embeddings_model)
                st.success(f"{len(uploaded_files)} document(s) uploaded and indexed!")
            else:
                st.warning("Could not extract text from the uploaded files.")

    # Available Tools info section (Sidebar)
    st.subheader("ℹ️ Available Tools:")
    st.write("- PDF RAG (for uploaded documents)")
    st.write("- Web Search (Tavily)")
    st.write("- Academic Search (Arxiv)")
    st.write("- Wikipedia Search")

# User Input and Query Processing
user_query = st.chat_input("Ask a question or request analysis...")

if user_query:
    # Add user query to chat history for Chat Mode
    if st.session_state["conversation_mode"] == "Chat Mode":
        st.session_state["chat_history"].append({"role": "user", "content": user_query})

    if st.session_state["tavily_api_key"]:
        os.environ["TAVILY_API_KEY"] = st.session_state["tavily_api_key"]

    api_key_status = True
    if not st.session_state["openrouter_api_key"]:
        st.error("OpenRouter API Key is required. Please enter it in the sidebar.")
        api_key_status = False
    # Tavily API key is optional for web search, but warn if missing
    if not st.session_state["tavily_api_key"]:
        st.warning("Tavily API Key is missing. Web search may not function.")

    if api_key_status:
        with st.spinner("Processing request..."):
            try:
                llm = initialize_llm(st.session_state["openrouter_api_key"])

                if st.session_state["conversation_mode"] == "Chat Mode":
                    tools = get_all_tools(st.session_state["faiss_index"])
                    agent_executor = create_rag_agent(llm, tools)
                    response = agent_executor.invoke({"input": user_query})
                    agent_response_content = response["output"]
                    st.session_state["chat_history"].append({"role": "assistant", "content": agent_response_content})

                elif st.session_state["conversation_mode"] == "Analysis Mode":
                    if st.session_state["faiss_index"] is None:
                        st.warning("Please upload and process documents before using Analysis Mode.")
                    else:
                        # Combine all document text for context
                        all_docs_content = " ".join([doc.page_content for doc in st.session_state["faiss_index"].docstore._dict.values()])
                        context_docs = [Document(page_content=all_docs_content)]

                        # Basic routing based on keywords in the query
                        if "summarize" in user_query.lower():
                            summary_chain = create_summarization_chain(llm)
                            analysis_result = summary_chain.invoke({"input_documents": context_docs})
                            st.subheader("Document Summary:")
                            st.write(analysis_result["output_text"])

                        elif "table" in user_query.lower() or "tabular" in user_query.lower():
                            tabular_chain = create_tabular_chain(llm)
                            analysis_result = tabular_chain.invoke({"query": user_query, "context": all_docs_content})
                            st.subheader("Tabular Data:")
                            df = pd.DataFrame(analysis_result["data"], columns=analysis_result["columns"])
                            st.table(df)

                        elif "chart" in user_query.lower() or "plot" in user_query.lower():
                            chart_chain = create_chart_chain(llm)
                            analysis_result = chart_chain.invoke({"query": user_query, "context": all_docs_content})
                            st.subheader("Chart Data:")
                            # Simple bar chart rendering; more complex logic could be added for other chart types
                            if analysis_result["chart_type"] in ["bar", "line"] and 'labels' in analysis_result["data"] and 'values' in analysis_result["data"]:
                                chart_df = pd.DataFrame(analysis_result["data"])
                                chart_df.set_index("labels", inplace=True)
                                st.bar_chart(chart_df)
                            else:
                                st.warning(f"Could not generate a '{analysis_result['chart_type']}' chart with the provided data.")
                                st.json(analysis_result) # Display raw JSON as a fallback
                        else:
                            st.info("Analysis query not recognized. Please use keywords like 'summarize', 'table', or 'chart'.")

            except Exception as e:
                st.error(f"An error occurred: {e}")

# Display chat history or analysis results
placeholder = st.empty()
with placeholder.container():
    if st.session_state["conversation_mode"] == "Chat Mode":
        for i, message in enumerate(st.session_state["chat_history"]):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    else: # Analysis Mode display
        st.info("Analysis results will appear here. Enter your query below.")

