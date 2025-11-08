# agents/adaptive_repair.py

from agents.script_generator import _script_demoblaze_checkout_v2

# Centralized LLM helpers (under agents.llm). Fallbacks keep this optional.
try:
    from agents.llm.llm_client import llm_chat
    from agents.llm.llm_utils import has_meaningful_code_change, clean_llm_code
except ImportError:
    try:
        from llm.llm_client import llm_chat  # alt layout
        from llm.llm_utils import has_meaningful_code_change, clean_llm_code
    except ImportError:
        llm_chat = None  # type: ignore

        def has_meaningful_code_change(old: str, new: str) -> bool:  # type: ignore
            return False

        def clean_llm_code(text: str) -> str:  # type: ignore
            return text


def self_heal(script_code: str, error_log: str):
    """
    Adaptive repair entrypoint.

    Returns:
        (repaired_script: str | None, note: str)

    Behavior:
      1. Deterministic Demoblaze upgrade: broken v1 -> hardened v2.
      2. Optional minimal LLM-based patch for other scripts.
      3. Otherwise, no-op with explanation.
    """
    if not script_code:
        return None, "No script provided for self-heal."

    lower_log = (error_log or "").lower()
    lower_script = (script_code or "").lower()

    # ---------- 1) Deterministic Demoblaze fix ----------

    if "demoblaze.com" in lower_log or "demoblaze.com" in lower_script:
        if "sony vaio i5" in lower_log or "sony vaio i5" in lower_script:
            # Try to infer base URL; fallback to canonical
            base_url = "https://www.demoblaze.com"
            for line in script_code.splitlines():
                if "page.goto(" in line and "demoblaze" in line:
                    frag = line.split("page.goto(")[1].split(")")[0]
                    candidate = frag.strip().strip('"').strip("'")
                    if candidate:
                        base_url = candidate
                    break

            note = (
                "Replaced brittle Demoblaze checkout flow with hardened version "
                "using better waits, stable selectors, and the correct confirmation check."
            )
            return _script_demoblaze_checkout_v2(base_url), note

    # ---------- 2) Minimal LLM-based fix (conservative, optional) ----------

    if llm_chat is not None:
        system_prompt = (
            "You are improving a flaky Playwright sync script used for browser automation tests. "
            "Return ONLY a full Python script. "
            "You may adjust selectors and add waits, but MUST NOT:\n"
            "- Change the overall scenario intent.\n"
            "- Add unrelated imports.\n"
            "- Start sync_playwright() outside the existing harness.\n"
            "- Remove screenshot capture on success."
        )

        user_prompt = (
            "Here is the current script:\n\n"
            "```python\n"
            f"{script_code}\n"
            "```\n\n"
            "Here is the error log from its last run:\n\n"
            "```text\n"
            f"{error_log}\n"
            "```\n\n"
            "Make the SMALLEST possible changes needed to improve reliability:\n"
            "- Fix clearly wrong or outdated selectors.\n"
            "- Add wait_for_selector or wait_for_timeout where elements are used too early.\n"
            "- Keep the same structure and harness pattern.\n\n"
            "Return ONLY the updated full Python script, with no explanation."
        )

        raw = llm_chat(system_prompt, user_prompt, max_tokens=1800)
        if raw:
            candidate = clean_llm_code(raw)

            # Only accept if it still looks like our harness-based script
            if "def run(" in candidate and "sync_playwright" in candidate:
                if has_meaningful_code_change(script_code, candidate):
                    return candidate, "Applied minimal LLM-suggested fix to selectors/waits."

    # ---------- 3) Fallback ----------

    return None, (
        "No automatic self-heal applied. The failure likely requires manual adjustment."
    )
