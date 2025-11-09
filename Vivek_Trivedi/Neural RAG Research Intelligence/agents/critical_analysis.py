"""Critical Analysis Agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel

from .base import (
    CriticalAnalysisOutput,
    AnalysisPoint,
    RetrievedContext,
)


CRITICAL_ANALYSIS_SYSTEM_PROMPT = """You are a critical analyst. Given retrieved context snippets, produce:
- summary (paragraph)
- key_points (JSON list of {{statement, supporting_sources}})
- contradictions (list)
- validated_sources (list of source identifiers).
Always respond as compact JSON with these keys."""


@dataclass
class CriticalAnalysisAgent:
    llm: BaseLanguageModel

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", CRITICAL_ANALYSIS_SYSTEM_PROMPT),
            ("user", "Question: {query}\n\nContext:\n{context}"),
        ])

    def run(self, query: str, contexts: List[RetrievedContext]) -> CriticalAnalysisOutput:
        serialized_context = self._serialize_contexts(contexts)
        prompt = self.build_prompt()
        response = self.llm.invoke(prompt.format_messages(query=query, context=serialized_context))
        payload = self._safe_json(response.content if hasattr(response, "content") else str(response))
        return CriticalAnalysisOutput(
            summary=payload.get("summary", ""),
            key_points=[AnalysisPoint(**kp) for kp in payload.get("key_points", [])],
            contradictions=payload.get("contradictions", []),
            validated_sources=payload.get("validated_sources", []),
        )

    @staticmethod
    def _serialize_contexts(contexts: List[RetrievedContext]) -> str:
        lines = []
        for ctx in contexts:
            lines.append(f"Source: {ctx.source}\nScore: {ctx.score}\nContent: {ctx.content}")
        return "\n\n".join(lines[:10])

    @staticmethod
    def _safe_json(raw: str) -> dict:
        import json

        cleaned = raw.strip()
        if cleaned.startswith("```") and cleaned.endswith("```"):
            cleaned = cleaned.strip("`").strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "summary": cleaned,
                "key_points": [],
                "contradictions": [],
                "validated_sources": [],
            }
