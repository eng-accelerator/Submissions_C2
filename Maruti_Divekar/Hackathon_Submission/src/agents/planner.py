from __future__ import annotations
from typing import Any, Dict
from src.utils.config import load_settings
from src.utils.costs import CostTracker
import time

SETTINGS = load_settings()

class PlannerAgent:
    def __init__(self, constraints: Dict[str,Any] | None = None):
        self.constraints = constraints or {}
        self.costs = CostTracker(self.constraints.get('max_budget_usd', SETTINGS['budgets']['max_budget_usd_default']))
        self.start = time.time()

    def plan(self, query: str) -> Dict[str,Any]:
        depth = self.constraints.get('depth','shallow')
        if depth == 'deep':
            hops = ['scoping','retrieval','analysis','verification','insights','reporting']
        else:
            hops = ['scoping','retrieval','analysis','verification','reporting']
        plan = {
            'query': query,
            'hops': hops,
            'estimated_cost_usd': 0.1 * len(hops),
            'estimated_tokens': 1000 * len(hops)
        }
        return plan
