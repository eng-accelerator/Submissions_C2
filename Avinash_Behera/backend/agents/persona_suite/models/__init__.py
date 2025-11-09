"""Schemas and state definitions for the persona suite pipeline."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field


class UsageMeta(TypedDict, total=False):
    """Metadata returned alongside agent outputs."""

    model: str
    tokens: Optional[int]
    cost_usd: Optional[float]
    batchMode: str


class DesignArtifact(TypedDict, total=False):
    """Representation of a design asset passed into the pipeline."""

    id: str
    path: str
    label: Optional[str]
    ocr_text: Optional[str]
    captions: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]


class DesignSummaryModel(BaseModel):
    """High-level understanding of the uploaded designs."""

    product_type: str = Field(..., description="What type of product or experience this design represents.")
    primary_goals: List[str] = Field(..., description="Key objectives the design is trying to achieve.")
    target_audience: List[str] = Field(..., description="Segments the design appears to serve.")
    customer_journeys: List[str] = Field(default_factory=list, description="Notable journeys or flows identified.")
    positioning: str = Field(..., description="How the design positions the product or brand.")
    supporting_evidence: List[str] = Field(default_factory=list, description="Evidence or cues found within the designs.")


class PersonaProfileModel(BaseModel):
    """Description of a generated persona."""

    name: str
    archetype: str
    goals: List[str]
    frustrations: List[str]
    behaviors: List[str]
    accessibility_needs: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    clarity_expectations: str
    trust_expectations: str


class PersonaObservationModel(BaseModel):
    """Output from persona simulation agent."""

    persona_id: str
    first_impressions: List[str]
    predicted_actions: List[str]
    confusion_points: List[str]
    emotional_response: str
    clarity_score: float = Field(..., ge=0.0, le=1.0)
    trust_score: float = Field(..., ge=0.0, le=1.0)
    friction_notes: List[str] = Field(default_factory=list)
    recommended_changes: List[str] = Field(default_factory=list)


class PersonaListModel(BaseModel):
    """Wrapper model used for structured persona generation responses."""

    personas: List[PersonaProfileModel]


class FrictionModel(BaseModel):
    """Aggregated friction analysis."""

    friction_score: float = Field(..., ge=0.0, le=1.0)
    irritants: List[str]
    misleading_elements: List[str]
    cognitive_load_issues: List[str]
    drop_off_points: List[str]


class TaskAssessmentModel(BaseModel):
    """Results from validating key tasks."""

    task_name: str
    success: bool
    steps: List[str]
    time_to_understand: float = Field(..., ge=0.0, description="Estimated seconds to understand the task.")
    time_to_act: float = Field(..., ge=0.0, description="Estimated seconds to take action.")
    friction_points: List[str]
    task_score: float = Field(..., ge=0.0, le=1.0)


class TaskAssessmentListModel(BaseModel):
    """Wrapper for structured task assessment responses."""

    assessments: List[TaskAssessmentModel]


class ReportJSONModel(BaseModel):
    """Canonical JSON payload returned by the persona suite."""

    design_summary: DesignSummaryModel
    personas: List[PersonaProfileModel]
    persona_observations: List[PersonaObservationModel]
    frustration: FrictionModel
    tasks: List[TaskAssessmentModel]
    scores: Dict[str, float]


class SuiteState(TypedDict, total=False):
    """Mutable state passed between pipeline nodes."""

    artifacts: List[DesignArtifact]
    brief: Optional[str]
    design_summary: DesignSummaryModel
    personas: List[PersonaProfileModel]
    per_persona: List[PersonaObservationModel]
    frustration: FrictionModel
    tasks_to_validate: List[str]
    task_results: List[TaskAssessmentModel]
    scores: Dict[str, float]
    report_json: Dict[str, Any]
    report_md: str
    usage: Dict[str, UsageMeta]
    errors: List[Dict[str, Any]]


def init_state(
    artifacts: List[DesignArtifact],
    brief: Optional[str],
    tasks_to_validate: Optional[List[str]],
) -> SuiteState:
    """Create the initial suite state with sensible defaults."""

    return SuiteState(
        artifacts=artifacts,
        brief=brief,
        tasks_to_validate=tasks_to_validate or [],
        usage={},
        errors=[],
    )


