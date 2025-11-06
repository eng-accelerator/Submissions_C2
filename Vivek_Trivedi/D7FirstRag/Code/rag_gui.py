import gradio as gr
import time

def create_rag_gui():
    """
    Create the complete RAG Application GUI based on GUI.excalidraw design
    Returns a Gradio interface with all 22 elements as specified in gui.readme.md
    """
    
    # Placeholder functions for backend functionality
    def process_question(question, chunk_size, overlap_size, top_k, similarity_threshold, 
                        enable_postprocessor, response_synthesizer, model_name):
        """Process user question through RAG pipeline"""
        if not question.strip():
            return "Please enter a question to get started."
        
        # Simulate processing
        time.sleep(1)
        response = f"""Based on the document analysis with the following settings:
- Model: {model_name}
- Chunk Size: {chunk_size}
- Overlap: {overlap_size}
- Top-K Results: {top_k}
- Similarity Threshold: {similarity_threshold}
- Postprocessor: {'Enabled' if enable_postprocessor else 'Disabled'}
- Synthesizer: {response_synthesizer}

Here are the key findings for your question: "{question}"

This is a simulated response. In the actual implementation, this would connect to your RAG backend to process the query through vector search and LLM generation."""
        
        return response
    
    def initialize_database():
        """Initialize the vector database"""
        time.sleep(2)
        return "Database initialized successfully! Ready to process documents."
    
    def check_database_status():
        """Check current database status"""
        return "Database: Ready | Documents: 150 | Last Updated: 2025-11-05 | Status: Operational"
    
    def update_status_display():
        """Update status display"""
        return "Database: Ready | Documents: 150 | Last Updated: 2025-11-05"

    def build_config_html(model, temperature, chunk_size, overlap_size, top_k, similarity_threshold, postprocessor_enabled, synthesizer):
        """Return small popup HTML with current configuration."""
        post_text = "Enabled" if postprocessor_enabled else "Disabled"
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
    
    # Professional CSS with excellent readability and modern design
    css = """
    /* Global styling without forcing theme colors */
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    /* Header styling */
    .header-text {
        text-align: left !important;
        font-size: 2.5em !important;
        font-weight: 700 !important;
        margin-bottom: 25px !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1) !important;
    }
    
    /* Section headers with professional styling - removed border to prevent double lines */
    .section-header {
        text-align: center !important;
        font-size: 1.4em !important;
        font-weight: 600 !important;
        margin: 5px 0 5px 0 !important;
        padding-bottom: 5px !important;
    }
    
    /* Custom panel separator */
    .panel-separator {
        margin: 20px 0 10px 0 !important;
    }
    
    /* Status display with professional look */
    .status-display {
        border-radius: 8px !important;
        padding: 18px !important;
        font-family: 'Consolas', 'Monaco', monospace !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    }
    
    /* SURGICAL PANEL STYLING - Target ONLY the container, not its children */
    .panel-container {
        border-radius: 12px !important;
        padding: 20px !important;
        margin: 8px 0 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
        transition: box-shadow 0.3s ease !important;
    }
    
    .panel-container:hover {
        box-shadow: 0 6px 20px rgba(0,0,0,0.12) !important;
    }
    

    
    /* Clean input field styling */
    .gr-textbox textarea, 
    .gr-textbox input {
        border: 2px solid #bdc3c7 !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 12px !important;
    }
    
    .gr-textbox textarea:focus, 
    .gr-textbox input:focus {
        border-color: #3498db !important;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2) !important;
    }
    
    /* Clean slider styling */
    
    .gr-slider .gr-slider-track {
        background-color: #ecf0f1 !important;
    }
    
    .gr-slider .gr-slider-thumb {
        background-color: #3498db !important;
        border: 2px solid #2980b9 !important;
    }
    
    /* Button styling */
    .gr-button {
        background-color: #3498db !important;
        color: #ffffff !important;
        border: 2px solid #2980b9 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
    }
    
    .gr-button:hover {
        background-color: #2980b9 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3) !important;
    }
    
    /* Dropdown styling */
    .gr-dropdown {
        background-color: #ffffff !important;
        color: #2b2b2b !important;
        border: 2px solid #bdc3c7 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    
    /* Checkbox styling */
    .gr-checkbox {
        color: #2b2b2b !important;
        font-weight: 600 !important;
    }
    
    /* Labels and text with excellent readability - Force override Gradio defaults */
    .gr-markdown, .gr-markdown p, .gr-markdown h1, .gr-markdown h2, .gr-markdown h3 {
        color: #2b2b2b !important;
        font-weight: 600 !important;
        line-height: 1.5 !important;
    }
    
    .gr-label, .gr-info, label {
        color: #b9231c !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* NUCLEAR FORM LABELS - RED COLOR #b9231c - PREVENT ALL GRADIO INTERFERENCE */
    .gradio-container label,
    .gradio-container .gr-label,
    .gradio-container .block-label,
    .gradio-container .label-wrap,
    .gradio-container [class*="label"]:not(.status-display *),
    .gradio-container [data-testid="block-info"]:not(.status-display *),
    .gr-textbox label,
    .gr-textbox .gr-label,
    .gr-slider label,
    .gr-slider .gr-label,
    .gr-dropdown label,
    .gr-dropdown .gr-label,
    .gr-checkbox label,
    .gr-checkbox .gr-label,
    .gr-number label,
    .gr-number .gr-label,
    .gradio-container * label:not(.status-display *),
    .gradio-container * .gr-label:not(.status-display *) {
        color: #b9231c !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        background: none !important;
        text-shadow: none !important;
        background-color: transparent !important;
    }
    
    /* Override any inline styles for form labels */
    .gradio-container [style*="color"]:not(.status-display *) label,
    .gradio-container label[style*="color"]:not(.status-display *),
    .gradio-container .gr-label[style*="color"]:not(.status-display *) {
        color: #b9231c !important;
    }
    
    /* Force red color with CSS variables for form labels */
    .gradio-container:not(.status-display) {
        --color-text-label: #b9231c !important;
        --text-color-primary: #b9231c !important;
    }
    
    /* NUCLEAR SYSTEM STATUS LABEL STYLING - PREVENT ALL GRADIO INTERFERENCE */
    .status-display label, 
    .status-display .gr-label,
    .status-display .block-label,
    .status-display .label-wrap,
    .status-display .wrap label,
    .status-display [data-testid="block-info"],
    div:has(.status-display) label,
    div:has(.status-display) .gr-label,
    div:has(.status-display) .block-label,
    .gradio-container .status-display label,
    .gradio-container .status-display .gr-label,
    .gradio-container .status-display .block-label,
    .gradio-container .status-display [class*="label"] {
        color: #353535 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        background: none !important;
        text-shadow: none !important;
        background-color: transparent !important;
    }
    
    /* Force System Status label color with maximum CSS specificity */
    .gradio-container * .status-display label,
    .gradio-container * .status-display .gr-label {
        color: #353535 !important;
    }
    
    /* Override any inline styles that Gradio might apply to System Status */
    .status-display [style*="color"],
    .status-display label[style*="color"],
    .status-display .gr-label[style*="color"] {
        color: #353535 !important;
    }
    
    /* Override Gradio's CSS variables globally */
    * {
        --body-text-color: #2b2b2b !important;
        --body-text-color-subdued: #2b2b2b !important;
        --color-text-label: #2b2b2b !important;
    }
    
    /* Element identifier styling */
    .element-identifier {
        font-size: 12px !important;
        color: #666666 !important;
        font-weight: 500 !important;
        margin: 5px 0 !important;
        text-align: left !important;
    }
    
    .gr-info {
        color: #5d6d7e !important;
        font-style: italic !important;
        font-weight: 500 !important;
    }
    
    /* Accordion styling */
    .gr-accordion {
        border: 2px solid #e9ecef !important;
        border-radius: 12px !important;
        background-color: #f8f9fa !important;
    }
    
    .gr-accordion-header {
        background-color: #ecf0f1 !important;
        color: #2b2b2b !important;
        font-weight: 600 !important;
        border-bottom: 1px solid #bdc3c7 !important;
    }
    
    /* FINAL NUCLEAR OVERRIDE - Disable ALL Gradio CSS functions on System Status */
    .gradio-container .status-display {
        --color-text-label: #353535 !important;
        --body-text-color: #353535 !important;
        --text-color-primary: #353535 !important;
    }
    
    /* Kill all Gradio theme application on System Status completely */
    .gradio-container .status-display .theme {
        display: none !important;
    }
    
    /* Force color inheritance for System Status to prevent any Gradio overrides */
    .gradio-container .status-display * {
        color: #353535 !important;
    }
    
    /* Override ALL possible Gradio label classes for System Status */
    .gradio-container [class*="status-display"] label,
    .gradio-container [class*="status-display"] .gr-label,
    .gradio-container [class*="status-display"] [class*="label"] {
        color: #353535 !important;
        background: transparent !important;
    }
    

    
    /* ULTIMATE FORM LABEL OVERRIDE - NUCLEAR APPROACH */
    .gradio-container label:not(.status-display label):not(.status-display .gr-label),
    .gradio-container .gr-label:not(.status-display label):not(.status-display .gr-label),
    .gradio-container .block-label:not(.status-display label):not(.status-display .gr-label) {
        color: #b9231c !important;
    }
    
    /* Kill all Gradio theme application on form labels completely */
    .gradio-container:not(.status-display) .theme label {
        color: #b9231c !important;
    }
    
    /* Force color inheritance for all labels to prevent any Gradio overrides */
    .gradio-container *:not(.status-display) label,
    .gradio-container *:not(.status-display) .gr-label {
        color: #b9231c !important;
    }
    
    /* FULL WIDTH ELEMENTS - Remove container divs and expand to parent size */
    .full-width-element,
    .full-width-element .gr-textbox,
    .full-width-element textarea,
    .full-width-element input {
        width: 100% !important;
        height: 100% !important;
        box-sizing: border-box !important;
    }
    
    /* Remove any wrapper padding/margin for full-width elements */
    .gradio-container .full-width-element {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Ensure output display takes full available space */
    .status-display.full-width-element {
        min-height: 200px !important;
        width: 100% !important;
    }
    

    """
    
    with gr.Blocks(title="RAG Document Assistant") as interface:
        
        # 1. Website Header
        with gr.Row():
            with gr.Column(scale=5):
                gr.Markdown("# RAG Document Assistant v1.0")
            with gr.Column(scale=1):
                config_button = gr.Button("System Configuration", variant="secondary", size="sm", elem_id="config_toggle_btn")
        # Hidden popup and visibility state
        config_popup = gr.HTML(value="", visible=False)
        config_visible = gr.State(False)
        # Fixed-position close button that sits above the popup
        close_config_button = gr.Button("×", variant="secondary", size="sm", visible=False, elem_id="config_close_btn")
        # Scoped CSS for light borders on Advanced Configuration panels
        gr.HTML("""
        <style>
        #panel_model, #panel_retrieval, #panel_advanced {
            border: 1px solid rgba(128,128,128,0.35);
            border-radius: 8px;
            padding: 12px;
            pointer-events: auto;
            cursor: auto;
        }
        /* Theme-aware popup colors */
        #config_popup_box { background: #ffffff; color: #222; }
        @media (prefers-color-scheme: dark) {
          #config_popup_box { background: #2b2b2b; color: #f2f2f2; border-color: rgba(255,255,255,0.25); box-shadow: 0 6px 18px rgba(0,0,0,0.6); }
        }
        /* Tiny header toggle button */
        #config_toggle_btn { width: auto !important; display: inline-block; }
        #config_toggle_btn button { font-size: 12px; padding: 2px 8px; min-height: 26px; width: auto !important; min-width: 0 !important; display: inline-flex; }
        /* Fixed small close button above the popup */
        #config_close_btn { position: fixed; top: 15px; right: 12px; z-index: 10000; width: auto !important; }
        #config_close_btn button { font-size: 14px; padding: 2px 8px; min-height: 26px; width: auto !important; min-width: 0 !important; display: inline-flex; }
        </style>
        """)
        

        
        # 2. Output Display Area
        output_display = gr.Textbox(
            label="",
            value="Welcome! Enter your question below to get AI-powered insights from your documents.",
            lines=8,
            max_lines=12,
            interactive=False,
            show_label=False,
            container=False
        )
        
        # Question Input Section - No wrapper div
        with gr.Row():
            # 3. Question Input Field
            question_input = gr.Textbox(
                label="",
                placeholder="Ask your question here...",
                lines=1,
                scale=4,
                show_label=False,
                container=False
            )
            
            # 4. Answer Button
            answer_button = gr.Button(
                "Submit",
                variant="primary",
                scale=1,
                size="lg"
            )
        
        # Add separator line before Data Chunking Configuration section
        gr.Markdown("---")
        
        # 5. Data Chunking Section Header
        gr.Markdown("<h3 style='text-align:center; font-family: Georgia, \"Times New Roman\", serif; margin: 6px 0 11px 0;'>Data Chunking Configuration</h3>")
        # Small spacer under header for breathing room
        gr.HTML("<div style='height:10px'></div>")

        with gr.Row():
            # 6. Size Input Field (NumericUpDown)
            chunk_size = gr.Number(
                label="Chunk Size",
                value=512,
                minimum=50,
                maximum=2000,
                step=50,
                scale=1,
                interactive=True
            )
            
            # 7. OverLap Input Field (NumericUpDown)  
            overlap_size = gr.Number(
                label="Overlap Size", 
                value=50,
                minimum=0,
                maximum=500,
                step=10,
                scale=1,
                interactive=True
            )
        
        # Add explanatory text for chunking
        with gr.Row():
            gr.Markdown("**Chunk Size:** Controls how large each text segment should be (50-2000 characters)")
            gr.Markdown("**Overlap:** Amount of text shared between consecutive chunks (0-500 characters)")
        
        # Add separator line before Database Setup section
        gr.Markdown("---")
        
        # 8. Database Setup Section Header
        gr.Markdown("<h3 style='text-align:center; font-family: Georgia, \"Times New Roman\", serif; margin: 6px 0 11px 0;'>Database Setup</h3>")
        # Small spacer under header for breathing room
        gr.HTML("<div style='height:10px'></div>")

        with gr.Row():
            # 9. Initialize Database Button (single CTA)
            init_db_button = gr.Button(
                "Initialize Database",
                variant="primary",
                size="lg",
                scale=1
            )
        
        # 11. Status Display (StatusBar)
        status_display = gr.Textbox(
            label="System Status",
            value="Database: Ready | Documents: 150 | Last Updated: 2025-11-05",
            interactive=False,
            lines=2,
            
        )
        
        # Add separator line before Advanced Configuration section
        gr.Markdown("---")
        
        # 12. Advanced Configuration Section Header
        gr.Markdown("<h3 style='text-align:center; font-family: Georgia, \"Times New Roman\", serif; margin: 6px 0 11px 0;'>Advanced Configuration</h3>")
        # Small spacer under header for breathing room
        gr.HTML("<div style='height:10px'></div>")

        with gr.Row():
            # 13. Model Settings Panel
            with gr.Column(scale=1, elem_id="panel_model"):
                gr.Markdown("### Model Settings")
                
                # 15. Model Selection (gpt-4o-mini)
                model_selection = gr.Textbox(
                    label="AI Model",
                    value="gpt-4o-mini",
                    interactive=True,
                    info="Current language model for response generation"
                )
                
                # Temperature slider (generation control)
                temperature_slider = gr.Slider(
                    label="Temperature",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.1,
                    step=0.1,
                    info="Lower = focused, Higher = creative",
                    interactive=True
                )
                
                gr.Markdown("*gpt-4o-mini is faster and more cost-effective*")
            
            # 14. Retrieval Settings Panel  
            with gr.Column(scale=1, elem_id="panel_retrieval"):
                gr.Markdown("### Retrieval Settings")
                
                # 16. Top-K Settings
                top_k_settings = gr.Slider(
                    label="Top-K Settings",
                    minimum=1,
                    maximum=20,
                    value=5,
                    step=1,
                    info="Controls how many top-ranked results to retrieve from vector database",
                    interactive=True
                )
                
                # 19. Similarity Threshold Slider
                similarity_threshold_slider = gr.Slider(
                    label="Similarity Threshold",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.7,
                    step=0.05,
                    info="Minimum similarity score for result inclusion",
                    interactive=True
                )
            
            # 17. Advanced Options Panel
            with gr.Column(scale=1, elem_id="panel_advanced"):
                gr.Markdown("### Advanced Options")
                
                # 20. Response Synthesizer Dropdown
                response_synthesizer = gr.Dropdown(
                    label="Response Synthesizer",
                    choices=["Compact", "Refine", "Tree Summarize", "Simple Concatenate"],
                    value="Compact",
                    info="Controls how multiple retrieved chunks are combined for response"
                )
                
                # 18. Postprocessor Configuration & 21. Enable Similarity Postprocessor Label
                enable_similarity_postprocessor = gr.Checkbox(
                    label="Enable Similarity Postprocessor",
                    value=False,
                    info="Enables/disables similarity-based result postprocessing"
                )
        
        # Event Handlers
        
        # Answer button click handler
        answer_button.click(
            fn=process_question,
            inputs=[
                question_input, 
                chunk_size, 
                overlap_size, 
                top_k_settings, 
                similarity_threshold_slider,
                enable_similarity_postprocessor,
                response_synthesizer,
                model_selection
            ],
            outputs=output_display
        )
        
        # Initialize database button handler
        init_db_button.click(
            fn=initialize_database,
            outputs=status_display
        )
        
        # (Removed Check Status button and handler)
        
        # Enter key handler for question input
        question_input.submit(
            fn=process_question,
            inputs=[
                question_input,
                chunk_size,
                overlap_size, 
                top_k_settings,
                similarity_threshold_slider,
                enable_similarity_postprocessor,
                response_synthesizer,
                model_selection
            ],
            outputs=output_display
        )

        # Toggle configuration popup (show/hide and refresh content)
        config_button.click(
            fn=toggle_config,
            inputs=[
                config_visible,
                model_selection,
                temperature_slider,
                chunk_size,
                overlap_size,
                top_k_settings,
                similarity_threshold_slider,
                enable_similarity_postprocessor,
                response_synthesizer,
            ],
            outputs=[config_popup, config_visible, close_config_button]
        )
        # Close button toggles same state
        close_config_button.click(
            fn=toggle_config,
            inputs=[
                config_visible,
                model_selection,
                temperature_slider,
                chunk_size,
                overlap_size,
                top_k_settings,
                similarity_threshold_slider,
                enable_similarity_postprocessor,
                response_synthesizer,
            ],
            outputs=[config_popup, config_visible, close_config_button]
        )
        
        # Validation handlers for numeric inputs
        def validate_chunk_overlap(chunk_val, overlap_val):
            if overlap_val >= chunk_val:
                return gr.update(value=min(overlap_val, chunk_val - 1))
            return gr.update()
        
        chunk_size.change(
            fn=validate_chunk_overlap,
            inputs=[chunk_size, overlap_size],
            outputs=overlap_size
        )
    
    return interface

# Function to launch the GUI (for testing purposes)
def launch_gui():
    """Launch the RAG GUI for testing"""
    interface = create_rag_gui()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )

if __name__ == "__main__":
    launch_gui()
