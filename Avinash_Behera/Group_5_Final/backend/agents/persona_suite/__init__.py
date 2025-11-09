"""Public interface for the User Personas Agent Suite."""

from __future__ import annotations

import os
from typing import Dict, Iterable, List, Optional, Sequence
from uuid import uuid4

from .models import DesignArtifact, SuiteState
from .pipeline import run_pipeline, DEFAULT_MODEL


def _build_artifacts(paths: Sequence[str]) -> List[DesignArtifact]:
    artifacts: List[DesignArtifact] = []
    for path in paths:
        artifacts.append(
            DesignArtifact(
                id=str(uuid4()),
                path=path,
                label=os.path.basename(path),
            )
        )
    return artifacts


def _format_output(state: SuiteState, batch_mode: str) -> Dict[str, object]:
    personas = [persona.dict() for persona in state.get("personas", [])]
    observations = [obs.dict() for obs in state.get("per_persona", [])]
    frustration = state.get("frustration").dict() if state.get("frustration") else None
    tasks = [task.dict() for task in state.get("task_results", [])]
    usage = state.get("usage", {})

    usage_meta = {
        **usage,
        "suite": {
            "model": os.getenv("PERSONA_MODEL_NAME", DEFAULT_MODEL),
            "tokens": None,
            "cost_usd": None,
            "batchMode": batch_mode,
        },
    }

    return {
        "report": state.get("report_json"),
        "report_markdown": state.get("report_md"),
        "personas": personas,
        "observations": observations,
        "frustration": frustration,
        "tasks": tasks,
        "scores": state.get("scores"),
        "_meta": usage_meta,
        "errors": state.get("errors", []),
    }


def run_persona_batch(
    images: Dict[str, str],
    brief: Optional[str] = None,
    tasks_to_validate: Optional[Iterable[str]] = None,
    model: Optional[str] = None,
) -> Dict[str, object]:
    """Batch persona analysis, aligning with orchestrator expectations."""

    artifacts = _build_artifacts(list(images.values()))
    state = run_pipeline(artifacts, brief, list(tasks_to_validate or []), model=model)
    return _format_output(state, batch_mode="yes")


def run_persona_agent(
    path: str,
    brief: Optional[str] = None,
    tasks_to_validate: Optional[Iterable[str]] = None,
    model: Optional[str] = None,
) -> Dict[str, object]:
    """Single-artifact persona analysis."""

    artifacts = _build_artifacts([path])
    state = run_pipeline(artifacts, brief, list(tasks_to_validate or []), model=model)
    return _format_output(state, batch_mode="no")


__all__ = ["run_persona_batch", "run_persona_agent"]


