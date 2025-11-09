"""JSON report renderer for persona suite outputs."""

from __future__ import annotations

from typing import Any, Dict, List

from ..models import (
    FrictionModel,
    PersonaObservationModel,
    PersonaProfileModel,
    ReportJSONModel,
    SuiteState,
    TaskAssessmentModel,
)


def _model_list_to_dict(models: List[Any]) -> List[Dict[str, Any]]:
    return [model.dict() if hasattr(model, "dict") else model for model in models]


def render_json_report(state: SuiteState) -> Dict[str, Any]:
    """Return a JSON-serialisable dict summarising the state."""

    design_summary = state.get("design_summary")
    personas: List[PersonaProfileModel] = state.get("personas", [])
    observations: List[PersonaObservationModel] = state.get("per_persona", [])
    friction: FrictionModel | None = state.get("frustration")
    tasks: List[TaskAssessmentModel] = state.get("task_results", [])
    scores = state.get("scores", {})

    if not design_summary:
        return {
            "status": "incomplete",
            "reason": "Design summary missing; pipeline likely failed early.",
            "scores": scores,
        }

    try:
        report = ReportJSONModel(
            design_summary=design_summary,
            personas=personas,
            persona_observations=observations,
            frustration=friction or FrictionModel(
                friction_score=0.0,
                irritants=[],
                misleading_elements=[],
                cognitive_load_issues=[],
                drop_off_points=[],
            ),
            tasks=tasks,
            scores=scores,
        )
        payload = report.dict()
    except Exception as exc:  # pragma: no cover - defensive guard
        return {
            "status": "incomplete",
            "reason": f"Failed to serialise report: {exc}",
            "scores": scores,
        }

    payload.update(
        {
            "status": "complete",
            "usage": state.get("usage", {}),
            "errors": state.get("errors", []),
        }
    )
    return payload


