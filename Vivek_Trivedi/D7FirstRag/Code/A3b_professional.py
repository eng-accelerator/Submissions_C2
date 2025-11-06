"""
Assignment 3B: Advanced RAG System with Professional Gradio Interface
Professional-grade Retrieval-Augmented Generation with step-by-step UI design

This implementation provides:
- Step-by-step professional interface design
- Comprehensive configuration options
- Real-time status updates
- Clear separation of UI and business logic
- Advanced RAG features with full customization
"""

import os
import sys
import gradio as gr
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import A2 functions
from A2 import (setup_advanced_rag_settings, setup_basic_index, 
                create_query_engine_with_similarity_filter,
                create_query_engine_with_tree_summarize,
                create_advanced_rag_pipeline)


class AdvancedRAGBackend:
    """Backend handler for Advanced RAG operations with configuration management."""
    
    def __init__(self):
        """Initialize the advanced RAG backend."""
        self.index = None
        self.current_config = {}
        self.db_path = "./AssignmentDb/a3b_advanced_gradio_rag_vectordb"
        self.initial_chunk_size = 512
        self.initial_chunk_overlap = 50
        
    def initialize_database(self, chunk_size: int = 512, chunk_overlap: int = 50) -> str:
        """Initialize the vector database with specified chunking parameters."""
        try:
            print(f"🔄 Initializing Advanced RAG System...")
            print(f"📄 Chunk size: {chunk_size}, Overlap: {chunk_overlap}")
            
            # Setup advanced RAG settings first
            setup_advanced_rag_settings()
            
            # Create database directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Setup the index using A2 function
            self.index = setup_basic_index(data_folder="../data", force_rebuild=False)
            
            # Store current configuration
            self.current_config = {
                'chunk_size': chunk_size,
                'chunk_overlap': chunk_overlap,
                'database_path': self.db_path
            }
            
            success_msg = f"""✅ Advanced RAG System Initialized Successfully!

📊 Database Statistics:
   • Vector database path: {self.db_path}
   • Chunk configuration: {chunk_size} chars with {chunk_overlap} overlap
   • Index successfully created and loaded

🎯 Configuration Applied:
   • Chunk Size: {chunk_size} characters
   • Chunk Overlap: {chunk_overlap} characters
   • Vector Database: LanceDB with BGE embeddings
   • Advanced RAG components ready

🚀 System Status: Ready for advanced queries!
You can now configure query parameters and start asking questions."""
            
            print("✅ Advanced RAG initialization completed!")
            return success_msg
            
        except Exception as e:
            error_msg = f"""❌ Initialization Failed!

🚨 Error Details: {str(e)}

🔧 Troubleshooting Steps:
1. Check if all required packages are installed
2. Verify API key configuration
3. Ensure data directory exists at ../data
4. Try with different chunk size settings

💡 Tip: Make sure the data folder contains documents to process."""
            
            print(f"❌ Error during initialization: {e}")
            return error_msg

    def advanced_query(self, question: str, model: str, temperature: float,
                      chunk_size: int, chunk_overlap: int, similarity_top_k: int,
                      postprocessors: List[str], similarity_cutoff: float,
                      synthesizer: str) -> Dict[str, Any]:
        """Execute advanced RAG query with full configuration options."""
        try:
            # Check if system needs reinitialization
            if (self.index is None or 
                self.current_config.get('chunk_size') != chunk_size or
                self.current_config.get('chunk_overlap') != chunk_overlap):
                
                reinit_msg = self.initialize_database(chunk_size, chunk_overlap)
                if "Failed" in reinit_msg:
                    return {"response": f"❌ System reinitialization failed:\n{reinit_msg}"}
            
            # Select query engine based on configuration
            if synthesizer == "TreeSummarize":
                query_engine = create_query_engine_with_tree_summarize(self.index, top_k=similarity_top_k)
            elif postprocessors and "SimilarityPostprocessor" in postprocessors:
                query_engine = create_query_engine_with_similarity_filter(
                    self.index, similarity_cutoff=similarity_cutoff, top_k=similarity_top_k
                )
            else:
                # Use advanced pipeline that combines everything
                query_engine = create_advanced_rag_pipeline(
                    self.index, similarity_cutoff=similarity_cutoff, top_k=similarity_top_k
                )
            
            print(f"🔍 Processing query with synthesizer: {synthesizer}")
            
            # Execute the query
            response = query_engine.query(question)
            
            return {
                "response": str(response),
                "configuration": {
                    'model': model,
                    'temperature': temperature,
                    'similarity_top_k': similarity_top_k,
                    'postprocessors': postprocessors,
                    'similarity_cutoff': similarity_cutoff,
                    'synthesizer': synthesizer
                },
                "status": "success"
            }
            
        except Exception as e:
            error_response = f"""❌ Query Processing Failed

🚨 Error: {str(e)}

🔧 Possible Solutions:
1. Verify the database is properly initialized
2. Check if the question is not empty
3. Ensure valid configuration parameters
4. Try reinitializing the database

💡 Current Configuration:
   • Model: {model}
   • Temperature: {temperature}
   • Top-K: {similarity_top_k}
   • Synthesizer: {synthesizer}"""
            
            return {
                "response": error_response,
                "configuration": {},
                "status": "error"
            }


