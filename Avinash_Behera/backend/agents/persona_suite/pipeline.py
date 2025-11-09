"""LangGraph pipeline that powers the User Personas Agent Suite."""

from __future__ import annotations

import json
import os
from statistics import mean
from typing import Dict, List, Sequence
from uuid import uuid4

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from functools import lru_cache

from .models import (
    DesignArtifact,
    DesignSummaryModel,
    FrictionModel,
    PersonaObservationModel,
    PersonaProfileModel,
    PersonaListModel,
    SuiteState,
    TaskAssessmentModel,
    TaskAssessmentListModel,
    init_state,
)
from .report.json_renderer import render_json_report
from .report.markdown_renderer import render_markdown_report
from .tools import analyze_visual_features, extract_text, generate_caption

# Load environment variables if using .env file
from dotenv import load_dotenv
load_dotenv()

DEFAULT_MODEL = os.getenv("PERSONA_MODEL_NAME", "openai/gpt-4o-mini")


def _build_llm(model: str | None = None, temperature: float = 0.0) -> ChatOpenAI:
    """Factory for ChatOpenAI with repo-wide environment defaults."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not configured for persona suite.")

    base_url = os.getenv("OPENAI_BASE_URL")

    return ChatOpenAI(
        model=model or DEFAULT_MODEL,
        temperature=temperature,
        timeout=120,
        max_retries=2,
        openai_api_key=api_key,
        openai_api_base=base_url,
    )


def _run_normalizers(artifacts: Sequence[DesignArtifact]) -> List[DesignArtifact]:
    """Augment artifacts with OCR, captions, and visual heuristics."""

    enriched: List[DesignArtifact] = []
    for artifact in artifacts:
        path = artifact.get("path")
        if not path:
            continue

        enriched_artifact: DesignArtifact = DesignArtifact(
            id=artifact.get("id") or str(uuid4()),
            path=path,
            label=artifact.get("label") or os.path.basename(path),
        )

        ocr_text = artifact.get("ocr_text") or extract_text(path)
        captions = artifact.get("captions") or generate_caption(path)
        metadata = artifact.get("metadata") or analyze_visual_features(path)

        enriched_artifact["ocr_text"] = ocr_text
        enriched_artifact["captions"] = captions
        enriched_artifact["metadata"] = metadata

        enriched.append(enriched_artifact)
    return enriched


def _aggregate_text(artifacts: Sequence[DesignArtifact]) -> str:
    return "\n\n".join(
        text for art in artifacts for text in [art.get("ocr_text", "")] if text
    )


def _aggregate_captions(artifacts: Sequence[DesignArtifact]) -> str:
    captions: List[str] = []
    for art in artifacts:
        if art.get("captions"):
            captions.extend(art["captions"])  # type: ignore[arg-type]
    return "\n".join(captions)


def _describe_artifacts(artifacts: Sequence[DesignArtifact]) -> str:
    summaries: List[Dict[str, object]] = []
    for art in artifacts:
        summaries.append(
            {
                "label": art.get("label"),
                "path": art.get("path"),
                "captions": art.get("captions"),
                "notes": (art.get("metadata") or {}).get("notes"),
            }
        )
    return json.dumps(summaries, indent=2)


def _safe_mean(values: Sequence[float]) -> float:
    return float(mean(values)) if values else 0.0


def compute_scores(state: SuiteState) -> Dict[str, float]:
    clarity = _safe_mean([obs.clarity_score for obs in state.get("per_persona", [])])
    trust = _safe_mean([obs.trust_score for obs in state.get("per_persona", [])])
    friction_model = state.get("frustration")
    friction = friction_model.friction_score if friction_model else 0.0
    task_scores = _safe_mean([task.task_score for task in state.get("task_results", [])])

    overall = round(
        0.35 * clarity + 0.25 * trust + 0.20 * task_scores + 0.20 * (1 - friction),
        3,
    )

    return {
        "clarity": round(clarity, 3),
        "trust": round(trust, 3),
        "friction": round(friction, 3),
        "task": round(task_scores, 3),
        "overall": overall,
    }


def build_graph(model_name: str):
    """Return a compiled LangGraph for the persona suite."""

    base_llm = _build_llm(model_name)
    design_understanding_llm = base_llm.with_structured_output(DesignSummaryModel)
    persona_generator_llm = base_llm.with_structured_output(PersonaListModel)
    persona_simulation_llm = base_llm.with_structured_output(PersonaObservationModel)
    frustration_llm = base_llm.with_structured_output(FrictionModel)
    task_llm = base_llm.with_structured_output(TaskAssessmentListModel)

    def ingest(state: SuiteState) -> SuiteState:
        try:
            state["artifacts"] = _run_normalizers(state.get("artifacts", []))
        except Exception as exc:
            state.setdefault("errors", []).append({"stage": "ingest", "error": str(exc)})
        return state

    def understand_design(state: SuiteState) -> SuiteState:
        try:
            context = {
                "brief": state.get("brief", ""),
                "ocr_text": _aggregate_text(state.get("artifacts", [])),
                "captions": _aggregate_captions(state.get("artifacts", [])),
                "artifact_notes": _describe_artifacts(state.get("artifacts", [])),
            }
            prompt = (
                "You are a senior product design analyst. Produce the structured design "
                "summary described by the schema. Base your reasoning on the context below.\n\n"
                f"{json.dumps(context, indent=2)}"
            )
            summary = design_understanding_llm.invoke(prompt)
            state["design_summary"] = summary
            state.setdefault("usage", {})["design_summary"] = {
                "model": base_llm.model_name,
                "tokens": None,
                "cost_usd": None,
                "batchMode": "n/a",
            }
        except Exception as exc:
            state.setdefault("errors", []).append({"stage": "design_understanding", "error": str(exc)})
        return state

    def personas(state: SuiteState) -> SuiteState:
        if "design_summary" not in state:
            return state
        try:
            prompt = (
                "You are a persona strategist. Create between three and five personas that "
                "match the provided schema. Use the design summary as the source of truth.\n\n"
                f"{json.dumps(state['design_summary'].model_dump(), indent=2)}"
            )
            generated = persona_generator_llm.invoke(prompt)
            state["personas"] = generated.personas
            state.setdefault("usage", {})["persona_generation"] = {
                "model": base_llm.model_name,
                "tokens": None,
                "cost_usd": None,
                "batchMode": "n/a",
            }
        except Exception as exc:
            state.setdefault("errors", []).append({"stage": "persona_generation", "error": str(exc)})
            state["personas"] = []
        return state

    def persona_simulations(state: SuiteState) -> SuiteState:
        personas_in_state = state.get("personas", [])
        design_summary = state.get("design_summary")
        if not personas_in_state or not design_summary:
            state["per_persona"] = []
            return state

        results: List[PersonaObservationModel] = []
        try:
            artifact_overview = _describe_artifacts(state.get("artifacts", []))
            design_json = json.dumps(design_summary.model_dump(), indent=2)
            for persona in personas_in_state:
                prompt = (
                    "You are simulating a target persona interacting with the design. "
                    "Follow the schema exactly and base your answer on the data provided.\n\n"
                    f"Persona profile:\n{json.dumps(persona.model_dump(), indent=2)}\n\n"
                    f"Design summary:\n{design_json}\n\n"
                    f"Artifact overview:\n{artifact_overview}"
                )
                results.append(persona_simulation_llm.invoke(prompt))

            state["per_persona"] = results
            state.setdefault("usage", {})["persona_simulation"] = {
                "model": base_llm.model_name,
                "tokens": None,
                "cost_usd": None,
                "batchMode": "sequential",
            }
        except Exception as exc:
            state.setdefault("errors", []).append({"stage": "persona_simulation", "error": str(exc)})
            state["per_persona"] = []
        return state

    def frustration(state: SuiteState) -> SuiteState:
        try:
            observations = [obs.dict() for obs in state.get("per_persona", [])]
            prompt = (
                "You are a UX researcher consolidating persona observations into friction insights. "
                "Return the data described by the schema.\n\n"
                f"{json.dumps(observations, indent=2)}"
            )
            state["frustration"] = frustration_llm.invoke(prompt)
            state.setdefault("usage", {})["frustration"] = {
                "model": base_llm.model_name,
                "tokens": None,
                "cost_usd": None,
                "batchMode": "n/a",
            }
        except Exception as exc:
            state.setdefault("errors", []).append({"stage": "frustration", "error": str(exc)})
        return state

    def task_completion(state: SuiteState) -> SuiteState:
        tasks = state.get("tasks_to_validate", [])
        if not tasks:
            state["task_results"] = []
            return state

        try:
            design_summary = state.get("design_summary")
            observations = [obs.dict() for obs in state.get("per_persona", [])]
            prompt = (
                "You are evaluating key user tasks for the experience. For each task, produce the "
                "assessment described by the schema.\n\n"
                f"Tasks:\n{json.dumps(tasks, indent=2)}\n\n"
                f"Design summary:\n{json.dumps(design_summary.model_dump(), indent=2) if design_summary else '{}'}\n\n"
                f"Persona observations:\n{json.dumps(observations, indent=2)}"
            )
            task_response = task_llm.invoke(prompt)
            state["task_results"] = task_response.assessments
            state.setdefault("usage", {})["task_completion"] = {
                "model": base_llm.model_name,
                "tokens": None,
                "cost_usd": None,
                "batchMode": "n/a",
            }
        except Exception as exc:
            state.setdefault("errors", []).append({"stage": "task_completion", "error": str(exc)})
            state["task_results"] = []
        return state

    def scoring(state: SuiteState) -> SuiteState:
        state["scores"] = compute_scores(state)
        return state

    def reporting(state: SuiteState) -> SuiteState:
        state["report_json"] = render_json_report(state)
        state["report_md"] = render_markdown_report(state)
        return state

    graph = StateGraph(SuiteState)
    graph.add_node("ingest", ingest)
    graph.add_node("design_understanding", understand_design)
    graph.add_node("persona_generation", personas)
    graph.add_node("persona_simulation", persona_simulations)
    graph.add_node("frustration", frustration)
    graph.add_node("task_completion", task_completion)
    graph.add_node("scoring", scoring)
    graph.add_node("reporting", reporting)

    graph.add_edge(START, "ingest")
    graph.add_edge("ingest", "design_understanding")
    graph.add_edge("design_understanding", "persona_generation")
    graph.add_edge("persona_generation", "persona_simulation")
    graph.add_edge("persona_simulation", "frustration")
    graph.add_edge("frustration", "task_completion")
    graph.add_edge("task_completion", "scoring")
    graph.add_edge("scoring", "reporting")
    graph.add_edge("reporting", END)

    return graph.compile()


@lru_cache(maxsize=2)
def _get_compiled_graph(model_name: str):
    return build_graph(model_name)


def run_pipeline(
    artifacts: Sequence[DesignArtifact],
    brief: str | None,
    tasks_to_validate: Sequence[str] | None = None,
    model: str | None = None,
) -> SuiteState:
    """Public entrypoint for executing the persona suite pipeline."""

    state = init_state(list(artifacts), brief, list(tasks_to_validate or []))
    model_name = model or DEFAULT_MODEL
    graph = _get_compiled_graph(model_name)
    return graph.invoke(state)


