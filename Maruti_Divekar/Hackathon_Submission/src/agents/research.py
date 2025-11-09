"""Research Agent for retrieving relevant research content."""
from __future__ import annotations
from typing import List, Dict, Any, Optional
import json
from src.utils.config import load_settings
from src.tools.vectorstore_new import VectorStore
from src.tools.websearch import WebSearch
from src.tools.loaders import FileLoader, APILoader

SETTINGS = load_settings()

class ResearchAgent:
    """Retrieves and processes research content."""
    def __init__(self, settings=None):
        self.settings = settings or SETTINGS
        self.vector = VectorStore()
        self.websearch = WebSearch()
    
    def search(self,
             query: str,
             constraints: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for research content."""
        constraints = constraints or {}
        max_results = constraints.get('max_results', 20)
        min_score = constraints.get('min_score', 0.7)
        
        # Search vector store
        vec_results = self._search_vectors(
            query=query,
            top_k=max_results,
            min_score=min_score
        )
        
        # Search web if needed
        if len(vec_results) < max_results:
            web_results = self._search_web(
                query=query,
                max_results=max_results - len(vec_results)
            )
            
            # Merge results
            if web_results:
                vec_results.extend(web_results)
        
        return vec_results
    
    def process_files(self,
                     files: List[str],
                     source_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Process files into searchable passages."""
        source_types = source_types or ['text', 'pdf']
        passages = []
        
        for file_path in files:
            try:
                # Load content based on file type
                if file_path.lower().endswith('.pdf'):
                    content = FileLoader.load_pdf_text(file_path)
                else:
                    content = FileLoader.load_text(file_path)
                # Convert to passages
                file_passages = self._split_content(content, source=file_path)
                if file_passages:
                    passages.extend(file_passages)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        return passages
    
    def process_urls(self,
                    urls: List[str]) -> List[Dict[str, Any]]:
        """Process web URLs into searchable passages."""
        passages = []
        
        for url in urls:
            try:
                # Load content from URL
                loader = APILoader()
                content = loader.load_data(url)
                
                # Convert to passages
                url_passages = self._split_content(content, source=url)
                if url_passages:
                    passages.extend(url_passages)
                    
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue
        
        return passages
    
    def _search_vectors(self,
                       query: str,
                       top_k: int = 10,
                       min_score: float = 0.7) -> List[Dict[str, Any]]:
        """Search vector store for relevant passages."""
        try:
            results = self.vector.search(
                query=query,
                top_k=top_k,
                min_score=min_score
            )
            
            return [
                {
                    'id': r.get('id'),
                    'text': r.get('text', ''),
                    'score': r.get('score', 0.0),
                    'meta': r.get('meta', {})
                }
                for r in results if r.get('text')
            ]
            
        except Exception as e:
            print(f"Vector search error: {e}")
            return []
    
    def _search_web(self,
                    query: str,
                    max_results: int = 10) -> List[Dict[str, Any]]:
        """Search web for relevant content."""
        try:
            results = self.websearch.search(
                query=query,
                max_results=max_results
            )
            
            passages = []
            for r in results:
                if r.get('text'):
                    passages.extend(
                        self._split_content(r['text'], source=r.get('url', 'web'))
                    )
                    
            return passages[:max_results]
            
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    
    def _split_content(self,
                      text: str,
                      source: str,
                      min_length: int = 100,
                      max_length: int = 1000) -> List[Dict[str, str]]:
        """Split content into manageable passages."""
        passages = []
        
        # Basic sentence splitting
        sentences = text.split('. ')
        current = []
        current_len = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if adding this sentence exceeds max length
            if current_len + len(sentence) > max_length and current:
                # Save current passage
                passage_text = '. '.join(current) + '.'
                if len(passage_text) >= min_length:
                    passages.append({
                        'source': source,
                        'text': passage_text
                    })
                current = []
                current_len = 0
            
            # Add sentence to current passage    
            current.append(sentence)
            current_len += len(sentence)
        
        # Handle remaining text
        if current:
            passage_text = '. '.join(current) + '.'
            if len(passage_text) >= min_length:
                passages.append({
                    'source': source,
                    'text': passage_text
                })
        
        return passages