from __future__ import annotations
import os
import pickle
from typing import List, Dict, Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.utils.llm import get_embeddings


class VectorStore:
    """Hybrid VectorStore.

    - If LangChain + FAISS + embeddings are available and an embeddings key is set,
      use FAISS semantic retrieval.
    - Otherwise fall back to a simple TF-IDF store (as before).

    Methods: upsert(id,text,meta), query(text, top_k)
    """
    def __init__(self, path: str = './data/faiss.index'):
        self.path = path
        self.ids: List[str] = []
        self.texts: List[str] = []
        self.meta: Dict[str, Dict[str, Any]] = {}

        # TF-IDF fallback state
        self._vectorizer = TfidfVectorizer(stop_words='english')
        self._matrix = None

        # FAISS/LangChain state
        self._use_faiss = False
        self._faiss_index = None
        self._faiss_docs: List[Document] = []
        self._embeddings = None

        # Decide whether to enable FAISS mode
        if _HAS_LANGCHAIN and os.getenv('OPENAI_API_KEY'):
            try:
                self._embeddings = OpenAIEmbeddings()
                self._use_faiss = True
            except Exception:
                self._use_faiss = False

        # Load persisted TF-IDF store if present
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'rb') as f:
                    obj = pickle.load(f)
                    self.ids = obj.get('ids', [])
                    self.texts = obj.get('texts', [])
                    self.meta = obj.get('meta', {})
                    if self.texts:
                        self._matrix = self._vectorizer.fit_transform(self.texts)
            except Exception:
                pass

    def _persist(self):
        try:
            with open(self.path, 'wb') as f:
                pickle.dump({'ids': self.ids, 'texts': self.texts, 'meta': self.meta}, f)
        except Exception:
            pass

    def delete(self, id: str) -> bool:
        """Delete a document by ID from the vector store.
        
        Returns True if document was found and deleted, False otherwise.
        """
        try:
            if id in self.meta:
                # Find index of document to remove
                idx = self.ids.index(id)
                
                # Remove from lists and dict
                self.ids.pop(idx)
                self.texts.pop(idx)
                self.meta.pop(id)
                
                # Rebuild TF-IDF matrix if needed
                if self.texts:
                    self._matrix = self._vectorizer.fit_transform(self.texts)
                else:
                    self._matrix = None
                    
                # Remove from FAISS index if present
                if self._use_faiss and self._faiss_index is not None:
                    # Create new index without this document
                    remaining_docs = []
                    for i, doc_id in enumerate(self.ids):
                        if doc_id != id:  # Only include docs that aren't being deleted
                            meta = self.meta.get(doc_id, {})
                            # Filter out None values from metadata
                            meta = {k: v for k, v in meta.items() if v is not None}
                            remaining_docs.append(Document(
                                page_content=self.texts[i],
                                metadata={'id': doc_id, **meta}
                            ))
                    if remaining_docs:
                        self._faiss_index = LangChainFAISS.from_documents(
                            remaining_docs,
                            self._embeddings
                        )
                    else:
                        self._faiss_index = None
                        
                # Save changes
                self._persist()
                return True
            return False
        except Exception as e:
            print(f"Error deleting document {id}: {e}")
            return False

    def upsert(self, id: str, text: str, meta: Dict[str, Any] | None = None):
        # Normalize id
        if id in self.ids:
            idx = self.ids.index(id)
            self.texts[idx] = text
        else:
            self.ids.append(id)
            self.texts.append(text)

        if meta:
            self.meta[id] = meta

        if self._use_faiss:
            # Rebuild FAISS index from all stored docs (simple but safe)
            try:
                # Create LangChain Document list with validated metadata
                self._faiss_docs = []
                for i, t in zip(self.ids, self.texts):
                    if t.strip():  # Skip empty documents
                        meta = self.meta.get(i, {})
                        # Filter out None values from metadata
                        meta = {k: v for k, v in meta.items() if v is not None}
                        self._faiss_docs.append(Document(
                            page_content=t,
                            metadata={'id': i, **meta}
                        ))
                
                if self._faiss_docs:
                    self._faiss_index = LangChainFAISS.from_documents(self._faiss_docs, self._embeddings)
                else:
                    self._faiss_index = None
            except Exception as e:
                # Fallback to TF-IDF mode if embeddings fail
                print('FAISS rebuild failed, falling back to TF-IDF:', e)
                self._use_faiss = False

        if not self._use_faiss:
            # rebuild TF-IDF matrix
            if self.texts:
                self._matrix = self._vectorizer.fit_transform(self.texts)
            self._persist()

    def query(self, text: str, top_k: int = 8, min_score: float = 0.1) -> List[Dict[str, Any]]:
        if self._use_faiss and self._faiss_index is not None:
            try:
                # Include more results initially to allow for better filtering
                docs_and_scores = self._faiss_index.similarity_search_with_score(text, k=top_k * 3)  # Get more candidates
                out = []
                for doc, score in docs_and_scores:
                    # Normalize FAISS score to 0-1 range with adjusted scaling
                    norm_score = 1.0 / (1.0 + score/2)  # Adjusted normalization to be more lenient
                    # More permissive score threshold
                    if norm_score < min_score:
                        continue
                    meta = doc.metadata or {}
                    doc_id = meta.get('id') or meta.get('source') or None
                    # Only include if content exists
                    if doc.page_content and doc.page_content.strip():
                        out.append({
                            'id': doc_id,
                            'text': doc.page_content,
                            'score': float(norm_score),
                            'meta': meta
                        })
                # Sort by score and take top_k
                out.sort(key=lambda x: float(x['score']), reverse=True)
                return out[:top_k]
            except Exception as e:
                print('FAISS query failed, falling back to TF-IDF:', e)
                # fall through to TF-IDF

        # TF-IDF fallback
        if not self.texts or self._matrix is None:
            return []
        qv = self._vectorizer.transform([text])
        sims = cosine_similarity(qv, self._matrix).flatten()
        idxs = np.argsort(-sims)[:top_k * 2]  # Get more results for filtering
        out = []
        for i in idxs:
            score = float(sims[i])
            if score >= min_score:
                out.append({'id': self.ids[i], 'text': self.texts[i], 'score': score, 'meta': self.meta.get(self.ids[i], {})})
        return out
