# Assignment 2: Advanced RAG Techniques Implementation
# Following the exact structure from assignment_2_advanced_rag.ipynb

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# Core LlamaIndex components
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever

# Vector store
from llama_index.vector_stores.lancedb import LanceDBVectorStore

# Embeddings and LLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter

# Advanced RAG components
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import TreeSummarize, Refine, CompactAndRefine
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.program import LLMTextCompletionProgram

from dotenv import load_dotenv

print("✅ Advanced RAG libraries imported successfully!")

# Load environment variables
load_dotenv()

# Configure Advanced RAG Settings (Using OpenRouter)
def setup_advanced_rag_settings():
    """
    Configure LlamaIndex with optimized settings for advanced RAG.
    Uses local embeddings and OpenRouter for LLM operations.
    """
    # Check for OpenRouter API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️  OPENROUTER_API_KEY not found - LLM operations will be limited")
        print("   You can still complete postprocessor and retrieval exercises")
    else:
        print("✅ OPENROUTER_API_KEY found - full advanced RAG functionality available")
        
        # Configure OpenRouter LLM
        Settings.llm = OpenRouter(
            api_key=api_key,
            model="gpt-4o",
            temperature=0.1  # Lower temperature for more consistent responses
        )
    
    # Configure local embeddings (no API key required)
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5",
        trust_remote_code=True
    )
    
    # Advanced RAG configuration
    Settings.chunk_size = 512  # Smaller chunks for better precision
    Settings.chunk_overlap = 50
    
    print("✅ Advanced RAG settings configured")
    print("   - Chunk size: 512 (optimized for precision)")
    print("   - Using local embeddings for cost efficiency")
    print("   - OpenRouter LLM ready for response synthesis")

# Setup the configuration
setup_advanced_rag_settings()

# Function to check if database exists (from Assignment 1)
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

# Setup: Create index from Assignment 1 (reuse the basic functionality)
def setup_basic_index(data_folder: str = "../data", force_rebuild: bool = False):
    """
    Create a basic vector index that we'll enhance with advanced techniques.
    This reuses the concepts from Assignment 1.
    """
    # Ensure AssignmentDb folder exists first
    Path("./AssignmentDb").mkdir(parents=True, exist_ok=True)
    
    # Get database path
    db_path = os.getenv("ASSIGNMENT_2_DB_PATH", "./AssignmentDb/a2_advanced_rag_vectordb")
    
    # Check if database already exists (unless force rebuild)
    if not force_rebuild and check_vector_db_exists(db_path):
        print("🔄 Loading existing database...")
        try:
            # Create vector store and load existing index
            vector_store = LanceDBVectorStore(
                uri=db_path,
                table_name="documents"
            )
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            index = VectorStoreIndex([], storage_context=storage_context)
            
            print("✅ Existing database loaded successfully")
            return index
        except Exception as e:
            print(f"⚠️  Error loading existing database: {e}")
            print("🔄 Will create fresh database...")
    
    # Create fresh database
    # Create vector store
    vector_store = LanceDBVectorStore(
        uri=db_path,
        table_name="documents"
    )
    
    # Load documents
    if not Path(data_folder).exists():
        print(f"❌ Data folder not found: {data_folder}")
        return None
        
    # Limit to common doc types to avoid audio/video dependencies (e.g., Whisper)
    safe_exts = [".txt", ".md", ".pdf", ".html", ".htm", ".csv", ".json"]
    reader = SimpleDirectoryReader(
        input_dir=data_folder, 
        recursive=True,
        required_exts=safe_exts
    )
    documents = reader.load_data()
    
    # Create storage context and index
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context,
        show_progress=True
    )
    
    print(f"✅ Basic index created with {len(documents)} documents")
    print("   Ready for advanced RAG techniques!")
    return index

# Create the basic index
print("📁 Setting up basic index for advanced RAG...")
data_folder = os.getenv("DATA_PATH", "../../../../ai-accelerator-C2-main/ai-accelerator-C2-main/Day_6/session_2/data")
index = setup_basic_index(data_folder)

if index:
    print("🚀 Ready to implement advanced RAG techniques!")
else:
    print("❌ Failed to create index - check data folder path")

# 1. Node Postprocessors - Similarity Filtering
def create_query_engine_with_similarity_filter(index, similarity_cutoff: float = 0.3, top_k: int = 10):
    """
    Create a query engine that filters results based on similarity scores.
    
    Args:
        index: Vector index to query
        similarity_cutoff: Minimum similarity score (0.0 to 1.0)
        top_k: Number of initial results to retrieve before filtering
        
    Returns:
        Query engine with similarity filtering
    """
    # Create similarity postprocessor with the cutoff threshold
    similarity_processor = SimilarityPostprocessor(similarity_cutoff=similarity_cutoff)
    
    # Create query engine with similarity filtering
    query_engine = index.as_query_engine(
        similarity_top_k=top_k,
        node_postprocessors=[similarity_processor]
    )
    
    return query_engine

