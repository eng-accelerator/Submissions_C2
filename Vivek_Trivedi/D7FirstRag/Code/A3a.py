# Assignment 3a: Basic Gradio RAG Frontend Implementation
# Following the exact structure from assignment_3a_basic_gradio_rag.ipynb

import gradio as gr
import os
from pathlib import Path

# Import Gradio first to avoid conflicts
import gradio as gr

# LlamaIndex components  
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.lancedb import LanceDBVectorStore

# Import these with error handling
try:
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    print("✅ HuggingFace embeddings imported successfully")
except Exception as e:
    print(f"⚠️ HuggingFace embeddings import issue: {e}")
    print("   Will use default embeddings instead")
    HuggingFaceEmbedding = None

try:
    from llama_index.llms.openrouter import OpenRouter
    print("✅ OpenRouter LLM imported successfully")
except Exception as e:
    print(f"⚠️ OpenRouter import issue: {e}")
    OpenRouter = None

from dotenv import load_dotenv

print("✅ All core libraries imported successfully!")

# Load environment variables
load_dotenv()

# 📚 Part 2: RAG Backend Class
def check_vector_db_exists(db_path: str, table_name: str = "documents"):
    """
    Check if vector database already exists and has data.
    """
    lance_file = Path(db_path) / f"{table_name}.lance"
    
    if lance_file.exists():
        try:
            import lancedb
            db = lancedb.connect(db_path)
            if table_name in db.table_names():
                table = db.open_table(table_name)
                count = table.count_rows()
                print(f"📊 Existing database found with {count} entries")
                return count > 0
        except Exception as e:
            print(f"⚠️  Error checking existing database: {e}")
            return False
    
    return False

