"""
Agentic RAG System with PDF, Wikipedia, and Web Search
Uses OpenRouter for LLM access
Run with: streamlit run app.py
"""

import streamlit as st
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain import hub
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun
import os
from dotenv import load_dotenv
import tempfile

# Load environment variables
load_dotenv()

# ============================================
# PDF RETRIEVER CLASS
# ============================================
class PDFRetriever:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.vectorstore = None
    
    def setup_vectorstore(self):
        """Load PDF and create searchable vector database"""
        try:
            # Load PDF
            loader = PyPDFLoader(self.pdf_path)
            documents = loader.load()
            
            if not documents:
                return False, "PDF is empty or could not be read"
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            # Create searchable vector store
            # Use OpenRouter for embeddings
            embeddings = OpenAIEmbeddings(
                openai_api_key=os.getenv("OPENROUTER_API_KEY"),
                openai_api_base="https://openrouter.ai/api/v1"
            )
            self.vectorstore = FAISS.from_documents(splits, embeddings)
            
            return True, f"Successfully loaded {len(documents)} pages from PDF"
        except Exception as e:
            return False, f"Error loading PDF: {str(e)}"
    
    def search(self, query: str, k: int = 3) -> str:
        """Search PDF for relevant information"""
        if not self.vectorstore:
            return "NO_ANSWER: PDF not loaded properly"
        
        try:
            # Find most relevant chunks
            docs = self.vectorstore.similarity_search(query, k=k)
            
            if not docs:
                return "NO_ANSWER: Could not find relevant information in PDF"
            
            # Combine results
            context = "\n\n".join([doc.page_content for doc in docs])
            return f"FOUND IN PDF:\n{context}"
        except Exception as e:
            return f"NO_ANSWER: Search error - {str(e)}"

# ============================================
# TOOL FUNCTIONS (Simple and Clear)
# ============================================

def search_pdf(query: str) -> str:
    """
    Tool 1: Search the uploaded PDF document
    This is the PRIMARY source - always check here first
    """
    if 'pdf_retriever' not in st.session_state or st.session_state.pdf_retriever is None:
        return "NO_ANSWER: No PDF loaded. Please upload a PDF first."
    
    result = st.session_state.pdf_retriever.search(query)
    return result

def search_wikipedia(query: str) -> str:
    """
    Tool 2: Search Wikipedia
    Use this when PDF doesn't have the answer
    """
    try:
        wikipedia = WikipediaAPIWrapper()
        result = wikipedia.run(query)
        return f"FOUND ON WIKIPEDIA:\n{result}"
    except Exception as e:
        return f"NO_ANSWER: Wikipedia search failed - {str(e)}"

def search_web(query: str) -> str:
    """
    Tool 3: Search the web using DuckDuckGo
    Use this as a last resort when PDF and Wikipedia don't help
    """
    try:
        search = DuckDuckGoSearchRun()
        result = search.run(query)
        return f"FOUND ON WEB:\n{result}"
    except Exception as e:
        return f"NO_ANSWER: Web search failed - {str(e)}"

# ============================================
# AGENT SETUP (The Brain of the System)
# ============================================

def create_agentic_rag():
    """
    Create an agent that intelligently decides which tool to use
    
    Decision Logic:
    1. First try PDF (primary source)
    2. If PDF has no answer, try Wikipedia
    3. If Wikipedia has no answer, try web search
    """
    
    # Setup LLM with OpenRouter
    llm = ChatOpenAI(
        model="openai/gpt-4o",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0
    )
    
    # Define tools for the agent
    tools = [
        Tool(
            name="SearchPDF",
            func=search_pdf,
            description="""ALWAYS USE THIS FIRST! Search the PDF document for information. 
            If the result contains 'NO_ANSWER', then try other tools."""
        ),
        Tool(
            name="SearchWikipedia",
            func=search_wikipedia,
            description="""Use this when SearchPDF returns 'NO_ANSWER'. 
            Search Wikipedia for general knowledge and factual information."""
        ),
        Tool(
            name="SearchWeb",
            func=search_web,
            description="""Use this as a LAST RESORT when both SearchPDF and SearchWikipedia return 'NO_ANSWER'. 
            Search the web for current information."""
        )
    ]
    
    # Get the ReAct prompt template
    prompt = hub.pull("hwchase17/react")
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    
    return agent_executor

# ============================================
# STREAMLIT UI
# ============================================

def main():
    st.set_page_config(
        page_title="Agentic RAG System",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Agentic RAG System")
    st.markdown("""
    This intelligent system searches for answers in this order:
    1. **Your PDF** (primary source)
    2. **Wikipedia** (if PDF doesn't have the answer)
    3. **Web Search** (if Wikipedia doesn't have the answer)
    """)
    
    # Initialize session state
    if 'pdf_retriever' not in st.session_state:
        st.session_state.pdf_retriever = None
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar for PDF upload and sample PDFs
    with st.sidebar:
        st.header("📄 Document Upload")
        
        # Sample PDFs section
        st.subheader("Sample PDFs")
        st.markdown("""
        Download sample PDFs to test:
        - [AI Research Paper](https://arxiv.org/pdf/1706.03762.pdf) - "Attention is All You Need"
        - [Python Tutorial](https://www.python.org/ftp/python/doc/3.11.0/python-3.11.0-docs-pdf-a4.zip)
        - [Climate Report](https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_SPM.pdf)
        """)
        
        st.divider()
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload your PDF",
            type=['pdf'],
            help="Upload a PDF document to search"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Load PDF
            with st.spinner("Loading PDF..."):
                pdf_retriever = PDFRetriever(tmp_path)
                success, message = pdf_retriever.setup_vectorstore()
                
                if success:
                    st.session_state.pdf_retriever = pdf_retriever
                    st.success(message)
                    
                    # Create agent
                    st.session_state.agent = create_agentic_rag()
                    st.success("✅ Agent ready!")
                else:
                    st.error(message)
            
            # Clean up temp file
            os.unlink(tmp_path)
        
        st.divider()
        
        # API Key status
        if os.getenv("OPENROUTER_API_KEY"):
            st.success("✅ OpenRouter API Key loaded")
        else:
            st.error("❌ OpenRouter API Key not found in .env")
        
    
    # Main chat interface
    st.divider()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        # Check if agent is ready
        if st.session_state.agent is None:
            st.error("⚠️ Please upload a PDF first!")
            return
        
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    # Show agent's thinking process
                    with st.expander("🔍 Agent's Decision Process", expanded=False):
                        response = st.session_state.agent.invoke({"input": prompt})
                        st.text(response.get("intermediate_steps", ""))
                    
                    # Get final answer
                    answer = response["output"]
                    st.markdown(answer)
                    
                    # Add to messages
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()