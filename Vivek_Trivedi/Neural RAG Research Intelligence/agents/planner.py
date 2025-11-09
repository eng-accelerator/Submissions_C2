"""Research Planner Agent."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel

from .base import PlannerOutput, PlannerTask


PLANNER_SYSTEM_PROMPT = """You are an expert research strategist. Given a user query, break it into actionable research tasks.
Return JSON with keys: sub_questions (list of objects with question + rationale), key_entities, priority_topics."""


@dataclass
class ResearchPlannerAgent:
    llm: BaseLanguageModel

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", PLANNER_SYSTEM_PROMPT),
            ("user", "Research query: {query}"),
        ])

    def run(self, query: str) -> PlannerOutput:
        prompt = self.build_prompt()
        response = self.llm.invoke(prompt.format_messages(query=query))
        content = getattr(response, "content", str(response))
        data = self._safe_parse_json(content)
        return PlannerOutput(
            sub_questions=[PlannerTask(**item) for item in data.get("sub_questions", [])],
            key_entities=data.get("key_entities", []),
            priority_topics=data.get("priority_topics", []),
        )

    @staticmethod
    def _safe_parse_json(raw: str) -> dict:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {
                "sub_questions": [],
                "key_entities": [],
                "priority_topics": [],
            }