# Test the function
if index:
    filtered_engine = create_query_engine_with_similarity_filter(index, similarity_cutoff=0.3)
    
    if filtered_engine:
        print("✅ Query engine with similarity filtering created")
        
        # Test query
        test_query = "What are the benefits of AI agents?"
        print(f"\n🔍 Testing query: '{test_query}'")
        
        # Uncomment when implemented:
        # response = filtered_engine.query(test_query)
        # print(f"📝 Response: {response}")
        print("   (Complete the function above to test the response)")
    else:
        print("❌ Failed to create filtered query engine")
else:
    print("❌ No index available - run previous cells first")

# 2. Response Synthesizers - TreeSummarize
def create_query_engine_with_tree_summarize(index, top_k: int = 5):
    """
    Create a query engine that uses TreeSummarize for comprehensive responses.
    
    Args:
        index: Vector index to query
        top_k: Number of results to retrieve
        
    Returns:
        Query engine with TreeSummarize synthesis
    """
    # Create TreeSummarize response synthesizer
    tree_synthesizer = TreeSummarize()
    
    # Create query engine with the synthesizer
    query_engine = index.as_query_engine(
        similarity_top_k=top_k,
        response_synthesizer=tree_synthesizer
    )
    
    return query_engine

# Test the function
if index:
    tree_engine = create_query_engine_with_tree_summarize(index)
    
    if tree_engine:
        print("✅ Query engine with TreeSummarize created")
        
        # Test with a complex analytical query
        analytical_query = "Compare the advantages and disadvantages of different AI agent frameworks"
        print(f"\n🔍 Testing analytical query: '{analytical_query}'")
        
        # Uncomment when implemented:
        # response = tree_engine.query(analytical_query)
        # print(f"📝 TreeSummarize Response:\n{response}")
        print("   (Complete the function above to test comprehensive analysis)")
    else:
        print("❌ Failed to create TreeSummarize query engine")
else:
    print("❌ No index available - run previous cells first")

# 3. Structured Outputs with Pydantic Models
# First, define the Pydantic models for structured outputs  
class ResearchPaperInfo(BaseModel):
    """Structured information about a research paper or AI concept."""
    title: str = Field(description="The main title or concept name")
    key_points: List[str] = Field(description="3-5 main points or findings")
    applications: List[str] = Field(description="Practical applications or use cases")
    summary: str = Field(description="Brief 2-3 sentence summary")

def create_structured_output_program(output_model=ResearchPaperInfo):
    """
    Create a structured output program using Pydantic models.
    
    Args:
        output_model: Pydantic model class for structured output
        
    Returns:
        LLMTextCompletionProgram that returns structured data
    """
    # Create output parser with the Pydantic model
    output_parser = PydanticOutputParser(output_cls=output_model)
    
    # Create the structured output program
    prompt_template = """
    Based on the provided context, extract information about the topic and format it according to the schema.
    
    Context: {context}
    Query: {query}
    
    Please provide a structured response following the specified format.
    """
    
    program = LLMTextCompletionProgram.from_defaults(
        output_parser=output_parser,
        prompt_template_str=prompt_template,
        verbose=True
    )
    
    return program

# Test the function
if index:
    structured_program = create_structured_output_program(ResearchPaperInfo)
    
    if structured_program:
        print("✅ Structured output program created")
        
        # Test with retrieval and structured extraction
        structure_query = "Tell me about AI agents and their capabilities"
        print(f"\n🔍 Testing structured query: '{structure_query}'")
        
        # Get context for structured extraction (Uncomment when implemented)
        # retriever = VectorIndexRetriever(index=index, similarity_top_k=3)
        # nodes = retriever.retrieve(structure_query)
        # context = "\n".join([node.text for node in nodes])
        
        # Uncomment when implemented:
        # response = structured_program(context=context, query=structure_query)
        # print(f"📊 Structured Response:\n{response}")
        print("   (Complete the function above to get structured JSON output)")
        
        print("\n💡 Expected output format:")
        print("   - title: String")
        print("   - key_points: List of strings")
        print("   - applications: List of strings") 
        print("   - summary: String")
    else:
        print("❌ Failed to create structured output program")
else:
    print("❌ No index available - run previous cells first")

