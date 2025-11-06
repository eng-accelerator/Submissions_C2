# Assignment 3b: Advanced Gradio RAG Frontend
# Day 6 Session 2 - Building Configurable RAG Applications
# Advanced RAG interface with full configuration options

import gradio as gr
import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LlamaIndex core components
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter

# Advanced RAG components
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import TreeSummarize, Refine, CompactAndRefine
from llama_index.core.retrievers import VectorIndexRetriever

print("✅ All libraries imported successfully!")


def check_vector_db_exists(db_path: str, table_name: str = "documents"):
    """
    Check if vector database already exists and has data.
    
    Args:
        db_path (str): Path to the vector database
        table_name (str): Name of the table to check
        
    Returns:
        bool: True if database exists and has data, False otherwise
    """
    try:
        db_file = Path(db_path) / f"{table_name}.lance"
        return db_file.exists()
    except Exception:
        return False


def check_database_configuration(db_path: str, chunk_size: int, chunk_overlap: int):
    """
    Check if database exists with matching chunk configuration.
    
    Args:
        db_path (str): Path to the vector database
        chunk_size (int): Current chunk size
        chunk_overlap (int): Current chunk overlap
        
    Returns:
        tuple: (exists_with_matching_config, status_message)
    """
    db_path_obj = Path(db_path)
    
    # Check if database directory exists
    if not db_path_obj.exists():
        return False, "📁 No existing database found - will create new database"
    
    # Check if actual database files exist
    if not check_vector_db_exists(db_path):
        return False, "📁 Database directory exists but no data files found - will create new database"
    
    # Check configuration metadata
    config_file = db_path_obj / "chunk_config.json"
    if not config_file.exists():
        return False, "⚠️ Database exists but no configuration metadata found - will rebuild to ensure consistency"
    
    try:
        # Load stored configuration
        with open(config_file, 'r') as f:
            stored_config = json.load(f)
        
        # Compare with current configuration
        current_config = {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap
        }
        
        stored_chunk_config = {
            "chunk_size": stored_config.get("chunk_size"),
            "chunk_overlap": stored_config.get("chunk_overlap")
        }
        
        if stored_chunk_config != current_config:
            return False, f"""🔄 Configuration changed - database will be rebuilt:
   Previous: chunk_size={stored_chunk_config['chunk_size']}, chunk_overlap={stored_chunk_config['chunk_overlap']}
   New: chunk_size={current_config['chunk_size']}, chunk_overlap={current_config['chunk_overlap']}
   📊 This ensures optimal retrieval with your new chunking strategy"""
        
        # Configuration matches
        doc_count = stored_config.get("document_count", "unknown")
        return True, f"✅ Found existing database with matching configuration (chunk_size={chunk_size}, chunk_overlap={chunk_overlap}, {doc_count} documents)"
        
    except Exception as e:
        return False, f"⚠️ Error reading configuration metadata: {str(e)} - will rebuild database"


def save_database_configuration(db_path: str, chunk_size: int, chunk_overlap: int, document_count: int):
    """
    Save database configuration metadata.
    
    Args:
        db_path (str): Path to the vector database
        chunk_size (int): Chunk size used
        chunk_overlap (int): Chunk overlap used  
        document_count (int): Number of documents processed
    """
    db_path_obj = Path(db_path)
    config_file = db_path_obj / "chunk_config.json"
    
    config = {
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "document_count": document_count,
        "created_at": datetime.now().isoformat(),
        "data_path": os.getenv('DATA_PATH', 'N/A'),
        "version": "A3b_v1.0"
    }
    
    try:
        db_path_obj.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"💾 Configuration metadata saved: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}, documents={document_count}")
    except Exception as e:
        print(f"⚠️ Could not save configuration metadata: {e}")


