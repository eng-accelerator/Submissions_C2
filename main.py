#!/usr/bin/env python3
"""
Multi-Agent AI Deep Researcher
- Prefers JSON input from CLI (--input), else env var (RESEARCH_INPUT_FILE),
  else local fallback research_input.json / input.json
- Falls back to the built-in sample if nothing is found/valid
"""

import json
import os
import sys
from pathlib import Path
import argparse

from insight_agent import InsightGenerationAgent
from report_agent import ReportBuilderAgent
from config import Config


def setup_environment():
    """Setup and validate environment"""
    print("🚀 Setting up Multi-Agent AI Deep Researcher.")
    try:
        Config.validate_config()
        print("✅ Configuration validated successfully")
        Path(Config.OUTPUT_DIR).mkdir(exist_ok=True)
        print(f"✅ Output directory ready: {Config.OUTPUT_DIR}")
        return True
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False


def parse_args(argv=None):
    """Parse CLI args; ignore unknown (Spyder/IPython often injects extras)."""
    p = argparse.ArgumentParser(description="Run Multi-Agent AI Deep Researcher")
    p.add_argument(
        "--input",
        dest="input_path",
        help='Path to JSON file containing {"contextual_data": {...}, "analysis_results": {...}}',
    )
    # Ignore unknown args to avoid Spyder/IPython conflicts
    args, _ = p.parse_known_args(argv)
    return args


def resolve_input_path(args) -> str | None:
    """Decide which JSON to use: CLI > env var > local defaults."""
    # 1) CLI
    if args and args.input_path:
        return args.input_path

    # 2) ENV
    env_path = os.getenv("RESEARCH_INPUT_FILE")
    if env_path:
        return env_path

    # 3) Local defaults next to main.py
    here = Path(__file__).resolve().parent
    for candidate in ["research_input.json", "input.json"]:
        p = here / candidate
        if p.exists():
            return str(p)

    # 4) As a convenience, try the first *.json that has the right keys
    for jf in (here.glob("*.json")):
        try:
            with jf.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "contextual_data" in data and "analysis_results" in data:
                return str(jf)
        except Exception:
            pass

    return None


def load_research_data(input_path: str | None):
    """
    Load research data from JSON if provided, else return the built-in sample.
    The JSON file must contain keys: 'contextual_data' and 'analysis_results'.
    """
    if input_path:
        p = Path(input_path)
        print(f"\n🔎 Looking for input JSON: {p}")
        if not p.exists():
            raise FileNotFoundError(f"Input file not found: {p}")

        print(f"📊 Loading research data from {p}")
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict) or "contextual_data" not in data or "analysis_results" not in data:
            raise ValueError("Invalid input JSON. Expected top-level keys 'contextual_data' and 'analysis_results'.")

        return data["contextual_data"], data["analysis_results"]

    # -------- Built-in SAMPLE (unchanged idea) --------
    print("\n📊 Loading sample research data.")
    sample_contextual_data = {
        "sources": [
            {
                "type": "research_paper",
                "title": "The Impact of AI on Productivity",
                "year": 2024,
                "authors": ["Smith, J.", "Johnson, A."],
                "journal": "Journal of AI Research",
            },
            {
                "type": "news_article",
                "title": "Market Trends in AI Adoption",
                "year": 2024,
                "publication": "Tech Review",
            },
            {
                "type": "industry_report",
                "title": "Q3 2024 AI Market Analysis",
                "year": 2024,
                "organization": "AI Research Group",
            },
        ],
        "time_range": "2020-2024",
        "geographic_scope": "Global",
        "domain": "Artificial Intelligence",
        "key_topics": ["productivity", "adoption", "market trends", "implementation"],
    }

    sample_analysis_results = {
        "key_findings": [
            "AI adoption correlates with 25-35% productivity increase in early adopters",
            "Organizations with structured AI training programs show faster ROI",
            "Data quality is the primary barrier to successful AI implementation",
            "SMEs lag in AI adoption due to cost concerns",
        ],
        "contradictions": [
            "Study A shows 40% productivity boost vs Study B shows 20% boost",
            "Some reports emphasize technical barriers while others emphasize cultural resistance",
            "Conflicting timelines for ROI across industries",
        ],
        "source_validations": {
            "research_paper_1": True,
            "news_article_1": True,
            "industry_report_1": True,
            "blog_post_1": False,
        },
        "confidence_score": 0.82,
        "summary": "Strong evidence for AI productivity benefits, tempered by implementation challenges.",
        "patterns": [
            "Early adopters consistently outperform laggards",
            "Training investment correlates with success metrics",
            "Industry-specific variations in implementation success",
        ],
    }

    return sample_contextual_data, sample_analysis_results


def main():
    """Main execution function"""
    # Debug info to confirm args & context (very helpful in Spyder!)
    print(f"🐍 Python: {sys.executable}")
    print(f"📂 CWD:    {os.getcwd()}")
    print(f"🧵 argv:   {sys.argv}")

    args = parse_args()
    chosen_input = resolve_input_path(args)
    print(f"🗂️ Resolved input path: {chosen_input or '(none; will use sample)'}")

    if not setup_environment():
        return

    print("\n🤖 Initializing AI Agents.")
    insight_agent = InsightGenerationAgent()
    report_agent = ReportBuilderAgent()
    print("✅ Agents initialized successfully")

    # Load data (JSON if provided, else sample)
    contextual_data, analysis_results = load_research_data(chosen_input)

    print(
        f"📈 Data ready: {len(contextual_data.get('sources', []))} sources, "
        f"{len(analysis_results.get('key_findings', []))} findings"
    )

    # Step 1: Generate Insights
    print("\n💡 Generating insights with Insight Generation Agent.")
    insights = insight_agent.generate_insights(
        analysis_data=analysis_results,
        contradictions=analysis_results.get("contradictions", []),
        source_validations=analysis_results.get("source_validations", {}),
    )
    print(f"✅ Generated {len(insights)} insights")

    # Format insights for reporting
    formatted_insights = insight_agent.format_insights_report(insights)

    # Step 2: Build Comprehensive Report
    print("\n📄 Building comprehensive report with Report Builder Agent.")
    report = report_agent.build_comprehensive_report(
        contextual_data=contextual_data,
        analysis_results=analysis_results,
        insights=formatted_insights["insights"],
        report_type="research_report",
    )

    # Step 3: Save Report
    print("\n💾 Saving report.")
    report_agent.save_report(report)

    # Display summary
    print("\n🎉 MULTI-AGENT RESEARCH COMPLETED!")
    print("=" * 50)
    print(f"📊 Insights Generated: {len(insights)}")
    print(f"📄 Report ID: {report['metadata']['report_id']}")
    print(f"📁 Output Formats: {', '.join(report['formats'].keys())}")
    print(f"📂 Saved to: {Config.OUTPUT_DIR}/")
    print("=" * 50)

    if insights:
        sample_insight = insights[0]
        print(f"\n🔍 Sample Insight:")
        print(f"Statement: {sample_insight.statement}")
        print(f"Confidence: {sample_insight.confidence:.2f}")
        print(f"Type: {sample_insight.reasoning_type.value}")


if __name__ == "__main__":
    main()
