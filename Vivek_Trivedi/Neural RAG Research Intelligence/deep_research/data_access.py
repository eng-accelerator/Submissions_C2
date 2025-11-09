"""Shared data/retrieval helpers for the multi-agent researcher."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.core import VectorStoreIndex


BASE_DIR = Path(__file__).resolve().parent.parent
METADATA_DIR = BASE_DIR / "AssignmentDb"
INGEST_MANIFEST_PATH = METADATA_DIR / "a3b_processed_manifest.json"


def _normalize_path(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()
    return path


def get_database_path() -> Path:
    default_path = METADATA_DIR / "a3b_advanced_gradio_rag_vectordb"
    raw = os.getenv("ASSIGNMENT_3B_DB_PATH", str(default_path))
    return _normalize_path(raw)


def get_vector_store(table_name: str = "documents") -> LanceDBVectorStore:
    """Return a LanceDB vector store pointing at the shared Assignment 3b DB."""
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return LanceDBVectorStore(uri=str(db_path), table_name=table_name)


def load_vector_index(table_name: str = "documents") -> Tuple[Optional[VectorStoreIndex], str]:
    """Attempt to load the LanceDB-backed index for reuse across agents."""
    db_path = get_database_path()
    db_file = db_path / f"{table_name}.lance"
    if not db_file.exists():
        return None, f"Vector store not found at {db_file}. Run the Assignment 3b ingestion first."
    try:
        vector_store = get_vector_store(table_name=table_name)
        index = VectorStoreIndex.from_vector_store(vector_store)
        return index, "Vector index loaded from LanceDB."
    except Exception as exc:  # pragma: no cover - defensive logging
        return None, f"Failed to load vector index: {exc}"


def ensure_ingest_manifest() -> Dict[str, Any]:
    """Return the ingest manifest metadata if it exists, otherwise create a stub."""
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    if INGEST_MANIFEST_PATH.exists():
        with open(INGEST_MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    payload: Dict[str, Any] = {
        "document_count": 0,
        "chunk_size": None,
        "chunk_overlap": None,
        "data_path": os.getenv("DATA_PATH"),
        "updated_at": datetime.now().isoformat(),
        "processed_files": [],
    }
    with open(INGEST_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return payload