class SimpleRAGBackend:
    """Simple RAG backend for Gradio frontend."""
    
    def __init__(self):
        self.index = None
        self.is_initializing = False
        self.is_ready = False
        self.setup_settings()
    
    def setup_settings(self):
        """Configure LlamaIndex settings."""
        # Check for OpenRouter API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key or api_key.strip() == "your_openrouter_api_key_here":
            print("⚠️  OPENROUTER_API_KEY not configured properly")
            print("   🔍 Retrieval-only mode available (document search without AI responses)")
            print("   🤖 For full AI responses, configure a valid API key in .env file")
            print("   🌐 Get API key from: https://openrouter.ai/")
        else:
            print("✅ OPENROUTER_API_KEY found - attempting full RAG functionality")
            
            # Set up the LLM using OpenRouter if available
            if OpenRouter is not None:
                try:
                    Settings.llm = OpenRouter(
                        api_key=api_key,
                        model="gpt-4o",
                        temperature=0.1
                    )
                    print("✅ OpenRouter LLM configured successfully")
                except Exception as e:
                    print(f"⚠️ OpenRouter LLM setup failed: {e}")
                    print("   Will fall back to retrieval-only mode when needed")
        
        # Set up the embedding model (no API key required) if available
        if HuggingFaceEmbedding is not None:
            Settings.embed_model = HuggingFaceEmbedding(
                model_name="BAAI/bge-small-en-v1.5",
                trust_remote_code=True
            )
        else:
            print("⚠️ Using default embeddings (HuggingFace not available)")
        
        # Set chunking parameters
        Settings.chunk_size = 512
        Settings.chunk_overlap = 50
        
        print("✅ RAG Backend settings configured")
        print("   - Using local embeddings for cost efficiency")
        print("   - OpenRouter LLM ready for response generation")
    
    def initialize_database(self, data_folder=None):
        """Initialize the vector database with documents."""
        # Prevent multiple initializations
        if self.is_initializing:
            return "⚠️ Database initialization already in progress! Please wait..."
        
        if self.is_ready:
            return "✅ Database already initialized and ready!"
        
        # Ensure AssignmentDb folder exists first
        Path("./AssignmentDb").mkdir(parents=True, exist_ok=True)
        
        # Set initialization flag
        self.is_initializing = True
        self.is_ready = False
        
        # Use environment variable or default path
        if data_folder is None:
            data_folder = os.getenv("DATA_PATH", "../../../../ai-accelerator-C2-main/ai-accelerator-C2-main/Day_6/session_2/data")
        
        # Check if data folder exists
        if not Path(data_folder).exists():
            error_msg = f"❌ Data folder '{data_folder}' not found!"
            print(error_msg)
            self.is_initializing = False
            return error_msg
        
        try:
            # Get database path from environment variable
            db_path = os.getenv("ASSIGNMENT_3A_DB_PATH", "./AssignmentDb/a3a_basic_rag_vectordb")
            
            print(f"📁 Initializing database at: {db_path}")
            print(f"📂 Loading documents from: {data_folder}")
            
            # Check if database already exists
            if check_vector_db_exists(db_path):
                print("🔄 Loading existing database...")
                try:
                    # Create vector store and load existing index
                    vector_store = LanceDBVectorStore(
                        uri=db_path,
                        table_name="documents"
                    )
                    storage_context = StorageContext.from_defaults(vector_store=vector_store)
                    self.index = VectorStoreIndex([], storage_context=storage_context)
                    
                    # Mark as ready
                    self.is_initializing = False
                    self.is_ready = True
                    
                    success_msg = "✅ Existing database loaded successfully!\n🎯 Ready to answer questions!"
                    print(success_msg)
                    return success_msg
                except Exception as e:
                    print(f"⚠️  Error loading existing database: {e}")
                    print("🔄 Will create fresh database...")
            
            # Create fresh database
            # Create vector store
            vector_store = LanceDBVectorStore(
                uri=db_path,
                table_name="documents"
            )
            
            # Load documents with safe file extensions
            safe_exts = [".txt", ".md", ".pdf", ".html", ".htm", ".csv", ".json"]
            reader = SimpleDirectoryReader(
                input_dir=data_folder, 
                recursive=True,
                required_exts=safe_exts
            )
            documents = reader.load_data()
            
            if not documents:
                error_msg = f"❌ No documents found in '{data_folder}'"
                print(error_msg)
                return error_msg
            
            print(f"📄 Loaded {len(documents)} documents")
            print("🔄 Starting embedding process... This may take a few moments.")
            
            # Create storage context and index
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            self.index = VectorStoreIndex.from_documents(
                documents, 
                storage_context=storage_context,
                show_progress=True
            )
            
            # Mark as ready only AFTER embeddings are complete
            self.is_initializing = False
            self.is_ready = True
            
            success_msg = f"✅ Database initialized successfully with {len(documents)} documents!\n🎯 Ready to answer questions!"
            print(success_msg)
            return success_msg
        
        except Exception as e:
            error_msg = f"❌ Error initializing database: {str(e)}"
            print(error_msg)
            self.is_initializing = False
            self.is_ready = False
            return error_msg
    
    def query(self, question):
        """Query the RAG system and return response."""
        # Check initialization status
        if self.is_initializing:
            error_msg = "⏳ Database is still initializing... Please wait for initialization to complete!"
            print(error_msg)
            return error_msg
        
        if not self.is_ready or self.index is None:
            error_msg = "❌ Please initialize the database first!"
            print(error_msg)
            return error_msg
        
        # Check if question is empty
        if not question or not question.strip():
            warning_msg = "⚠️ Please enter a question first!"
            print(warning_msg)
            return warning_msg
        
        try:
            print(f"🔍 Processing query: '{question}'")
            
            # Check if we have LLM configured
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key or api_key.strip() == "your_openrouter_api_key_here":
                # Fallback to retrieval-only mode
                print("⚠️ No valid LLM API key - using retrieval-only mode")
                return self._retrieval_only_query(question)
            
            # Create query engine and get response
            query_engine = self.index.as_query_engine()
            response = query_engine.query(question)
            
            response_text = str(response)
            print(f"✅ Query processed successfully - Response length: {len(response_text)} characters")
            
            return response_text
        
        except Exception as e:
            error_str = str(e)
            print(f"❌ LLM Error: {error_str}")
            
            # Check for common API issues and fallback gracefully
            if "401" in error_str or "Unauthorized" in error_str or "cookie auth" in error_str:
                print("🔄 API authentication failed - falling back to retrieval-only mode")
                return self._retrieval_only_query(question)
            elif "429" in error_str or "rate limit" in error_str.lower():
                return "⏳ API rate limit reached. Please try again in a few moments."
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                return "🌐 Network connection issue. Please check your internet connection and try again."
            else:
                # General fallback to retrieval-only
                print("🔄 LLM unavailable - falling back to retrieval-only mode")
                return self._retrieval_only_query(question)
    
    def _retrieval_only_query(self, question):
        """Fallback method that provides retrieval results without LLM processing."""
        try:
            print(f"🔍 Fallback: Searching documents for: '{question}'")
            
            # Double-check index exists (for linter safety)
            if self.index is None:
                return "❌ Database not initialized. Please initialize the database first."
            
            # Create retriever and get relevant documents
            retriever = self.index.as_retriever(similarity_top_k=5)
            nodes = retriever.retrieve(question)
            
            if not nodes:
                return "❌ No relevant documents found for your question."
            
            # Format the results nicely
            response_parts = [
                "🔍 **Document Search Results** (LLM unavailable - showing retrieved content):",
                "",
                f"**Query**: {question}",
                f"**Found**: {len(nodes)} relevant document(s)",
                ""
            ]
            
            for i, node in enumerate(nodes, 1):
                score = getattr(node, 'score', 0.0)
                text_preview = node.text[:300] + "..." if len(node.text) > 300 else node.text
                
                response_parts.extend([
                    f"**Result {i}** (Relevance: {score:.3f}):",
                    text_preview,
                    ""
                ])
            
            response_parts.extend([
                "---",
                "💡 **Note**: This is a document search result. For AI-generated responses, please configure a valid OPENROUTER_API_KEY in your .env file.",
                "",
                "🔧 **To enable full AI responses**:",
                "1. Get an API key from https://openrouter.ai/",
                "2. Add it to your .env file: OPENROUTER_API_KEY=your_actual_key_here",
                "3. Restart the application"
            ])
            
            result = "\n".join(response_parts)
            print(f"✅ Retrieval completed - Found {len(nodes)} relevant documents")
            return result
            
        except Exception as e:
            error_msg = f"❌ Even retrieval failed: {str(e)}"
            print(error_msg)
            return error_msg

