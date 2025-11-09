"""Base utilities for agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class PlannerTask:
    question: str
    rationale: str


@dataclass
class PlannerOutput:
    sub_questions: List[PlannerTask]
    key_entities: List[str]
    priority_topics: List[str]


@dataclass
class RetrievedContext:
    content: str
    source: str
    score: Optional[float]
    metadata: Dict[str, Any]


@dataclass
class ContextualRetrievalOutput:
    contexts: List[RetrievedContext]
    notes: List[str]


@dataclass
class AnalysisPoint:
    statement: str
    supporting_sources: List[str]


@dataclass
class CriticalAnalysisOutput:
    summary: str
    key_points: List[AnalysisPoint]
    contradictions: List[str]
    validated_sources: List[str]


@dataclass
class InsightOutput:
    hypotheses: List[str]
    trends: List[str]
    reasoning_steps: List[str]


@dataclass
class ReportOutput:
    executive_summary: str
    detailed_findings: str
    citations: List[str]
