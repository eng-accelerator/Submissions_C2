"""End-to-end test of document processing pipeline."""
import os
from pathlib import Path
import pytest
from src.agents.context_retriever import ContextualRetrieverAgent
from src.tools.vectorstore import VectorStore

ROOT = Path(__file__).resolve().parents[1]
TEST_DATA = ROOT / 'tests' / 'data'
TEST_URL = "https://raw.githubusercontent.com/microsoft/vscode-docs/main/README.md"

@pytest.fixture
def clean_index():
    """Ensure fresh index for each test."""
    index_path = ROOT / 'data' / 'test.index'
    if index_path.exists():
        index_path.unlink()
    yield str(index_path)
    if index_path.exists():
        index_path.unlink()

def test_end_to_end_indexing(clean_index):
    """Test complete indexing pipeline with PDF and web content."""
    # Create retriever with test index
    retriever = ContextualRetrieverAgent()
    retriever.vector = VectorStore(path=clean_index)
    
    # Process test URL
    docs = retriever.process_urls([TEST_URL])
    assert docs, "Should process test URL"
    
    # Index documents
    indexed = retriever.index_documents(urls=[TEST_URL])
    assert len(indexed) > 0, "Should index documents"
    assert any(s['status'] == 'indexed' for s in indexed), "Should have successful indexes"
    
    # Verify retrieval
    results = retriever.retrieve(
        query="Visual Studio Code documentation",
        constraints={'top_k': 3}
    )
    assert results, "Should retrieve results"
    assert all('score' in r for r in results), "Results should have scores"
    assert all('meta' in r for r in results), "Results should have metadata"
    
    # Check index persistence
    assert os.path.exists(clean_index), "Should persist index file"
    vs = VectorStore(path=clean_index)
    assert len(vs.ids) > 0, "Should have indexed documents"
    
def test_error_handling():
    """Test error handling in document processing."""
    retriever = ContextualRetrieverAgent()
    
    # Test invalid URL
    bad_url = "http://invalid.url.that.does.not.exist"
    docs = retriever.process_urls([bad_url])
    assert len(docs) == 0, "Should handle invalid URL gracefully"
    
    # Test invalid file path
    bad_file = str(TEST_DATA / "nonexistent.pdf")
    docs = retriever.process_files([bad_file])
    assert len(docs) == 0, "Should handle missing file gracefully"