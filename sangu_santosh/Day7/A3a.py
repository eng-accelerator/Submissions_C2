from dotenv import load_dotenv
import os
import gradio as gr
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openrouter import OpenRouter
from llama_index.vector_stores.lancedb import LanceDBVectorStore
import lancedb
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# If the user has an OpenRouter API key, configure OpenRouter as the LLM
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
if openrouter_api_key:
    try:
        Settings.llm = OpenRouter(
            api_key=openrouter_api_key,
            model=os.getenv("OPENROUTER_MODEL", "gpt-4o"),
            temperature=float(os.getenv("OPENROUTER_TEMPERATURE", "0.1")),
        )
        logging.info("✅ OpenRouter configured for LLM responses")
    except Exception as _e:
        logging.warning(f"⚠️ Failed to configure OpenRouter LLM: {_e}. Falling back to vector-only mode.")

# Configure paths and settings
ASSIGNMENTS_DB_ROOT = os.getenv('ASSIGNMENTS_DB_ROOT', 'assignment_vectordb')
A3_DB_PATH = os.getenv('A3_DB_PATH', os.path.join(ASSIGNMENTS_DB_ROOT, 'documents.lance'))

def create_vector_index():
    logging.info("📁 Setting up basic index for Gradio RAG...")
    
    try:
        # Initialize the local HuggingFace embeddings
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        # Configure global settings
        Settings.embed_model = embed_model
        Settings.chunk_size = 512
        
        # Set up LanceDB
        db = lancedb.connect(ASSIGNMENTS_DB_ROOT)
        
        if "documents" not in db.table_names():
            logging.info("Creating new vector store...")
            # Load documents
            documents = SimpleDirectoryReader(
                input_dir="data",
                recursive=True,
                exclude_hidden=True,
                filename_as_id=True
            ).load_data()
            
            # Create vector store
            vector_store = LanceDBVectorStore(
                uri=ASSIGNMENTS_DB_ROOT,
                table_name="documents",
                create_table_if_not_exists=True
            )
            
            # Create index
            index = VectorStoreIndex.from_documents(
                documents,
                vector_store=vector_store
            )
            logging.info(f"✅ Created new index with {len(documents)} documents")
        else:
            logging.info("Loading existing vector store...")
            vector_store = LanceDBVectorStore(
                uri=ASSIGNMENTS_DB_ROOT,
                table_name="documents"
            )
            index = VectorStoreIndex.from_vector_store(
                vector_store
            )
            logging.info("✅ Loaded existing vector store")
        
        return index
    except Exception as e:
        logging.error(f"Error setting up vector store: {str(e)}")
        raise

def query_index(index, query_text):
    try:
        logging.info(f"🔍 Processing query: '{query_text}'")
        query_engine = index.as_query_engine(
            similarity_top_k=1,  # Get the most relevant result
            response_mode="no_text"  # Return only source nodes
        )
        response = query_engine.query(query_text)
        
        # Extract relevant text from the response
        if response and response.source_nodes:
            return response.source_nodes[0].node.text
        else:
            return "No relevant information found."
            
    except Exception as e:
        logging.error(f"Error processing query: {str(e)}")
        return f"An error occurred while processing your question: {str(e)}"

def create_gradio_interface(index):
    def process_query(query):
        if not query or query.strip() == "":
            return "Please enter a question."
        return query_index(index, query.strip())
    
    # Create Gradio interface
    iface = gr.Interface(
        fn=process_query,
        inputs=gr.Textbox(
            lines=2,
            placeholder="Ask a question about the documents in our knowledge base...",
            label="Question"
        ),
        outputs=gr.Textbox(
            label="Answer",
            lines=10
        ),
        title="📚 Basic RAG Q&A System",
        description="Ask questions about the documents in our knowledge base.",
        examples=[
            "What are the key capabilities of AI agents?",
            "How do you evaluate agent performance metrics?",
            "Tell me about Italian recipes and cooking techniques"
        ],
        allow_flagging="never"
    )
    return iface

def main():
    try:
        logging.info("🚀 Setting up Basic Gradio RAG System...")
        
        # Create or load the vector index
        index = create_vector_index()
        
        # Create and launch Gradio interface
        interface = create_gradio_interface(index)
        interface.launch(share=False)  # Set share=True if you want a public URL
        
    except Exception as e:
        logging.error(f"Failed to start Gradio interface: {str(e)}")
        raise

if __name__ == "__main__":
    main()