"""Test web scraping functionality."""
import pytest
from src.tools.loaders import HTMLLoader
from src.tools.websearch import WebSearchTool
from src.agents.context_retriever import ContextualRetrieverAgent

def test_html_loader():
    """Test HTML text extraction."""
    url = "https://raw.githubusercontent.com/microsoft/vscode-docs/main/README.md"
    text = HTMLLoader.load_text(url)
    assert text, "Should extract text from URL"
    assert len(text) > 100, "Should extract meaningful content"

def test_web_search():
    """Test web search with domains."""
    tool = WebSearchTool()
    results = tool.search(
        query="Visual Studio Code documentation", 
        domains=["code.visualstudio.com"],
        top_k=3
    )
    assert results, "Should return search results"
    assert all('url' in r for r in results), "Each result should have URL"
    assert all('snippet' in r for r in results), "Each result should have snippet"

def test_context_retriever_urls():
    """Test URL processing in context retriever."""
    retriever = ContextualRetrieverAgent()
    urls = [
        "https://raw.githubusercontent.com/microsoft/vscode-docs/main/README.md"
    ]
    docs = retriever.process_urls(urls)
    assert docs, "Should process URLs"
    assert all('text' in d and len(d['text']) > 100 for d in docs), "Should extract content"
    assert all('source' in d and d['source'].startswith('http') for d in docs), "Should normalize sources"