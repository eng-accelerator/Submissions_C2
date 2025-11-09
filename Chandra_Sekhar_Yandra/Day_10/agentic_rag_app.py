import streamlit as st
from openai import OpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.utilities import GoogleSearchAPIWrapper
import streamlit as st
from dotenv import load_dotenv
import os
import tempfile

import os

# Load environment variables at the start
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Agentic RAG System",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent' not in st.session_state:
    st.session_state.agent = None

def load_pdf(file):
    """Load and process PDF file"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_file_path = tmp_file.name
    
    loader = PyPDFLoader(tmp_file_path)
    documents = loader.load()
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)
    
    # Clean up temp file
    os.unlink(tmp_file_path)
    
    return splits

def create_vector_store(documents, api_key):
    """Create FAISS vector store from documents"""
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store

def create_agent(vector_store, openai_key, google_api_key, google_cse_id):
    """Create LangChain agent with PDF retrieval and web search tools"""
    
    # Initialize LLM
    llm = ChatOpenAI(
        temperature=0.7,
        #model_name="gpt-3.5-turbo",
        base_url="https://openrouter.ai/api/v1",
        api_key=openai_key
    )

    
    # Create retrieval QA chain for PDF
    pdf_qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3})
    )
    
    # Initialize web search
    search = GoogleSearchAPIWrapper(
        google_api_key=google_api_key,
        google_cse_id=google_cse_id
    )
    
    # Define tools
    tools = [
        Tool(
            name="PDF_Search",
            func=pdf_qa.run,
            description="Useful for answering questions based on the uploaded PDF document. Use this when the question is related to the document content."
        ),
        Tool(
            name="Web_Search",
            func=search.run,
            description="Useful for answering questions that require current information or information not available in the PDF. Use this for recent events, news, or general knowledge."
        )
    ]
    
    # Initialize memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Create agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent

# Main UI
st.markdown('<div class="main-header">🤖 Agentic RAG System</div>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    #openai_api_key = st.text_input("OpenAI API Key", type="password")
    openai_api_key = os.getenv('OPENAI_API_KEY')
    #google_api_key = st.text_input("Google API Key", type="password")
    google_api_key = os.getenv('GOOGLE_API_KEY')
    #google_cse_id = st.text_input("Google CSE ID", type="password")
    google_cse_id = os.getenv('GOOGLE_CSE_ID')
    
    st.divider()
    
    st.header("📄 Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    if uploaded_file and openai_api_key:
        if st.button("Process PDF"):
            with st.spinner("Processing PDF..."):
                try:
                    documents = load_pdf(uploaded_file)
                    st.session_state.vector_store = create_vector_store(documents, openai_api_key)
                    st.success(f"✅ PDF processed! {len(documents)} chunks created.")
                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")
    
    st.divider()
    
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.agent = None
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat Interface")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Assistant:** {message['content']}")
    
    # User input
    user_question = st.text_input("Ask a question:", key="user_input")
    
    if st.button("Send"):
        if not user_question:
            st.warning("Please enter a question.")
       # elif not openai_api_key:
       # st.warning("Please provide OpenAI API key.")
       # elif not st.session_state.vector_store:
       #     st.warning("Please upload and process a PDF first.")
        else:
            # Create agent if not exists
            if not st.session_state.agent:
                try:
                    st.session_state.agent = create_agent(
                        st.session_state.vector_store,
                        openai_api_key,
                        google_api_key,
                        google_cse_id
                    )
                except Exception as e:
                    st.error(f"Error creating agent: {str(e)}")
                    st.stop()
            
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_question
            })
            
            # Get response from agent
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent.run(user_question)
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with col2:
    st.header("ℹ️ System Info")
    
    st.markdown("""
    ### How it works:
    
    1. **Upload PDF**: Load your document
    2. **Process**: System creates embeddings
    3. **Ask Questions**: Agent decides:
       - 📄 Search in PDF if context relevant
       - 🌐 Search web if additional info needed
    4. **Get Answers**: Intelligent responses from the right source
    
    ### Features:
    - ✅ Automatic source selection
    - ✅ Conversational memory
    - ✅ Web search integration
    - ✅ Context-aware responses
    """)
    
    if st.session_state.vector_store:
        st.success("✅ PDF Ready")
    else:
        st.info("⏳ Waiting for PDF")
    
    if st.session_state.agent:
        st.success("✅ Agent Active")
    else:
        st.info("⏳ Agent Not Initialized")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    Built with LangChain 🦜🔗 | Powered by OpenAI | Enhanced with Web Search
</div>
""", unsafe_allow_html=True)