class AdvancedRAGBackend:
    """Advanced RAG backend with configurable parameters."""
    
    def __init__(self):
        self.index = None
        self.is_initializing = False
        self.is_ready = False
        self.available_models = ["gpt-4o", "gpt-4o-mini"]
        self.available_postprocessors = ["SimilarityPostprocessor"]
        self.available_synthesizers = ["TreeSummarize", "Refine", "CompactAndRefine", "Default"]
        self.setup_initial_settings()
        
    def setup_initial_settings(self):
        """Set up initial LlamaIndex settings."""
        # Check for OpenRouter API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key or api_key.strip() == "your_openrouter_api_key_here":
            print("⚠️  OPENROUTER_API_KEY not configured properly")
            print("   🔍 Retrieval-only mode available (document search without AI responses)")
            print("   🤖 For full AI responses, configure a valid API key in .env file")
            print("   🌐 Get API key from: https://openrouter.ai/")
        else:
            print("✅ OPENROUTER_API_KEY found - full advanced RAG functionality available")
        
        # Set up basic settings (but delay embedding model initialization)
        self.embedding_initialized = False
        print("✅ Advanced RAG Backend initialized (models will load when needed)")
        
    def update_settings(self, model: str = "gpt-4o-mini", temperature: float = 0.1, chunk_size: int = 512, chunk_overlap: int = 50, init_embeddings: bool = False):
        """Update LlamaIndex settings based on user configuration."""
        # Set up the LLM using OpenRouter
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key and api_key.strip() != "your_openrouter_api_key_here":
            try:
                Settings.llm = OpenRouter(
                    api_key=api_key,
                    model=model,
                    temperature=temperature
                )
                print(f"✅ OpenRouter LLM configured: {model} (temp: {temperature})")
            except Exception as e:
                print(f"⚠️  Error configuring OpenRouter LLM: {e}")
        
        # Set up the embedding model only when needed (lazy loading)
        if init_embeddings and not self.embedding_initialized:
            try:
                print("🔄 Initializing HuggingFace embeddings (this may take a moment)...")
                Settings.embed_model = HuggingFaceEmbedding(
                    model_name="BAAI/bge-small-en-v1.5",
                    trust_remote_code=True
                )
                self.embedding_initialized = True
                print("✅ HuggingFace embeddings configured")
            except Exception as e:
                print(f"⚠️  Error configuring embeddings: {e}")
                return f"❌ Failed to initialize embeddings: {e}"
        
        # Set chunking parameters from function parameters
        Settings.chunk_size = chunk_size
        Settings.chunk_overlap = chunk_overlap
        print(f"✅ Chunking parameters set: size={chunk_size}, overlap={chunk_overlap}")
        
        return "✅ Settings updated successfully"
    
    def initialize_database(self, data_folder=None, chunk_size=512, chunk_overlap=50, force_rebuild=False):
        """Initialize the vector database with configuration-aware duplicate checking."""
        # Prevent multiple initializations
        if self.is_initializing:
            return "⚠️ Database initialization already in progress! Please wait..."
        
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
            db_path = os.getenv("ASSIGNMENT_3B_DB_PATH", "./AssignmentDb/a3b_advanced_gradio_rag_vectordb")
            
            print(f"� Checking database configuration...")
            print(f"📁 Database path: {db_path}")
            print(f"� Requested configuration: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
            
            # Check if database exists with matching configuration
            config_matches, config_message = check_database_configuration(db_path, chunk_size, chunk_overlap)
            print(config_message)
            
            if config_matches and not force_rebuild:
                print("🔄 Loading existing database with matching configuration...")
                try:
                    # Create vector store and load existing index
                    vector_store = LanceDBVectorStore(
                        uri=db_path,
                        table_name="documents"
                    )
                    storage_context = StorageContext.from_defaults(vector_store=vector_store)
                    self.index = VectorStoreIndex([], storage_context=storage_context)
                    
                    print("✅ Existing database loaded successfully!")
                    self.is_ready = True
                    self.is_initializing = False
                    return f"✅ Database loaded successfully!\n{config_message}\n🚀 Ready for advanced queries with full configuration options."
                    
                except Exception as e:
                    print(f"⚠️  Error loading existing database: {e}")
                    print("🔄 Creating fresh database...")
            
            # Database needs to be created or rebuilt
            if Path(db_path).exists():
                print("🗑️ Removing old database to rebuild with new configuration...")
                shutil.rmtree(db_path)
                print("✅ Old database removed")
            
            # Update settings with new chunk configuration
            print(f"⚙️ Applying chunk configuration: size={chunk_size}, overlap={chunk_overlap}")
            self.update_settings(
                model=getattr(self, 'current_model', 'gpt-4o-mini'),
                temperature=getattr(self, 'current_temperature', 0.1),
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                init_embeddings=True  # ensure HF embeddings are initialized (avoid OpenAI default)
            )
            
            # Create vector store
            print(f"📦 Creating vector store at: {db_path}")
            vector_store = LanceDBVectorStore(
                uri=db_path,
                table_name="documents"
            )
            
            # Load documents
            print("📄 Loading documents from data folder...")
            reader = SimpleDirectoryReader(input_dir=data_folder, recursive=True)
            documents = reader.load_data()
            
            if not documents:
                error_msg = f"❌ No documents found in {data_folder}"
                print(error_msg)
                self.is_initializing = False
                return error_msg
            
            print(f"📚 Successfully loaded {len(documents)} documents")
            print(f"🔧 Processing documents with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
            
            # Create storage context and index
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            print("🔗 Building vector index with new chunking configuration...")
            print("   This may take a few minutes for large document sets...")
            
            self.index = VectorStoreIndex.from_documents(
                documents, 
                storage_context=storage_context,
                show_progress=True
            )
            
            # Save configuration metadata
            print("💾 Saving configuration metadata...")
            save_database_configuration(db_path, chunk_size, chunk_overlap, len(documents))
            
            success_msg = f"""✅ Advanced database initialized successfully!
📊 Processed {len(documents)} documents with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}
🚀 Ready for advanced queries with full configuration options"""
            print(success_msg.replace('\n', ' '))
            self.is_ready = True
            self.is_initializing = False
            return success_msg
        
        except Exception as e:
            error_msg = f"❌ Error initializing database: {str(e)}"
            print(error_msg)
            self.is_initializing = False
            return error_msg
    
    def get_postprocessor(self, postprocessor_name: str, similarity_cutoff: float):
        """Get the selected postprocessor."""
        if postprocessor_name == "SimilarityPostprocessor":
            return SimilarityPostprocessor(similarity_cutoff=similarity_cutoff)
        elif postprocessor_name == "None":
            return None
        else:
            return None
    
    def get_synthesizer(self, synthesizer_name: str):
        """Get the selected response synthesizer."""
        if synthesizer_name == "TreeSummarize":
            return TreeSummarize()
        elif synthesizer_name == "Refine":
            return Refine()
        elif synthesizer_name == "CompactAndRefine":
            return CompactAndRefine()
        elif synthesizer_name == "Default":
            return None
        else:
            return None
    
    def _retrieval_only_query(self, question: str, similarity_top_k: int = 5) -> Dict[str, Any]:
        """Fallback method for retrieval-only queries when LLM is not available."""
        try:
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=similarity_top_k,
            )
            
            nodes = retriever.retrieve(question)
            
            # Format retrieved content
            retrieved_content = []
            sources = []
            
            for i, node in enumerate(nodes, 1):
                content = node.text[:300] + "..." if len(node.text) > 300 else node.text
                retrieved_content.append(f"**Document {i}:**\n{content}")
                
                sources.append({
                    "text": node.text[:200] + "...",
                    "score": getattr(node, 'score', 0.0),
                    "source": getattr(node.node, 'metadata', {}).get('file_name', 'Unknown')
                })
            
            response = "🔍 **Retrieved Documents (Retrieval-Only Mode):**\n\n" + "\n\n".join(retrieved_content)
            response += f"\n\n💡 **Note:** This is retrieval-only mode. Configure OPENROUTER_API_KEY for AI-generated responses."
            
            return {
                "response": response,
                "sources": sources,
                "config": {"mode": "retrieval_only", "similarity_top_k": similarity_top_k}
            }
            
        except Exception as e:
            return {
                "response": f"❌ Error in retrieval-only query: {str(e)}",
                "sources": [],
                "config": {"mode": "error"}
            }
    
    def advanced_query(self, question: str, model: str, temperature: float, 
                      chunk_size: int, chunk_overlap: int, similarity_top_k: int,
                      postprocessor_names: List[str], similarity_cutoff: float,
                      synthesizer_name: str) -> Dict[str, Any]:
        """Query the RAG system with advanced configuration."""
        
        # Check if index exists
        if self.index is None:
            return {"response": "❌ Please initialize the database first!", "sources": [], "config": {}}
        
        # Check if question is empty
        if not question or not question.strip():
            return {"response": "⚠️ Please enter a question first!", "sources": [], "config": {}}
        
        # Check if API key is available for full RAG functionality
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key or api_key.strip() == "your_openrouter_api_key_here":
            print("⚠️  No valid API key found, using retrieval-only mode")
            return self._retrieval_only_query(question, similarity_top_k)
        
        try:
            # Update settings with new parameters
            self.update_settings(model, temperature, chunk_size, chunk_overlap)
            
            # Get postprocessors
            postprocessors = []
            for name in postprocessor_names:
                processor = self.get_postprocessor(name, similarity_cutoff)
                if processor is not None:
                    postprocessors.append(processor)
            
            # Get synthesizer
            synthesizer = self.get_synthesizer(synthesizer_name)
            
            # Create query engine with all parameters
            query_engine_kwargs = {"similarity_top_k": similarity_top_k}
            if postprocessors:
                query_engine_kwargs["node_postprocessors"] = postprocessors
            if synthesizer is not None:
                query_engine_kwargs["response_synthesizer"] = synthesizer
            
            query_engine = self.index.as_query_engine(**query_engine_kwargs)
            
            # Query and get response
            response = query_engine.query(question)
            
            # Extract source information if available
            sources = []
            if hasattr(response, 'source_nodes'):
                for node in response.source_nodes:
                    sources.append({
                        "text": node.text[:200] + "...",
                        "score": getattr(node, 'score', 0.0),
                        "source": getattr(node.node, 'metadata', {}).get('file_name', 'Unknown')
                    })
            
            return {
                "response": str(response),
                "sources": sources,
                "config": {
                    "model": model,
                    "temperature": temperature,
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "similarity_top_k": similarity_top_k,
                    "postprocessors": postprocessor_names,
                    "similarity_cutoff": similarity_cutoff,
                    "synthesizer": synthesizer_name,
                    "mode": "full_rag"
                }
            }
        
        except Exception as e:
            return {"response": f"❌ Error processing advanced query: {str(e)}", "sources": [], "config": {"mode": "error"}}


def get_api_status_html():
    """Generate API status HTML display."""
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if api_key and api_key.strip() != "your_openrouter_api_key_here":
        return """
        <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 15px; margin: 10px 0; color: #155724;">
            <strong>🤖 Full AI Mode Active!</strong> OpenRouter API key detected - all features available.
        </div>
        """
    else:
        return """
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 10px 0; color: #856404;">
            <strong>⚠️ Retrieval-Only Mode</strong> - No API key found. You'll get document search results only.<br>
            <em>Configure OPENROUTER_API_KEY in .env file for full AI responses.</em>
        </div>
        """


def get_config_display_html():
    """Generate initial configuration display HTML."""
    return """
    <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 15px; margin: 10px 0; color: #155724;">
        <strong>🤖 AI Model:</strong> gpt-4o-mini (Temperature: 0.1) &nbsp;&nbsp;
        <strong>📄 Chunking:</strong> Size=512, Overlap=50<br>
        <strong>🎯 Retrieval:</strong> Top-K=8, Cutoff=0.3 &nbsp;&nbsp;
        <strong>🔧 Postprocessor:</strong> ✅ Enabled &nbsp;&nbsp;
        <strong>🧠 Synthesizer:</strong> TreeSummarize
    </div>
    """


def create_advanced_rag_interface_legacy():
    """Legacy UI (unused) kept for reference."""
    
    # No custom CSS; use Gradio defaults
    css = ""
    
    # UI Event Handlers (separate from backend)
    def update_chunk_status(chunk_size, chunk_overlap):
        """Update chunk configuration status display."""
        return f"""
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 10px 0; color: #856404;">
            <strong>🎯 Current Configuration:</strong> chunk_size={chunk_size}, chunk_overlap={chunk_overlap}<br>
            <strong>⚠️ Status:</strong> Configuration changed - click "🚀 Initialize Database" to apply changes
        </div>
        """
    
    def update_config_display(model, temp, chunk_size, chunk_overlap, top_k, cutoff, postprocessor, synth):
        """Update real-time configuration display."""
        return f"""
        <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 15px; margin: 10px 0; color: #155724;">
            <strong>🤖 AI Model:</strong> {model} (Temperature: {temp}) &nbsp;&nbsp;
            <strong>📄 Chunking:</strong> Size={chunk_size}, Overlap={chunk_overlap}<br>
            <strong>🎯 Retrieval:</strong> Top-K={top_k}, Cutoff={cutoff} &nbsp;&nbsp;
            <strong>🔧 Postprocessor:</strong> {'✅ Enabled' if postprocessor else '❌ Disabled'} &nbsp;&nbsp;
            <strong>🧠 Synthesizer:</strong> {synth}
        </div>
        """
    
    # Backend Interface Handlers
    def initialize_db(chunk_size, chunk_overlap):
        """Handle database initialization with chunk configuration."""
        return rag_backend.initialize_database(chunk_size=int(chunk_size), chunk_overlap=int(chunk_overlap))
    
    def handle_advanced_query(question, model, temperature, chunk_size, chunk_overlap, 
                             similarity_top_k, use_postprocessor, similarity_cutoff, synthesizer):
        """Handle advanced RAG queries with all configuration options."""
        # Convert postprocessor boolean to list format expected by backend
        postprocessors = ["SimilarityPostprocessor"] if use_postprocessor else []
        
        result = rag_backend.advanced_query(
            question, model, temperature, int(chunk_size), int(chunk_overlap),
            int(similarity_top_k), postprocessors, similarity_cutoff, synthesizer
        )
        
        return result["response"]
    
    def clear_inputs():
        """Clear input fields."""
        return "", ""

    # System Configuration popup helpers (match rag_gui style)
    def build_config_html(model, temperature, chunk_size, overlap_size, top_k, similarity_threshold, postprocessor_enabled, synthesizer):
        post_text = "Enabled" if (postprocessor_enabled and len(postprocessor_enabled) > 0) else "Disabled"
        return f"""
        <div id='config_popup_box' style='position: fixed; top: 56px; right: 16px; width: 300px; max-width: 90vw; padding: 10px; border: 1px solid rgba(128,128,128,0.35); border-radius: 8px; box-shadow: 0 6px 18px rgba(0,0,0,0.12); z-index: 9999;'>
            <div style='font-weight: 600; margin-bottom: 6px; font-size: 13px;'>System Configuration</div>
            <div style='font-size: 13px; line-height: 1.4;'>
                <div><strong>Model:</strong> {model}</div>
                <div><strong>Temperature:</strong> {temperature}</div>
                <div><strong>Chunk Size:</strong> {int(chunk_size)}</div>
                <div><strong>Overlap:</strong> {int(overlap_size)}</div>
                <div><strong>Top-K:</strong> {int(top_k)}</div>
                <div><strong>Similarity Threshold:</strong> {similarity_threshold}</div>
                <div><strong>Postprocessor:</strong> {post_text}</div>
                <div><strong>Synthesizer:</strong> {synthesizer}</div>
            </div>
        </div>
        """

    def toggle_config(is_visible, model, temperature, chunk_size, overlap_size, top_k, similarity_threshold, postprocessor_enabled, synthesizer):
        new_visible = not bool(is_visible)
        html = build_config_html(model, temperature, chunk_size, overlap_size, top_k, similarity_threshold, postprocessor_enabled, synthesizer)
        return gr.update(value=html, visible=new_visible), new_visible, gr.update(visible=new_visible)
    
    # Create the Gradio Interface
    with gr.Blocks(css=css, title="🚀 Advanced RAG System - A3b") as interface:
        # Header Section
        gr.HTML("""
        <div class="main-container">
            <h1 style="text-align: center; color: #2c3e50; margin-bottom: 10px; font-size: 2.5em;">
                � Advanced RAG System (Assignment 3B)
            </h1>
            <p style="text-align: center; color: #7f8c8d; font-size: 18px; margin-bottom: 30px;">
                Professional-grade Retrieval-Augmented Generation with full configurability
            </p>
        </div>
        """)
        
        # System Configuration toggle and popup
        with gr.Row():
            with gr.Column(scale=5):
                pass
            with gr.Column(scale=1):
                config_button = gr.Button("System Configuration", variant="secondary", size="sm", elem_id="config_toggle_btn_a3b")
        config_popup = gr.HTML(value="", visible=False)
        config_visible = gr.State(False)
        close_config_button = gr.Button("×", variant="secondary", size="sm", visible=False, elem_id="config_close_btn_a3b")

        gr.HTML("""
        <style>
        #config_popup_box { background: #ffffff; color: #222; }
        @media (prefers-color-scheme: dark) {
          #config_popup_box { background: #2b2b2b; color: #f2f2f2; border-color: rgba(255,255,255,0.25); box-shadow: 0 6px 18px rgba(0,0,0,0.6); }
        }
        #config_toggle_btn_a3b { width: auto !important; display: inline-block; }
        #config_toggle_btn_a3b button { font-size: 12px; padding: 2px 8px; min-height: 26px; width: auto !important; min-width: 0 !important; display: inline-flex; }
        #config_close_btn_a3b { position: fixed; top: 15px; right: 12px; z-index: 10000; width: auto !important; }
        #config_close_btn_a3b button { font-size: 14px; padding: 2px 8px; min-height: 26px; width: auto !important; min-width: 0 !important; display: inline-flex; }
        </style>
        """)
        
        # API Status Display
        api_status = gr.HTML(get_api_status_html())

        # Top output display and question row (align with rag_gui)
        response_output = gr.Textbox(label="", value="Welcome! Enter your question below to get AI-powered insights from your documents.", lines=8, max_lines=12, interactive=False, show_label=False, container=False)
        with gr.Row():
            query_input = gr.Textbox(label="", placeholder="Ask your question here...", lines=1, scale=4, show_label=False, container=False)
            submit_btn = gr.Button("Submit", variant="primary", size="lg", scale=1)

        # Database Initialization Section
        gr.Markdown("### 📁 Database Setup")
        with gr.Row():
            init_btn = gr.Button("🔄 Initialize Vector Database", variant="primary", scale=1)
            status_output = gr.Textbox(
                label="Initialization Status", 
                value="Click 'Initialize Vector Database' to get started...",
                interactive=False,
                scale=2
            )
        
        # Main layout with columns
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ RAG Configuration")
                
                # Model selection
                model_dropdown = gr.Dropdown(
                    choices=["gpt-4o", "gpt-4o-mini"],
                    value="gpt-4o-mini",
                    label="🤖 Language Model",
                    info="Choose your preferred model"
                )
                
                # Temperature control  
                temperature_slider = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    step=0.1,
                    value=0.1,
                    label="🌡️ Temperature",
                    info="Lower = more focused, Higher = more creative"
                )
                
                # Chunking parameters
                with gr.Row():
                    chunk_size_input = gr.Number(
                        value=512,
                        minimum=128,
                        maximum=2048,
                        step=64,
                        label="📄 Chunk Size",
                        info="Text chunk size for processing"
                    )
                    
                    chunk_overlap_input = gr.Number(
                        value=50,
                        minimum=0,
                        maximum=200,
                        step=10,
                        label="🔗 Chunk Overlap",
                        info="Overlap between chunks"
                    )
                
                # Retrieval parameters
                similarity_topk_slider = gr.Slider(
                    minimum=1,
                    maximum=20,
                    step=1,
                    value=5,
                    label="🎯 Similarity Top-K",
                    info="Number of similar documents to retrieve"
                )
                
                # Postprocessor selection
                postprocessor_checkbox = gr.CheckboxGroup(
                    choices=["SimilarityPostprocessor"],
                    value=[],
                    label="🔧 Node Postprocessors",
                    info="Additional result filtering"
                )
                
                # Similarity filtering
                similarity_cutoff_slider = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    step=0.1,
                    value=0.3,
                    label="✂️ Similarity Cutoff",
                    info="Minimum similarity score threshold"
                )
                
                # Response synthesizer
                synthesizer_dropdown = gr.Dropdown(
                    choices=["TreeSummarize", "Refine", "CompactAndRefine", "Default"],
                    value="Default",
                    label="🧠 Response Synthesizer",
                    info="How to combine retrieved information"
                )
            
            with gr.Column(scale=2):
                gr.Markdown("### 💬 Query Interface")
                
                # Query input
                query_input2 = gr.Textbox(
                    label="❓ Ask a question",
                    placeholder="Enter your question here... (e.g., 'What are AI agents and their capabilities?')",
                    lines=3
                )
                
                # Submit button
                submit_btn2 = gr.Button(
                    "🚀 Ask Question", 
                    variant="primary",
                    size="lg"
                )
                
                # Response output
                response_output2 = gr.Textbox(
                    label="🤖 AI Response",
                    lines=12,
                    interactive=False,
                    placeholder="AI response will appear here..."
                )
                
                # Configuration display
                config_display_hidden = gr.Textbox(visible=False,
                    label="📋 Current Configuration",
                    lines=8,
                    interactive=False,
                    placeholder="Configuration details will appear here..."
                )
        
        # Connect functions to components
        init_btn.click(
            initialize_db, 
            inputs=[chunk_size_input, chunk_overlap_input],
            outputs=[status_output]
        )
        
        submit_btn.click(
            handle_advanced_query,
            inputs=[
                query_input, model_dropdown, temperature_slider,
                chunk_size_input, chunk_overlap_input, similarity_topk_slider,
                postprocessor_checkbox, similarity_cutoff_slider, synthesizer_dropdown
            ],
            outputs=[response_output]
        )

        # Toggle System Configuration popup
        config_button.click(
            fn=toggle_config,
            inputs=[
                config_visible,
                model_dropdown,
                temperature_slider,
                chunk_size_input,
                chunk_overlap_input,
                similarity_topk_slider,
                similarity_cutoff_slider,
                postprocessor_checkbox,
                synthesizer_dropdown,
            ],
            outputs=[config_popup, config_visible, close_config_button]
        )
        close_config_button.click(
            fn=toggle_config,
            inputs=[
                config_visible,
                model_dropdown,
                temperature_slider,
                chunk_size_input,
                chunk_overlap_input,
                similarity_topk_slider,
                similarity_cutoff_slider,
                postprocessor_checkbox,
                synthesizer_dropdown,
            ],
            outputs=[config_popup, config_visible, close_config_button]
        )
    
    return interface


