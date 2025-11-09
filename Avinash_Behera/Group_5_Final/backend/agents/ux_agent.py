# agents/ux_agent.py
import base64
import os
import json
from typing import Dict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.callbacks import get_openai_callback

from agents.state import AnalysisState
from agents.models import UXAnalysisResult, UsabilityProblem

modelName="gpt-4o"
PRICE_PER_MTOKEN = 6.25  # USD per 1M tokens (approx GPT-4o blended cost)

def load_image_as_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
    
def clean_json(raw):
    return raw.replace("```json", "").replace("```", "").strip()
    
def run_ux_batch(images: dict):
    """
    LangChain-based batch UX analysis.
    images: { "path/to/screen.png": "path/to/screen.png", ... }
    returns:
    {
      "path/to/screen.png": {
        "usability_problems": [...],
        "confusing_elements": [...],
        "improvements": [...]
      },
      ...
    }
    """
    print(f"[LANGCHAIN] ux_batch: Starting batch UX analysis for {len(images)} screens")

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

    # ----- Build multimodal input with SCREEN_ID markers -----
    batch_content = []
    for path in images:
        img_b64 = load_image_as_base64(images[path])
        batch_content.append({"type": "text", "text": f"SCREEN_ID: {path}"})
        batch_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}})

    system_prompt = """
You are a UX Heuristic Review Agent.
Use Nielsen Norman heuristics.

You must return **only JSON**.

For each screen, return:

{
  "SCREEN_ID": {
    "usability_problems": [
      {
        "description": "...",
        "impact": "High | Medium | Low",
        "effort": "High | Medium | Low",
        "improvement": "..."
      }
    ],
    "confusing_elements": [...],
    "improvements": [...]
  }
}

If a section is empty, return an empty list — do NOT omit fields.

Return one JSON object containing all screens.
No markdown, no explanation, no commentary.
"""

    print("[LANGCHAIN] ux_batch: Sending batch request to GPT-4o with callbacks")

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
              "batchMode":"yes"
          }
    except Exception:
        print("\n[ERROR] JSON PARSE FAILED. RAW OUTPUT:\n", raw, "\n")
        raise

    print(f"[LANGCHAIN] ux_batch: Done. Tokens: {total_tokens}, Cost: ${cost:.4f}")
    return parsed



def run_ux_agent(image_path: str):
    """LangChain-based single image UX analysis."""
    print(f"[LANGCHAIN] ux_agent: Starting analysis for {image_path}")

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

    if not api_key:
        print("[ERROR] ux_agent: OPENAI_API_KEY not found in environment")
        return {"error": "OPENAI_API_KEY not configured"}

    try:
        image_b64 = load_image_as_base64(image_path)
        print(f"[LANGCHAIN] ux_agent: Image loaded, size: {len(image_b64)} bytes")

        # Initialize LangChain ChatOpenAI
        llm = ChatOpenAI(
            model=modelName,
            temperature=0,
            openai_api_key=api_key,
            openai_api_base=base_url,
            timeout=60.0
        )

        system_prompt = """You are a UX Heuristic Review Agent.
Use Nielsen Norman heuristics.

Return JSON:
{
  "usability_problems": [
    {
      "description": "...",
      "impact": "High | Medium | Low",
      "effort": "High | Medium | Low",
      "improvement": "..."
    }
  ],
  "confusing_elements": [...],
  "improvements": [...]
}"""

        print(f"[LANGCHAIN] ux_agent: Calling API with callbacks...")

        # Use LangChain callbacks for tracking
        with get_openai_callback() as cb:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=[
                    {"type": "text", "text": "Evaluate usability issues."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                ])
            ]

            response = llm.invoke(messages)
            result = response.content

            # Track usage
            prompt_tokens = cb.prompt_tokens
            completion_tokens = cb.completion_tokens
            total_tokens = cb.total_tokens
            cost = cb.total_cost if cb.total_cost else (total_tokens / 1_000_000) * PRICE_PER_MTOKEN

        print(f"[LANGCHAIN] ux_agent: Analysis complete. Tokens: {total_tokens}, Cost: ${cost:.4f}")
        return {
            "result": result,
            "_meta": {
                "model": modelName,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "tokens": total_tokens,
                "cost_usd": cost,
                "batchMode": "no"
            }
        }

    except Exception as e:
        print(f"[ERROR] ux_agent failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# ============ LangGraph Node Functions ============

def ux_agent_node(state: AnalysisState) -> dict:
    """
    LangGraph node for UX analysis.
    Processes images based on batch_mode and stores results in state.
    Returns only the fields this node updates.
    """
    print(f"[LANGGRAPH] ux_agent_node: Starting with {len(state['file_paths'])} files")

    file_paths = state["file_paths"]
    batch_mode = state["batch_mode"]

    try:
        if batch_mode:
            # Batch mode: analyze all images together
            images = {path: path for path in file_paths}
            ux_results = run_ux_batch(images)
        else:
            # Non-batch mode: analyze each image separately
            ux_results = {}
            for path in file_paths:
                ux_raw = run_ux_agent(path)
                ux_json_str = clean_json(ux_raw["result"])
                ux_json = json.loads(ux_json_str)

                # Add priority classification
                for problem in ux_json.get("usability_problems", []):
                    problem["priority"] = classify_priority(problem["impact"], problem["effort"])

                ux_json["_meta"] = ux_raw.get("_meta", {})
                ux_results[path] = ux_json

        print(f"[LANGGRAPH] ux_agent_node: Completed successfully")
        # Return ONLY the fields this node updates
        return {"ux_results": ux_results}

    except Exception as e:
        print(f"[LANGGRAPH ERROR] ux_agent_node failed: {str(e)}")
        # Return errors list
        return {"errors": [f"UX agent error: {str(e)}"]}


def classify_priority(impact, effort):
    """Helper function for priority classification"""
    if impact == "High" and effort == "Low":
        return "Do Now"
    if impact == "High" and effort == "High":
        return "Plan"
    if impact == "Low" and effort == "Low":
        return "Quick Win"
    return "Low Value"
