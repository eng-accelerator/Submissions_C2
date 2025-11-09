# Sample pipeline execution script

import json
from src.agents.planner import PlannerAgent
from src.agents.retriever import RetrieverAgent
from src.agents.analyst import AnalystAgent
from src.agents.verifier import VerifierAgent
from src.agents.reporter import ReporterAgent
from .demo_query import QUERY, CONSTRAINTS

def run_demo():
    """Run the research pipeline with demo query and constraints."""
    print(f"Query: {QUERY}")
    print(f"Constraints: {json.dumps(CONSTRAINTS, indent=2)}")
    print("\nExecuting research pipeline...")

    # Initialize agents
    planner = PlannerAgent(CONSTRAINTS)
    retriever = RetrieverAgent()
    analyst = AnalystAgent()
    verifier = VerifierAgent()
    reporter = ReporterAgent()

    # Execute pipeline
    plan = planner.plan(QUERY)
    print(f"\nPlan: {json.dumps(plan, indent=2)}")

    passages = retriever.retrieve(
        QUERY,
        domains=CONSTRAINTS.get("domains"),
        time_window=CONSTRAINTS.get("time_window")
    )
    print(f"\nRetrieved {len(passages)} passages")

    analyses = analyst.summarize_sources(passages)
    claims = analyst.claim_evidence_map(analyses["merged"], passages)
    print(f"\nMapped {len(claims)} claims to evidence")

    verified = verifier.verify_claims(claims)
    cleaned = verifier.remove_unsupported(verified)
    print(f"\nVerified {len(cleaned)} claims with citations")

    artifact = reporter.build_report(QUERY, plan, analyses, cleaned)
    print(f"\nReport generated at: {artifact['md_path']}")
    print(f"JSON artifact at: {artifact['json_path']}")

if __name__ == "__main__":
    run_demo()