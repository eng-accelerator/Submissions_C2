"""
LangGraph State Definition for Design Analysis Pipeline
"""
from typing import TypedDict, List, Dict, Optional, Annotated
from operator import add


def merge_dicts(left: Optional[Dict], right: Optional[Dict]) -> Dict:
    """
    Reducer function to merge dictionaries from parallel agent updates.
    Used for visual_results and ux_results that are updated concurrently.
    """
    if left is None:
        return right or {}
    if right is None:
        return left
    return {**left, **right}


class AnalysisState(TypedDict):
    """
    Shared state across all agents in the analysis workflow.

    Uses Annotated types with reducers to support parallel agent execution.
    """
    # Input data (these don't change during execution)
    file_paths: List[str]
    agents_config: Dict[str, bool]  # {"visual": True, "ux": True, "accessibility": True, "personaFit": True}
    batch_mode: bool
    persona: Optional[str]  # User persona description
    goals: Optional[str]    # Business goals

    # Results storage (updated by parallel agents, use reducers)
    visual_results: Annotated[Optional[Dict[str, dict]], merge_dicts]  # {file_path: result}
    ux_results: Annotated[Optional[Dict[str, dict]], merge_dicts]      # {file_path: result}
    accessibility_results: Annotated[Optional[Dict[str, dict]], merge_dicts]  # {file_path: result}
    persona_results: Annotated[Optional[Dict[str, dict]], merge_dicts]  # {file_path: result}
    research_results: Annotated[Optional[Dict[str, dict]], merge_dicts]  # {file_path: result}

    # Final output
    final_results: Optional[dict]

    # Error handling (can be updated by multiple agents)
    errors: Annotated[Optional[List[str]], merge_dicts]
