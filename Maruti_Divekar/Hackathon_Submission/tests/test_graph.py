import pytest
from src.agents.planner import PlannerAgent
from src.agents.retriever import RetrieverAgent
from src.agents.reporter import ReporterAgent
import os
import json
import tempfile
from src.utils.config import load_settings

def test_planner_shallow():
    """Test planner with shallow depth."""
    c = {"depth": "shallow", "max_budget_usd": 1.0}
    p = PlannerAgent(c)
    plan = p.plan("What causes X?")
    assert isinstance(plan, dict)
    assert "hops" in plan
    assert "query" in plan
    assert isinstance(plan["estimated_cost_usd"], (int, float))
    assert plan["estimated_cost_usd"] <= c["max_budget_usd"]

def test_planner_constraints():
    """Test planner respects various constraints."""
    c = {
        "depth": "deep",
        "max_budget_usd": 2.0,
        "domains": ["nature.com", "who.int"],
        "time_window": "2020-01-01..2025-12-31"
    }
    p = PlannerAgent(c)
    plan = p.plan("Complex query")
    assert len(plan["hops"]) >= 5  # Deep has more steps
    assert plan["estimated_cost_usd"] <= c["max_budget_usd"]

def test_retriever_search(monkeypatch):
    """Test retriever with mocked search."""
    search_results = [
        {"url": "https://example.com/a", "snippet": "alpha", "title": "Test A"},
        {"url": "https://example.com/b", "snippet": "beta", "title": "Test B"}
    ]
    monkeypatch.setattr(
        'agents.retriever.WebSearchTool.search',
        lambda q, domains, time_window, top_k: search_results
    )
    r = RetrieverAgent()
    res = r.search_web("query", domains=["example.com"], time_window="2020..2025", top_k=2)
    assert len(res) == 2
    assert all(d["url"].startswith("http") for d in res)
    assert all("text" in d for d in res)  # Check snippet mapped to text

def test_reporter_artifacts():
    """Test reporter output format and paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        r = ReporterAgent(out_dir=tmpdir)
        plan = {"hops": ["test"], "estimated_cost_usd": 0.5}
        claims = [
            {
                "claim_id": "c1",
                "claim": "Test claim",
                "evidence": [{"id": "e1", "url": "http://test.com"}],
                "verified": True,
                "notes": ["High confidence"]
            }
        ]
        artifact = r.build_report(
            query="Does X affect Y?",
            plan=plan,
            analyses={"merged": "Test found correlation."},
            claims=claims
        )
        # Check files exist
        assert os.path.exists(artifact["md_path"])
        assert os.path.exists(artifact["json_path"])
        
        # Validate JSON structure
        with open(artifact["json_path"]) as f:
            data = json.load(f)
            assert "query" in data
            assert "plan" in data
            assert "claims" in data
            assert "meta" in data
            assert isinstance(data["meta"].get("generated"), str)
        
        # Check markdown contains key sections
        with open(artifact["md_path"]) as f:
            md = f.read()
            assert "# Research Report" in md
            assert "Evidence" in md
            assert "Claims & Evidence" in md
            assert "[citation:" in md  # Has citation markers

def test_settings_load():
    """Test config loader with defaults."""
    settings = load_settings()
    assert isinstance(settings, dict)
    assert "project" in settings
    assert "budgets" in settings
    assert isinstance(settings["budgets"].get("max_budget_usd_default"), (int, float))
