# Import required libraries
import gradio as gr
import os
from pathlib import Path

# LlamaIndex components
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter
from dotenv import load_dotenv
load_dotenv()


print("✅ All libraries imported successfully!")



class SimpleRAGBackend:
    """Simple RAG backend for Gradio frontend."""

    def __init__(self):
        self.index = None
        self.setup_settings()

    def setup_settings(self):
        """Configure LlamaIndex settings."""
        # Set up the LLM using OpenRouter
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            Settings.llm = OpenRouter(
                api_key=api_key,
                model="gpt-4o",
                temperature=0.1
            )

        # Set up the embedding model
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            trust_remote_code=True
        )

        # Set chunking parameters
        Settings.chunk_size = 512
        Settings.chunk_overlap = 50

    def initialize_database(self, data_folder="data"):
        """Initialize the vector database with documents."""
        # Check if data folder exists
        if not Path(data_folder).exists():
            return f"❌ Data folder '{data_folder}' not found!"

        try:
            # Create vector store
            vector_store = LanceDBVectorStore(
                uri="./basic_rag_vectordb",
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

    def query(self, question):
        """Query the RAG system and return response."""
        # Check if index exists
        if self.index is None:
            return "❌ Please initialize the database first!"

        # Check if question is empty
        if not question or not question.strip():
            return "⚠️ Please enter a question first!"

        try:
            # Create query engine and get response
            query_engine = self.index.as_query_engine()
            response = query_engine.query(question)
            return str(response)

        except Exception as e:
            return f"❌ Error processing query: {str(e)}"

# Initialize the backend
rag_backend = SimpleRAGBackend()
print("🚀 RAG Backend initialized and ready!")



def create_basic_rag_interface():
    """Create basic RAG interface with essential features."""

    def initialize_db():
        """Handle database initialization."""
        return rag_backend.initialize_database()

    def handle_query(question):
        """Handle user queries."""
        return rag_backend.query(question)

    # TODO: Create Gradio interface using gr.Blocks()
    # Hint: Look at the structure below and fill in the missing components

    with gr.Blocks(title="Basic RAG Assistant") as interface:
        # TODO: Add title and description
        # Hint: Use gr.Markdown() for formatted text
        gr.Markdown(
            """
            # 🤖 Basic RAG Assistant
            This interface demonstrates a simple **Retrieval-Augmented Generation (RAG)** setup.
            Initialize the database first, then submit your queries.
            """
        )

        # TODO: Add initialization section
        # Hint: You need to use gr.Button to initialize the database
        init_btn = gr.Button("Initialize Database") # TODO: Use gr.Button to initialize the database

        # TODO: Add status output
        # Hint: You need to use gr.Textbox to display the status
        status_output = gr.Textbox(label="Status Log", interactive=False)

        # The connection between the button and the status output has already been implemented
        # at the end of this function

        # TODO: Add query section
        # Hint: You need a text input, submit button, and response output
        gr.Markdown("---") # Visual separator
        gr.Markdown("## Query Section")

        # Use gr.Textbox to create a text input
        query_input = gr.Textbox(label="Your Query", placeholder="Ask me anything...")

        # Use gr.Button to create a submit button
        submit_btn = gr.Button("Submit Query")

        # Use gr.Textbox to create a response output
        response_output = gr.Textbox(label="Assistant Response", interactive=False)

        # 5. Connect buttons to functions (Uncommenting the lines from your SS)
        init_btn.click(initialize_db, outputs=[status_output])
        submit_btn.click(handle_query, inputs=[query_input], outputs=[response_output])

    return interface

# Create the interface
basic_interface = create_basic_rag_interface()
print("✅ Basic RAG interface created successfully!")




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
print("")
print("🚀 Launch your app:")

# Your launch code here:
# Uncomment when implemented
basic_interface.launch()