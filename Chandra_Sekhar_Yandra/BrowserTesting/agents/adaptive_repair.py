# agents/adaptive_repair.py

"""
Adaptive Repair Agent (harness-aware)

We now own the Playwright harness (imports, run(), lifecycle).
LLM only generates the body inside the try: block.

This module:
  - Inspects failures.
  - Optionally tweaks the body (selectors / waits) in a safe way.
  - Or asks the LLM to regenerate ONLY the body, with strict rules.
  - Never touches imports, def run, with sync_playwright, or finally.
"""

from typing import Tuple, List
import re

from .llm.llm_client import llm_chat
from .llm.llm_utils import clean_llm_code, has_meaningful_code_change


# ---------------------------
# Helpers to work with harness
# ---------------------------

def _find_body_region(lines: List[str]) -> Tuple[int, int]:
    """
    Find indices (start, end) of the body inside the try: block.

    start = first line AFTER the 'try:' line
    end   = line index of 'except ' that closes the try

    Returns (-1, -1) if structure not found.
    """
    try_idx = -1
    except_idx = -1

    for i, line in enumerate(lines):
        if "try:" in line and "page" in line:
            try_idx = i
            break

    if try_idx == -1:
        return -1, -1

    for i in range(try_idx + 1, len(lines)):
        if line_startswith(lines[i], "except "):
            except_idx = i
            break

    if except_idx == -1:
        return -1, -1

    return try_idx + 1, except_idx


def line_startswith(line: str, prefix: str) -> bool:
    return line.lstrip().startswith(prefix)


def _get_body(script: str) -> Tuple[List[str], int, int]:
    lines = script.splitlines()
    start, end = _find_body_region(lines)
    return lines, start, end


def _rebuild_script(lines: List[str], start: int, end: int, new_body: str) -> str:
    """Rebuild script with new_body replacing [start:end]."""
    new_body_lines: List[str] = []
    for raw in new_body.splitlines():
        stripped = raw.rstrip()
        if not stripped:
            continue
        # ensure it's indented to same level as original body
        stripped = stripped.lstrip()
        new_body_lines.append(" " * 12 + stripped)
    if not new_body_lines:
        # never leave body empty; keep old body if nothing valid
        return "\n".join(lines)

    return "\n".join(lines[:start] + new_body_lines + lines[end:])


# ---------------------------
# Deterministic small fixes
# ---------------------------

def _fix_saucedemo_add_to_cart(script: str, logs: str) -> Tuple[str, str, bool]:
    """
    If logs show a failing 'Add to cart' for a Sauce Labs product,
    replace complex get_by_role chains in the BODY with stable data-test selectors.

    Works with the harness: only body is modified.
    """
    if "Sauce Labs" not in logs or "Add to cart" not in logs:
        return script, "", False

    # Extract product name: name="Sauce Labs Bike Light"
    m = re.search(r'name="(Sauce Labs[^"]+)"', logs)
    if not m:
        return script, "", False

    product_name = m.group(1).strip()
    slug = (
        product_name.strip().lower()
        .replace(" ", "-")
        .replace("™", "")
    )
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    selector = f"[data-test='add-to-cart-{slug}']"

    lines, start, end = _get_body(script)
    if start == -1:
        return script, "", False

    changed = False
    new_body_lines: List[str] = []

    for i in range(start, end):
        line = lines[i]
        stripped = line.strip()

        # if we see fancy get_by_role Add to cart stuff: replace with stable locator
        if ("Add to cart" in stripped and "get_by_role" in stripped) or (
            product_name in stripped and "Add to cart" in stripped
        ):
            new_body_lines.append(" " * 12 + f'page.locator("{selector}").click()')
            changed = True
        else:
            new_body_lines.append(line)

    if not changed:
        return script, "", False

    new_script = "\n".join(lines[:start] + new_body_lines + lines[end:])
    note = (
        f"Replaced fragile 'Add to cart' locator for '{product_name}' "
        f"with stable `{selector}` based on SauceDemo conventions."
    )
    return new_script, note, True


def _fix_products_wait(script: str, logs: str) -> Tuple[str, str, bool]:
    """
    If failure suggests waiting for Products page, ensure we wait for '.inventory_list'.
    """
    if "Products" not in logs and "inventory_item" not in logs:
        return script, "", False

    if ".inventory_list" in script:
        return script, "", False

    lines, start, end = _get_body(script)
    if start == -1:
        return script, "", False

    new_body_lines: List[str] = []
    inserted = False
    changed = False

    for i in range(start, end):
        line = lines[i]
        new_body_lines.append(line)

        if (
            not inserted
            and "page.goto" in line
        ):
            new_body_lines.append(" " * 12 + "page.wait_for_selector('.inventory_list', timeout=8000)")
            inserted = True
            changed = True

    if not changed:
        return script, "", False

    new_script = "\n".join(lines[:start] + new_body_lines + lines[end:])
    note = "Added wait_for_selector('.inventory_list') to stabilize Products page load."
    return new_script, note, True


# ---------------------------
# LLM-based body repair
# ---------------------------

def _llm_repair_body(script: str, logs: str) -> Tuple[str, str, bool]:
    """
    Ask LLM to rewrite ONLY the body inside try:; keep harness intact.
    """
    lines, start, end = _get_body(script)
    if start == -1:
        return script, "", False

    old_body = "\n".join(l[12:] for l in lines[start:end])  # de-indent

    system_prompt = (
        "You are a senior QA engineer specializing in Playwright Python.\n"
        "You are given a test harness with a try/finally around a `page` object.\n"
        "You MUST edit ONLY the body inside the try: block (the test steps).\n"
        "Do NOT modify imports, def run, with sync_playwright, or the finally block.\n"
        "Use robust selectors (data-test, ids) and proper waits.\n"
        "Return ONLY the Python statements for the new body. No imports, no def run, no markdown."
    )

    user_prompt = (
        "Here is the current body of the try: block:\n"
        f"{old_body}\n\n"
        "Here are the Playwright error logs:\n"
        f"{logs}\n\n"
        "Rewrite the body to fix the failure while keeping the same high-level goal."
    )

    raw = llm_chat(system_prompt, user_prompt, max_tokens=1500)
    if not raw:
        return script, "", False

    new_body = clean_llm_code(raw)

    # Must contain page actions
    if "page." not in new_body:
        return script, "", False

    if not has_meaningful_code_change(old_body, new_body):
        return script, "", False

    new_script = _rebuild_script(lines, start, end, new_body)
    note = "LLM-based repair: updated the test steps inside try: based on the error logs."
    return new_script, note, True


# ---------------------------
# Public entry
# ---------------------------

def self_heal(script: str, error_logs: str) -> Tuple[str, str]:
    """
    Try safe repairs in order:

      1. Deterministic SauceDemo-specific fixes (if applicable)
      2. LLM-guided rewrite of the body inside try:

    Returns (repaired_script, note).
    If no change, returns original script and an explanation.
    """
    if not script:
        return script, "No script available to repair."

    logs = error_logs or ""

    # 1) SauceDemo add-to-cart fix
    repaired, note, changed = _fix_saucedemo_add_to_cart(script, logs)
    if changed:
        return repaired, note

    # 2) Products wait fix
    repaired, note, changed = _fix_products_wait(script, logs)
    if changed:
        return repaired, note

    # 3) LLM-based body repair (generic)
    repaired, note, changed = _llm_repair_body(script, logs)
    if changed:
        return repaired, note

    return script, (
        "No automatic self-heal applied. "
        "The failure may require manual adjustment of selectors or assertions."
    )
