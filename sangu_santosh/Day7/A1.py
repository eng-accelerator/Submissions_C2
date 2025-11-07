import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load environment variables
load_dotenv()

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

def load_documents_from_folder(folder_path: str):
    """
    Load documents from a folder using SimpleDirectoryReader.
    
    Args:
        folder_path (str): Path to the folder containing documents
        
    Returns:
        List of documents loaded from the folder
    """
    # Create SimpleDirectoryReader instance with recursive loading
    reader = SimpleDirectoryReader(
        input_dir=folder_path,
        recursive=True
    )
    
    # Load and return documents
    documents = reader.load_data()
    return documents

def create_vector_store(db_path: str = "./vectordb", table_name: str = "documents"):
    """
    Create a LanceDB vector store for storing document embeddings.
    
    Args:
        db_path (str): Path where the vector database will be stored
        table_name (str): Name of the table in the vector database
        
    Returns:
        LanceDBVectorStore: Configured vector store
    """
    # Create the directory if it doesn't exist
    Path(db_path).mkdir(parents=True, exist_ok=True)
    
    # Create and return vector store
    vector_store = LanceDBVectorStore(uri=str(db_path), table_name=table_name)
    return vector_store

def create_vector_index(documents: List, vector_store):
    """
    Create a vector index from documents using the provided vector store.
    
    Args:
        documents: List of documents to index
        vector_store: LanceDB vector store to use for storage
        
    Returns:
        VectorStoreIndex: The created vector index
    """
    # Create storage context with vector store
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Create and return index from documents
    index = VectorStoreIndex.from_documents(
        documents=documents,
        storage_context=storage_context
    )
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
    
    # Retrieve and return documents for the query
    results = retriever.retrieve(query)
    return results

def test_pipeline():
    """
    Test the complete vector database pipeline
    """
    print("🚀 Testing Complete Vector Database Pipeline")
    print("=" * 50)

    # Define paths
    data_folder = "data"  # Data folder in Day-7/codes
    
    # Get database path from environment
    vector_db_path = os.getenv("A1_DB_PATH", "AssignmentsDB/Assignment1")
    Path(vector_db_path).mkdir(parents=True, exist_ok=True)

    # Step 1: Load documents
    print("\n📂 Step 1: Loading documents...")
    documents = load_documents_from_folder(data_folder)
    print(f"   Loaded {len(documents)} documents")

    # Step 2: Create vector store
    print("\n🗄️ Step 2: Creating vector store...")
    vector_store = create_vector_store(vector_db_path)
    print("   Vector store status:", "✅ Created" if vector_store else "❌ Failed")

    # Step 3: Create vector index
    print("\n🔗 Step 3: Creating vector index...")
    if documents and vector_store:
        index = create_vector_index(documents, vector_store)
        print("   Index status:", "✅ Created" if index else "❌ Failed")
    else:
        index = None
        print("   ❌ Cannot create index - missing documents or vector store")

    # Step 4: Test multiple search queries
    print("\n🔍 Step 4: Testing search functionality...")
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
    else:
        print("   ❌ Cannot test search - index not created")

    print("\n" + "=" * 50)
    print("🎯 Assignment Status:")
    print(f"   Documents loaded: {'✅' if documents else '❌'}")
    print(f"   Vector store created: {'✅' if vector_store else '❌'}")
    print(f"   Index created: {'✅' if index else '❌'}")
    print(f"   Search working: {'✅' if index else '❌'}")

    if documents and vector_store and index:
        print("\n🎉 Congratulations! You've successfully completed the assignment!")
        print("   You've built a complete vector database with search functionality!")
    else:
        print("\n📝 Please complete the TODO functions above to finish the assignment.")

if __name__ == "__main__":
    # Initialize LlamaIndex settings
    setup_llamaindex_settings()
    
    # Run the test pipeline
    test_pipeline()