def launch_application():
    """Launch the advanced RAG application."""
    print("🎉 Launching your Advanced RAG Assistant...")
    print("🔗 Your application will open in a new browser tab!")
    print("")
    print("⚠️  Make sure your OPENROUTER_API_KEY environment variable is set!")
    print("")
    print("📋 Testing Instructions:")
    print("1. Click 'Initialize Vector Database' button first")
    print("2. Wait for success message")
    print("3. Configure your RAG parameters:")
    print("   - Choose model (gpt-4o, gpt-4o-mini)")
    print("   - Adjust temperature (0.0 = deterministic, 1.0 = creative)")
    print("   - Set chunk size and overlap")
    print("   - Choose similarity top-k")
    print("   - Select postprocessors and synthesizer")
    print("4. Enter a question and click 'Ask Question'")
    print("5. Review both the response and configuration used")
    print("")
    print("🧪 Experiments to try:")
    print("- Compare different models with the same question")
    print("- Test temperature effects (0.1 vs 0.9)")
    print("- Try different chunk sizes (256 vs 1024)")
    print("- Compare synthesizers (TreeSummarize vs Refine)")
    print("- Adjust similarity cutoff to filter results")
    print("")
    print("🚀 Starting application server...")
    print("=" * 60)
    
    try:
        advanced_interface.launch(
            server_name="127.0.0.1",
            server_port=7862,  # Different port from A3a.py (7860) and previous A3b (7861)
            share=False,
            show_error=True
        )
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        print("💡 Try closing other Gradio applications and retry")


