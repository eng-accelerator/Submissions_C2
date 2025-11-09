# Import required libraries
import os
from pathlib import Path
from typing import List
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings, load_index_from_storage
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

print("✅ Libraries imported successfully!")

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Access API keys
openai_key = os.getenv("OPENAI_API_KEY")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

# Configure LlamaIndex Settings (Using OpenRouter - No OpenAI API Key needed)
def setup_llamaindex_settings():
    """
    Configure LlamaIndex with local embeddings and OpenRouter for LLM.
    This assignment focuses on vector database operations, so we'll use local embeddings only.
    """
    # Check for OpenRouter API key (for future use, not needed for this basic assignment)
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("ℹ️  OPENROUTER_API_KEY not found - that's OK for this assignment!")
        print("   This assignment only uses local embeddings for vector operations.")
    
    # Configure local embeddings (no API key required)
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5",
        trust_remote_code=True
    )
    
    print("✅ LlamaIndex configured with local embeddings")
    print("   Using BAAI/bge-small-en-v1.5 for document embeddings")

# Setup the configuration
setup_llamaindex_settings()

def load_documents_from_folder(folder_path: str):
    """
    Load documents from a folder using SimpleDirectoryReader.
    
    Args:
        folder_path (str): Path to the folder containing documents
        
    Returns:
        List of documents loaded from the folder
    """
    # Limit to common doc types to avoid audio/video dependencies (e.g., Whisper)
    safe_exts = [".txt", ".md", ".pdf", ".html", ".htm", ".csv", ".json"]

    reader = SimpleDirectoryReader(
        input_dir=folder_path,
        recursive=True,
        required_exts=safe_exts
    )
    documents = reader.load_data()
    print(f"✅ Loaded {len(documents)} documents from {folder_path}")
    return documents

def check_vector_db_exists(db_path: str, table_name: str = "documents"):
    """
    Check if vector database already exists and has data.
    
    Args:
        db_path (str): Path to the vector database
        table_name (str): Name of the table in the database
        
    Returns:
        bool: True if database exists and has data, False otherwise
    """
    lance_file = Path(db_path) / f"{table_name}.lance"
    
    if lance_file.exists():
        # Try to check if the table has data
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

def create_vector_store(db_path: str = "./vectordb", table_name: str = "documents"):
    """
    Create a LanceDB vector store for storing document embeddings.
    
    Args:
        db_path (str): Path where the vector database will be stored
        table_name (str): Name of the table in the vector database
        
    Returns:
        LanceDBVectorStore: Configured vector store
    """
    # Ensure AssignmentDb folder exists first
    Path("./AssignmentDb").mkdir(parents=True, exist_ok=True)
    
    # Create the directory if it doesn't exist
    Path(db_path).mkdir(parents=True, exist_ok=True)
    
    # Create vector store
    vector_store = LanceDBVectorStore(
        uri=db_path,
        table_name=table_name
    )
    
    print(f"✅ Vector store connected to {db_path}")
    return vector_store

def create_or_load_index(documents, vector_store, db_path):
    """
    Create a new index or load existing one from storage.
    
    Args:
        documents: List of documents to index (only used if creating new)
        vector_store: LanceDB vector store to use
        db_path: Path to the database
        
    Returns:
        VectorStoreIndex: The created or loaded index
    """
    # Check if we already have indexed data
    if check_vector_db_exists(db_path):
        print("🔄 Attempting to load existing index...")
        try:
            # Create storage context with the existing vector store
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            # Try to create index from existing vector store
            index = VectorStoreIndex([], storage_context=storage_context)
            
            # Test the index with a simple query to ensure it's working
            test_retriever = index.as_retriever(similarity_top_k=1)
            test_retriever.retrieve("test")
            
            print("✅ Existing index loaded and verified successfully")
            return index
        except Exception as e:
            print(f"⚠️  Existing database is corrupted: {str(e)[:100]}...")
            print("🗑️  Removing corrupted database...")
            
            # Remove corrupted database
            import shutil
            if Path(db_path).exists():
                shutil.rmtree(db_path)
                print("✅ Corrupted database removed")
            
            print("🔄 Will create fresh database...")
    
    # Ensure we have documents to create new index
    if not documents:
        raise ValueError("Cannot create new index: no documents provided and existing database is corrupted")
    
    # Create new index from documents
    # Recreate directory for fresh database
    Path(db_path).mkdir(parents=True, exist_ok=True)
    
    # Create new vector store
    vector_store = LanceDBVectorStore(uri=db_path, table_name="documents")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    print(f"🔄 Creating fresh index from {len(documents)} documents...")
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context
    )
    print(f"✅ Fresh index created successfully with {len(documents)} documents")
    return index

