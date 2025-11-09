"""Vector storage with FAISS.

Improvements added:
- Explicit L2 normalization of embeddings (remote or local) before adding to FAISS.
- More robust keyword fallback tokenization (handles punctuation, possessives, plurals).
- Logging of fallback path and match counts for debugging retrieval issues.
"""
from __future__ import annotations
import os
import pickle
import re
import logging
from typing import List, Dict, Any
import numpy as np
import faiss
from src.utils.llm import get_embeddings

class VectorStore:
    """Vector store using FAISS for efficient similarity search."""
    def __init__(self, path: str = './data/faiss.index'):
        self.path = path
        self.ids: List[str] = []
        self.texts: List[str] = []
        self.meta: Dict[str, Dict[str, Any]] = {}
        self.embeddings: List[List[float]] = []
        self.index = None

        # Load existing index if available
        self._load()
    
    def _load(self):
        """Load persisted vector store."""
        if os.path.exists(self.path):
            try:
                with open(self.path, 'rb') as f:
                    data = pickle.load(f)
                    self.ids = data.get('ids', [])
                    self.texts = data.get('texts', [])
                    self.meta = data.get('meta', {})
                    self.embeddings = data.get('embeddings', [])

                    if self.embeddings:
                        # Detect if embeddings are all near-zero (broken prior run) and repair
                        arr = np.array(self.embeddings, dtype='float32')
                        norms = np.linalg.norm(arr, axis=1)
                        if float(np.median(norms)) < 1e-6:
                            # Re-embed locally to repair
                            prev_mode = os.environ.get('EMBEDDINGS_MODE', '')
                            os.environ['EMBEDDINGS_MODE'] = 'local'
                            try:
                                repaired = get_embeddings(self.texts)
                                self.embeddings = repaired
                            finally:
                                if prev_mode:
                                    os.environ['EMBEDDINGS_MODE'] = prev_mode
                                else:
                                    os.environ.pop('EMBEDDINGS_MODE', None)
                            self._persist()

                        # Recreate FAISS index
                        dim = len(self.embeddings[0])
                        self.index = faiss.IndexFlatIP(dim)
                        self.index.add(np.array(self.embeddings).astype('float32'))
                        
            except Exception as e:
                print(f"Error loading vector store: {e}")

    def _persist(self):
        """Save vector store to disk."""
        try:
            with open(self.path, 'wb') as f:
                pickle.dump({
                    'ids': self.ids,
                    'texts': self.texts,
                    'meta': self.meta,
                    'embeddings': self.embeddings
                }, f)
        except Exception as e:
            print(f"Error saving vector store: {e}")

    def delete(self, id: str) -> bool:
        """Delete a document by ID."""
        try:
            if id in self.meta:
                idx = self.ids.index(id)
                
                # Remove from all lists
                self.ids.pop(idx)
                self.texts.pop(idx)
                self.meta.pop(id)
                self.embeddings.pop(idx)
                
                # Rebuild FAISS index
                if self.embeddings:
                    dim = len(self.embeddings[0])
                    self.index = faiss.IndexFlatIP(dim)
                    self.index.add(np.array(self.embeddings).astype('float32'))
                else:
                    self.index = None
                    
                self._persist()
                return True
                
            return False
            
        except Exception as e:
            print(f"Error deleting document {id}: {e}")
            return False

    def upsert(self, id: str, text: str, meta: Dict[str, Any] | None = None):
        """Add or update a document."""
        try:
            # Generate embedding
            embedding = get_embeddings([text])[0]
            # Detect all-zero embedding and replace with local hash fallback (first 384 dims non-zero)
            if not any(embedding):
                import hashlib, math
                tokens = [t.lower() for t in re.findall(r"[A-Za-z0-9_]+", text)]
                dim_local = 384
                buckets = [0.0] * dim_local
                for tok in tokens:
                    h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
                    buckets[h % dim_local] += 1.0
                total = len(tokens) or 1
                buckets = [math.log1p(v / total) for v in buckets]
                norm = math.sqrt(sum(v*v for v in buckets)) or 1.0
                buckets = [v / norm for v in buckets]
                embedding = buckets + [0.0] * (len(embedding) - dim_local)

            # L2 normalize embedding to keep inner products comparable and <=1
            arr = np.array(embedding, dtype='float32')
            norm = float(np.linalg.norm(arr)) or 1.0
            embedding = (arr / norm).tolist()
            
            # Update or append
            if id in self.ids:
                idx = self.ids.index(id)
                self.texts[idx] = text
                self.embeddings[idx] = embedding
            else:
                self.ids.append(id)
                self.texts.append(text)
                self.embeddings.append(embedding)

            if meta:
                self.meta[id] = meta

            # Rebuild FAISS index
            if self.embeddings:
                dim = len(embedding)
                self.index = faiss.IndexFlatIP(dim)
                self.index.add(np.array(self.embeddings).astype('float32'))
                
            self._persist()
                
        except Exception as e:
            print(f"Error upserting document {id}: {e}")

    def search(self, 
             query: str,
             top_k: int = 10,
             min_score: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            def tokenize(s: str) -> List[str]:
                # Lowercase, remove possessive/apostrophes, simple word chars
                s = s.lower()
                s = re.sub(r"'s\b", "", s)  # remove possessive 's
                tokens = re.findall(r"[a-z0-9]+", s)
                # Basic singularization for plural 's'
                normed = []
                for t in tokens:
                    if len(t) > 3 and t.endswith('s') and not t.endswith('ss'):
                        normed.append(t[:-1])
                    else:
                        normed.append(t)
                return normed

            def keyword_fallback() -> List[Dict[str, Any]]:
                q_tokens = tokenize(query)
                if not q_tokens:
                    return []
                scored = []
                for doc_id, text in zip(self.ids, self.texts):
                    t_tokens = tokenize(text)
                    token_set = set(t_tokens)
                    hits = sum(1 for w in q_tokens if w in token_set)
                    if hits:
                        # Normalize score to 0-1 by dividing by query token count
                        scored.append({
                            'id': doc_id,
                            'text': text,
                            'score': float(hits) / float(len(q_tokens)),
                            'meta': self.meta.get(doc_id, {})
                        })
                scored.sort(key=lambda x: x['score'], reverse=True)
                logging.info(f"Keyword fallback used. Matches: {len(scored)} query_tokens={len(q_tokens)}")
                return scored[:top_k]

            # If index missing -> keyword fallback
            if not self.index or not self.embeddings:
                return keyword_fallback()

            # Get query embedding
            query_emb = get_embeddings([query])[0]
            # Normalize query embedding
            q_arr = np.array(query_emb, dtype='float32')
            q_norm = float(np.linalg.norm(q_arr)) or 1.0
            query_emb = (q_arr / q_norm).astype('float32')
            zero_query = not any(query_emb)

            # Search FAISS index
            if zero_query:
                # Skip vector search; fall back to keyword scoring
                D, I = np.array([[0.0]]), np.array([[0]])
            else:
                D, I = self.index.search(
                    np.array([query_emb]).reshape(1, -1).astype('float32'),
                    k=top_k * 2  # Get extra results for filtering
                )

            results = []
            for score, idx in zip(D[0], I[0]):
                if idx < len(self.ids):
                    sim_score = float(score)
                    if sim_score >= min_score:
                        results.append({
                            'id': self.ids[idx],
                            'text': self.texts[idx],
                            'score': min(sim_score, 1.0),
                            'meta': self.meta.get(self.ids[idx], {})
                        })
                        
            # If no vector results, fallback to keyword match ranking
            if not results:
                return keyword_fallback()

            # Sort by score and limit to top_k
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []