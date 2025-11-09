# orchestrator.py
"""
LangGraph-based orchestrator for multi-agent design analysis.
This module creates and manages the workflow for coordinating visual, UX, accessibility, persona, and research agents.
"""
from agents.visual_agent import visual_agent_node
from agents.ux_agent import ux_agent_node
from agents.accessibility_agent import accessibility_agent_node
from agents.persona_agent import persona_agent_node
from agents.research_agent import research_agent_node
from agents.state import AnalysisState

from langgraph.graph import StateGraph, START, END


# ============ LangGraph Workflow Functions ============

def aggregate_results_node(state: AnalysisState) -> dict:
    """
    Aggregates results from all agents into final output format.
    This maintains the same output structure as the original functions.
    Returns only the fields this node updates.
    """
    print("[LANGGRAPH] aggregate_results_node: Combining agent results")

    file_paths = state["file_paths"]
    agents_config = state["agents_config"]

    results = {}
    for path in file_paths:
        screen_result = {}

        # Add visual results if agent was enabled
        if agents_config.get("visual") and state.get("visual_results"):
            screen_result["visual"] = state["visual_results"].get(path)

        # Add UX results if agent was enabled
        if agents_config.get("ux") and state.get("ux_results"):
            screen_result["ux"] = state["ux_results"].get(path)

        # Add accessibility results if agent was enabled
        if agents_config.get("accessibility") and state.get("accessibility_results"):
            screen_result["accessibility"] = state["accessibility_results"].get(path)

        # Add persona results if agent was enabled
        if agents_config.get("personaFit") and state.get("persona_results"):
            screen_result["persona"] = state["persona_results"].get(path)

        # Add research results if agent was enabled
        if agents_config.get("research") and state.get("research_results"):
            screen_result["research"] = state["research_results"].get(path)

        results[path] = screen_result

    response = {
        "status": "complete",
        "screens": results
    }

    state["final_results"] = response

    print("[LANGGRAPH] aggregate_results_node: Aggregation complete")
    # Return ONLY the fields this node updates
    return {"final_results": response}


def create_analysis_workflow(agents_config: dict, has_figma: bool = False):
    """
    Creates a LangGraph workflow based on which agents are enabled.
    Agents run in PARALLEL for maximum performance.

    Args:
        agents_config: Dict like {"visual": True, "ux": True, "accessibility": True, "personaFit": True, "research": True}

    Returns:
        Compiled LangGraph workflow
    """
    print(f"[LANGGRAPH] Creating PARALLEL workflow with agents: {agents_config}")

    workflow = StateGraph(AnalysisState)

    # Add nodes for enabled agents
    active_agents = []

    if agents_config.get("visual"):
        workflow.add_node("visual_agent", visual_agent_node)
        active_agents.append("visual_agent")

    if agents_config.get("ux"):
        workflow.add_node("ux_agent", ux_agent_node)
        active_agents.append("ux_agent")

    if agents_config.get("accessibility"):
        workflow.add_node("accessibility_agent", accessibility_agent_node)
        active_agents.append("accessibility_agent")

    if agents_config.get("personaFit"):
        workflow.add_node("persona_agent", persona_agent_node)
        active_agents.append("persona_agent")

    if agents_config.get("research"):
        workflow.add_node("research_agent", research_agent_node)
        active_agents.append("research_agent")

    # Add aggregator node
    workflow.add_node("aggregate", aggregate_results_node)

    # PARALLEL EXECUTION: All agents start simultaneously from START
    for agent in active_agents:
        workflow.add_edge(START, agent)
        # Each agent connects directly to aggregator
        workflow.add_edge(agent, "aggregate")

    # Aggregator ends the workflow
    workflow.add_edge("aggregate", END)

    print(f"[LANGGRAPH] Workflow configured for parallel execution of {len(active_agents)} agents")

    return workflow.compile()


def run_langgraph_pipeline(file_paths: list, agents: dict, batch_mode: bool,
                          figma_url: str = None, figma_token: str = None,
                          persona: str = None, goals: str = None):
    """
    Main entry point for LangGraph-based analysis pipeline.

    Args:
        file_paths: List of image file paths (empty if using Figma)
        agents: Dict like {"visual": True, "ux": False, "personaFit": True, "research": True}
        batch_mode: Boolean indicating batch processing mode
        figma_url: Optional Figma file URL
        figma_token: Optional user's Figma access token
        persona: Optional user persona description
        goals: Optional business goals

    Returns:
        Dict with status and screens results (same format as original)
    """
    has_figma = bool(figma_url)
    source = "Figma URL" if has_figma else f"{len(file_paths)} files"
    print(f"[LANGGRAPH] Starting pipeline with {source}, batch_mode={batch_mode}")

    # Initialize state
    initial_state: AnalysisState = {
        "file_paths": file_paths,
        "agents_config": agents,
        "batch_mode": batch_mode,
        "persona": persona,
        "goals": goals,
        "figma_url": figma_url,
        "figma_token": figma_token,
        "source_type": "figma" if has_figma else "upload",
        "visual_results": None,
        "ux_results": None,
        "accessibility_results": None,
        "persona_results": None,
        "research_results": None,
        "final_results": None,
        "errors": None
    }

    # Create and run workflow
    workflow = create_analysis_workflow(agents, has_figma=has_figma)
    final_state = workflow.invoke(initial_state)

    # Check for errors
    if final_state.get("errors"):
        print(f"[LANGGRAPH WARNING] Errors occurred: {final_state['errors']}")

    print("[LANGGRAPH] Pipeline complete")
    return final_state["final_results"]
