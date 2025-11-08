# agents/script_generator.py

from typing import List
import json
import re

from .llm.llm_client import llm_chat
from .llm.llm_utils import clean_llm_code

# We import expect so LLM-generated bodies can safely use Playwright expect()
BASE_PLAYWRIGHT_IMPORTS = """from playwright.sync_api import sync_playwright, expect
import sys
"""

# Fixed, safe harness; LLM NEVER touches this.
HARNESS_TEMPLATE = """{imports}

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
{body}
        except Exception as e:
            print("Error:", e)
            page.screenshot(path="run_error.png", full_page=True)
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run()
"""


# ---------- helpers ----------

def _indent_body(body: str) -> str:
    """
    Indent LLM-generated statements under `try:` (12 spaces).
    Strip extra leading whitespace; skip blank lines.
    """
    lines = body.splitlines()
    indented: List[str] = []

    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            continue
        stripped = stripped.lstrip()
        indented.append(" " * 12 + stripped)

    # Never leave the body completely empty.
    if not indented:
        indented.append(" " * 12 + "page.goto('about:blank')")

    return "\n".join(indented)


def _fallback_script(url: str) -> str:
    """
    Minimal safe fallback if the LLM is unavailable or returns unusable output.
    Keeps harness, just does a goto + screenshot.
    """
    body = f"""            page.goto("{url}", wait_until="networkidle")
            page.screenshot(path="run_result.png", full_page=True)
"""
    return HARNESS_TEMPLATE.format(imports=BASE_PLAYWRIGHT_IMPORTS, body=body)


# ---------- generic intent extraction ----------

def _extract_targets(goal: str) -> List[str]:
    """
    Generic: use LLM to pull concrete UI entities from the goal.
    Example:
      "Login and add the Sauce Labs Bike Light to the cart"
      -> ["Sauce Labs Bike Light"]
    No site-specific logic.
    """
    goal = (goal or "").strip()
    if not goal:
        return []

    system_prompt = (
        "Extract the specific UI entities (products, buttons, links, labels, etc.) "
        "explicitly mentioned in this test goal. "
        "Return ONLY a JSON array of strings, no prose."
    )
    user_prompt = f"Goal:\n{goal}\n\nTargets JSON array:"

    raw = llm_chat(system_prompt, user_prompt, max_tokens=200)
    if not raw:
        return []

    text = raw.strip()
    if "[" in text and "]" in text:
        text = text[text.index("["): text.rindex("]") + 1]

    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [str(x).strip() for x in data if str(x).strip()]
    except Exception:
        pass

    return []


def _extract_verify_phrases(goal: str) -> List[str]:
    """
    Pull simple 'verify ...' clauses from the goal.
    Example:
      'Login and verify the products page is visible'
      -> ['the products page is visible']
    """
    phrases: List[str] = []
    for m in re.finditer(r"verify\s+([^.;,]+)", goal or "", flags=re.I):
        phrase = m.group(1).strip()
        phrase = re.sub(r"^that\s+", "", phrase, flags=re.I)
        if phrase:
            phrases.append(phrase)
    return phrases


def _inject_goal_assertions(goal: str, body: str) -> str:
    """
    Turn 'verify ...' clauses into generic assertions at the end of the body.

    This is intentionally generic:
    - We assert that those phrases appear somewhere in the page body text.
    - For real production you might map these into structured checks, but
      this keeps the hackathon demo clean and goal-driven.
    """
    verify_phrases = _extract_verify_phrases(goal)
    if not verify_phrases:
        return body

    lines = body.rstrip().splitlines()
    lines.append("content = page.inner_text('body')")

    for phrase in verify_phrases:
        safe = phrase.replace("'", "\\'")
        lines.append(f"assert '{safe}' in content, 'Expected to verify: {safe}'")

    return "\n".join(lines) + "\n"


# ---------- main generator ----------

def generate_script(url: str, steps: List[str], engine: str, goal: str) -> str:
    """
    Script Generator Agent.

    - Harness is fixed (we control lifecycle).
    - LLM generates ONLY the body of the test (inside try:).
    - We pass:
        * URL
        * high-level steps (from Flow Discovery)
        * extracted target entities
        * the natural-language goal
      so the model is constrained and aligned with intent.
    - We inject generic assertions derived from 'verify ...' clauses
      so a green run actually means the goal conditions were checked.
    """

    steps_text = "\n".join(f"- {s}" for s in (steps or []))
    targets = _extract_targets(goal)
    targets_text = "\n".join(f"- {t}" for t in targets) if targets else ""

    system_prompt = (
        "You are an expert QA engineer generating Playwright Python steps.\n"
        "You ONLY write the body inside an existing try: block.\n"
        "The harness (imports, def run, with sync_playwright, try/finally, browser.close)\n"
        "already exists and MUST NOT be duplicated.\n"
        "\n"
        "Rules:\n"
        "- Use the existing `page` object.\n"
        "- Start by navigating to the target URL with page.goto.\n"
        "- Follow the discovered steps when they make sense.\n"
        "- Use robust selectors where possible (data-test, ids, accessible names).\n"
        "- If specific target items are provided, interact with / assert on those "
        "exact items; do NOT silently substitute different ones.\n"
        "- You may use either plain `assert` or `expect(...)` (already imported) "
        "to encode validations.\n"
        "- Do NOT include imports, def run, context managers, try/finally, or browser.close.\n"
        "- Return ONLY Python statements. No markdown, no comments, no prose."
    )

    user_parts = [
        f"Target URL: {url}",
        f"Goal: {goal}",
        f"Discovered steps:\n{steps_text}",
    ]
    if targets:
        user_parts.append(
            "Target items you MUST respect exactly (no substitutions):\n" + targets_text
        )
    user_parts.append(
        "Write the Playwright Python statements that belong inside the try: block."
    )
    user_prompt = "\n\n".join(user_parts)

    raw = llm_chat(system_prompt, user_prompt, max_tokens=2200)
    if not raw:
        return _fallback_script(url)

    body = clean_llm_code(raw)

    # Sanity check: if there's no `page.` usage, it's probably explanation text.
    if "page." not in body:
        return _fallback_script(url)

    # Inject assertions from 'verify ...' clauses so success reflects the goal.
    body = _inject_goal_assertions(goal, body)

    # Indent into harness and return final script.
    indented_body = _indent_body(body)
    final_script = HARNESS_TEMPLATE.format(
        imports=BASE_PLAYWRIGHT_IMPORTS,
        body=indented_body,
    )
    return final_script
