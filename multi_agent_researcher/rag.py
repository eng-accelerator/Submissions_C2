"""
rag.py
------
Backend orchestrator for the Streamlit UI.
Replaces previous stubbed agents with the real multi-agent pipeline backend.
"""

from backend_pipeline import PipelineState, build_pipeline
import json
import traceback

def run_research(query: str, num_agents: int = 4, retrieval_depth: int = 3, model: str = "gpt-4o", temperature: float = 0.2):
    """
    Runs the real multi-agent pipeline using backend_pipeline.py.
    Returns a structured dictionary compatible with the Streamlit UI.
    """
    try:
        # Build and compile the backend pipeline
        if __name__ == "__main__":
            pipeline = build_pipeline()

        state: PipelineState = PipelineState(
            query="Latest developments and ethical concerns in AI governance",
            sources=[
            {"type": "research", "query": "AI ethics and governance"},
            {"type": "news", "query": "AI regulation policy updates"}
         ]
        )

        result = pipeline.run(state) 
            #handles invoke/run internally)




        # Normalize backend outputs into the UI-compatible structure
        retrieval = {
            "docs": [ {"title": f"Doc {i+1}", "snippet": d.page_content[:120], "source": d.metadata.get("source", "N/A")}
                      for i, d in enumerate(result.get("chunks", [])) ],
            "summary": "Contextual retrieval completed successfully."
        }

        analysis = {
            "analysis": result.get("critical_analysis", {}).get("summary", "No analysis summary."),
            "contradictions": result.get("critical_analysis", {}).get("contradictions", []),
            "insights": [i.get("insight") for i in result.get("insights", []) if isinstance(i, dict)]
        }

        insights = {
            "hypotheses": [i.get("insight") for i in result.get("insights", []) if isinstance(i, dict)],
            "confidence": 0.75  # placeholder — could be derived from LLM confidence later
        }

        report_json = result.get("report_json", {})
        report_text = result.get("report_text", "")
        report_md = "# Research Report\n\n"
        if report_json:
            report_md += f"**Executive Summary:** {report_json.get('executive_summary', '')}\n\n"
            for sec, val in report_json.items():
                if sec not in ["executive_summary"]:
                    report_md += f"## {sec.replace('_', ' ').title()}\n{json.dumps(val, indent=2)}\n\n"
        else:
            report_md += report_text

        report = {
            "report_markdown": report_md
        }

        return {
            "retrieval": retrieval,
            "analysis": analysis,
            "insights": insights,
            "report": report
        }

    except Exception as e:
        print("❌ Error in run_research:", e)
        print(traceback.format_exc())
        return {
            "retrieval": {"docs": [], "summary": "Error occurred during retrieval."},
            "analysis": {"analysis": str(e), "contradictions": [], "insights": []},
            "insights": {"hypotheses": [], "confidence": 0.0},
            "report": {"report_markdown": f"Error: {e}"}
        }
