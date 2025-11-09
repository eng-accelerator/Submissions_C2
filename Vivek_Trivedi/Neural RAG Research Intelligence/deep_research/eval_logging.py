"""Lightweight logging for retrieval experiments."""

from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


LOG_PATH = Path("logs/retrieval_log.csv")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class RetrievalEvent:
    timestamp: str
    query: str
    source: str
    doc_identifier: str
    score: Optional[float]
    passed_cutoff: bool
    metadata: str


def log_retrieval_event(event: RetrievalEvent) -> None:
    is_new_file = not LOG_PATH.exists()
    with LOG_PATH.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(asdict(event).keys()))
        if is_new_file:
            writer.writeheader()
        writer.writerow(asdict(event))


def create_event(
    query: str,
    source: str,
    doc_identifier: str,
    score: Optional[float],
    passed_cutoff: bool,
    metadata: Optional[str] = None,
) -> RetrievalEvent:
    return RetrievalEvent(
        timestamp=datetime.utcnow().isoformat(),
        query=query,
        source=source,
        doc_identifier=doc_identifier,
        score=score,
        passed_cutoff=passed_cutoff,
        metadata=metadata or "",
    )
