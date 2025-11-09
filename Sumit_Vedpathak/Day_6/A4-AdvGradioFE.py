#region:Initializing the Libraries
# Import all required libraries
import gradio as gr
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

# LlamaIndex core components
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter

# Advanced RAG components
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import TreeSummarize, Refine, CompactAndRefine
from llama_index.core.retrievers import VectorIndexRetriever

from dotenv import load_dotenv
load_dotenv()

print("✅ All libraries imported successfully!")
#endregion

#region:Advanced RAG Backend Class
class AdvancedRAGBackend:
    """Advanced RAG backend with configurable parameters."""
    
    def __init__(self):
        self.index = None
        self.available_models = ["gpt-4o", "gpt-4o-mini"]
        self.available_postprocessors = ["SimilarityPostprocessor"]
        self.available_synthesizers = ["TreeSummarize", "Refine", "CompactAndRefine", "Default"]
        self.update_settings()
        
    def update_settings(self, model: str = "gpt-4o-mini", temperature: float = 0.1, chunk_size: int = 512, chunk_overlap: int = 50):
        """Update LlamaIndex settings based on user configuration."""
        # Set up the LLM using OpenRouter
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            Settings.llm = OpenRouter(
                api_key=api_key,
                model=model,
                temperature=temperature
            )
        
        # Set up the embedding model (keep this constant)
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            trust_remote_code=True
        )
        
        # Set chunking parameters from function parameters
        Settings.chunk_size = chunk_size
        Settings.chunk_overlap = chunk_overlap
    
    def initialize_database(self, data_folder="../data"):
        """Initialize the vector database with documents."""
        # Check if data folder exists
        if not Path(data_folder).exists():
            return f"❌ Data folder '{data_folder}' not found!"
        
        try:
            # Create vector store
            vector_store = LanceDBVectorStore(
                uri="./advanced_rag_vectordb",
                table_name="documents"
            )
            
            # Load documents
            reader = SimpleDirectoryReader(input_dir=data_folder, recursive=True)
            documents = reader.load_data()
            
            # Create storage context and index
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            self.index = VectorStoreIndex.from_documents(
                documents, 
                storage_context=storage_context,
                show_progress=True
            )
            
            return f"✅ Database initialized successfully with {len(documents)} documents!"
        
        except Exception as e:
            return f"❌ Error initializing database: {str(e)}"
    
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
                    "synthesizer": synthesizer_name
                }
            }
        
        except Exception as e:
            return {"response": f"❌ Error processing query: {str(e)}", "sources": [], "config": {}}

# Initialize the backend
rag_backend = AdvancedRAGBackend()
print("🚀 Advanced RAG Backend initialized and ready!")
#endregion

