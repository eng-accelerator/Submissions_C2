"""
utils.py
--------
Small utility helpers for the UI: timestamps and markdown assembly.

Why:
- Centralizes small formatting helpers so the UI code remains compact.
"""

import datetime

def timestamp():
    """Return a local timestamp string for report footers."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def compile_report_md(report_dict):
    """
    Accepts the dict returned by rag.run_research and returns a final markdown string
    with a generated timestamp footer.
    """
    md = report_dict["report"]["report_markdown"]
    md += f"\n\n---\nGenerated: {timestamp()}\n"
    return md
