from src.agents.verifier import VerifierAgent
from src.agents.analyst import AnalystAgent
from src.utils.costs import CostTracker

def test_verify_claims():
    """Test verification of claims with and without evidence."""
    v = VerifierAgent()
    claims = [
        {"claim_id":"c1", "claim":"x", "evidence":[{"id":"abc", "url":"https://x"}]},
        {"claim_id":"c2", "claim":"y", "evidence":[]},
        {"claim_id":"c3", "claim":"z", "evidence":[{"id":"def"}]}  # Missing URL
    ]
    res = v.verify_claims(claims)
    assert res[0]["verified"] is True  # Has valid evidence
    assert res[1]["verified"] is False  # No evidence
    assert res[2]["verified"] is False  # Missing URL in evidence

def test_remove_unsupported():
    """Test filtering of unsupported claims."""
    v = VerifierAgent()
    claims = [
        {"claim_id":"c1", "verified":True, "evidence":[{"url":"a"}]},
        {"claim_id":"c2", "verified":False},
        {"claim_id":"c3", "verified":True, "evidence":[{"url":"b"}]}
    ]
    # Test with keep_unsupported=False (default)
    kept = v.remove_unsupported(claims, keep_unsupported=False)
    assert len(kept) == 2
    assert all(c["verified"] for c in kept)
    
    # Test with keep_unsupported=True
    all_kept = v.remove_unsupported(claims, keep_unsupported=True)
    assert len(all_kept) == 3

def test_cost_tracking():
    """Test budget tracking utility."""
    tracker = CostTracker(budget=1.0)
    tracker.add(0.3)
    tracker.add(0.4)
    assert abs(tracker.remaining() - 0.3) < 1e-6  # Use epsilon for float comparison
    assert abs(tracker.spent - 0.7) < 1e-6
    tracker.add(0.2)
    assert abs(tracker.remaining() - 0.1) < 1e-6

def test_analyst_contradiction():
    """Test contradiction detection in analyst."""
    a = AnalystAgent()
    summaries = [
        {"id": "1", "summary": "There is no evidence for X causing Y."},
        {"id": "2", "summary": "X definitely causes Y according to study Z."}
    ]
    contradictions = a.detect_contradictions(summaries)
    assert len(contradictions) >= 1
    assert any("no evidence" in c.lower() for c in contradictions)
