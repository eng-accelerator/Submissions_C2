"""
agents_stub.py
--------------
Stubbed agent implementations to simulate the backend pipeline.

Why:
- UI testing should not depend on backend development.
- Each function simulates latency and returns minimal structured outputs
  expected by the UI and the `rag.run_research` orchestrator.
"""

import time
import random

def fake_retriever(query: str, depth: int = 3):
    """Simulate a retrieval agent returning 'depth' docs and a short summary."""
    time.sleep(1.0 + random.random()*0.8)
    docs = [
        {"title": f"Paper {i+1} about {query[:30]}...", "snippet": f"Summary snippet {i+1}", "source": f"https://example.org/doc/{i+1}"}
        for i in range(depth)
    ]
    return {"docs": docs, "summary": f"Retrieved {depth} documents for query: '{query}'"}

def fake_critical_analysis(retrieval_output):
    """Simulate an analysis agent which finds contradictions and key insights."""
    time.sleep(1.0 + random.random()*1.0)
    contradictions = ["Doc 2 claims X while Doc 3 claims not X"]
    insights = ["Key theme: increased computational power will pressure cryptography migration."]
    return {"analysis": "Critical analysis complete", "contradictions": contradictions, "insights": insights}

def fake_insight_generation(analysis_output):
    """Simulate an insight generation agent producing hypotheses and confidence."""
    time.sleep(1.0 + random.random()*0.8)
    hypotheses = [
        "Hypothesis 1: Post-quantum adoption will accelerate in 5-8 years.",
        "Hypothesis 2: Hybrid classical-quantum-resistant stacks will be common."
    ]
    return {"hypotheses": hypotheses, "confidence": 0.72}

def fake_report_builder(retrieval, analysis, insights):
    """Simulate a report builder that outputs markdown content."""
    time.sleep(0.6)
    report_md = "# Research Report\n\n"
    report_md += f"**Retrieval summary:** {retrieval['summary']}\n\n"
    report_md += f"**Analysis:** {analysis['analysis']}\n\n"
    report_md += "## Hypotheses\n"
    for h in insights['hypotheses']:
        report_md += f"- {h}\n"
    return {"report_markdown": report_md}