def search_documents(index, query: str, top_k: int = 3):
    """
    Search for relevant documents using the vector index.
    
    Args:
        index: Vector index to search
        query (str): Search query
        top_k (int): Number of top results to return
        
    Returns:
        List of retrieved document nodes
    """
    # Create retriever from index
    retriever = index.as_retriever(similarity_top_k=top_k)
    
    # Retrieve documents for the query
    results = retriever.retrieve(query)
    
    print(f"🔍 Found {len(results)} results for query: '{query}'")
    return results

def main():
    """Main function to run the RAG system"""
    print("🚀 RAG System with Duplicate Prevention")
    print("=" * 50)

    # Configuration
    test_folder = os.getenv("DATA_PATH", "../../../../ai-accelerator-C2-main/ai-accelerator-C2-main/Day_6/session_2/data")
    vector_db_path = os.getenv("ASSIGNMENT_1_DB_PATH", "./AssignmentDb/a1_assignment_vectordb")
    
    # Validate that the data path exists
    if not os.path.exists(test_folder):
        print(f"❌ Data folder '{test_folder}' does not exist!")
        print(f"   Current working directory: {os.getcwd()}")
        return
    
    print(f"✅ Data folder found: {test_folder}")

    # Step 1: Check if database already exists
    db_exists = check_vector_db_exists(vector_db_path)
    
    # Step 2: Load documents (always load in case we need to rebuild)
    print("\n📂 Loading documents...")
    documents = load_documents_from_folder(test_folder)
    print(f"   Loaded {len(documents)} documents")
    
    if db_exists:
        print("   � Will try to use existing database first")

    # Step 3: Create/connect to vector store
    print("\n🗄️ Setting up vector store...")
    vector_store = create_vector_store(vector_db_path)

    # Step 4: Create or load index (with fallback to rebuild if corrupted)
    print("\n🔗 Setting up vector index...")
    try:
        index = create_or_load_index(documents, vector_store, vector_db_path)
    except Exception as e:
        print(f"❌ Failed to create index: {e}")
        return

    # Step 5: Test search functionality
    print("\n🔍 Testing search functionality...")
    if index:
        search_queries = [
            "What are AI agents?",
            "How to evaluate agent performance?", 
            "Italian recipes and cooking",
            "Financial analysis and investment"
        ]
        
        for query in search_queries:
            print(f"\n   🔎 Query: '{query}'")
            results = search_documents(index, query, top_k=2)
            
            if results:
                for i, result in enumerate(results, 1):
                    text_preview = result.text[:100] if hasattr(result, 'text') else "No text available"
                    score = f" (Score: {result.score:.4f})" if hasattr(result, 'score') else ""
                    print(f"      {i}. {text_preview}...{score}")
            else:
                print("      No results found")
    
    print("\n" + "=" * 50)
    print("🎯 RAG System Status:")
    print(f"   Database exists: {'✅' if db_exists else '❌'}")
    print(f"   Vector store: {'✅' if vector_store else '❌'}")
    print(f"   Index ready: {'✅' if index else '❌'}")
    
    if index:
        print("\n🎉 RAG System is ready for queries!")
        print("   Run this script again - it will use the existing database without recreating data!")
    else:
        print("\n❌ RAG System setup failed")

# Run the main function
if __name__ == "__main__":
    main()