# Initialize the backend
print("🔧 Initializing RAG Backend...")
rag_backend = SimpleRAGBackend()
print("🚀 RAG Backend initialized and ready!")

# 🎨 Part 3: Gradio Interface
def create_basic_rag_interface():
    """Create basic RAG interface with essential features."""
    
    def initialize_db():
        """Handle database initialization."""
        print("\n" + "="*50)
        print("🔄 Database Initialization Started...")
        result = rag_backend.initialize_database()
        print("🔄 Database Initialization Completed")
        print("="*50 + "\n")
        return result
    
    def handle_query(question):
        """Handle user queries."""
        if not question or not question.strip():
            return "⚠️ Please enter a question first!"
        
        print("\n" + "-"*40)
        print("🔍 Processing User Query...")
        result = rag_backend.query(question)
        print("🔍 Query Processing Completed")
        print("-"*40 + "\n")
        return result
    
    # Create Gradio interface using gr.Blocks()
    with gr.Blocks(
        title="Basic RAG Assistant",
        css="footer {visibility: hidden}"
    ) as interface:
        
        # Add title and description
        # Check API key status for user information
        api_key = os.getenv("OPENROUTER_API_KEY")
        has_valid_key = api_key and api_key.strip() != "your_openrouter_api_key_here"
        
        mode_info = "🤖 **Full AI Mode**: Get intelligent responses generated by AI" if has_valid_key else "🔍 **Retrieval Mode**: Search documents and view relevant content (AI responses require API key configuration)"
        
        gr.Markdown(f"""
        # 🤖 Basic RAG Assistant
        ## AI-Powered Document Search and Question Answering
        
        {mode_info}
        
        Welcome to your RAG (Retrieval-Augmented Generation) Assistant! This application allows you to:
        - Initialize a vector database with your documents
        - Ask questions and get {'AI-powered answers' if has_valid_key else 'relevant document excerpts'} based on your data
        
        ### 📋 How to Use:
        1. **First**: Click "Initialize Database" to set up your document collection
        2. **Then**: Enter your question and click "Ask Question" to get responses
        
        {'### 🔧 For Full AI Responses:' if not has_valid_key else ''}
        {'- Get an API key from [OpenRouter](https://openrouter.ai/)' if not has_valid_key else ''}
        {'- Add `OPENROUTER_API_KEY=your_key` to your .env file' if not has_valid_key else ''}
        {'- Restart the application' if not has_valid_key else ''}
        """)
        
        # Add initialization section
        gr.Markdown("## 🗄️ Database Setup")
        
        with gr.Row():
            init_btn = gr.Button(
                "🔧 Initialize Database",
                variant="primary",
                size="lg"
            )
        
        # Add status output
        status_output = gr.Textbox(
            label="📊 Database Status",
            placeholder="Click 'Initialize Database' to start...",
            lines=3,
            interactive=False
        )
        
        # Add query section
        gr.Markdown("## 💬 Ask Your Questions")
        
        query_input = gr.Textbox(
            label="🔍 Enter your question",
            placeholder="What would you like to know about the documents?",
            lines=2
        )
        
        with gr.Row():
            submit_btn = gr.Button(
                "🚀 Ask Question",
                variant="secondary",
                size="lg"
            )
            clear_btn = gr.Button(
                "🗑️ Clear",
                variant="stop",
                size="lg"
            )
        
        # Add response output
        response_output = gr.Textbox(
            label="🤖 AI Response",
            placeholder="Your AI-powered answer will appear here...",
            lines=10,
            interactive=False,
            show_copy_button=True
        )
        
        # Add examples section
        gr.Markdown("## 💡 Example Questions")
        
        examples = gr.Examples(
            examples=[
                ["What are the main topics in the documents?"],
                ["Summarize the key findings from the research"],
                ["What are AI agents and their capabilities?"],
                ["How do you evaluate agent performance?"],
                ["Tell me about Italian cooking techniques"],
                ["What investment strategies are mentioned?"]
            ],
            inputs=query_input
        )
        
        # Connect buttons to functions
        init_btn.click(
            fn=initialize_db,
            outputs=[status_output]
        )
        
        submit_btn.click(
            fn=handle_query,
            inputs=[query_input],
            outputs=[response_output]
        )
        
        clear_btn.click(
            lambda: ("", ""),
            outputs=[query_input, response_output]
        )
        
        # Add footer information
        gr.Markdown("""
        ---
        ### 🔧 Technical Details:
        - **Vector Database**: LanceDB with HuggingFace embeddings
        - **LLM**: OpenRouter GPT-4o for response generation
        - **Documents**: Loaded from configured data directory
        - **Framework**: LlamaIndex for RAG pipeline
        
        **💡 Tip**: For best results, ask specific questions about topics that might be covered in your documents!
        """)
        
    return interface

