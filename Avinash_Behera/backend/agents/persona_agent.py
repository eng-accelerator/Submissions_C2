# agents/persona_agent.py
"""
Simplified persona-based analysis agent that provides per-screen insights.
Returns concise, actionable insights similar to visual and UX agents.
"""
import base64
import os
import json
from typing import Dict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.callbacks import get_openai_callback

from agents.state import AnalysisState

modelName = "gpt-4o-mini-2024-07-18"
PRICE_PER_MTOKEN = 6.25  # USD per 1M tokens


def load_image_as_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def clean_json(raw):
    return raw.replace("```json", "").replace("```", "").strip()


def run_persona_batch(images: dict, persona: str = None, goals: str = None):
    """
    LangChain-based batch persona analysis.
    images: { "path/to/screen.png": "path/to/screen.png", ... }
    persona: User persona description
    goals: Business goals
    returns:
    {
      "path/to/screen.png": {
        "confusion_points": [...],
        "recommendations": [...],
        "clarity_score": 0-100,
        "trust_score": 0-100
      },
      ...
    }
    """
    print(f"[LANGCHAIN] persona_batch: Starting batch analysis for {len(images)} screens")

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    # Initialize LangChain ChatOpenAI
    llm = ChatOpenAI(
        model=modelName,
        temperature=0,
        openai_api_key=api_key,
        openai_api_base=base_url,
        timeout=120.0
    )

    # Build persona context
    persona_context = ""
    if persona:
        persona_context += f"\nUser Persona: {persona}"
    if goals:
        persona_context += f"\nBusiness Goals: {goals}"

    # Build multimodal input with SCREEN_ID markers
    batch_content = []
    for path in images:
        img_b64 = load_image_as_base64(images[path])
        batch_content.append({"type": "text", "text": f"SCREEN_ID: {path}"})
        batch_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}})

    system_prompt = f"""You are a Persona-Based UX Analyst. Evaluate screens from the perspective of the target user persona.
{persona_context}

You must return **only JSON**.

For each screen, return:

{{
  "SCREEN_ID": {{
    "confusion_points": [
      "Clear description of what might confuse the user",
      ...
    ],
    "recommendations": [
      "Actionable recommendation to improve user experience",
      ...
    ],
    "clarity_score": 0-100,
    "trust_score": 0-100
  }}
}}

Focus on:
- What would confuse or frustrate this specific persona
- How well the screen aligns with their goals
- Trust signals (or lack thereof)
- Clarity of messaging and actions

Keep confusion_points and recommendations to 2-4 items each - only the most important.

Return one JSON object containing all screens.
No markdown, no explanation, no commentary.
"""

    print("[LANGCHAIN] persona_batch: Sending batch request with callbacks")

    # Use LangChain callbacks for token tracking
    with get_openai_callback() as cb:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=batch_content)
        ]

        response = llm.invoke(messages)
        raw = response.content.strip()

        # Track usage via callback
        total_tokens = cb.total_tokens
        cost = cb.total_cost if cb.total_cost else (total_tokens / 1_000_000) * PRICE_PER_MTOKEN

    # Remove accidental markdown fences if present
    raw = clean_json(raw)

    try:
        parsed = json.loads(raw)

        for screen_id in parsed:
            parsed[screen_id]["_meta"] = {
                "model": modelName,
                "tokens": total_tokens,
                "cost_usd": cost,
                "batchMode": "yes"
            }
    except Exception:
        print("\n[ERROR] JSON PARSE FAILED. RAW OUTPUT:\n", raw, "\n")
        raise

    print(f"[LANGCHAIN] persona_batch: Done. Tokens: {total_tokens}, Cost: ${cost:.4f}")
    return parsed


def run_persona_agent(image_path: str, persona: str = None, goals: str = None):
    """LangChain-based single image persona analysis."""
    print(f"[LANGCHAIN] persona_agent: Starting analysis for {image_path}")

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

    if not api_key:
        print("[ERROR] persona_agent: OPENAI_API_KEY not found in environment")
        return {"error": "OPENAI_API_KEY not configured"}

    try:
        image_b64 = load_image_as_base64(image_path)
        print(f"[LANGCHAIN] persona_agent: Image loaded, size: {len(image_b64)} bytes")

        # Build persona context
        persona_context = ""
        if persona:
            persona_context += f"\nUser Persona: {persona}"
        if goals:
            persona_context += f"\nBusiness Goals: {goals}"

        # Initialize LangChain ChatOpenAI
        llm = ChatOpenAI(
            model=modelName,
            temperature=0,
            openai_api_key=api_key,
            openai_api_base=base_url,
            timeout=60.0
        )

        system_prompt = f"""You are a Persona-Based UX Analyst. Evaluate the screen from the perspective of the target user persona.
{persona_context}

Return JSON:
{{
  "confusion_points": [
    "Clear description of what might confuse the user",
    ...
  ],
  "recommendations": [
    "Actionable recommendation to improve user experience",
    ...
  ],
  "clarity_score": 0-100,
  "trust_score": 0-100
}}

Focus on:
- What would confuse or frustrate this specific persona
- How well the screen aligns with their goals
- Trust signals (or lack thereof)
- Clarity of messaging and actions

Keep confusion_points and recommendations to 2-4 items each - only the most important.
"""

        print(f"[LANGCHAIN] persona_agent: Calling API with callbacks...")

        # Use LangChain callbacks for tracking
        with get_openai_callback() as cb:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=[
                    {"type": "text", "text": "Evaluate from the persona's perspective."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                ])
            ]

            response = llm.invoke(messages)
            result = response.content

            # Track usage
            total_tokens = cb.total_tokens
            cost = cb.total_cost if cb.total_cost else (total_tokens / 1_000_000) * PRICE_PER_MTOKEN

        print(f"[LANGCHAIN] persona_agent: Analysis complete. Tokens: {total_tokens}, Cost: ${cost:.4f}")
        return {
            "result": result,
            "_meta": {
                "model": modelName,
                "tokens": total_tokens,
                "cost_usd": cost,
                "batchMode": "no"
            }
        }

    except Exception as e:
        print(f"[ERROR] persona_agent failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# ============ LangGraph Node Functions ============

def persona_agent_node(state: AnalysisState) -> dict:
    """
    LangGraph node for persona analysis.
    Processes images based on batch_mode and stores results in state.
    Returns only the fields this node updates.
    """
    print(f"[LANGGRAPH] persona_agent_node: Starting with {len(state['file_paths'])} files")

    file_paths = state["file_paths"]
    batch_mode = state["batch_mode"]

    # Get persona and goals from project data if available
    persona = state.get("persona")
    goals = state.get("goals")

    try:
        if batch_mode:
            # Batch mode: analyze all images together
            images = {path: path for path in file_paths}
            persona_results = run_persona_batch(images, persona, goals)
        else:
            # Non-batch mode: analyze each image separately
            persona_results = {}
            for path in file_paths:
                persona_raw = run_persona_agent(path, persona, goals)
                persona_json_str = clean_json(persona_raw["result"])
                persona_json = json.loads(persona_json_str)
                persona_json["_meta"] = persona_raw.get("_meta", {})
                persona_results[path] = persona_json

        print(f"[LANGGRAPH] persona_agent_node: Completed successfully")
        # Return ONLY the fields this node updates
        return {"persona_results": persona_results}

    except Exception as e:
        print(f"[LANGGRAPH ERROR] persona_agent_node failed: {str(e)}")
        # Return errors list
        return {"errors": [f"Persona agent error: {str(e)}"]}
