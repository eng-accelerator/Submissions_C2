"""Insight Generation Agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel

from .base import InsightOutput, AnalysisPoint


INSIGHT_SYSTEM_PROMPT = """You are an insight-generation specialist. Given a question and key analysis points, produce strictly JSON output matching this schema:
{{
  "hypotheses": ["..."],
  "trends": ["..."],
  "reasoning_steps": ["..."],
}}
Each list should contain at least one informative entry. Avoid empty strings and paraphrase the provided analysis points when needed."""


@dataclass
class InsightGenerationAgent:
    llm: BaseLanguageModel

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", INSIGHT_SYSTEM_PROMPT),
            ("user", "Question: {query}\n\nKey Points:\n{points}"),
        ])

    def run(self, query: str, key_points: List[AnalysisPoint]) -> InsightOutput:
        prompt = self.build_prompt()
        serialized_points = self._serialize_points(key_points)
        response = self.llm.invoke(prompt.format_messages(query=query, points=serialized_points))
        payload = self._safe_parse(response.content if hasattr(response, "content") else str(response))
        hypotheses = payload.get("hypotheses") or self._fallback_hypotheses(key_points)
        trends = payload.get("trends") or self._fallback_trends(key_points)
        reasoning_steps = payload.get("reasoning_steps") or self._fallback_reasoning(query, hypotheses, trends)
        return InsightOutput(
            hypotheses=hypotheses,
            trends=trends,
            reasoning_steps=reasoning_steps,
        )

    @staticmethod
    def _serialize_points(points: List[AnalysisPoint]) -> str:
        lines = []
        for pt in points:
            lines.append(f"- {pt.statement} (sources: {', '.join(pt.supporting_sources)})")
        return "\n".join(lines[:10])

    @staticmethod
    def _safe_parse(raw: str) -> dict:
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
                "hypotheses": [cleaned],
                "trends": [],
                "reasoning_steps": [],
            }

    @staticmethod
    def _fallback_hypotheses(points: List[AnalysisPoint]) -> List[str]:
        if not points:
            return ["Insufficient context to propose hypotheses."]
        return [f"Hypothesis: {pt.statement}" for pt in points[:3]]

    @staticmethod
    def _fallback_trends(points: List[AnalysisPoint]) -> List[str]:
        trends = []
        for pt in points[:3]:
            trends.append(f"Trend: Evidence from {', '.join(pt.supporting_sources) or 'context'} suggests {pt.statement}.")
        return trends or ["No observable trends identified in available context."]

    @staticmethod
    def _fallback_reasoning(query: str, hypotheses: List[str], trends: List[str]) -> List[str]:
        reasoning = [f"Started with query: {query}"]
        for hyp in hypotheses:
            reasoning.append(f"Considered hypothesis -> {hyp}")
        for tr in trends:
            reasoning.append(f"Observed trend -> {tr}")
        reasoning.append("Derived insights from available key points due to missing LLM output.")
        return reasoning
