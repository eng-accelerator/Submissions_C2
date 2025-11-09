"""Report Builder Agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel

from .base import ReportOutput, CriticalAnalysisOutput, InsightOutput


REPORT_SYSTEM_PROMPT = """You are a research report writer. Using the analysis summary, key points, contradictions, and generated insights, craft a professional report with:
- executive_summary (2 paragraphs max)
- detailed_findings (markdown-style sections with bullet lists citing sources where possible)
- citations (list of source identifiers referenced). Always include at least one citation.
Return strict JSON with these keys."""


@dataclass
class ReportBuilderAgent:
    llm: BaseLanguageModel

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", REPORT_SYSTEM_PROMPT),
            (
                "user",
                "Question: {query}\n\nAnalysis Summary:\n{summary}\n\nKey Points:\n{key_points}\nContradictions:\n{contradictions}\nInsights:\n{insights}",
            ),
        ])

    def run(
        self,
        query: str,
        analysis: CriticalAnalysisOutput,
        insights: InsightOutput,
    ) -> ReportOutput:
        prompt = self.build_prompt()
        messages = prompt.format_messages(
            query=query,
            summary=analysis.summary,
            key_points=self._serialize_key_points(analysis),
            contradictions="\n".join(analysis.contradictions) or "None",
            insights=self._serialize_insights(insights),
        )
        response = self.llm.invoke(messages)
        payload = self._safe_parse(response.content if hasattr(response, "content") else str(response))
        citations = payload.get("citations") or analysis.validated_sources or [
            src for point in analysis.key_points for src in point.supporting_sources
        ]
        findings = payload.get("detailed_findings", "")
        if isinstance(findings, dict):
            findings = "\n".join(f"- {k}: {v}" for k, v in findings.items())
        elif isinstance(findings, list):
            findings = "\n".join(str(item) for item in findings)
        return ReportOutput(
            executive_summary=payload.get("executive_summary", ""),
            detailed_findings=str(findings),
            citations=citations or [],
        )

    @staticmethod
    def _serialize_key_points(analysis: CriticalAnalysisOutput) -> str:
        lines = []
        for point in analysis.key_points:
            sources = ", ".join(point.supporting_sources) or "context"
            lines.append(f"- {point.statement} (sources: {sources})")
        return "\n".join(lines)

    @staticmethod
    def _serialize_insights(insights: InsightOutput) -> str:
        lines = ["Hypotheses:"] + [f"  - {hyp}" for hyp in insights.hypotheses]
        lines.append("Trends:")
        lines.extend([f"  - {tr}" for tr in insights.trends])
        lines.append("Reasoning:")
        lines.extend([f"  - {step}" for step in insights.reasoning_steps])
        return "\n".join(lines)

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
                "executive_summary": cleaned,
                "detailed_findings": cleaned,
                "citations": [],
            }
