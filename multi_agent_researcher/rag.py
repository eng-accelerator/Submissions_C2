"""
rag.py
------
Simple orchestrator wrapper for UI. For phase 1 it calls the local agent stubs.
Later, replace the internals of `run_research` with real LangChain / LangGraph orchestration.

API contract:
- run_research(query, num_agents, retrieval_depth, model, temperature)
  returns a dict with keys: 'retrieval', 'analysis', 'insights', 'report'
"""
from agents_stub import fake_retriever, fake_critical_analysis, fake_insight_generation, fake_report_builder

def run_research(query: str, num_agents: int = 4, retrieval_depth: int = 3, model: str = "local-mock", temperature: float = 0.2):
    """
    Execute the current (stubbed) agent pipeline and return the structured results dict.
    Important: maintain keys exactly as shown so the UI remains compatible.
    """
    # 1. Retriever Agent
    retrieval = fake_retriever(query, depth=retrieval_depth)

    # 2. Critical Analysis
    analysis = fake_critical_analysis(retrieval)

    # 3. Insight Generation
    insights = fake_insight_generation(analysis)

    # 4. Report Builder
    report = fake_report_builder(retrieval, analysis, insights)

    return {
        "retrieval": retrieval,
        "analysis": analysis,
        "insights": insights,
        "report": report
    }
