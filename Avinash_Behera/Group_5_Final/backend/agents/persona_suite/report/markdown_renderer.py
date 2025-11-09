"""Markdown renderer for persona suite outputs."""

from __future__ import annotations

from typing import List

from ..models import (
    FrictionModel,
    PersonaObservationModel,
    PersonaProfileModel,
    SuiteState,
    TaskAssessmentModel,
)


def _render_list(items: List[str]) -> str:
    if not items:
        return "- _None_"
    return "\n".join(f"- {item}" for item in items)


def render_markdown_report(state: SuiteState) -> str:
    """Return a markdown summary for display or export."""

    summary = state.get("design_summary")
    personas: List[PersonaProfileModel] = state.get("personas", [])
    observations: List[PersonaObservationModel] = state.get("per_persona", [])
    friction: FrictionModel | None = state.get("frustration")
    tasks: List[TaskAssessmentModel] = state.get("task_results", [])
    scores = state.get("scores", {})

    lines: List[str] = ["# Persona Insights Report"]

    if summary:
        lines.extend(
            [
                "## Design Summary",
                f"- **Product Type:** {summary.product_type}",
                f"- **Positioning:** {summary.positioning}",
                "### Primary Goals",
                _render_list(summary.primary_goals),
                "### Target Audience",
                _render_list(summary.target_audience),
            ]
        )

    if personas:
        lines.append("\n## Personas")
        for persona in personas:
            lines.extend(
                [
                    f"### {persona.name} · {persona.archetype}",
                    "#### Goals",
                    _render_list(persona.goals),
                    "#### Frustrations",
                    _render_list(persona.frustrations),
                    "#### Behaviours",
                    _render_list(persona.behaviors),
                ]
            )

    if observations:
        lines.append("\n## Persona Simulations")
        for obs in observations:
            lines.extend(
                [
                    f"### Simulation – {obs.persona_id}",
                    f"- **Clarity:** {obs.clarity_score:.2f}",
                    f"- **Trust:** {obs.trust_score:.2f}",
                    "#### First Impressions",
                    _render_list(obs.first_impressions),
                    "#### Predicted Actions",
                    _render_list(obs.predicted_actions),
                    "#### Confusion Points",
                    _render_list(obs.confusion_points),
                    "#### Recommended Changes",
                    _render_list(obs.recommended_changes),
                ]
            )

    if friction:
        lines.extend(
            [
                "\n## Frustration Analysis",
                f"- **Friction Score:** {friction.friction_score:.2f}",
                "### Irritants",
                _render_list(friction.irritants),
                "### Misleading Elements",
                _render_list(friction.misleading_elements),
                "### Cognitive Load Issues",
                _render_list(friction.cognitive_load_issues),
            ]
        )

    if tasks:
        lines.append("\n## Task Simulations")
        for task in tasks:
            lines.extend(
                [
                    f"### {task.task_name}",
                    f"- **Success:** {'✅' if task.success else '⚠️'}",
                    f"- **Task Score:** {task.task_score:.2f}",
                    f"- **Time to understand:** {task.time_to_understand:.1f}s",
                    f"- **Time to act:** {task.time_to_act:.1f}s",
                    "#### Steps",
                    _render_list(task.steps),
                    "#### Friction Points",
                    _render_list(task.friction_points),
                ]
            )

    if scores:
        lines.extend(
            [
                "\n## Scorecard",
                *(f"- **{key.title()}:** {value:.3f}" for key, value in scores.items()),
            ]
        )

    if state.get("errors"):
        lines.append("\n## Pipeline Warnings")
        for error in state["errors"]:
            lines.append(f"- {error.get('stage', 'unknown')}: {error.get('error')}")

    return "\n".join(lines)


