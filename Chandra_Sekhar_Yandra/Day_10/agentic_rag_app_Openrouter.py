import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
#from langchain.utilities import GoogleSerperAPIWrapper
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.memory import ConversationBufferMemory
import os
from pathlib import Path
import tempfile

# Page configuration
st.set_page_config(
    page_title="Agentic RAG System",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent_executor' not in st.session_state:
    st.session_state.agent_executor = None

# Sidebar for configuration
st.sidebar.title("⚙️ Configuration")

# API Keys
openrouter_api_key = st.sidebar.text_input("OpenRouter API Key", type="password")
openrouter_base_url = st.sidebar.text_input(
    "OpenRouter Base URL", 
    value="https://openrouter.ai/api/v1",
    help="OpenRouter API endpoint"
)
selected_model = st.sidebar.selectbox(
    "Select Model",
    ["openai/gpt-4", "openai/gpt-3.5-turbo", "anthropic/claude-2", "meta-llama/llama-2-70b-chat"],
    help="Choose the LLM model from OpenRouter"
)
#serper_api_key = st.sidebar.text_input("Serper API Key (for web search)", type="password")

# replaced Serper key with Google API + CSE ID
google_api_key = st.sidebar.text_input("Google API Key", type="password")
google_cse_id = st.sidebar.text_input("Google CSE ID", help="Programmable Search Engine ID (cx)")

# PDF Upload
st.sidebar.title("📄 Upload PDF Documents")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF files",
    type=['pdf'],
    accept_multiple_files=True
)

def process_pdfs(uploaded_files):
    """Process uploaded PDF files and create vector store"""
    if not uploaded_files:
        return None
    
    documents = []
    
    with st.spinner("Processing PDFs..."):
        for uploaded_file in uploaded_files:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Load PDF
            loader = PyPDFLoader(tmp_path)
            docs = loader.load()
            documents.extend(docs)
            
            # Clean up temp file
            os.unlink(tmp_path)
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        
        # Create embeddings and vector store
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_store = FAISS.from_documents(splits, embeddings)
        
    st.sidebar.success(f"✅ Processed {len(uploaded_files)} PDF(s) with {len(splits)} chunks")
    return vector_store

#def create_agent(vector_store, openrouter_api_key, openrouter_base_url, model_name, serper_api_key):
def create_agent(vector_store, openrouter_api_key, openrouter_base_url, model_name, google_api_key=None, google_cse_id=None):
    """Create LangChain agent with PDF and web search tools"""
    
    # Initialize LLM with OpenRouter
    #llm = ChatOpenAI(
    #    model=model_name,
    #    openai_api_key=openrouter_api_key,
    #    openai_api_base=openrouter_base_url,
    #    temperature=0,
    #    headers={
    #        "HTTP-Referer": "https://agentic-rag-system.app",
    #        "X-Title": "Agentic RAG System"
    #    }
    #)
    llm = ChatOpenAI(
         model=model_name,
        openai_api_key=openrouter_api_key,
        openai_api_base=openrouter_base_url,
        temperature=0
     )
    
    # PDF Retrieval Tool
    pdf_qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3})
    )
    
    pdf_tool = Tool(
        name="PDF_Search",
        func=pdf_qa.run,
        description="Useful for answering questions based on the uploaded PDF documents. Use this first to check if the answer exists in the PDFs."
    )
    
    # Web Search Tool with Serper_api_key
    #search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)
    #web_tool = Tool(
    #    name="Web_Search",
    #    func=search.run,
    #    description="Useful for searching current information on the web when the PDF documents don't contain relevant information."
    #)
    
    #tools = [pdf_tool, web_tool]

    # Web Search Tool — use Google Custom Search instead of Serper
    search = None
    web_tool = None
    if google_api_key and google_cse_id:
        search = GoogleSearchAPIWrapper(google_api_key=google_api_key, google_cse_id=google_cse_id)
        web_tool = Tool(
            name="Web_Search",
            func=search.run,
            description="Useful for searching current information on the web when the PDF documents don't contain relevant information."
        )
        tools = [pdf_tool, web_tool]
    else:
        # fallback: only PDF tool available
        tools = [pdf_tool]

    
    # Agent prompt template
    template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT: 
1. Always check PDF_Search first to see if the answer is in the uploaded documents
2. Only use Web_Search if the PDF documents don't contain relevant information
3. Provide clear and concise answers

Begin!

Question: {input}
Thought: {agent_scratchpad}"""
    
    prompt = PromptTemplate.from_template(template)
    
    # Create agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    
    return agent_executor

# Process PDFs button
if st.sidebar.button("Process PDFs") and uploaded_files:
    st.session_state.vector_store = process_pdfs(uploaded_files)

# Main interface
st.title("🤖 Agentic RAG System")
st.markdown("Ask questions about your documents. The system will search PDFs first, then the web if needed.")

# Display system architecture
with st.expander("📊 System Architecture"):
    st.image("https://via.placeholder.com/800x400?text=RAG+Architecture+Flow", use_column_width=True)
    st.markdown("""
    **Workflow:**
    1. User submits a question
    2. System retrieves relevant context from PDF documents
    3. Evaluates if context is relevant
    4. If yes: Generates answer from PDF
    5. If no: Performs web search and generates answer
    6. Returns final answer to user
    """)

# Chat interface
st.markdown("---")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_question = st.chat_input("Ask a question about your documents...")

if user_question:
    # Validate configuration
    if not openrouter_api_key:
        st.error("⚠️ Please enter your OpenRouter API key in the sidebar")
    elif not st.session_state.vector_store:
        st.error("⚠️ Please upload and process PDF documents first")
    else:
        # Add user message to chat
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
        
        # Create or get agent
        if not st.session_state.agent_executor:
            with st.spinner("Initializing agent..."):
                st.session_state.agent_executor = create_agent(
                    st.session_state.vector_store,
                    openrouter_api_key,
                    openrouter_base_url,
                    selected_model,
                    google_api_key if google_api_key else None,
                    google_cse_id if google_cse_id else None
                )
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent_executor.invoke({"input": user_question})
                    answer = response.get('output', 'No answer generated')
                    st.markdown(answer)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Clear chat button
if st.sidebar.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
**About:**
- Built with LangChain & Streamlit
- Uses OpenRouter for LLM access
- Uses FAISS for vector storage
- HuggingFace embeddings for semantic search
- Agentic workflow with ReAct pattern
""")
