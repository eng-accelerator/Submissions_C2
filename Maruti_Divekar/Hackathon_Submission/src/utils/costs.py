from __future__ import annotations
from dataclasses import dataclass

@dataclass
class CostTracker:
    budget: float
    spent: float = 0.0

    def add(self, amount: float):
        self.spent += float(amount)

    def remaining(self) -> float:
        return max(0.0, self.budget - self.spent)