# 4. Advanced Pipeline - Combining All Techniques
def create_advanced_rag_pipeline(index, similarity_cutoff: float = 0.3, top_k: int = 10):
    """
    Create a comprehensive advanced RAG pipeline combining multiple techniques.
    
    Args:
        index: Vector index to query
        similarity_cutoff: Minimum similarity score for filtering
        top_k: Number of initial results to retrieve
        
    Returns:
        Advanced query engine with filtering and synthesis combined
    """
    # Create similarity postprocessor
    similarity_processor = SimilarityPostprocessor(similarity_cutoff=similarity_cutoff)
    
    # Create TreeSummarize for comprehensive responses
    tree_synthesizer = TreeSummarize()
    
    # Create the comprehensive query engine combining both techniques
    advanced_engine = index.as_query_engine(
        similarity_top_k=top_k,
        node_postprocessors=[similarity_processor],
        response_synthesizer=tree_synthesizer
    )
    
    return advanced_engine

# Test the comprehensive pipeline
if index:
    advanced_pipeline = create_advanced_rag_pipeline(index)
    
    if advanced_pipeline:
        print("✅ Advanced RAG pipeline created successfully!")
        print("   🔧 Similarity filtering: ✅")
        print("   🌳 TreeSummarize synthesis: ✅")
        
        # Test with complex query
        complex_query = "Analyze the current state and future potential of AI agent technologies"
        print(f"\n🔍 Testing complex query: '{complex_query}'")
        
        # Uncomment when implemented:
        # response = advanced_pipeline.query(complex_query)
        # print(f"🚀 Advanced RAG Response:\n{response}")
        print("   (Complete the function above to test the full pipeline)")
        
        print("\n🎯 This should provide:")
        print("   - Filtered relevant results only")
        print("   - Comprehensive analytical response")
        print("   - Combined postprocessing and synthesis")
    else:
        print("❌ Failed to create advanced RAG pipeline")
else:
    print("❌ No index available - run previous cells first")

# 5. Final Test - Compare Basic vs Advanced RAG
# Final comparison: Basic vs Advanced RAG
print("🚀 Advanced RAG Techniques Assignment - Final Test")
print("=" * 60)

# Test queries for comparison
test_queries = [
    "What are the key capabilities of AI agents?",
    "How do you evaluate agent performance metrics?",
    "Explain the benefits and challenges of multimodal AI systems"
]

# Check if all components were created
# pylint: disable=possibly-used-before-assignment
components_status = {
    "Basic Index": index is not None,
    "Similarity Filter": 'filtered_engine' in locals() and filtered_engine is not None,  # type: ignore
    "TreeSummarize": 'tree_engine' in locals() and tree_engine is not None,  # type: ignore
    "Structured Output": 'structured_program' in locals() and structured_program is not None,  # type: ignore
    "Advanced Pipeline": 'advanced_pipeline' in locals() and advanced_pipeline is not None  # type: ignore
}

print("\n📊 Component Status:")
for component, status in components_status.items():
    status_icon = "✅" if status else "❌"
    print(f"   {status_icon} {component}")

# Create basic query engine for comparison
if index:
    print("\n🔍 Creating basic query engine for comparison...")
    basic_engine = index.as_query_engine(similarity_top_k=5)
    
    print("\n" + "=" * 60)
    print("🆚 COMPARISON: Basic vs Advanced RAG")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test Query {i}: '{query}'")
        print("-" * 50)
        
        # Basic RAG
        print("🔹 Basic RAG:")
        if basic_engine:
            # Uncomment when testing:
            # basic_response = basic_engine.query(query)
            # print(f"   Response: {str(basic_response)[:200]}...")
            print("   (Standard vector search + simple response)")
        
        # Advanced RAG (if implemented)
        print("\n🔸 Advanced RAG:")
        if components_status["Advanced Pipeline"]:
            # Uncomment when testing:
            # advanced_response = advanced_pipeline.query(query)
            # print(f"   Response: {advanced_response}")
            print("   (Filtered + TreeSummarize + Structured output)")
        else:
            print("   Complete the advanced pipeline function to test")

# Final status
print("\n" + "=" * 60)
print("🎯 Assignment Status:")
completed_count = sum(components_status.values())
total_count = len(components_status)

print(f"   Completed: {completed_count}/{total_count} components")

if completed_count == total_count:
    print("\n🎉 Congratulations! You've mastered Advanced RAG Techniques!")
    print("   ✅ Node postprocessors for result filtering")
    print("   ✅ Response synthesizers for better answers")
    print("   ✅ Structured outputs for reliable data")
    print("   ✅ Advanced pipelines combining all techniques")
    print("\n🚀 You're ready for production RAG systems!")
else:
    missing = total_count - completed_count
    print(f"\n📝 Complete {missing} more components to finish the assignment:")
    for component, status in components_status.items():
        if not status:
            print(f"   - {component}")

print("\n💡 Key learnings:")
print("   - Postprocessors improve result relevance and precision")
print("   - Different synthesizers work better for different query types")
print("   - Structured outputs enable reliable system integration")
print("   - Advanced techniques can be combined for production systems")