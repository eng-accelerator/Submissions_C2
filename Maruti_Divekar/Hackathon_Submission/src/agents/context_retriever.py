"""Contextual Retriever Agent for handling multiple data sources."""
from __future__ import annotations
from typing import List, Dict, Any
import os
from src.tools.loaders import FileLoader, HTMLLoader, PDFLoader, APILoader
from src.tools.websearch import WebSearch
from src.tools.vectorstore_new import VectorStore
from src.utils.config import load_settings
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlparse, urlunparse
import logging

SETTINGS = load_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('indexing.log')
    ]
)

class ContextualRetrieverAgent:
    """Enhanced retrieval agent that handles multiple data sources:
    - Research papers (PDF)
    - News articles (HTML)
    - Reports (PDF/HTML)
    - API data
    """
    def __init__(self, settings=None):
        self.settings = settings or SETTINGS
        self.vector = VectorStore(path=os.getenv('FAISS_INDEX_PATH', './data/faiss.index'))
        self.web_tool = WebSearch()
        
    def _canonical_id(self, source: str) -> str:
        return sha256(source.encode('utf-8')).hexdigest()[:12]

    def _normalize_source(self, src: str) -> str:
        """Normalize a source string to a canonical form.

        - File paths -> absolute path with file:// prefix
        - URLs -> scheme://netloc/path (no fragment)
        - Other strings are returned as-is
        """
        if not src:
            return src
        # Already URL-like
        if src.startswith('http://') or src.startswith('https://'):
            try:
                p = urlparse(src)
                # strip fragment and query for canonicalization
                p = p._replace(fragment='', query='')
                norm = urlunparse(p).rstrip('/')
                return norm
            except Exception:
                return src

        # Treat as a file path
        try:
            p = Path(src)
            if p.exists() or src.startswith('file://') or p.is_absolute():
                # remove file:// if present
                s = src[7:] if src.startswith('file://') else src
                abs_path = str(Path(s).resolve())
                return f'file://{abs_path}'
        except Exception:
            pass

        return src

    def process_files(self, files: List[str]) -> List[Dict[str, Any]]:
        """Process uploaded documents (PDF, txt, etc)."""
        docs = []
        for file_path in files:
            try:
                logging.info(f"Processing file: {file_path}")
                
                # Normalize source path
                norm = self._normalize_source(file_path)
                # Don't skip Gradio temp files anymore - we need to process them
                logging.info(f"Processing file with normalized path: {norm}")

                if file_path.lower().endswith('.pdf'):
                    # Use PyMuPDF-based loader for better PDF extraction
                    text = PDFLoader.load_text(file_path)
                    if not text.strip():
                        continue

                    # Clean and normalize the extracted text
                    text = ' '.join(text.split())  # Normalize whitespace

                    if not text.strip():
                        logging.warning(f"Skipping empty PDF: {file_path}")
                        continue

                    logging.info(f"Successfully extracted {len(text.split())} words from PDF: {file_path}")
                    # Create document with PDF-specific metadata
                    docs.append({
                        'id': self._canonical_id(norm),
                        'source': norm,
                        'text': text,
                        'type': 'document',
                        'format': 'pdf'
                    })
                else:
                    # Handle non-PDF files
                    text = FileLoader.load_text(file_path)
                    if text.strip():
                        text = ' '.join(text.split())
                        docs.append({
                            'id': self._canonical_id(norm),
                            'source': norm,
                            'text': text,
                            'type': 'document',
                            'format': 'text'
                        })
            except Exception as e:
                logging.error(f"Error processing file {file_path}: {str(e)}", exc_info=True)
                continue
        return docs

    def index_documents(self, files: List[str] = None, urls: List[str] = None) -> int:
        """Process and index provided files and urls into the vector store.

        Returns the number of documents indexed.
        """
        all_docs = []
        statuses = []
        if files:
            file_docs = self.process_files(files)
            all_docs.extend(file_docs)

        if urls:
            url_docs = self.process_urls(urls)
            all_docs.extend(url_docs)

        # Chunking parameters (match retrieve())
        CHUNK_WORDS = 180
        OVERLAP_WORDS = 30

        def chunk_text(doc_id: str, text: str):
            words = text.split()
            chunks = []
            start = 0
            while start < len(words):
                end = min(start + CHUNK_WORDS, len(words))
                chunk_words = words[start:end]
                ctext = ' '.join(chunk_words).strip()
                if ctext:
                    suffix = f"_chunk_{len(chunks)+1}" if len(words) > CHUNK_WORDS else ""
                    chunks.append((doc_id + suffix, ctext))
                if end == len(words):
                    break
                start = end - OVERLAP_WORDS
            return chunks

        # Upsert into vector store with chunking and build per-file statuses
        seen_ids = set()
        for doc in all_docs:
            source = doc.get('source')
            try:
                doc_id = doc.get('id') or self._canonical_id(source or '')
                text = (doc.get('text') or '').strip()
                # server-side validation: skip empty texts
                if not text:
                    statuses.append({'source': source, 'status': 'skipped', 'reason': 'empty content'})
                    continue

                # Skip duplicates
                if doc_id in seen_ids:
                    statuses.append({'source': source, 'status': 'skipped', 'reason': 'duplicate'})
                    continue

                # Prepare metadata
                meta = {
                    'source': source,
                    'type': doc.get('type'),
                    'title': doc.get('title', ''),
                    'url': doc.get('url', '')
                }
                meta = {k: v for k, v in meta.items() if v is not None}

                # Chunk and upsert
                chunks = chunk_text(doc_id, text)
                for cid, ctext in chunks:
                    self.vector.upsert(id=cid, text=ctext, meta=meta)

                seen_ids.add(doc_id)
                statuses.append({'source': source, 'status': 'indexed', 'id': doc_id, 'indexed_chunks': len(chunks)})
            except Exception as e:
                statuses.append({'source': source, 'status': 'error', 'reason': str(e)})

        return statuses

    def process_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Process web articles and HTML content with timeouts."""
        import concurrent.futures
        docs = []
        
        def process_url(url: str) -> Dict[str, Any] | None:
            try:
                logging.info(f"Processing URL: {url}")
                norm = self._normalize_source(url)
                # Skip malformed or transient URLs
                if not norm.startswith('http'):
                    logging.warning(f"Skipping malformed URL: {url}")
                    return None
                text = HTMLLoader.load_text(url)
                if not text.strip():
                    logging.warning(f"Skipping empty content from URL: {url}")
                    return None
                text = ' '.join(text.split())
                logging.info(f"Successfully extracted {len(text.split())} words from URL: {url}")
                return {
                    'id': self._canonical_id(norm),
                    'source': norm,
                    'text': text,
                    'type': 'web'
                }
            except Exception as e:
                logging.error(f"Error loading {url}: {e}", exc_info=True)
                return None
                
        # Process URLs in parallel with timeout
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_url, url) for url in urls]
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=15)  # 15 sec timeout per URL
                    if result:
                        docs.append(result)
                except Exception as e:
                    print(f"URL processing failed: {e}")
                    
        return docs

    def search_academic(self, query: str, constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search academic sources and research papers."""
        papers = []
        # Connect to academic APIs (arxiv, pubmed, etc) based on constraints
        return papers

    def retrieve(self, 
                query: str,
                files: List[str] = None,
                urls: List[str] = None,
                constraints: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Enhanced retrieval combining multiple sources with improved relevance."""
        logging.info(f"Retrieving content for query: {query}")
        all_docs = []
        
        # Process uploaded files first since they're explicitly provided
        if files:
            file_docs = self.process_files(files)
            logging.info(f"Found {len(file_docs)} documents from files")
            all_docs.extend(file_docs)
        
        # Process provided URLs
        if urls:
            url_docs = self.process_urls(urls)
            logging.info(f"Found {len(url_docs)} documents from URLs")
            all_docs.extend(url_docs)
        
        # Search academic sources if needed
        if constraints and constraints.get('include_academic'):
            papers = self.search_academic(query, constraints)
            logging.info(f"Found {len(papers)} academic papers")
            all_docs.extend(papers)
        
        # Web search for recent/supplementary content
        web_results = self.web_tool.search(
            query=query,
            domains=constraints.get('domains') if constraints else None,
            time_window=constraints.get('time_window') if constraints else None
        )
        logging.info(f"Found {len(web_results)} web results")
        all_docs.extend(web_results)
        
        # Log the total number of documents being processed
        logging.info(f"Processing total of {len(all_docs)} documents")
        
        # Index everything in vector store (with chunking for better granularity)
        logging.info("Starting document indexing phase (with chunking)")
        CHUNK_WORDS = 180  # target chunk size
        OVERLAP_WORDS = 30
        
        def chunk_text(doc_id: str, text: str):
            words = text.split()
            chunks = []
            start = 0
            while start < len(words):
                end = min(start + CHUNK_WORDS, len(words))
                chunk_words = words[start:end]
                chunk_text = ' '.join(chunk_words).strip()
                if chunk_text:
                    suffix = f"_chunk_{len(chunks)+1}" if len(words) > CHUNK_WORDS else ""
                    chunks.append((doc_id + suffix, chunk_text))
                if end == len(words):
                    break
                start = end - OVERLAP_WORDS  # overlap for context continuity
            return chunks
        
        for doc in all_docs:
            try:
                # Extract and validate document content
                doc_id = doc.get('id') or doc.get('source')
                if not doc_id:
                    logging.warning("Document missing ID or source - skipping")
                    continue
                    
                text = doc.get('text', '').strip()
                if not text:
                    logging.warning(f"Skipping empty document: {doc_id}")
                    continue
                
                # Prepare metadata
                meta = {
                    'source': doc.get('source'),
                    'type': doc.get('type'),
                    'title': doc.get('title', ''),
                    'url': doc.get('url', '')
                }
                
                # Filter out None values from metadata
                meta = {k: v for k, v in meta.items() if v is not None}
                
                # Chunk and index
                chunks = chunk_text(doc_id, text)
                for cid, ctext in chunks:
                    self.vector.upsert(
                        id=cid,
                        text=ctext,
                        meta=meta
                    )
                logging.info(f"Indexed {len(chunks)} chunks for document {doc_id} ({len(text.split())} words)")
            except Exception as e:
                logging.error(f"Indexing error for {doc.get('source')}: {str(e)}", exc_info=True)

        # Retrieve with adjusted scoring and improved filtering
        min_score = constraints.get('min_score', 0.05)  # Even more permissive score threshold
        top_k = constraints.get('top_k', 5) if constraints else 10

        logging.info(f"Starting retrieval with min_score={min_score}, top_k={top_k}")

        raw_results = self.vector.search(
            query,
            top_k=top_k * 2,  # Get more results initially for better filtering
            min_score=min_score
        )

        logging.info(f"Initial retrieval found {len(raw_results)} results")
        filtered = []

        # Enhanced scoring and filtering with more detailed logging
        for r in raw_results:
            try:
                # Extract and validate score
                base_score = float(r.get('score', 0))
                if base_score <= 0:
                    logging.debug("Skipping result with zero or negative score")
                    continue

                # Extract and validate metadata
                meta = r.get('meta', {}) or {}
                src = meta.get('source', '')
                doc_type = meta.get('type', '')

                # Validate content
                text = r.get('text', '').strip()
                if not text:
                    logging.debug(f"Skipping empty result from {src}")
                    continue

                logging.debug(f"Processing result from {src} with base score {base_score:.3f}")

                # Apply boosting factors
                score = base_score

                # Title relevance boost
                title = meta.get('title', '').lower()
                if title and any(term.lower() in title for term in query.split()):
                    score *= 1.3
                    logging.debug(f"Applied title boost: {score:.3f}")

                # Content relevance boost
                query_lower = query.lower()
                text_lower = text.lower()

                # Exact phrase match
                if query_lower in text_lower:
                    score *= 1.4
                    logging.debug("Applied exact match boost")

                # Word overlap boost
                query_words = set(query_lower.split())
                text_words = set(text_lower.split())
                overlap = len(query_words & text_words) / len(query_words)
                score *= (1.0 + overlap * 0.2)

                # Document type boost
                if doc_type == 'document':  # Boost documents over web results
                    score *= 1.2

                # Cap final score
                score = min(1.0, score)
                r['score'] = score

                filtered.append(r)
                logging.debug(f"Final score for {src}: {score:.3f}")
            except Exception as e:
                logging.error(f"Error processing result: {str(e)}", exc_info=True)
                continue

        # Sort by score descending and return
        filtered.sort(key=lambda x: float(x.get('score', 0)), reverse=True)
        logging.info(f"Returning {len(filtered)} filtered results")
        # Deduplicate by normalized source to avoid showing the same document twice
        seen = set()
        unique = []
        for r in filtered:
            meta = r.get('meta') or {}
            src = meta.get('source', '')
            norm = self._normalize_source(src) if src else src
            if norm in seen:
                continue
            seen.add(norm)
            unique.append(r)

        # Cap to requested top_k for predictable UI behavior
        try:
            requested_k = int(constraints.get('top_k', 5)) if constraints else 5
        except Exception:
            requested_k = 5

        return unique[:requested_k]