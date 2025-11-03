# ============================================================
# COMPLETE CODE FOR ASSIGNMENT 3B - CELL 3
# Copy and paste this entire code into Cell 3 of your notebook
# ============================================================

def create_advanced_rag_interface():
    """Create advanced RAG interface with full configuration options."""
    
    def initialize_db():
        """Handle database initialization."""
        return rag_backend.initialize_database()
    
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
    
    # Create the advanced interface structure
    with gr.Blocks(title="Advanced RAG Assistant") as interface:
        # Add title and description
        gr.Markdown("# 🚀 Advanced RAG Assistant")
        gr.Markdown("Configure and query your RAG system with advanced parameters!")
        gr.Markdown("---")
        
        # Add database initialization section
        gr.Markdown("## 📁 Step 1: Initialize Database")
        init_btn = gr.Button("🚀 Initialize Vector Database", variant="primary")
        status_output = gr.Textbox(
            label="Initialization Status",
            placeholder="Click 'Initialize Vector Database' to begin...",
            interactive=False,
            lines=2
        )
        
        gr.Markdown("---")
        
        # Create main layout with columns
        gr.Markdown("## ⚙️ Configure & Query")
        with gr.Row():
            with gr.Column(scale=1):
                
                gr.Markdown("### ⚙️ RAG Configuration")
                
                # Model selection
                model_dropdown = gr.Dropdown(
                    choices=["gpt-4o", "gpt-4o-mini"],
                    value="gpt-4o-mini",
                    label="Model",
                    info="Choose the LLM model for responses"
                )
                
                # Temperature control
                temperature_slider = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    step=0.1,
                    value=0.1,
                    label="Temperature",
                    info="0.0 = deterministic, 1.0 = creative"
                )
                
                # Chunking parameters
                chunk_size_input = gr.Number(
                    value=512,
                    label="Chunk Size",
                    info="Size of document chunks (256-1024)",
                    minimum=256,
                    maximum=1024,
                    step=64
                )
                
                chunk_overlap_input = gr.Number(
                    value=50,
                    label="Chunk Overlap",
                    info="Overlap between chunks (10-200)",
                    minimum=10,
                    maximum=200,
                    step=10
                )
                
                # Retrieval parameters
                similarity_topk_slider = gr.Slider(
                    minimum=1,
                    maximum=20,
                    step=1,
                    value=5,
                    label="Similarity Top-K",
                    info="Number of documents to retrieve (1-20)"
                )
                
                # Postprocessor selection
                postprocessor_checkbox = gr.CheckboxGroup(
                    choices=["SimilarityPostprocessor"],
                    label="Node Postprocessors",
                    info="Filter and refine retrieval results"
                )
                
                # Similarity filtering
                similarity_cutoff_slider = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    step=0.05,
                    value=0.3,
                    label="Similarity Cutoff",
                    info="Minimum relevance score (0.0-1.0)"
                )
                
                # Response synthesizer
                synthesizer_dropdown = gr.Dropdown(
                    choices=["TreeSummarize", "Refine", "CompactAndRefine", "Default"],
                    value="Default",
                    label="Response Synthesizer",
                    info="How to combine retrieved information"
                )
            
            with gr.Column(scale=2):
                gr.Markdown("### 💬 Query Interface")
                
                # Query input
                query_input = gr.Textbox(
                    label="Ask a question",
                    placeholder="e.g., What are the main topics in the documents?",
                    lines=3
                )
                
                # Submit button
                submit_btn = gr.Button("🔍 Ask Question", variant="primary")
                
                # Response output
                response_output = gr.Textbox(
                    label="AI Response",
                    placeholder="Your response will appear here...",
                    interactive=False,
                    lines=12
                )
                
                # Configuration display
                config_display = gr.Textbox(
                    label="Configuration Used",
                    placeholder="Configuration details will appear here after query...",
                    interactive=False,
                    lines=8
                )
        
        # Connect functions to components
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