# Create the interface
print("🎨 Creating Basic RAG Interface...")
basic_interface = create_basic_rag_interface()
print("✅ Basic RAG interface created successfully!")

# 🚀 Part 4: Launch Your Application
def launch_application():
    """Launch the Gradio application with proper configuration."""
    print("\n" + "="*60)
    print("🎉 Launching your Basic RAG Assistant...")
    print("🔗 Your application will open in a new browser tab!")
    print("")
    print("📋 Testing Instructions:")
    print("1. Click 'Initialize Database' button first")
    print("2. Wait for success message")
    print("3. Enter a question in the query box")
    print("4. Click 'Ask Question' to get AI response")
    print("")
    print("💡 Example questions to try:")
    print("- What are the main topics in the documents?")
    print("- Summarize the key findings")
    print("- Explain the methodology used")
    print("- What are AI agents and their capabilities?")
    print("")
    print("🚀 Starting application server...")
    print("="*60 + "\n")
    
    # Launch the application
    basic_interface.launch(
        share=False,  # Set to True if you want a public link
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True,  # Automatically open browser
        quiet=False
    )

# Main execution
if __name__ == "__main__":
    print("\n🎯 Assignment 3a: Basic Gradio RAG Frontend")
    print("="*50)
    
    # Check environment setup
    api_key = os.getenv("OPENROUTER_API_KEY")
    data_path = os.getenv("DATA_PATH", "../../../../ai-accelerator-C2-main/ai-accelerator-C2-main/Day_6/session_2/data")
    
    print("🔍 Environment Check:")
    print(f"   OpenRouter API: {'✅ Found' if api_key else '⚠️  Not found (limited functionality)'}")
    print(f"   Data Path: {data_path}")
    print(f"   Database Path: {os.getenv('ASSIGNMENT_3A_DB_PATH', './AssignmentDb/a3a_basic_rag_vectordb')}")
    
    print("\n🚀 Ready to launch RAG Assistant!")
    print("   Run launch_application() to start the web interface")
    
    # Auto-launch the application
    launch_application()

print("\n✅ A3a.py is ready!")
print("🔥 To start your RAG Assistant, run: launch_application()")