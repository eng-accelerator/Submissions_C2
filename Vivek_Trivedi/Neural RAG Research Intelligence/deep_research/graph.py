"""LangGraph orchestration for the multi-agent researcher."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from langgraph.graph import StateGraph, END

from agents import (
    ResearchPlannerAgent,
    ContextualRetrieverAgent,
    CriticalAnalysisAgent,
    InsightGenerationAgent,
    ReportBuilderAgent,
    PlannerOutput,
    ContextualRetrievalOutput,
    CriticalAnalysisOutput,
    InsightOutput,
    ReportOutput,
)


class ResearchGraphState(dict):
    """Lightweight state container for LangGraph."""

    query: str
    planner: Optional[PlannerOutput]
    contexts: List
    analysis: Optional[CriticalAnalysisOutput]
    insights: Optional[InsightOutput]
    report: Optional[ReportOutput]
    notes: List[str]


@dataclass
class GraphAgents:
    planner: ResearchPlannerAgent
    retriever: ContextualRetrieverAgent
    analyst: CriticalAnalysisAgent
    insight: InsightGenerationAgent
    reporter: ReportBuilderAgent


def _planner_step(state: ResearchGraphState, agents: GraphAgents) -> ResearchGraphState:
    planner_output = agents.planner.run(state["query"])
    state["planner"] = planner_output
    return state


def _retriever_step(state: ResearchGraphState, agents: GraphAgents) -> ResearchGraphState:
    query = state["query"]
    contexts = agents.retriever.run(query)
    state["contexts"] = contexts.contexts
    notes = state.setdefault("notes", [])
    notes.extend(contexts.notes)
    return state


def _analysis_step(state: ResearchGraphState, agents: GraphAgents) -> ResearchGraphState:
    analysis = agents.analyst.run(state["query"], state.get("contexts", []))
    state["analysis"] = analysis
    return state


def _insight_step(state: ResearchGraphState, agents: GraphAgents) -> ResearchGraphState:
    insights = agents.insight.run(state["query"], state["analysis"].key_points if state.get("analysis") else [])
    state["insights"] = insights
    return state


def _report_step(state: ResearchGraphState, agents: GraphAgents) -> ResearchGraphState:
    if state.get("analysis") and state.get("insights"):
        report = agents.reporter.run(state["query"], state["analysis"], state["insights"])
        state["report"] = report
    return state


def build_research_graph(agents: GraphAgents) -> StateGraph:
    graph = StateGraph(ResearchGraphState)
    graph.add_node("planner", lambda state: _planner_step(state, agents))
    graph.add_node("retriever", lambda state: _retriever_step(state, agents))
    graph.add_node("analysis", lambda state: _analysis_step(state, agents))
    graph.add_node("insight", lambda state: _insight_step(state, agents))
    graph.add_node("report", lambda state: _report_step(state, agents))

    graph.set_entry_point("planner")
    graph.add_edge("planner", "retriever")
    graph.add_edge("retriever", "analysis")
    graph.add_edge("analysis", "insight")
    graph.add_edge("insight", "report")
    graph.add_edge("report", END)

    return graph.compile()


def run_research(graph, query: str) -> Dict[str, Any]:
    initial_state: ResearchGraphState = {
        "query": query,
        "planner": None,
        "contexts": [],
        "analysis": None,
        "insights": None,
        "report": None,
        "notes": [],
    }
    result = graph.invoke(initial_state)
    return {
        "planner": result.get("planner"),
        "contexts": result.get("contexts", []),
        "analysis": result.get("analysis"),
        "insights": result.get("insights"),
        "report": result.get("report"),
        "notes": result.get("notes", []),
    }
