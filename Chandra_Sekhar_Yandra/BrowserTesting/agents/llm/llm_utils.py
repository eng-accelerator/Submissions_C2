# agents/llm_utils.py

import re

def clean_llm_code(raw: str) -> str:
    """
    Normalize LLM output that is expected to be ONLY Python code.

    - Strip leading/trailing whitespace.
    - Remove ```...``` fences.
    - Drop a solitary leading 'python' language tag.
    """
    if not raw:
        return ""

    text = raw.strip()

    # If wrapped in ``` ``` fences, peel them off.
    if text.startswith("```"):
        # remove first fence
        text = text[3:]
        # optional language tag
        if text.lower().startswith("python"):
            text = text.split("\n", 1)[1] if "\n" in text else ""
        # strip trailing fence if present
        if "```" in text:
            text = text.split("```", 1)[0]

    # If first line is just 'python', drop it.
    lines = text.splitlines()
    if lines and lines[0].strip().lower() == "python":
        lines = lines[1:]

    return "\n".join(lines).strip()


def normalize_code_line(line: str) -> str:
    """Strip whitespace; treat blank/comment-only lines as empty."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return ""
    return stripped


def has_meaningful_code_change(original: str, candidate: str) -> bool:
    """
    True if candidate differs from original in REAL code (selectors, waits, actions),
    not just comments/whitespace.
    """
    if not candidate or candidate.strip() == original.strip():
        return False

    o_lines = original.splitlines()
    c_lines = candidate.splitlines()
    max_len = max(len(o_lines), len(c_lines))

    interesting = ["page.", "locator(", "get_by_", "wait_for_", "click(", "fill(", "goto(",
                   "assert", "expect("]

    for i in range(max_len):
        o = normalize_code_line(o_lines[i]) if i < len(o_lines) else ""
        c = normalize_code_line(c_lines[i]) if i < len(c_lines) else ""
        if o != c:
            if any(tok in o or tok in c for tok in interesting):
                return True

    return False
