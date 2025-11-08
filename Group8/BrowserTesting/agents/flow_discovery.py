# agents/flow_discovery.py

from typing import List

from .llm.llm_client import llm_chat


def _fallback_steps(url: str, goal: str) -> List[str]:
    return [
        f"Open '{url}'",
        "Perform the key actions described in the goal",
        "Capture a screenshot of the final state",
    ]


def discover_flow(url: str, goal: str) -> List[str]:
    """
    Flow Discovery Agent

    Uses LLM to turn (url, goal) into ordered, high-level steps.
    If LLM is unavailable, returns a simple generic list.
    """
    system_prompt = (
        "You are a senior QA engineer. "
        "Given a target URL and a testing goal, you output a concise, ordered list "
        "of key user actions. "
        "Return ONLY the steps, one per line. No numbering, no bullets, no prose."
    )

    user_prompt = (
        f"Target URL: {url}\n"
        f"Goal: {goal}\n\n"
        "List the essential user steps to achieve this goal in the web UI."
    )

    raw = llm_chat(system_prompt, user_prompt, max_tokens=400)
    if not raw:
        return _fallback_steps(url, goal)

    # Parse lines into clean steps
    steps: List[str] = []
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        # remove common bullet/number prefixes
        s = s.lstrip("-*0123456789. ").strip()
        if s:
            steps.append(s)

    return steps or _fallback_steps(url, goal)
