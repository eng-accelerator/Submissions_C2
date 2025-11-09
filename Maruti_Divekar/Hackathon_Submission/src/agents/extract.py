from __future__ import annotations
from typing import Dict, Any
import csv
import os

class ExtractAgent:
    """Optional data extraction from simple HTML/PDF text: extract tables to CSV (best-effort)."""
    def __init__(self):
        pass

    def table_to_csv(self, rows, out_path: str):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for r in rows:
                writer.writerow(r)
        return out_path
