"""Contextual Retriever Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from deep_research import (
    load_vector_index,
    TavilyConnector,
    ArxivConnector,
    WikipediaConnector,
    SourceDocument,
)
from deep_research.eval_logging import create_event, log_retrieval_event

from .base import ContextualRetrievalOutput, RetrievedContext


@dataclass
class RetrieverConfig:
    similarity_top_k: int = 5
    similarity_cutoff: float = 0.5
    use_database: bool = True
    use_tavily: bool = False
    use_arxiv: bool = False
    use_wikipedia: bool = False
    tavily_results: int = 4
    arxiv_results: int = 3
    wikipedia_results: int = 2


@dataclass
class ContextualRetrieverAgent:
    config: RetrieverConfig = field(default_factory=RetrieverConfig)
    vector_index: Optional[VectorStoreIndex] = None
    tavily: Optional[TavilyConnector] = None
    arxiv: Optional[ArxivConnector] = None
    wikipedia: Optional[WikipediaConnector] = None

    def __post_init__(self):
        self._ensure_embeddings()
        if self.vector_index is None and self.config.use_database:
            self.vector_index, self.vector_status = load_vector_index()
        elif self.vector_index is not None:
            self.vector_status = "Vector index injected."
        else:
            self.vector_status = "Vector store disabled."
        if self.config.use_tavily and self.tavily is None:
            self.tavily = TavilyConnector()
        if self.config.use_arxiv and self.arxiv is None:
            self.arxiv = ArxivConnector()
        if self.config.use_wikipedia and self.wikipedia is None:
            self.wikipedia = WikipediaConnector()

    def run(self, query: str) -> ContextualRetrievalOutput:
        contexts: List[RetrievedContext] = []
        notes: List[str] = []
        if self.vector_status:
            notes.append(self.vector_status)

        if self.config.use_database and self.vector_index is not None:
            contexts.extend(self._retrieve_from_vector_store(query, notes))
        else:
            notes.append("Vector store disabled or unavailable.")

        contexts.extend(self._retrieve_external_sources(query, notes))

        return ContextualRetrievalOutput(contexts=contexts, notes=notes)

    def _retrieve_from_vector_store(self, query: str, notes: List[str]) -> List[RetrievedContext]:
        retriever = VectorIndexRetriever(
            index=self.vector_index,
            similarity_top_k=self.config.similarity_top_k,
        )
        nodes = retriever.retrieve(query)
        filtered: List[RetrievedContext] = []
        for node in nodes:
            score = getattr(node, "score", None)
            passed = (score is None) or (score >= self.config.similarity_cutoff)
            metadata = getattr(node.node, "metadata", {}) if hasattr(node, "node") else {}
            doc_identifier = metadata.get("file_name") or metadata.get("file_path") or "unknown"
            log_retrieval_event(
                create_event(
                    query=query,
                    source="database",
                    doc_identifier=str(doc_identifier),
                    score=score,
                    passed_cutoff=passed,
                    metadata=str(metadata)[:250],
                )
            )
            if not passed:
                continue
            filtered.append(
                RetrievedContext(
                    content=node.text,
                    source=str(doc_identifier),
                    score=score,
                    metadata=dict(metadata),
                )
            )
        if not filtered:
            notes.append("No database chunks met the similarity cutoff.")
        return filtered

    def _retrieve_external_sources(self, query: str, notes: List[str]) -> List[RetrievedContext]:
        results: List[RetrievedContext] = []
        if self.config.use_tavily and self.tavily:
            try:
                tavily_docs = self.tavily.search(query, max_results=self.config.tavily_results)
                results.extend(self._convert_source_docs(tavily_docs, "tavily", query))
            except Exception as exc:
                notes.append(f"Tavily error: {exc}")
        if self.config.use_arxiv and self.arxiv:
            try:
                arxiv_docs = self.arxiv.search(query, max_results=self.config.arxiv_results)
                results.extend(self._convert_source_docs(arxiv_docs, "arxiv", query))
            except Exception as exc:
                notes.append(f"ArXiv error: {exc}")
        if self.config.use_wikipedia and self.wikipedia:
            try:
                wiki_docs = self.wikipedia.search(query, max_results=self.config.wikipedia_results)
                results.extend(self._convert_source_docs(wiki_docs, "wikipedia", query))
            except Exception as exc:
                notes.append(f"Wikipedia error: {exc}")
        return results

    def _convert_source_docs(
        self, docs: List[SourceDocument], source_name: str, query: str
    ) -> List[RetrievedContext]:
        converted: List[RetrievedContext] = []
        for doc in docs:
            log_retrieval_event(
                create_event(
                    query=query,
                    source=source_name,
                    doc_identifier=doc.url or doc.title,
                    score=None,
                    passed_cutoff=True,
                    metadata=str(doc.metadata)[:250],
                )
            )
            converted.append(
                RetrievedContext(
                    content=doc.content,
                    source=f"{source_name}:{doc.title}",
                    score=None,
                    metadata={"url": doc.url, **doc.metadata},
                )
            )
        return converted

    @staticmethod
    def _ensure_embeddings():
        if getattr(Settings, "_embed_model", None) is not None:
            return
        model_name = os.getenv("A3B_EMBED_MODEL", "BAAI/bge-small-en-v1.5")
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=model_name,
            trust_remote_code=True,
        )