def get_api_status_html() -> str:
    """Generate HTML for API status display."""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if api_key:
        return """
        <div class="api-status-good">
            ✅ OpenRouter API Key Detected & Configured
            <br>Ready for GPT-4o and GPT-4o-mini model access
        </div>
        """
    else:
        return """
        <div class="api-status-error">
            ❌ OpenRouter API Key Not Found!
            <br>Please set OPENROUTER_API_KEY environment variable
            <br>System will operate in limited mode
        </div>
        """


def create_professional_rag_interface():
    """Create the professional step-by-step RAG interface."""
    
    # Initialize backend
    rag_backend = AdvancedRAGBackend()
    
    # Professional CSS Styling
    css = """
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
    }
    .step-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        margin: 30px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
    }
    .step-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffeaa7);
        background-size: 300% 300%;
        animation: gradient-shift 3s ease infinite;
    }
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .step-title {
        color: white;
        font-size: 28px;
        font-weight: bold;
        margin: 0 0 12px 0;
        text-shadow: 0 3px 6px rgba(0,0,0,0.4);
        text-align: center;
        letter-spacing: 0.5px;
    }
    .step-description {
        color: #e8f4fd;
        font-size: 17px;
        margin: 0;
        opacity: 0.95;
        text-align: center;
        line-height: 1.5;
        text-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 20px;
        font-weight: bold;
        margin: 20px 0 15px 0;
        padding: 15px 20px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .section-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    .section-header:hover::before {
        left: 100%;
    }
    .section-header:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    .status-message {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 18px 25px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 18px 0;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0 4px 15px rgba(86, 171, 47, 0.3);
        border: 1px solid rgba(255,255,255,0.2);
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .status-message:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(86, 171, 47, 0.4);
    }
    .api-status-good {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 25px 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 25px 0;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 5px 20px rgba(79, 172, 254, 0.3);
        border: 1px solid rgba(255,255,255,0.2);
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    .api-status-good::before {
        content: '✨';
        position: absolute;
        top: 10px;
        right: 20px;
        font-size: 24px;
        opacity: 0.7;
        animation: twinkle 2s ease-in-out infinite alternate;
    }
    .api-status-error {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 25px 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 25px 0;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 5px 20px rgba(250, 112, 154, 0.3);
        border: 1px solid rgba(255,255,255,0.2);
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    .api-status-error::before {
        content: '⚠️';
        position: absolute;
        top: 10px;
        right: 20px;
        font-size: 24px;
        opacity: 0.8;
        animation: pulse-warning 1.5s ease-in-out infinite;
    }
    @keyframes twinkle {
        0% { opacity: 0.5; transform: scale(1); }
        100% { opacity: 1; transform: scale(1.1); }
    }
    @keyframes pulse-warning {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    """
    
    # Backend Interface Functions
    def initialize_db(chunk_size, chunk_overlap):
        """Handle database initialization with chunk configuration."""
        return rag_backend.initialize_database(chunk_size=int(chunk_size), chunk_overlap=int(chunk_overlap))
    
    def check_database_status():
        """Check current database status."""
        try:
            db_path = "./AssignmentDb/a3b_advanced_gradio_rag_vectordb"
            if os.path.exists(db_path):
                files = os.listdir(db_path)
                return f"✅ Database found at: {db_path}\n📊 Database contains: {len(files)} files\n🔄 Status: Ready for queries"
            else:
                return f"❌ No database found at: {db_path}\n🚨 Action needed: Click 'Initialize Vector Database' to create the knowledge base"
        except Exception as e:
            return f"⚠️ Error checking database: {str(e)}"
    
    def handle_advanced_query(question, model, temperature, chunk_size, chunk_overlap, 
                             similarity_top_k, use_postprocessor, similarity_cutoff, synthesizer):
        """Handle advanced RAG queries with comprehensive validation and guidance."""
        
        # Validate inputs first
        errors, warnings = validate_inputs(chunk_size, chunk_overlap, similarity_top_k, similarity_cutoff, temperature)
        
        if errors:
            error_msg = "❌ **Cannot process query due to invalid parameters:**\n\n"
            for i, error in enumerate(errors, 1):
                error_msg += f"{i}. {error}\n"
            error_msg += "\n**Please fix these issues in STEP 2 before submitting your query.**"
            
            config_text = f"""❌ Invalid Configuration Detected:
🤖 Model: {model} (Temperature: {temperature})
📄 Chunking: Size={chunk_size}, Overlap={chunk_overlap}
🎯 Retrieval: Top-K={similarity_top_k}, Cutoff={similarity_cutoff}
🔧 Postprocessor: {'✅ Enabled' if use_postprocessor else '❌ Disabled'}
🧠 Synthesizer: {synthesizer}

⚠️ Errors found - please fix parameters above."""
            
            return error_msg, config_text
        
        # Check if database needs reinitialization
        needs_reinit = (chunk_size != rag_backend.initial_chunk_size or 
                       chunk_overlap != rag_backend.initial_chunk_overlap)
        
        if needs_reinit and (not hasattr(rag_backend, 'current_config') or 
                            rag_backend.current_config.get('chunk_size') != chunk_size or
                            rag_backend.current_config.get('chunk_overlap') != chunk_overlap):
            
            reinit_msg = f"""⚠️ **Database Reinitialization Required**

Your chunking parameters have changed:
• **Current Database:** Chunk Size = {rag_backend.initial_chunk_size}, Overlap = {rag_backend.initial_chunk_overlap}  
• **Your Settings:** Chunk Size = {chunk_size}, Overlap = {chunk_overlap}

**Action Required:** Go back to STEP 1 and click "🔄 Initialize Vector Database" to apply your new chunking settings.

💡 **Why is this needed?** 
The vector database was created with specific chunk sizes. Changing these parameters requires rebuilding the database with the new chunking strategy for optimal results."""
            
            config_text = f"""⚠️ Configuration Mismatch - Reinitialization Needed:
🤖 Model: {model} (Temperature: {temperature})
📄 Chunking: Size={chunk_size}, Overlap={chunk_overlap} ← **Changed from defaults**
🎯 Retrieval: Top-K={similarity_top_k}, Cutoff={similarity_cutoff}
🔧 Postprocessor: {'✅ Enabled' if use_postprocessor else '❌ Disabled'}
🧠 Synthesizer: {synthesizer}

🔄 Please reinitialize database with new chunk settings."""
            
            return reinit_msg, config_text
        
        # Process the query
        if not question.strip():
            return "❌ Please enter a question to get started!", "❌ No question provided"
        
        # Convert postprocessor to expected format
        postprocessors = ["SimilarityPostprocessor"] if use_postprocessor else []
        
        try:
            result = rag_backend.advanced_query(
                question, model, temperature, int(chunk_size), int(chunk_overlap),
                int(similarity_top_k), postprocessors, similarity_cutoff, synthesizer
            )
            
            # Format success configuration display
            config_text = f"""✅ Successfully Processed Query:
🤖 Model: {model} (Temperature: {temperature})
📄 Chunking: Size={chunk_size}, Overlap={chunk_overlap}
🎯 Retrieval: Top-K={similarity_top_k}, Cutoff={similarity_cutoff}
🔧 Postprocessor: {'✅ Enabled' if use_postprocessor else '❌ Disabled'}
🧠 Synthesizer: {synthesizer}

📊 Query processed successfully with above configuration."""
            
            if warnings:
                config_text += f"\n\n⚠️ Recommendations for better results:\n"
                for warning in warnings:
                    config_text += f"• {warning}\n"
            
            return result["response"], config_text
            
        except Exception as e:
            error_response = f"""❌ **Query Processing Failed**

**Error:** {str(e)}

**Troubleshooting Steps:**
1. **Check Database:** Make sure you've initialized the database in STEP 1
2. **Verify Settings:** Ensure all parameters in STEP 2 are valid
3. **Try Simple Query:** Start with a basic question like "What are AI agents?"
4. **Reinitialize:** If issues persist, reinitialize the database

**Current Configuration:**
• Model: {model} (Temperature: {temperature})
• Chunking: Size={chunk_size}, Overlap={chunk_overlap}
• Retrieval: Top-K={similarity_top_k}, Cutoff={similarity_cutoff}"""
            
            config_text = f"""❌ Query Failed:
🤖 Model: {model} (Temperature: {temperature})  
📄 Chunking: Size={chunk_size}, Overlap={chunk_overlap}
🎯 Retrieval: Top-K={similarity_top_k}, Cutoff={similarity_cutoff}
🔧 Postprocessor: {'✅ Enabled' if use_postprocessor else '❌ Disabled'}
🧠 Synthesizer: {synthesizer}

❌ Error: {str(e)[:100]}..."""
            
            return error_response, config_text
    
    def get_chunking_guidance(chunk_size, chunk_overlap):
        """Generate real-time chunking parameter guidance with prominent warnings."""
        needs_reinit = chunk_size != 512 or chunk_overlap != 50
        
        # Check for critical validation issues
        if chunk_overlap >= chunk_size:
            return f"""
            <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); padding: 20px; border-radius: 10px; color: white; text-align: center; margin: 15px 0; font-weight: bold; border: 3px solid #c44569;">
                🚨 CRITICAL ERROR: Overlap ({chunk_overlap}) must be LESS than Chunk Size ({chunk_size})<br>
                <span style="font-size: 14px;">Fix this immediately - the system cannot work with these settings!</span>
            </div>
            """
        elif chunk_size < 64:
            return f"""
            <div style="background: linear-gradient(135deg, #ff9ff3 0%, #f368e0 100%); padding: 20px; border-radius: 10px; color: white; text-align: center; margin: 15px 0; font-weight: bold; border: 3px solid #e056fd;">
                ⚠️ VERY SMALL CHUNK SIZE: {chunk_size} characters<br>
                <span style="font-size: 14px;">This may cause poor results. Recommended minimum: 128 characters</span><br>
                <strong style="font-size: 16px; text-decoration: underline;">CLICK "INITIALIZE" TO APPLY CHANGES</strong>
            </div>
            """
        elif needs_reinit:
            return f"""
            <div style="background: linear-gradient(135deg, #ffa726 0%, #ff7043 100%); padding: 20px; border-radius: 10px; color: white; text-align: center; margin: 15px 0; font-weight: bold; border: 3px solid #ff8a50; animation: pulse 2s infinite;">
                🔄 DATABASE REINITIALIZATION REQUIRED!<br>
                <span style="font-size: 16px;">Chunk Size: {chunk_size} | Overlap: {chunk_overlap}</span><br>
                <strong style="font-size: 18px; text-decoration: underline; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                ➡️ CLICK "INITIALIZE VECTOR DATABASE" NOW ⬅️
                </strong><br>
                <span style="font-size: 14px; opacity: 0.9;">Changes won't take effect until you reinitialize!</span>
            </div>
            <style>
            @keyframes pulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(255, 138, 80, 0.7); }}
                70% {{ box-shadow: 0 0 0 10px rgba(255, 138, 80, 0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(255, 138, 80, 0); }}
            }}
            </style>
            """
        else:
            return f"""
            <div class="status-message">
                ✅ Default chunking settings: {chunk_size} characters with {chunk_overlap} overlap. Ready to initialize!
            </div>
            """
    
    def get_config_summary(model, temp, chunk_size, chunk_overlap, top_k, postprocessor, cutoff, synth):
        """Generate live configuration summary."""
        return f"""
        <div class="status-message">
            ✅ Query Configuration: {model} @ {temp}°C | Top-K: {top_k} | Cutoff: {cutoff:.1f} | Synthesizer: {synth}
        </div>
        """
    
    def validate_inputs(chunk_size, chunk_overlap, top_k, cutoff, temp):
        """Validate user inputs and provide helpful guidance."""
        errors = []
        warnings = []
        
        # Validate chunk_size - be more flexible, only warn don't error
        if chunk_size < 1:
            errors.append("Chunk Size must be at least 1 character")
        elif chunk_size > 2048:
            errors.append("Chunk Size should not exceed 2048 characters to avoid memory issues")
        elif chunk_size < 64:
            warnings.append(f"Very small chunk size ({chunk_size} chars) may cause poor results. Consider 128+ for better performance")
        elif chunk_size < 256:
            warnings.append("Small chunk sizes (< 256) may result in fragmented context")
            
        # Validate chunk_overlap
        if chunk_overlap < 0:
            errors.append("Chunk Overlap cannot be negative")
        elif chunk_overlap >= chunk_size:
            errors.append(f"Chunk Overlap ({chunk_overlap}) must be less than Chunk Size ({chunk_size})")
        elif chunk_overlap > chunk_size * 0.5:
            warnings.append("Large overlap (>50% of chunk size) may cause redundancy")
            
        # Validate other parameters
        if top_k < 1:
            errors.append("Top-K must be at least 1 to retrieve documents")
        elif top_k > 15:
            warnings.append("High Top-K values (>15) may include irrelevant results")
            
        if cutoff < 0.1:
            warnings.append("Very low similarity cutoff may include irrelevant results")
        elif cutoff > 0.9:
            warnings.append("Very high similarity cutoff may exclude relevant results")
            
        if temp > 0.8:
            warnings.append("High temperature (>0.8) may produce inconsistent responses")
        
        return errors, warnings
    
    def get_validation_message(errors, warnings):
        """Generate validation feedback message."""
        if errors:
            error_list = "<br>• ".join(errors)
            return f"""
            <div class="status-warning">
                ❌ Please Fix These Issues:<br>• {error_list}
            </div>
            """
        elif warnings:
            warning_list = "<br>• ".join(warnings)
            return f"""
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 15px 0; color: #856404;">
                ⚠️ Recommendations:<br>• {warning_list}
            </div>
            """
        else:
            return """
            <div class="status-message">
                ✅ All parameters look good! Ready to process queries.
            </div>
            """
    
    # Create the Gradio Interface
    with gr.Blocks(css=css, title="🚀 Advanced RAG System") as interface:
        # Header Section
        gr.HTML("""
        <div class="main-container">
            <h1 style="text-align: center; color: #2c3e50; margin-bottom: 10px; font-size: 2.8em; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                🚀 Advanced RAG System (Assignment 3B)
            </h1>
            <p style="text-align: center; color: #7f8c8d; font-size: 20px; margin-bottom: 30px;">
                Professional-grade Retrieval-Augmented Generation with comprehensive configuration
            </p>
        </div>
        """)
        
        # API Status Display
        api_status = gr.HTML(get_api_status_html())
        
        # STEP 1: Database Configuration & Initialization
        gr.HTML("""
        <div class="step-container">
            <h2 class="step-title">STEP 1: Initialize Your Knowledge Base</h2>
            <p class="step-description">Start by initializing the vector database with your documents. Use default settings for quick start, or customize chunking parameters for advanced control.</p>
        </div>
        """)
        
        with gr.Row():
            # Database Setup Buttons
            with gr.Column(scale=1):
                gr.HTML('<h3 class="section-header">🚀 Database Setup</h3>')
                
                init_btn = gr.Button(
                    "🔄 Initialize Vector Database", 
                    variant="primary", 
                    size="lg"
                )
                
                refresh_btn = gr.Button(
                    "🔍 Check Database Status", 
                    variant="secondary",
                    size="lg"
                )
                
                gr.HTML("""
                <div style="background: #d1ecf1; border: 1px solid #bee5eb; border-radius: 8px; padding: 15px; margin: 15px 0; color: #0c5460; font-size: 14px;">
                    💡 <strong>Quick Start:</strong> Click "Initialize Vector Database" to get started with default settings. Advanced users can customize chunking parameters below.
                </div>
                """)
            
            with gr.Column(scale=2):
                # Just show status info in this column for now
                pass
        
        status_output = gr.Textbox(
            label="📊 Database Status & Information", 
            value="Ready to initialize database. Click 'Initialize Vector Database' above to get started...",
            interactive=False,
            lines=4
        )
        
        # Document Chunking Configuration Section (Moved below Database Setup)
        gr.HTML('<h3 class="section-header">📄 Document Chunking Configuration</h3>')
        
        with gr.Row():
            chunk_size_input = gr.Number(
                value=512,
                minimum=1,
                maximum=2048,
                step=1,
                label="Chunk Size",
                info="Recommended: 256-1024. Smaller = more precise, Larger = more context"
            )
            
            chunk_overlap_input = gr.Number(
                value=50,
                minimum=0,
                maximum=500,
                step=10,
                label="Chunk Overlap",
                info="Recommended: 10-20% of chunk size. Helps maintain context continuity"
            )
        
        # Real-time chunking guidance
        chunking_guidance = gr.HTML("""
        <div class="status-message">
            ✅ Using default chunking settings (512/50). Good for most use cases.
        </div>
        """)
        
        # Prominent reinitialization warning that appears when needed
        reinit_warning = gr.HTML("""
        <div style="display: none;"></div>
        """, visible=False)
        
        # STEP 2: Ask Your Questions  
        gr.HTML("""
        <div class="step-container">
            <h2 class="step-title">STEP 2: Ask Your Questions</h2>
            <p class="step-description">Once your database is initialized, start asking questions! Use the quick start with defaults, or customize the AI model and retrieval settings below.</p>
        </div>
        """)
        
        with gr.Row():
            # Query Section (Main focus - moved to prominent position)
            with gr.Column(scale=3):
                gr.HTML('<h3 class="section-header">💬 Chat with Your Documents</h3>')
                
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask me anything about the loaded documents... (e.g., 'What are AI agents and their capabilities?')",
                    lines=3
                )
                
                submit_btn = gr.Button(
                    "🚀 Get Answer", 
                    variant="primary", 
                    size="lg"
                )
                
                # Response Display
                response_output = gr.Textbox(
                    label="📝 AI Assistant Response",
                    lines=12,
                    interactive=False,
                    show_copy_button=True,
                    placeholder="Your AI-generated response will appear here after submitting a question..."
                )
            
            # Quick Settings Panel (Moved to side for easy access)
            with gr.Column(scale=2):
                gr.HTML('<h3 class="section-header">⚡ Quick Settings</h3>')
                
                model_dropdown = gr.Dropdown(
                    choices=["gpt-4o", "gpt-4o-mini"],
                    value="gpt-4o-mini",
                    label="🤖 AI Model",
                    info="gpt-4o-mini is faster and cheaper"
                )
                
                temperature_slider = gr.Slider(
                    minimum=0.0, maximum=1.0, value=0.1, step=0.1,
                    label="🎯 Temperature",
                    info="0.0=focused, 1.0=creative"
                )
                
                similarity_topk_slider = gr.Slider(
                    minimum=1, maximum=20, value=5, step=1,
                    label="📊 Top-K Results",
                    info="How many documents to find"
                )
                
                similarity_cutoff_slider = gr.Slider(
                    minimum=0.0, maximum=1.0, value=0.3, step=0.1,
                    label="🎯 Similarity Threshold",
                    info="Filter out irrelevant results"
                )
        
        # STEP 3: Advanced Configuration (Collapsible)
        gr.HTML("""
        <div class="step-container">
            <h2 class="step-title">STEP 3: Advanced Configuration (Optional)</h2>
            <p class="step-description">Fine-tune advanced processing options for specialized use cases. Most users can skip this section.</p>
        </div>
        """)
        
        with gr.Accordion("🔧 Advanced Processing Settings", open=False):
            with gr.Row():
                # Advanced Processing Options
                with gr.Column():
                    postprocessor_checkbox = gr.Checkbox(
                        value=False,
                        label="Enable Similarity Postprocessor",
                        info="Additional filtering and processing"
                    )
                    
                    synthesizer_dropdown = gr.Dropdown(
                        choices=["TreeSummarize", "Refine", "CompactAndRefine", "Default"],
                        value="Default",
                        label="Response Synthesizer",
                        info="Strategy for combining retrieved information"
                    )
                
                # Status displays
                with gr.Column():
                    # Configuration Status
                    config_status = gr.HTML("""
                    <div class="status-message">
                        <p>✅ Configuration ready! Adjust parameters as needed.</p>
                    </div>
                    """)
                    
                    # Add validation feedback display
                    validation_status = gr.HTML("""
                    <div class="status-message">
                        ✅ All parameters are valid. Ready to go!
                    </div>
                    """)
        
        # Configuration Display (collapsible)
        with gr.Accordion("📋 View Current Configuration Details", open=False):
            config_display = gr.Textbox(
                label="Configuration Summary",
                lines=8,
                interactive=False,
                placeholder="Configuration details will be displayed here when you submit a query..."
            )
        
        # Event Handlers
        init_btn.click(
            initialize_db, 
            inputs=[chunk_size_input, chunk_overlap_input],
            outputs=[status_output]
        )
        
        refresh_btn.click(
            check_database_status,
            outputs=[status_output]
        )
        
        submit_btn.click(
            handle_advanced_query,
            inputs=[
                query_input, model_dropdown, temperature_slider,
                chunk_size_input, chunk_overlap_input, similarity_topk_slider,
                postprocessor_checkbox, similarity_cutoff_slider, synthesizer_dropdown
            ],
            outputs=[response_output, config_display]
        )
        
        # Real-time validation and configuration updates
        def update_all_status(model, temp, chunk_size, chunk_overlap, top_k, postprocessor, cutoff, synth):
            """Update configuration and validation status."""
            # Get validation feedback
            errors, warnings = validate_inputs(chunk_size, chunk_overlap, top_k, cutoff, temp)
            validation_msg = get_validation_message(errors, warnings)
            
            # Get configuration summary
            config_msg = get_config_summary(model, temp, chunk_size, chunk_overlap, top_k, postprocessor, cutoff, synth)
            
            return config_msg, validation_msg
        
        def update_chunking_status(chunk_size, chunk_overlap):
            """Update chunking guidance and reinitialization warning."""
            guidance_msg = get_chunking_guidance(chunk_size, chunk_overlap)
            
            # Show additional prominent warning if reinitialization is needed
            needs_reinit = chunk_size != 512 or chunk_overlap != 50
            has_error = chunk_overlap >= chunk_size or chunk_size < 1
            
            if needs_reinit and not has_error:
                warning_msg = f"""
                <div style="background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%); padding: 25px; border-radius: 15px; color: white; text-align: center; margin: 20px 0; font-weight: bold; border: 4px solid #ff8c42; box-shadow: 0 8px 25px rgba(255, 107, 53, 0.4);">
                    <h2 style="margin: 0 0 15px 0; font-size: 24px; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                        🚨 ACTION REQUIRED 🚨
                    </h2>
                    <p style="font-size: 18px; margin: 10px 0;">
                        You changed chunking settings to: <strong>{chunk_size}/{chunk_overlap}</strong>
                    </p>
                    <p style="font-size: 20px; margin: 15px 0; text-decoration: underline;">
                        ⬆️ CLICK "INITIALIZE VECTOR DATABASE" ABOVE ⬆️
                    </p>
                    <p style="font-size: 16px; opacity: 0.9; margin: 10px 0;">
                        Your queries will use OLD chunking until you reinitialize!
                    </p>
                </div>
                """
                return guidance_msg, warning_msg, True
            else:
                return guidance_msg, "<div style='display: none;'></div>", False
        
        # Chunking parameters - update guidance immediately when changed
        chunk_size_input.change(
            lambda cs, co: update_chunking_status(cs, co)[:2],  # Only return first 2 values
            inputs=[chunk_size_input, chunk_overlap_input],
            outputs=[chunking_guidance, reinit_warning]
        )
        
        chunk_overlap_input.change(
            lambda cs, co: update_chunking_status(cs, co)[:2],  # Only return first 2 values
            inputs=[chunk_size_input, chunk_overlap_input],
            outputs=[chunking_guidance, reinit_warning]
        )
        
        # Configuration inputs (excluding chunk parameters since they're handled above)
        config_inputs = [
            model_dropdown, temperature_slider, similarity_topk_slider, 
            postprocessor_checkbox, similarity_cutoff_slider, synthesizer_dropdown
        ]
        
        # Add chunk parameters for validation but handle separately for chunking guidance
        all_inputs = config_inputs + [chunk_size_input, chunk_overlap_input]
        
        # Update configuration and validation status when any parameter changes
        for input_component in config_inputs:
            if hasattr(input_component, 'change'):
                input_component.change(
                    update_all_status,
                    inputs=all_inputs,
                    outputs=[config_status, validation_status]
                )
    
    return interface


def launch_application():
    """Launch the professional advanced RAG application."""
    print("🎉 Launching Professional Advanced RAG System...")
    print("🔗 Opening in browser with step-by-step interface!")
    print("")
    print("⚠️  Make sure your OPENROUTER_API_KEY environment variable is set!")
    print("")
    print("📋 Usage Instructions:")
    print("STEP 1: Click 'Initialize Vector Database' for quick start")
    print("STEP 2: Ask your questions immediately - defaults work great!")
    print("STEP 3: Optionally fine-tune advanced settings if needed")
    print("")
    print("🎯 Professional Features:")
    print("✅ Streamlined workflow: Initialize → Query → Customize")
    print("✅ Quick start with smart defaults")
    print("✅ Side-by-side query and settings panels")
    print("✅ Advanced options safely tucked away")
    print("✅ Real-time validation and guidance")
    
    interface = create_professional_rag_interface()
    interface.launch(
        server_name="127.0.0.1",
        server_port=None,  # Let Gradio find an available port automatically
        share=False,
        debug=True,
        show_error=True
    )


if __name__ == "__main__":
    launch_application()