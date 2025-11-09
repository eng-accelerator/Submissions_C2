# agents/visual_agent.py
import base64
import os
import json
from typing import Dict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.callbacks import get_openai_callback

from agents.state import AnalysisState
from agents.models import VisualAnalysisResult, VisualIssue

PRICE_PER_MTOKEN = 6.25  # USD per 1M tokens (approx GPT-4o blended cost)


def load_image_as_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
    
def clean_json(raw):
    return raw.replace("```json", "").replace("```", "").strip()
    
def run_visual_batch(images: dict):
    """
    LangChain-based batch visual analysis.
    images: { "path/to/file.png": "/absolute/storage/path/file.png", ... }
    returns: { path: {strengths:[], issues:[...]}, ... }
    """

    print(f"[LANGCHAIN] visual_batch: Starting batch analysis for {len(images)} images")

    modelName="openai/gpt-4o"

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Initialize LangChain ChatOpenAI
    llm = ChatOpenAI(
        model=modelName,
        temperature=0,
        openai_api_key=api_key,
        openai_api_base=base_url,
        timeout=120.0
    )

    


    # --- Construct multimodal prompt content ---
    # Structure: text "SCREEN_ID: <path>" + image data for each screen
    batch_content = []
    for path in images:
        img_b64 = load_image_as_base64(images[path])
        batch_content.append({"type": "text", "text": f"SCREEN_ID: {path}"})
        batch_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})

    system_prompt = """
You are a Visual Design Critique Agent.

You must return structured JSON only.

Evaluate:
- layout, spacing, hierarchy
- typography clarity & readability
- color contrast and visual balance

For each screen, return:

{
  "SCREEN_ID": {
    "strengths": [...],
    "issues": [
      {
        "description": "...",
        "impact": "High | Medium | Low",
        "effort": "High | Medium | Low",
        "recommendation": "..."
      }
    ]
  }
}

Return **one JSON object containing ALL screens**.
No markdown fences. No commentary.
"""

    print("[LANGCHAIN] visual_batch: Sending batch request to GPT-4o with callbacks")

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

    # Remove accidental code fences if present
    raw = clean_json(raw)

    try:
        parsed = json.loads(raw)

    except Exception:
        print("\n[ERROR] JSON parse failed. Raw output:\n", raw, "\n")
        raise

    print(f"[LANGCHAIN] visual_batch: Batch analysis done. Tokens: {total_tokens}, Cost: ${cost:.4f}")
    # attach metadata to every screen result
    for screen_id in parsed:
        parsed[screen_id]["_meta"] = {
            "model": modelName,
            "tokens": total_tokens,
            "cost_usd": cost,
            "batchMode":"yes"
        }
    return parsed

def run_visual_agent(image_path: str):
    print(f"[DEBUG] visual_agent: Starting analysis for {image_path}")

    
    modelName="gpt-4o"

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

    if not api_key:
        print("[ERROR] visual_agent: OPENAI_API_KEY not found in environment")
        return {"error": "OPENAI_API_KEY not configured"}

    print(f"[DEBUG] visual_agent: API key found, base_url={base_url}")

    try:
        print(f"[DEBUG] visual_agent: Loading image")
        image_b64 = load_image_as_base64(image_path)
        print(f"[DEBUG] visual_agent: Image loaded, size: {len(image_b64)} bytes")

        print(f"[DEBUG] visual_agent: Creating OpenAI client")
        llm = ChatOpenAI(
            model=modelName,
            temperature=0,
            openai_api_key=api_key,
            openai_api_base=base_url,
            timeout=60.0
        )

        
        print(f"[DEBUG] visual_agent: OpenAI client created")

        print(f"[DEBUG] visual_agent: Calling API...")
        # Use LangChain callbacks for token tracking
        with get_openai_callback() as cb:
            messages = [
                SystemMessage(content="""
You are a Visual Design Critique Agent.

You must return structured JSON only.

Evaluate:
- layout, spacing, hierarchy
- typography clarity & readability
- color contrast and visual balance

For **each issue**, assign:
- impact: High / Medium / Low
- effort: High / Medium / Low
- recommendation: specific action

Return format:
{
  "strengths": [...],
  "issues": [
    {
      "description": "...",
      "impact": "High | Medium | Low",
      "effort": "High | Medium | Low",
      "recommendation": "..."
    }
  ]
}
"""),
                HumanMessage(content=[
                    {"type": "text", "text": "Analyze this image."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
                ])
            ]
            
            response = llm.invoke(messages)
            raw = response.content.strip()
            
            # Track usage via callback
            total_tokens = cb.total_tokens
            cost = cb.total_cost if cb.total_cost else (total_tokens / 1_000_000) * PRICE_PER_MTOKEN

        # Remove accidental code fences if present
        raw = clean_json(raw)

        try:
            parsed = json.loads(raw)

        except Exception:
            print("\n[ERROR] JSON parse failed. Raw output:\n", raw, "\n")
            raise

        print(f"[DEBUG] visual_agent: Analysis complete")
        return {
            "result": parsed,
            "_meta":{
                      "model": modelName,
                      "tokens": total_tokens,
                      "cost_usd": cost,
                      "batchMode":"no"
                    }
                }
        

    except Exception as e:
        print(f"[ERROR] visual_agent failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# ============ LangGraph Node Functions ============

def visual_agent_node(state: AnalysisState) -> dict:
    """
    LangGraph node for visual analysis.
    Processes images based on batch_mode and stores results in state.
    Returns only the fields this node updates.
    """
    print(f"[LANGGRAPH] visual_agent_node: Starting with {len(state['file_paths'])} files")

    file_paths = state["file_paths"]
    batch_mode = state["batch_mode"]

    try:
        if batch_mode:
            # Batch mode: analyze all images together
            images = {path: path for path in file_paths}
            visual_results = run_visual_batch(images)
        else:
            # Non-batch mode: analyze each image separately
            visual_results = {}
            for path in file_paths:
                visual_raw = run_visual_agent(path)
                visual_results[path] = visual_raw["result"]

                # Add priority classification
                for issue in visual_results[path].get("issues", []):
                    issue["priority"] = classify_priority(issue["impact"], issue["effort"])

                visual_results[path]["_meta"] = visual_raw.get("_meta", {})

        print(f"[LANGGRAPH] visual_agent_node: Completed successfully")
        # Return ONLY the fields this node updates
        return {"visual_results": visual_results}

    except Exception as e:
        print(f"[LANGGRAPH ERROR] visual_agent_node failed: {str(e)}")
        # Return errors list
        return {"errors": [f"Visual agent error: {str(e)}"]}


def classify_priority(impact, effort):
    """Helper function for priority classification"""
    if impact == "High" and effort == "Low":
        return "Do Now"
    if impact == "High" and effort == "High":
        return "Plan"
    if impact == "Low" and effort == "Low":
        return "Quick Win"
    return "Low Value"
