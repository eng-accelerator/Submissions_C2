"""
Contextual Retriever Agent for MediScout.

Retrieves relevant documents from multiple sources (knowledge base + PubMed).
"""

import time
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from mediscout.config import get_settings
from mediscout.knowledge_base import KnowledgeBase
from mediscout.services.pubmed_client import PubMedClient
from mediscout.schemas import Document, RetrievalResult
from mediscout.state import ResearchState


class RetrieverAgent:
    """Agent for multi-source document retrieval."""
    
    def __init__(self):
        """Initialize retriever with knowledge base and API clients."""
        self.settings = get_settings()
        self.knowledge_base = KnowledgeBase()
        self.pubmed_client = PubMedClient()
        
        logger.info("Retriever Agent initialized")
    
    def __call__(self, state: ResearchState) -> Dict[str, Any]:
        """
        Retrieve relevant documents based on search scope (parallelized for speed).
        
        Args:
            state: Current research state
            
        Returns:
            Updated state with retrieved documents
        """
        query = state.get("refined_query") or state["research_topic"]
        search_scope = state.get("search_scope", "local_and_pubmed")
        
        logger.info(f"Retrieving documents for query: '{query}' (scope: {search_scope})")
        
        start_time = time.time()
        user_docs = []
        pubmed_docs = []
        sources_used = []
        
        # Determine which sources to search based on scope
        search_local = search_scope in ["local_only", "local_and_pubmed"]
        search_pubmed = search_scope in ["pubmed_only", "local_and_pubmed"]
        
        # Use ThreadPoolExecutor for parallel searches with timeouts
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}
            
            # Submit searches based on scope
            if search_local:
                futures["kb"] = executor.submit(self._search_knowledge_base, query)
            
            if search_pubmed:
                futures["pubmed"] = executor.submit(self._search_pubmed, query)
            
            # Get results with BALANCED timeouts (fast but allow completion)
            if "kb" in futures:
                try:
                    user_docs = futures["kb"].result(timeout=3.0)  # 3s for local KB
                    if user_docs:
                        sources_used.append("user")
                        logger.info(f"⚡ LOCAL KB: Found {len(user_docs)} documents (scores: {[f'{d.relevance_score:.2f}' for d in user_docs[:3]]})")
                except FutureTimeoutError:
                    logger.warning("⏱️ Knowledge base search timed out after 3s")
                except Exception as e:
                    logger.error(f"❌ Knowledge base search failed: {e}", exc_info=True)
            
            if "pubmed" in futures:
                try:
                    pubmed_docs = futures["pubmed"].result(timeout=10.0)  # 10s for PubMed (API is slow)
                    if pubmed_docs:
                        sources_used.append("pubmed")
                        logger.info(f"🌐 PUBMED: Found {len(pubmed_docs)} articles: {[d.title[:50] for d in pubmed_docs[:3]]}")
                    else:
                        logger.warning("⚠️ PubMed returned 0 results")
                except FutureTimeoutError:
                    logger.warning("⏱️ PubMed search timed out after 10s (continuing with available results)")
                except Exception as e:
                    logger.error(f"❌ PubMed search failed: {e}", exc_info=True)
        
        # Combine and sort by relevance
        all_docs = self._combine_and_rank(user_docs, pubmed_docs)
        
        retrieval_time = time.time() - start_time
        
        # Create retrieval result
        retrieval_result = RetrievalResult(
            query=query,
            user_documents=user_docs,
            pubmed_documents=pubmed_docs,
            total_count=len(all_docs),
            sources_used=sources_used,
            retrieval_time_seconds=retrieval_time
        )
        
        logger.info(
            f"Retrieval complete: {len(all_docs)} total documents "
            f"from {len(sources_used)} sources in {retrieval_time:.2f}s"
        )
        
        return {
            "retrieval_result": retrieval_result,
            "retrieved_documents": all_docs,
            "current_stage": "documents_retrieved"
        }
    
    def _search_knowledge_base(self, query: str) -> List[Document]:
        """Search local knowledge base (for parallel execution - FAST)."""
        try:
            logger.info("⚡ Searching local knowledge base...")
            results = self.knowledge_base.search(
                query=query,
                top_k=3  # REDUCED to 3 for speed
            )
            logger.info(f"KB search complete: {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"KB search error: {e}", exc_info=True)
            return []
    
    def _search_pubmed(self, query: str) -> List[Document]:
        """Search PubMed (for parallel execution - FAST)."""
        try:
            logger.info("🌐 Searching PubMed...")
            results = self.pubmed_client.search(
                query=query,
                max_results=3  # REDUCED to 3 for speed
            )
            logger.info(f"PubMed search complete: {len(results)} articles retrieved")
            return results
        except Exception as e:
            logger.error(f"PubMed search error: {e}", exc_info=True)
            return []
    
    def _combine_and_rank(
        self,
        user_docs: List[Document],
        pubmed_docs: List[Document]
    ) -> List[Document]:
        """
        Combine documents from multiple sources and rank by relevance.
        
        Args:
            user_docs: Documents from knowledge base
            pubmed_docs: Documents from PubMed
            
        Returns:
            Combined and ranked list of documents
        """
        all_docs = user_docs + pubmed_docs
        
        # If we have relevance scores, sort by them
        if all_docs and all_docs[0].relevance_score is not None:
            all_docs.sort(key=lambda d: d.relevance_score or 0.0, reverse=True)
        
        # Limit to top_k
        all_docs = all_docs[:self.settings.top_k_results]
        
        logger.info(f"Ranked and limited to top {len(all_docs)} documents")
        return all_docs
    
    def ingest_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Ingest multiple documents into knowledge base.
        
        Args:
            file_paths: List of file paths to ingest
            
        Returns:
            Ingestion results
        """
        results = {
            "successful": [],
            "failed": [],
            "total_chunks": 0
        }
        
        for file_path in file_paths:
            try:
                chunks, doc_id = self.knowledge_base.ingest_document(Path(file_path))
                results["successful"].append({
                    "file": file_path,
                    "doc_id": doc_id,
                    "chunks": chunks
                })
                results["total_chunks"] += chunks
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")
                results["failed"].append({
                    "file": file_path,
                    "error": str(e)
                })
        
        return results