#region: Create advanced rag interface  
def create_advanced_rag_interface():
    """Create advanced RAG interface with full configuration options."""
    
    def initialize_db():
        """Handle database initialization."""
        return rag_backend.initialize_database("data")
    
    def handle_advanced_query(question, model, temperature, chunk_size, chunk_overlap, 
                             similarity_top_k, postprocessors, similarity_cutoff, synthesizer):
        """Handle advanced RAG queries with all configuration options."""
        result = rag_backend.advanced_query(
            question, model, temperature, chunk_size, chunk_overlap,
            similarity_top_k, postprocessors, similarity_cutoff, synthesizer
        )
        
        # Format configuration for display
        config_text = f"""**Current Configuration:**
        - Model: {result['config'].get('model', 'N/A')}
        - Temperature: {result['config'].get('temperature', 'N/A')}
        - Chunk Size: {result['config'].get('chunk_size', 'N/A')}
        - Chunk Overlap: {result['config'].get('chunk_overlap', 'N/A')}
        - Similarity Top-K: {result['config'].get('similarity_top_k', 'N/A')}
        - Postprocessors: {', '.join(result['config'].get('postprocessors', []))}
        - Similarity Cutoff: {result['config'].get('similarity_cutoff', 'N/A')}
        - Synthesizer: {result['config'].get('synthesizer', 'N/A')}"""
        
        return result["response"], config_text
    
    # TODO: Create the advanced interface structure
    # Hint: This interface needs more complex layout with configuration controls
    
    with gr.Blocks(title="Advanced RAG Assistant") as interface:
        # TODO: Add title and description
        # Hint: Use gr.Markdown() for formatted text
        gr.Markdown(
            """
            # 🤖 Advanced RAG Assistant
            This interface demonstrates a simple **Retrieval-Augmented Generation (RAG)** setup.
            Initialize the database first, then submit your queries.
            """
        )
        
        
        # TODO: Add database initialization section
        # Hint: Use gr.Button() for initialization and gr.Textbox() for status
        init_btn = gr.Button("Initialize Database")
        status_output = gr.Textbox(lines=1, interactive=False)
        init_btn.click(initialize_db, outputs=[status_output])
        
        
        
        # TODO: Create main layout with columns
        # Hint: Configuration controls on left, query/response on right makes sense
        # Use gr.Row() and gr.Column() to organize this
        
        with gr.Row():
            with gr.Column(scale=1):
                
                gr.Markdown("### ⚙️ RAG Configuration")
                
                # TODO: Model selection
                # Hint: Use gr.Dropdown() with choices=["gpt-4o", "gpt-4o-mini"]
                model_dropdown = gr.Dropdown(label="Model", choices=["gpt-4o", "gpt-4o-mini"], value="gpt-4o-mini")
                
                
                # TODO: Temperature control  
                # Hint: Use gr.Slider() with minimum=0.0, maximum=1.0, step=0.1, value=0.1
                temperature_slider = gr.Slider(label="Temperature", minimum=0.0, maximum=1.0, step=0.1, value=0.1)
                
                
                # TODO: Chunking parameters
                # Hint: Use gr.Number() for numeric inputs with default values
                chunk_size_input = gr.Number(label="Chunk Size", value=512)
                chunk_overlap_input = gr.Number(label="Chunk Overlap", value=50)
                
                
                # TODO: Retrieval parameters
                # Hint: Use gr.Slider() with minimum=1, maximum=20, step=1, value=5
                similarity_topk_slider = gr.Slider(label="Similarity Top-K", minimum=1, maximum=20, step=1, value=5)
                
                
                # TODO: Postprocessor selection
                # Hint: Use gr.CheckboxGroup() with choices=["SimilarityPostprocessor"]
                postprocessor_checkbox = gr.CheckboxGroup( label="Postprocessors", choices=["SimilarityPostprocessor"], value=["SimilarityPostprocessor"])
                
                
                # TODO: Similarity filtering
                # Hint: Use gr.Slider() with minimum=0.0, maximum=1.0, step=0.1, value=0.3
                similarity_cutoff_slider = gr.Slider(label="Similarity Cutoff", minimum=0.0, maximum=1.0, step=0.1, value=0.3)
                
                
                # TODO: Response synthesizer
                # Hint: Use gr.Dropdown() with choices=["TreeSummarize", "Refine", "CompactAndRefine", "Default"]
                synthesizer_dropdown = gr.Dropdown(label="Response Synthesizer", choices=["TreeSummarize", "Refine", "CompactAndRefine", "Default"], value="Default")
                
            
            with gr.Column(scale=2):
                gr.Markdown("### 💬 Query Interface")
                
                # TODO: Query input
                # Hint: Use gr.Textbox() with label="Ask a question", placeholder text, lines=3
                query_input = gr.Textbox(label="Ask a question", placeholder="Enter your question here", lines=3)
                
                
                # TODO: Submit button
                # Hint: Use gr.Button() with variant="primary"
                submit_btn = gr.Button("Submit")
                
                
                # TODO: Response output
                # Hint: Use gr.Textbox() with lines=12, interactive=False
                response_output = gr.Textbox(label="Response", lines=12, interactive=False)
                
                
                # TODO: Configuration display
                # Hint: Use gr.Textbox() with lines=8, interactive=False
                config_display = gr.Textbox(label="Configuration", lines=8, interactive=False)
        
        
        # Uncomment to Connect functions to components
        init_btn.click(initialize_db, outputs=[status_output])
        
        submit_btn.click(
            handle_advanced_query,
            inputs=[
                query_input, model_dropdown, temperature_slider,
                chunk_size_input, chunk_overlap_input, similarity_topk_slider,
                postprocessor_checkbox, similarity_cutoff_slider, synthesizer_dropdown
            ],
            outputs=[response_output, config_display]
        )
        
    
    return interface

# Create the interface
advanced_interface = create_advanced_rag_interface()
print("✅ Advanced RAG interface created successfully!")
advanced_interface.launch()
#endregion