from __future__ import annotations
from typing import List, Dict, Any
from src.tools.loaders import FileLoader, HTMLLoader
from src.tools.websearch import WebSearchTool
from src.tools.vectorstore import VectorStore
from src.utils.config import load_settings
from hashlib import sha256
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SETTINGS = load_settings()

def canonical_id(source_url: str) -> str:
    return sha256(source_url.encode('utf-8')).hexdigest()[:12]

class RetrieverAgent:
    def __init__(self, settings=None):
        self.settings = settings or SETTINGS
        path = os.getenv('FAISS_INDEX_PATH', './data/faiss.index')
        self.vector = VectorStore(path=path)

    def fetch_seed(self, seeds: List[str]) -> List[Dict[str,Any]]:
        docs = []
        for s in seeds or []:
            if s.lower().endswith('.pdf'):
                txt = FileLoader.load_pdf_text(s)
            else:
                txt = HTMLLoader.load_text(s)
            docs.append({'id': canonical_id(s), 'url': s, 'text': txt})
        return docs

    def search_web(self, query: str, domains=None, time_window=None, top_k=8):
        hits = WebSearchTool.search(query, domains=domains, time_window=time_window, top_k=top_k)
        docs = []
        for h in hits:
            docs.append({'id': canonical_id(h.get('url','')), 'url': h.get('url'), 'text': h.get('snippet',''), 'meta': h})
        return docs

    def embed_and_store(self, docs: List[Dict[str,Any]]):
        for d in docs:
            self.vector.upsert(id=d['id'], text=d.get('text',''), meta=d.get('meta',{}))

    def retrieve(self, query: str, top_k: int = 8, domains=None, time_window=None) -> List[Dict[str,Any]]:
        web_docs = self.search_web(query, domains=domains, time_window=time_window, top_k=top_k)
        self.embed_and_store(web_docs)
        hits = self.vector.query(query, top_k=top_k)
        passages = []
        for h in hits:
            passages.append({'id': h['id'], 'text': h['text'][:2000], 'url': h.get('meta',{}).get('url')})
        return passages