# Initialize the backend
rag_backend = AdvancedRAGBackend()
print("🚀 Advanced RAG Backend initialized and ready!")

# UI function rewritten to mirror rag_gui
def create_advanced_rag_interface():
    import gradio as gr

    def build_config_html(model, temperature, chunk_size, overlap_size, top_k, similarity_threshold, postprocessor_enabled, synthesizer):
        post_text = "Enabled" if (postprocessor_enabled and len(postprocessor_enabled) > 0) else "Disabled"
        return f"""
        <div id='config_popup_box' style='position: fixed; top: 56px; right: 16px; width: 300px; max-width: 90vw; padding: 10px; border-radius: 8px; box-shadow: 0 6px 18px rgba(0,0,0,0.12); z-index: 9999;'>
            <div style='font-weight: 600; margin-bottom: 6px; font-size: 13px;'>System Configuration</div>
            <div style='font-size: 13px; line-height: 1.4;'>
                <div><strong>Model:</strong> {model}</div>
                <div><strong>Temperature:</strong> {temperature}</div>
                <div><strong>Chunk Size:</strong> {int(chunk_size)}</div>
                <div><strong>Overlap:</strong> {int(overlap_size)}</div>
                <div><strong>Top-K:</strong> {int(top_k)}</div>
                <div><strong>Similarity Threshold:</strong> {similarity_threshold}</div>
                <div><strong>Postprocessor:</strong> {post_text}</div>
                <div><strong>Synthesizer:</strong> {synthesizer}</div>
            </div>
        </div>
        """

    def toggle_config(is_visible, model, temperature, chunk_size, overlap_size, top_k, similarity_threshold, postprocessor_enabled, synthesizer):
        new_visible = not bool(is_visible)
        html = build_config_html(model, temperature, chunk_size, overlap_size, top_k, similarity_threshold, postprocessor_enabled, synthesizer)
        return gr.update(value=html, visible=new_visible), new_visible, gr.update(visible=new_visible)

    # Backend adapters (mirror legacy handlers but scoped to this UI)
    def initialize_db(chunk_size, chunk_overlap):
        return rag_backend.initialize_database(chunk_size=int(chunk_size), chunk_overlap=int(chunk_overlap))

    def handle_advanced_query(question, model, temperature, chunk_size, chunk_overlap,
                              similarity_top_k, use_postprocessor, similarity_cutoff, synthesizer):
        # Normalize postprocessor input from CheckboxGroup (list) or Checkbox (bool)
        enabled = False
        if isinstance(use_postprocessor, list):
            enabled = len(use_postprocessor) > 0
        else:
            enabled = bool(use_postprocessor)
        postprocessors = ["SimilarityPostprocessor"] if enabled else []

        result = rag_backend.advanced_query(
            question, model, float(temperature), int(chunk_size), int(chunk_overlap),
            int(similarity_top_k), postprocessors, float(similarity_cutoff), synthesizer
        )
        return result["response"]

    with gr.Blocks(title="Advanced RAG System - A3b") as interface:
        with gr.Row():
            with gr.Column(scale=5):
                gr.Markdown("# Advanced RAG System (Assignment 3B)")
            with gr.Column(scale=1):
                config_button = gr.Button("System Configuration", variant="secondary", size="sm", elem_id="config_toggle_btn_a3b")
        config_popup = gr.HTML(value="", visible=False)
        config_visible = gr.State(False)
        close_config_button = gr.Button("×", variant="secondary", size="sm", visible=False, elem_id="config_close_btn_a3b")

        gr.HTML("""
        <style>
        #panel_model, #panel_retrieval, #panel_advanced { border: 1px solid rgba(128,128,128,0.35); border-radius: 8px; padding: 12px; }
        /* Popup uses Gradio theme variables for background/text/border */
        #config_popup_box {
          background: var(--background-fill-primary, var(--color-background-primary, #ffffff));
          color: var(--body-text-color, var(--color-text, inherit));
          border: 1px solid var(--border-color-primary, rgba(128,128,128,0.35));
        }
        #config_toggle_btn_a3b { width: auto !important; display: inline-block; }
        #config_toggle_btn_a3b button { font-size: 12px; padding: 2px 8px; min-height: 26px; width: auto !important; min-width: 0 !important; display: inline-flex; }
        #config_close_btn_a3b { position: fixed; top: 15px; right: 12px; z-index: 10000; width: auto !important; }
        #config_close_btn_a3b button { font-size: 14px; padding: 2px 8px; min-height: 26px; width: auto !important; min-width: 0 !important; display: inline-flex; }
        </style>
        """)

        # Output and question
        response_output = gr.Textbox(label="", value="Welcome! Enter your question below to get AI-powered insights from your documents.", lines=8, max_lines=12, interactive=False, show_label=False, container=False)
        with gr.Row():
            query_input = gr.Textbox(label="", placeholder="Ask your question here...", lines=1, scale=4, show_label=False, container=False)
            submit_btn = gr.Button("Submit", variant="primary", size="lg", scale=1)

        # Data Chunking
        gr.Markdown("---")
        gr.Markdown("<h3 style='text-align:center; font-family: Georgia, \"Times New Roman\", serif; margin: 6px 0 11px 0;'>Data Chunking Configuration</h3>")
        gr.HTML("<div style='height:10px'></div>")
        with gr.Row():
            chunk_size_input = gr.Number(label="Chunk Size", value=512, minimum=128, maximum=2048, step=64)
            chunk_overlap_input = gr.Number(label="Overlap Size", value=50, minimum=0, maximum=200, step=10)
        with gr.Row():
            gr.Markdown("**Chunk Size:** Controls how large each text segment should be (128-2048 characters)")
            gr.Markdown("**Overlap:** Amount of text shared between consecutive chunks (0-200 characters)")

        # Database Setup
        gr.Markdown("---")
        gr.Markdown("<h3 style='text-align:center; font-family: Georgia, \"Times New Roman\", serif; margin: 6px 0 11px 0;'>Database Setup</h3>")
        gr.HTML("<div style='height:10px'></div>")
        with gr.Row():
            init_btn = gr.Button("Initialize Database", variant="primary", size="lg", scale=1)
        status_output = gr.Textbox(label="System Status", value="Click 'Initialize Database' to get started...", interactive=False, lines=2)

        # Advanced Configuration panels
        gr.Markdown("---")
        gr.Markdown("<h3 style='text-align:center; font-family: Georgia, \"Times New Roman\", serif; margin: 6px 0 11px 0;'>Advanced Configuration</h3>")
        gr.HTML("<div style='height:10px'></div>")
        with gr.Row():
            with gr.Column(scale=1, elem_id="panel_model"):
                gr.Markdown("### Model Settings")
                model_selection = gr.Textbox(label="AI Model", value="gpt-4o-mini", interactive=True, info="Current language model for response generation")
                temperature_slider = gr.Slider(label="Temperature", minimum=0.0, maximum=1.0, value=0.1, step=0.1, info="Lower = focused, Higher = creative")
                gr.Markdown("*gpt-4o-mini is faster and more cost-effective*")

            with gr.Column(scale=1, elem_id="panel_retrieval"):
                gr.Markdown("### Retrieval Settings")
                similarity_topk_slider = gr.Slider(label="Top-K Settings", minimum=1, maximum=20, value=5, step=1, info="Controls how many top-ranked results to retrieve from vector database")
                similarity_cutoff_slider = gr.Slider(label="Similarity Threshold", minimum=0.0, maximum=1.0, value=0.7, step=0.05, info="Minimum similarity score for result inclusion")

            with gr.Column(scale=1, elem_id="panel_advanced"):
                gr.Markdown("### Advanced Options")
                synthesizer_dropdown = gr.Dropdown(label="Response Synthesizer", choices=["TreeSummarize", "Refine", "CompactAndRefine", "Default"], value="Default", info="How to combine retrieved information")
                postprocessor_checkbox = gr.CheckboxGroup(choices=["SimilarityPostprocessor"], value=[], label="Enable Similarity Postprocessor", info="Enables/disables similarity-based result postprocessing")

        # Events
        submit_btn.click(
            handle_advanced_query,
            inputs=[
                query_input, model_selection, temperature_slider,
                chunk_size_input, chunk_overlap_input, similarity_topk_slider,
                postprocessor_checkbox, similarity_cutoff_slider, synthesizer_dropdown
            ],
            outputs=[response_output]
        )

        init_btn.click(
            initialize_db,
            inputs=[chunk_size_input, chunk_overlap_input],
            outputs=[status_output]
        )

        config_button.click(
            fn=toggle_config,
            inputs=[
                config_visible,
                model_selection,
                temperature_slider,
                chunk_size_input,
                chunk_overlap_input,
                similarity_topk_slider,
                similarity_cutoff_slider,
                postprocessor_checkbox,
                synthesizer_dropdown,
            ],
            outputs=[config_popup, config_visible, close_config_button]
        )
        close_config_button.click(
            fn=toggle_config,
            inputs=[
                config_visible,
                model_selection,
                temperature_slider,
                chunk_size_input,
                chunk_overlap_input,
                similarity_topk_slider,
                similarity_cutoff_slider,
                postprocessor_checkbox,
                synthesizer_dropdown,
            ],
            outputs=[config_popup, config_visible, close_config_button]
        )

        return interface

# Create the interface
advanced_interface = create_advanced_rag_interface()
print("✅ Advanced RAG interface created successfully!")

# Environment check and launch info
print("")
print("🎯 Assignment 3b: Advanced Gradio RAG Frontend")
print("=" * 50)
print("🔍 Environment Check:")
api_key = os.getenv("OPENROUTER_API_KEY")
if api_key and api_key.strip() != "your_openrouter_api_key_here":
    print("   OpenRouter API: ✅ Found")
else:
    print("   OpenRouter API: ⚠️  Not configured (retrieval-only mode)")

print(f"   Data Path: {os.getenv('DATA_PATH', '../../../../ai-accelerator-C2-main/ai-accelerator-C2-main/Day_6/session_2/data')}")
print(f"   Database Path: {os.getenv('ASSIGNMENT_3B_DB_PATH', './AssignmentDb/a3b_advanced_gradio_rag_vectordb')}")
print("")
print("🚀 Ready to launch Advanced RAG Assistant!")
print("   Run launch_application() to start the web interface")

# Auto-launch when script is run directly
if __name__ == "__main__":
    launch_application()
