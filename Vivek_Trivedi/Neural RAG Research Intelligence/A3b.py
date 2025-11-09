# Assignment 3b: Advanced Gradio RAG Frontend
# Day 6 Session 2 - Building Configurable RAG Applications
# Advanced RAG interface with full configuration options

import gradio as gr
import os
import json
import shutil
import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections.abc import Iterable
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LlamaIndex core components
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.core.schema import TextNode
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter

# Advanced RAG components
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import TreeSummarize, Refine, CompactAndRefine
from llama_index.core.retrievers import VectorIndexRetriever

from langchain_openai import ChatOpenAI

from agents import (
    ResearchPlannerAgent,
    ContextualRetrieverAgent,
    CriticalAnalysisAgent,
    InsightGenerationAgent,
    ReportBuilderAgent,
    RetrieverConfig,
    PlannerOutput,
    RetrievedContext,
    CriticalAnalysisOutput,
    InsightOutput,
    ReportOutput,
)
try:  # pragma: no cover - optional dependency
    from deep_research.graph import GraphAgents, build_research_graph, run_research
    LANGGRAPH_AVAILABLE = True
except Exception as e:  # pragma: no cover - optional dependency
    LANGGRAPH_AVAILABLE = False
    LANGGRAPH_IMPORT_ERROR = e

print("✅ All libraries imported successfully!")

# Resolve repository base so relative paths work even if script is launched elsewhere
BASE_DIR = Path(__file__).resolve().parent
METADATA_DIR = BASE_DIR / "AssignmentDb"
INGEST_MANIFEST_PATH = METADATA_DIR / "a3b_processed_manifest.json"
CONFIG_DIR = BASE_DIR / "config"
UI_CONFIG_PATH = CONFIG_DIR / "rag_ui_config.json"
UPLOADS_DIR = BASE_DIR / "uploads"
ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".txt", ".md", ".doc", ".docx", ".rtf", ".epub"}


def load_ui_config() -> Dict[str, Any]:
    """Load UI configuration values from rag_ui_config.json if present."""
    try:
        with open(UI_CONFIG_PATH, "r", encoding="utf-8") as fp:
            return json.load(fp)
    except FileNotFoundError:
        return {}
    except Exception as exc:
        print(f"⚠️ Could not load {UI_CONFIG_PATH}: {exc}")
        return {}


UI_CONFIG = load_ui_config()


def get_rag_default(key: str, fallback: Any) -> Any:
    """Convenience helper to read default values from the UI config."""
    defaults = UI_CONFIG.get("rag_defaults", {})
    value = defaults.get(key)
    return fallback if value is None else value


def _sanitize_filename(name: str) -> str:
    """Return a filesystem-safe filename while preserving extensions."""
    name = (name or "").strip()
    if not name:
        return "document"
    sanitized = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    sanitized = sanitized.strip("._")
    return sanitized or "document"


def handle_document_upload(files: Optional[List[Any]]) -> str:
    """Copy uploaded documents into the default data folder."""
    if not files:
        return "⚠️ Please select at least one document to upload."

    if not isinstance(files, list):
        files = [files]

    target_dir = UPLOADS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    saved: List[str] = []
    skipped: List[str] = []

    for file_obj in files:
        if not file_obj:
            continue
        temp_path = Path(getattr(file_obj, "name", ""))
        if not temp_path or not temp_path.exists():
            continue
        original_name = getattr(file_obj, "orig_name", temp_path.name)
        suffix = Path(original_name).suffix.lower()
        if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
            skipped.append(original_name or temp_path.name)
            continue
        safe_name = _sanitize_filename(original_name)
        if not safe_name.lower().endswith(suffix):
            safe_name = f"{safe_name}{suffix}"
        destination = target_dir / safe_name
        counter = 1
        while destination.exists():
            destination = target_dir / f"{destination.stem}_{counter}{destination.suffix}"
            counter += 1
        shutil.copy(temp_path, destination)
        saved.append(destination.name)

    if not saved:
        details = ", ".join(skipped) if skipped else "unsupported files"
        return f"⚠️ Upload failed. Unsupported file types: {details}."

    status = [
        f"✅ Uploaded {len(saved)} file(s) to `{target_dir.name}` for review:",
        ", ".join(saved),
        "🔒 We'll verify the content before adding it to the shared knowledge base.",
    ]
    if skipped:
        status.append(f"⚠️ Skipped unsupported files: {', '.join(skipped)}.")
    try:
        gr.Info("Upload received! We'll review it before making it available.")
    except Exception:
        pass
    return "\n".join(status)


def _flatten_documents(possible_docs: Any) -> List[Any]:
    """
    Recursively flatten nested iterable containers of documents into
    a single list while preserving order.
    """
    flat: List[Any] = []

    def _walk(item: Any):
        if item is None:
            return
        if isinstance(item, (str, bytes)):
            flat.append(item)
            return
        if isinstance(item, dict):
            flat.append(item)
            return
        if isinstance(item, Iterable):
            try:
                iterator = iter(item)
            except TypeError:
                flat.append(item)
                return
            # Avoid treating BaseNode-like objects (Documents, TextNodes) as containers
            if hasattr(item, "id_") or hasattr(item, "doc_id") or hasattr(item, "node_id"):
                flat.append(item)
                return
            for sub in iterator:
                _walk(sub)
            return
        flat.append(item)

    _walk(possible_docs)
    return flat


def _standardize_documents(raw_docs: Any) -> Tuple[List[TextNode], List[str]]:
    """
    Flatten nested outputs from SimpleDirectoryReader and convert
    each entry into a TextNode (or accept an existing BaseNode).
    """
    flattened = _flatten_documents(raw_docs)
    accepted: List[TextNode] = []
    skipped: List[str] = []

    for item in flattened:
        node = None

        if hasattr(item, "id_") and hasattr(item, "text"):
            node = item
        else:
            text = None
            metadata = {}
            node_id = None

            if hasattr(item, "text"):
                text = getattr(item, "text", None)
                metadata = getattr(item, "metadata", {}) or {}
                node_id = getattr(item, "doc_id", None) or getattr(item, "node_id", None)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")
                metadata = item.get("metadata") or {}
                node_id = item.get("id") or item.get("doc_id")
            elif isinstance(item, (str, bytes)):
                text = item.decode("utf-8") if isinstance(item, bytes) else item

            if text:
                try:
                    node = TextNode(text=text, metadata=metadata)
                    if node_id:
                        node.id_ = node_id
                except Exception:
                    node = None

        if node is not None and hasattr(node, "id_"):
            accepted.append(node)
        else:
            item_type = type(item).__name__
            skipped.append(item_type)

    return accepted, skipped


def _normalize_path(path_str: str) -> Path:
    """Return absolute Path for a potential relative/user path."""
    candidate = Path(path_str).expanduser()
    if not candidate.is_absolute():
        candidate = (BASE_DIR / candidate).resolve()
    return candidate


def get_default_data_folder() -> Path:
    """
    Determine the best available data-folder path.
    
    Priority:
    1. DATA_PATH env var (if it exists on disk)
    2. ./DataSource inside the repo
    3. ./data inside the repo
    Returns the first match even if it doesn't exist so the caller can raise a clear error.
    """
    candidates = []
    env_path = os.getenv("DATA_PATH")
    if env_path:
        candidates.append(_normalize_path(env_path))
    candidates.append(BASE_DIR / "DataSource")
    candidates.append(BASE_DIR / "data")
    
    for path in candidates:
        if path.exists():
            return path
    return candidates[0] if candidates else BASE_DIR


def scan_data_files(directory: Path) -> Dict[str, Dict[str, Any]]:
    """Return mapping of relative file paths to metadata for all files under directory."""
    files: Dict[str, Dict[str, Any]] = {}
    if not directory.exists():
        return files
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            rel_path = str(file_path.relative_to(directory))
            stat = file_path.stat()
            files[rel_path] = {
                "absolute_path": str(file_path),
                "size": stat.st_size,
                "modified": stat.st_mtime,
            }
    return files


def serialize_processed_files(file_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert scanned file metadata into a JSON-serializable list."""
    serialized: List[Dict[str, Any]] = []
    timestamp = datetime.now().isoformat()
    for rel_path in sorted(file_map.keys()):
        meta = file_map[rel_path]
        serialized.append({
            "relative_path": rel_path,
            "absolute_path": meta["absolute_path"],
            "size": meta["size"],
            "modified": datetime.fromtimestamp(meta["modified"]).isoformat(),
            "modified_ts": meta["modified"],
            "recorded_at": timestamp
        })
    return serialized


def build_processed_lookup(processed_files: Optional[List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    """Create lookup dict keyed by relative path for processed file metadata."""
    lookup: Dict[str, Dict[str, Any]] = {}
    if not processed_files:
        return lookup
    for entry in processed_files:
        rel_path = entry.get("relative_path") or entry.get("path")
        if rel_path:
            lookup[rel_path] = entry
    return lookup


def load_ingest_manifest(expected_chunk_size: Optional[int] = None, expected_chunk_overlap: Optional[int] = None) -> Dict[str, Any]:
    """Load persisted ingest manifest from disk."""
    if not INGEST_MANIFEST_PATH.exists():
        return {}
    try:
        with open(INGEST_MANIFEST_PATH, "r") as f:
            manifest = json.load(f)
        if expected_chunk_size is not None and expected_chunk_overlap is not None:
            if (
                manifest.get("chunk_size") != expected_chunk_size
                or manifest.get("chunk_overlap") != expected_chunk_overlap
            ):
                return {}
        return manifest
    except Exception as e:
        print(f"⚠️ Could not read ingest manifest: {e}")
        return {}


def save_ingest_manifest(manifest: Dict[str, Any]):
    """Persist ingest manifest outside the database folder."""
    try:
        METADATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(INGEST_MANIFEST_PATH, "w") as f:
            json.dump(manifest, f, indent=2)
    except Exception as e:
        print(f"⚠️ Could not save ingest manifest: {e}")


def get_assignment_3b_db_path() -> Path:
    """Return normalized Assignment 3B database path."""
    raw_db_path = os.getenv(
        "ASSIGNMENT_3B_DB_PATH",
        str(BASE_DIR / "AssignmentDb" / "a3b_advanced_gradio_rag_vectordb")
    )
    return _normalize_path(raw_db_path)


def read_existing_chunk_parameters() -> Tuple[Optional[int], Optional[int]]:
    """Read previously stored chunk_size/chunk_overlap if available."""
    db_path = get_assignment_3b_db_path()
    config_file = db_path / "chunk_config.json"
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                cfg = json.load(f)
            chunk_size = cfg.get("chunk_size")
            chunk_overlap = cfg.get("chunk_overlap")
            if chunk_size is not None and chunk_overlap is not None:
                return int(chunk_size), int(chunk_overlap)
        except Exception as e:
            print(f"⚠️ Could not read chunk configuration file: {e}")
    manifest = load_ingest_manifest()
    if manifest:
        chunk_size = manifest.get("chunk_size")
        chunk_overlap = manifest.get("chunk_overlap")
        if chunk_size is not None and chunk_overlap is not None:
            return int(chunk_size), int(chunk_overlap)
    return None, None


def check_vector_db_exists(db_path: str, table_name: str = "documents"):
    """
    Check if vector database already exists and has data.
    
    Args:
        db_path (str): Path to the vector database
        table_name (str): Name of the table to check
        
    Returns:
        bool: True if database exists and has data, False otherwise
    """
    try:
        db_file = Path(db_path) / f"{table_name}.lance"
        return db_file.exists()
    except Exception:
        return False

def check_database_configuration(db_path: str, chunk_size: int, chunk_overlap: int):
    db_path_obj = Path(db_path)
    if not db_path_obj.exists():
        return False, "📁 No existing database found - will create new database"
    if not check_vector_db_exists(db_path):
        return False, "📁 Database directory exists but no data files found - will create new database"
    config_file = db_path_obj / "chunk_config.json"
    if not config_file.exists():
        return False, "⚠️ Database exists but no configuration metadata found - will rebuild to ensure consistency"
    try:
        with open(config_file, 'r') as f:
            stored_config = json.load(f)
        # Ensure types match
        stored_chunk_config = {
            "chunk_size": int(stored_config.get("chunk_size")),
            "chunk_overlap": int(stored_config.get("chunk_overlap"))
        }
        current_config = {
            "chunk_size": int(chunk_size),
            "chunk_overlap": int(chunk_overlap)
        }
        if stored_chunk_config != current_config:
            return False, f"""🔄 Configuration changed - database will be rebuilt:
   Previous: chunk_size={stored_chunk_config['chunk_size']}, chunk_overlap={stored_chunk_config['chunk_overlap']}
   New: chunk_size={current_config['chunk_size']}, chunk_overlap={current_config['chunk_overlap']}
   📊 This ensures optimal retrieval with your new chunking strategy"""
        doc_count = stored_config.get("document_count", "unknown")
        return True, f"✅ Found existing database with matching configuration (chunk_size={chunk_size}, chunk_overlap={chunk_overlap}, {doc_count} documents)"
    except Exception as e:
        return False, f"⚠️ Error reading configuration metadata: {str(e)} - will rebuild database"

def save_database_configuration(
    db_path: str,
    chunk_size: int,
    chunk_overlap: int,
    document_count: int,
    data_path: Optional[str] = None,
    processed_files: Optional[List[Dict[str, Any]]] = None
):
    """
    Save database configuration metadata.
    
    Args:
        db_path (str): Path to the vector database
        chunk_size (int): Chunk size used
        chunk_overlap (int): Chunk overlap used  
        document_count (int): Number of documents processed
    """
    db_path_obj = Path(db_path)
    config_file = db_path_obj / "chunk_config.json"
    
    config = {
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "document_count": document_count,
        "created_at": datetime.now().isoformat(),
        "data_path": data_path or os.getenv('DATA_PATH', 'N/A'),
        "version": "A3b_v1.0",
        "processed_files": processed_files or []
    }
    
    try:
        db_path_obj.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"💾 Configuration metadata saved: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}, documents={document_count}")
    except Exception as e:
        print(f"⚠️ Could not save configuration metadata: {e}")


def persist_ingest_metadata(
    db_path: str,
    chunk_size: int,
    chunk_overlap: int,
    document_count: int,
    data_path: str,
    processed_files: List[Dict[str, Any]]
):
    """Persist chunk configuration (inside DB folder) and processed manifest (outside)."""
    save_database_configuration(
        db_path,
        chunk_size,
        chunk_overlap,
        document_count,
        data_path=data_path,
        processed_files=processed_files
    )
    manifest_payload = {
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "document_count": document_count,
        "data_path": data_path,
        "updated_at": datetime.now().isoformat(),
        "processed_files": processed_files
    }
    save_ingest_manifest(manifest_payload)


class AdvancedRAGBackend:
    """Advanced RAG backend with configurable parameters."""
    
    def __init__(self):
        self.index = None
        self.is_initializing = False
        self.is_ready = False
        self.current_chunk_size: Optional[int] = None
        self.current_chunk_overlap: Optional[int] = None
        self.available_models = ["gpt-4o", "gpt-4o-mini"]
        self.available_postprocessors = ["SimilarityPostprocessor"]
        self.available_synthesizers = ["TreeSummarize", "Refine", "CompactAndRefine", "Default"]
        self.embedding_model_name = os.getenv("A3B_EMBED_MODEL", "BAAI/bge-small-en-v1.5")
        self.setup_initial_settings()

    @staticmethod
    def _append_source_note(response_text: str, source_note: str) -> str:
        """Attach a short provenance blurb at the end of the response."""
        separator = "\n" if response_text.endswith("\n") else "\n\n"
        return f"{response_text}{separator}{source_note}"

    @staticmethod
    def _format_score_suffix(scores: List[Optional[float]]) -> str:
        numeric_scores = [s for s in scores if isinstance(s, (int, float))]
        if not numeric_scores:
            return ""
        best = max(numeric_scores)
        return f" Top score: {best:.3f}"

    def _direct_llm_answer(self, prompt: str) -> Tuple[bool, str]:
        """Call the configured LLM directly without retrieval."""
        llm = getattr(Settings, "llm", None)
        if llm is None:
            return False, "LLM is not configured."
        try:
            if hasattr(llm, "complete"):
                response = llm.complete(prompt)
                text = getattr(response, "text", None) or str(response)
            elif hasattr(llm, "chat"):
                chat_response = llm.chat([("user", prompt)])
                text = getattr(chat_response, "message", None) or getattr(chat_response, "text", None) or str(chat_response)
            else:
                text = str(llm(prompt))
            return True, (text or "").strip()
        except Exception as e:
            return False, f"LLM error: {e}"

    @staticmethod
    def _needs_llm_elaboration(question: str, synthesizer_name: str) -> bool:
        """Heuristic to determine when the user implicitly requests LLM elaboration."""
        if synthesizer_name and synthesizer_name != "Default":
            return True
        lowered = (question or "").strip().lower()
        if not lowered:
            return False
        keywords = [
            "elaborate",
            "summarize",
            "explain",
            "detailed",
            "details",
            "analysis",
            "insight",
            "compare",
            "contrast",
            "implication",
            "why",
            "how does",
            "impact",
        ]
        return any(keyword in lowered for keyword in keywords)

    def _format_context_response(self, nodes: List[Any], header: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Create a plain-text response directly from retrieved nodes."""
        if not nodes:
            message = "⚠️ No relevant documents found in the vector database."
            return self._append_source_note(message, "📚 Response source: Database."), []

        retrieved_sections: List[str] = []
        sources: List[Dict[str, Any]] = []
        scores: List[Optional[float]] = []
        for idx, node in enumerate(nodes, 1):
            text = getattr(node, "text", "")
            if len(text) > 500:
                snippet = text[:500] + "..."
            else:
                snippet = text
            retrieved_sections.append(f"**Document {idx}:**\n{snippet}")
            metadata = getattr(getattr(node, "node", None), "metadata", {}) or {}
            score = getattr(node, 'score', None)
            scores.append(score)
            sources.append({
                "text": snippet[:200] + ("..." if len(snippet) > 200 else ""),
                "score": score or 0.0,
                "source": metadata.get('file_name') or metadata.get('file_path') or metadata.get('source', 'Unknown')
            })

        score_suffix = self._format_score_suffix(scores)
        prefix = f"📚 Response source: Database.{score_suffix}\n\n" if score_suffix else "📚 Response source: Database.\n\n"
        response = prefix + f"{header}\n\n" + "\n\n".join(retrieved_sections)
        return response, sources

    def setup_initial_settings(self):
        """Set up initial LlamaIndex settings."""
        # Check for OpenRouter API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key or api_key.strip() == "your_openrouter_api_key_here":
            print("⚠️  OPENROUTER_API_KEY not configured properly")
            print("   🔍 Retrieval-only mode available (document search without AI responses)")
            print("   🤖 For full AI responses, configure a valid API key in .env file")
            print("   🌐 Get API key from: https://openrouter.ai/")
        else:
            print("✅ OPENROUTER_API_KEY found - full advanced RAG functionality available")
        
        # Set up basic settings (but delay embedding model initialization)
        self.embedding_initialized = False
        print("✅ Advanced RAG Backend initialized (models will load when needed)")

    def _ensure_embeddings_initialized(self) -> Tuple[bool, Optional[str]]:
        """Lazy-load HuggingFace embeddings so we don't rely on OpenAI defaults."""
        if self.embedding_initialized:
            return True, None
        try:
            print(f"🔄 Initializing HuggingFace embeddings ({self.embedding_model_name})...")
            Settings.embed_model = HuggingFaceEmbedding(
                model_name=self.embedding_model_name,
                trust_remote_code=True
            )
            self.embedding_initialized = True
            print("✅ HuggingFace embeddings configured")
            return True, None
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️  Error configuring embeddings: {error_msg}")
            return False, error_msg
        
    def update_settings(self, model: str = "gpt-4o-mini", temperature: float = 0.1, chunk_size: int = 512, chunk_overlap: int = 50, init_embeddings: bool = False):
        """Update LlamaIndex settings based on user configuration."""
        # Set up the LLM using OpenRouter
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key and api_key.strip() != "your_openrouter_api_key_here":
            try:
                Settings.llm = OpenRouter(
                    api_key=api_key,
                    model=model,
                    temperature=temperature
                )
                print(f"✅ OpenRouter LLM configured: {model} (temp: {temperature})")
            except Exception as e:
                print(f"⚠️  Error configuring OpenRouter LLM: {e}")
        
        # Set up the embedding model only when needed (lazy loading)
        if init_embeddings:
            initialized, error = self._ensure_embeddings_initialized()
            if not initialized:
                return f"❌ Failed to initialize embeddings: {error}"
        
        # Set chunking parameters from function parameters
        Settings.chunk_size = chunk_size
        Settings.chunk_overlap = chunk_overlap
        print(f"✅ Chunking parameters set: size={chunk_size}, overlap={chunk_overlap}")
        
        return "✅ Settings updated successfully"
    
    def _resolve_data_folder(self, override_path: Optional[str]) -> Path:
        """Return the path to the data folder (env override > provided arg > defaults)."""
        if override_path is None:
            return get_default_data_folder()
        return _normalize_path(override_path)

    def try_load_existing_database(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        """Attempt to load existing vector DB without rebuilding."""
        if chunk_size is None or chunk_overlap is None:
            stored_size, stored_overlap = read_existing_chunk_parameters()
            chunk_size = chunk_size or stored_size
            chunk_overlap = chunk_overlap or stored_overlap
        
        if chunk_size is None or chunk_overlap is None:
            return False, "📁 No existing database detected. Click 'Initialize Vector Database' after adding documents."
        
        db_path = get_assignment_3b_db_path()
        db_path_str = str(db_path)
        config_matches, config_message = check_database_configuration(db_path_str, chunk_size, chunk_overlap)
        if not config_matches:
            return False, config_message

        initialized, init_error = self._ensure_embeddings_initialized()
        if not initialized:
            return False, f"⚠️ Could not initialize embedding model while attaching existing database: {init_error}"

        try:
            vector_store = LanceDBVectorStore(uri=db_path_str, table_name="documents")
            self.index = VectorStoreIndex.from_vector_store(vector_store)
            self.is_ready = True
            self.current_chunk_size = chunk_size
            self.current_chunk_overlap = chunk_overlap
            return True, f"✅ Existing database loaded automatically!\n{config_message}"
        except Exception as e:
            return False, f"⚠️ Existing database detected but could not be loaded automatically: {e}"

    def initialize_database(self, data_folder=None, chunk_size=512, chunk_overlap=50, force_rebuild=False):
        """Initialize (or load) the vector database with configuration-aware duplicate checking."""
        if self.is_initializing:
            return "⚠️ Database initialization already in progress! Please wait..."
        
        self.is_initializing = True
        self.is_ready = False
        
        incremental_env = os.getenv("A3B_INCREMENTAL_UPDATES", "false")
        incremental_enabled = str(incremental_env).strip().lower() not in {"0", "false", "no", "off"}
         
        try:
            db_path = get_assignment_3b_db_path()
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db_path_str = str(db_path)
            config_file = db_path / "chunk_config.json"
            
           
            stored_config: Dict[str, Any] = {}
            processed_lookup: Dict[str, Dict[str, Any]] = {}
            existing_doc_count = 0
            manifest_data_path = None
            stored_chunk_size = None
            stored_chunk_overlap = None
            if config_file.exists():
                try:
                    with open(config_file, "r") as cfg:
                        stored_config = json.load(cfg)
                    processed_lookup = build_processed_lookup(stored_config.get("processed_files"))
                    existing_doc_count = stored_config.get("document_count", 0) or 0
                    stored_chunk_size = stored_config.get("chunk_size")
                    stored_chunk_overlap = stored_config.get("chunk_overlap")
                except Exception as cfg_err:
                    print(f"⚠️ Could not read existing configuration metadata: {cfg_err}")
                    processed_lookup = {}
            
            manifest_data = load_ingest_manifest(expected_chunk_size=chunk_size, expected_chunk_overlap=chunk_overlap)
            if manifest_data:
                manifest_lookup = build_processed_lookup(manifest_data.get("processed_files"))
                if manifest_lookup:
                    processed_lookup = manifest_lookup
                if not existing_doc_count:
                    existing_doc_count = manifest_data.get("document_count", existing_doc_count) or existing_doc_count
                manifest_data_path = manifest_data.get("data_path")
                if stored_chunk_size is None:
                    stored_chunk_size = manifest_data.get("chunk_size")
                if stored_chunk_overlap is None:
                    stored_chunk_overlap = manifest_data.get("chunk_overlap")
            
            print(f"� Checking database configuration...")
            print(f"📁 Database path: {db_path_str}")
            print(f"� Requested configuration: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
            
            config_matches, config_message = check_database_configuration(db_path_str, chunk_size, chunk_overlap)
            print(config_message)
            
            db_vector_file = db_path / "documents.lance"
            db_files_present = db_vector_file.exists()
            load_error = None
            load_success = False
            
            if db_files_present:
                print("🔄 Attempting to load existing database files...")
                embeddings_ready, embeddings_error = self._ensure_embeddings_initialized()
                if not embeddings_ready:
                    load_error = RuntimeError(embeddings_error or "Unknown embedding initialization error")
                    print(f"⚠️  Could not initialize embedding model: {embeddings_error}")
                    print("🔄 Creating fresh database...")
                else:
                    try:
                        vector_store = LanceDBVectorStore(uri=db_path_str, table_name="documents")
                        self.index = VectorStoreIndex.from_vector_store(vector_store)
                        self.is_ready = True
                        load_success = True
                    except Exception as load_err:
                        load_error = load_err
                        print(f"⚠️  Error loading existing database: {load_err}")
                        print("🔄 Creating fresh database...")
            
            can_reuse_existing = load_success and config_matches and not force_rebuild
            
            if can_reuse_existing:
                self.current_chunk_size = chunk_size
                self.current_chunk_overlap = chunk_overlap
                if not incremental_enabled:
                    self.is_initializing = False
                    return f"""✅ Database loaded successfully!
{config_message}
🚀 Ready for advanced queries with full configuration options."""
                
                resolved_data_folder = self._resolve_data_folder(data_folder)
                data_folder_str = str(resolved_data_folder)
                
                if not resolved_data_folder.exists():
                    info_msg = f"""✅ Database loaded successfully!
{config_message}
ℹ️ Data folder '{data_folder_str}' not found, so incremental updates were skipped.
🚀 Ready for advanced queries with full configuration options."""
                    print(info_msg.replace('\n', ' '))
                    self.is_initializing = False
                    return info_msg
                
                current_files = scan_data_files(resolved_data_folder)
                
                if config_file.exists() and stored_config and not processed_lookup and current_files:
                    print("ℹ️ Existing database lacks file-tracking metadata. Capturing current file list for future incremental updates.")
                    processed_snapshot = serialize_processed_files(current_files)
                    processed_lookup = build_processed_lookup(processed_snapshot)
                    try:
                        doc_count_snapshot = existing_doc_count or stored_config.get("document_count", 0) or 0
                        data_path_snapshot = stored_config.get("data_path", manifest_data_path or data_folder_str) or data_folder_str
                        persist_ingest_metadata(
                            db_path_str,
                            stored_config.get("chunk_size", chunk_size),
                            stored_config.get("chunk_overlap", chunk_overlap),
                            doc_count_snapshot,
                            data_path_snapshot,
                            processed_snapshot
                        )
                        print("✅ File-tracking metadata saved for existing database.")
                    except Exception as meta_err:
                        print(f"⚠️ Could not persist retroactive file metadata: {meta_err}")
                
                if not current_files:
                    info_msg = f"""✅ Database loaded successfully!
{config_message}
ℹ️ No source files found in '{data_folder_str}'. Existing vectors remain available.
🚀 Ready for advanced queries with full configuration options."""
                    print(info_msg.replace('\n', ' '))
                    self.is_initializing = False
                    return info_msg
                
                new_relative_paths = [rel for rel in current_files.keys() if rel not in processed_lookup]
                changed_files = []
                for rel, meta in current_files.items():
                    if rel in processed_lookup and processed_lookup[rel]:
                        stored_entry = processed_lookup[rel]
                        stored_size = stored_entry.get("size")
                        stored_ts = stored_entry.get("modified_ts")
                        if stored_ts is None:
                            stored_mod = stored_entry.get("modified")
                            try:
                                stored_ts = datetime.fromisoformat(stored_mod).timestamp()
                            except Exception:
                                stored_ts = None
                        if stored_size is None or stored_ts is None:
                            continue
                        if stored_size != meta["size"] or not math.isclose(stored_ts, meta["modified"], rel_tol=0, abs_tol=1e-6):
                            changed_files.append(rel)
                
                new_detected = len(new_relative_paths) > 0
                changed_detected = len(changed_files) > 0

                if not new_detected and not changed_detected:
                    success_msg = f"""✅ Database loaded successfully!
{config_message}
📂 No new or modified files detected — everything is already indexed.
🚀 Ready for advanced queries with full configuration options."""
                    print(success_msg.replace('\n', ' '))
                    self.is_initializing = False
                    return success_msg

                if changed_detected:
                    print("⚠️ Detected modified files since last ingestion:")
                    for rel in changed_files:
                        print(f"   • {rel}")
                if new_detected:
                    print(f"📥 Detected {len(new_relative_paths)} new file(s) awaiting ingestion.")

                print("ℹ️ Rebuilding the vector database to include the latest files...")
                force_rebuild = True
            
            if load_error:
                print("⚠️ Falling back to full rebuild because the existing database could not be loaded.")
            elif not db_files_present:
                print("ℹ️ No existing database files found. Creating a new database from data folder.")
            elif not chunk_params_match:
                print("ℹ️ Chunk configuration changed since last build. Rebuilding database with new settings.")
            elif force_rebuild:
                print("ℹ️ Force rebuild requested - recreating the database from source files.")
            
            if load_error:
                print("⚠️ Falling back to full rebuild because the existing database could not be loaded.")
            elif not db_files_present:
                print("ℹ️ No existing database files found. Creating a new database from data folder.")
            elif not config_matches:
                print("ℹ️ Chunk configuration changed since last build. Rebuilding database with new settings.")
            elif force_rebuild:
                print("ℹ️ Force rebuild requested - recreating the database from source files.")
            
            resolved_data_folder = self._resolve_data_folder(data_folder)
            data_folder_str = str(resolved_data_folder)
            print(f"📂 Data folder: {data_folder_str}")
            
            if not resolved_data_folder.exists():
                error_msg = f"❌ Data folder '{data_folder_str}' not found!"
                print(error_msg)
                self.is_initializing = False
                return error_msg
            
            current_files = scan_data_files(resolved_data_folder)
            
            if db_path.exists():
                print("🗑️ Removing old database to rebuild with new configuration...")
                shutil.rmtree(db_path_str)
                print("✅ Old database removed")
            
            print(f"⚙️ Applying chunk configuration: size={chunk_size}, overlap={chunk_overlap}")
            self.update_settings(
                model=getattr(self, 'current_model', 'gpt-4o-mini'),
                temperature=getattr(self, 'current_temperature', 0.1),
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                init_embeddings=True
            )
            
            print(f"📦 Creating vector store at: {db_path_str}")
            vector_store = LanceDBVectorStore(uri=db_path_str, table_name="documents")
            
            print("📄 Loading documents from data folder...")
            reader = SimpleDirectoryReader(input_dir=data_folder_str, recursive=True)
            documents, skipped_items = _standardize_documents(reader.load_data())
            if skipped_items:
                sample = ", ".join(skipped_items[:5])
                print(f"ℹ️ Skipped {len(skipped_items)} unsupported items while loading documents ({sample}).")
            
            if not documents:
                error_msg = f"❌ No documents found in {data_folder_str}"
                print(error_msg)
                self.is_initializing = False
                return error_msg
            
            print(f"📚 Successfully loaded {len(documents)} documents")
            print(f"🔧 Processing documents with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
            
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            print("🔗 Building vector index with new chunking configuration...")
            print("   This may take a few minutes for large document sets...")
            
            self.index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                show_progress=True
            )
            
            print("💾 Saving configuration metadata...")
            processed_snapshot = serialize_processed_files(current_files)
            persist_ingest_metadata(
                db_path_str,
                chunk_size,
                chunk_overlap,
                len(documents),
                data_folder_str,
                processed_snapshot
            )
            
            success_msg = f"""✅ Advanced database initialized successfully!
📊 Processed {len(documents)} documents with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}
🚀 Ready for advanced queries with full configuration options"""
            print(success_msg.replace('\n', ' '))
            self.is_ready = True
            self.is_initializing = False
            return success_msg
        
        except Exception as e:
            error_msg = f"❌ Error initializing database: {str(e)}"
            print(error_msg)
            self.is_initializing = False
            return error_msg
    def get_postprocessor(self, postprocessor_name: str, similarity_cutoff: float):
        """Get the selected postprocessor."""
        if postprocessor_name == "SimilarityPostprocessor":
            return SimilarityPostprocessor(similarity_cutoff=similarity_cutoff)
        elif postprocessor_name == "None":
            return None
        else:
            return None
    
    def get_synthesizer(self, synthesizer_name: str):
        """Get the selected response synthesizer."""
        if synthesizer_name == "TreeSummarize":
            return TreeSummarize()
        elif synthesizer_name == "Refine":
            return Refine()
        elif synthesizer_name == "CompactAndRefine":
            return CompactAndRefine()
        elif synthesizer_name == "Default":
            return None
        else:
            return None
    
    def _retrieval_only_query(self, question: str, similarity_top_k: int = 5) -> Dict[str, Any]:
        """Fallback method for retrieval-only queries when LLM is not available."""
        try:
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=similarity_top_k,
            )
            
            nodes = retriever.retrieve(question)
            
            response, sources = self._format_context_response(
                nodes,
                "🔍 **Retrieved Documents (Retrieval-Only Mode):**"
            )
            response += "\n💡 **Note:** This is retrieval-only mode. Configure OPENROUTER_API_KEY for AI-generated responses."
            
            return {
                "response": response,
                "sources": sources,
                "config": {"mode": "retrieval_only", "similarity_top_k": similarity_top_k}
            }
            
        except Exception as e:
            return {
                "response": f"❌ Error in retrieval-only query: {str(e)}",
                "sources": [],
                "config": {"mode": "error"}
            }
    
    def advanced_query(self, question: str, model: str, temperature: float, 
                      chunk_size: int, chunk_overlap: int, similarity_top_k: int,
                      postprocessor_names: List[str], similarity_cutoff: float,
                      synthesizer_name: str) -> Dict[str, Any]:
        """Query the RAG system with advanced configuration."""
        
        # Ensure index is ready (attempt auto-load if needed)
        if self.index is None:
            loaded, status_msg = self.try_load_existing_database(chunk_size, chunk_overlap)
            if loaded:
                print(status_msg.replace('\n', ' '))
            else:
                return {"response": status_msg or "❌ Please initialize the database first!", "sources": [], "config": {}}
        
        # Check if question is empty
        if not question or not question.strip():
            return {"response": "⚠️ Please enter a question first!", "sources": [], "config": {}}
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        api_key_valid = api_key and api_key.strip() != "your_openrouter_api_key_here"

        try:
            # Update settings (ensures chunk parameters + optional embeddings if LLM needed)
            self.update_settings(model, temperature, chunk_size, chunk_overlap)

            def build_postprocessors() -> List[Any]:
                instances: List[Any] = []
                for name in postprocessor_names:
                    processor = self.get_postprocessor(name, similarity_cutoff)
                    if processor is not None:
                        instances.append(processor)
                return instances

            retrieval_postprocessors = build_postprocessors()

            try:
                cutoff_value = float(similarity_cutoff)
            except (TypeError, ValueError):
                cutoff_value = 0.0

            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=similarity_top_k,
            )
            nodes = retriever.retrieve(question)
            for processor in retrieval_postprocessors:
                try:
                    nodes = processor.postprocess_nodes(nodes)
                except Exception as proc_err:
                    print(f"⚠️ Postprocessor error ({processor.__class__.__name__}): {proc_err}")

            score_values: List[float] = []
            filtered_nodes = []
            for node in nodes:
                score = getattr(node, 'score', None)
                if isinstance(score, (int, float)):
                    score_values.append(float(score))
                meets_cutoff = cutoff_value <= 0
                if not meets_cutoff:
                    if isinstance(score, (int, float)):
                        meets_cutoff = float(score) >= cutoff_value
                    else:
                        meets_cutoff = False
                if meets_cutoff:
                    filtered_nodes.append(node)

            highest_score = max(score_values) if score_values else None
            nodes = filtered_nodes
            has_context = bool(nodes)
            cutoff_block_reason = ""
            if cutoff_value > 0 and not has_context:
                cutoff_block_reason = f"🔎 No retrieved chunks met the similarity threshold of {cutoff_value:.3f}."
            needs_llm = self._needs_llm_elaboration(question, synthesizer_name)

            if has_context and not needs_llm:
                response_text, sources = self._format_context_response(
                    nodes,
                    "🔍 **Retrieved Documents:**"
                )
                return {
                    "response": response_text,
                    "sources": sources,
                    "config": {
                        "mode": "context_only",
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                        "similarity_top_k": similarity_top_k,
                        "postprocessors": postprocessor_names,
                        "similarity_cutoff": similarity_cutoff,
                        "synthesizer": synthesizer_name,
                    }
                }

            if not api_key_valid:
                if has_context:
                    fallback_text, sources = self._format_context_response(
                        nodes,
                        "🔍 **Retrieved Documents (LLM unavailable):**"
                    )
                    fallback_text += "\n⚠️ Set OPENROUTER_API_KEY to enable AI-generated summaries."
                    return {
                        "response": fallback_text,
                        "sources": sources,
                        "config": {"mode": "context_only_no_llm"}
                    }
                message = cutoff_block_reason or "⚠️ No relevant context found and OpenRouter API key is not configured."
                return {
                    "response": message,
                    "sources": [],
                    "config": {"mode": "no_llm_available"}
                }

            if not has_context:
                success, llm_text = self._direct_llm_answer(question)
                if not success or not llm_text:
                    llm_text = llm_text or "⚠️ LLM returned an empty response. Please try rephrasing your question."
                payload = cutoff_block_reason
                if llm_text:
                    payload = f"{payload}\n\n{llm_text}" if payload else llm_text
                prefix = "🧠 Response source: LLM.\n\n"
                response_text = f"{prefix}{payload}"
                return {
                    "response": response_text,
                    "sources": [],
                    "config": {
                        "mode": "llm_no_context",
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                        "similarity_top_k": similarity_top_k,
                        "postprocessors": postprocessor_names,
                        "similarity_cutoff": similarity_cutoff,
                        "synthesizer": synthesizer_name,
                    }
                }

            # LLM path with context (user requested elaboration)
            self.update_settings(model, temperature, chunk_size, chunk_overlap, init_embeddings=True)
            synthesizer = self.get_synthesizer(synthesizer_name)

            query_engine_kwargs = {"similarity_top_k": similarity_top_k}
            llm_postprocessors = build_postprocessors()
            if llm_postprocessors:
                query_engine_kwargs["node_postprocessors"] = llm_postprocessors
            if synthesizer is not None:
                query_engine_kwargs["response_synthesizer"] = synthesizer

            query_engine = self.index.as_query_engine(**query_engine_kwargs)
            response = query_engine.query(question)

            sources = []
            score_trace: List[Optional[float]] = []
            context_used = False
            if hasattr(response, 'source_nodes'):
                for node in response.source_nodes:
                    context_used = True
                    snippet = node.text[:200] + ("..." if len(node.text) > 200 else "")
                    score_value = getattr(node, 'score', None)
                    score_trace.append(score_value)
                    sources.append({
                        "text": snippet,
                        "score": score_value or 0.0,
                        "source": getattr(node.node, 'metadata', {}).get('file_name', 'Unknown')
                    })

            llm_prefix = cutoff_block_reason
            prefix = "🧠 Response source: LLM."
            if context_used:
                score_suffix = self._format_score_suffix(score_trace)
                prefix = f"🧠 Response source: LLM.{score_suffix}"

            response_payload = str(response)
            if llm_prefix:
                response_payload = f"{llm_prefix}\n\n{response_payload}"

            response_text = f"{prefix}\n\n{response_payload}"

            return {
                "response": response_text,
                "sources": sources,
                "config": {
                    "model": model,
                    "temperature": temperature,
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "similarity_top_k": similarity_top_k,
                    "postprocessors": postprocessor_names,
                    "similarity_cutoff": similarity_cutoff,
                    "synthesizer": synthesizer_name,
                    "mode": "llm" if not context_used else "llm_with_context"
                }
            }

        except Exception as e:
            return {"response": f"❌ Error processing advanced query: {str(e)}", "sources": [], "config": {"mode": "error"}}


def get_api_status_html():
    """Generate API status HTML display."""
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if api_key and api_key.strip() != "your_openrouter_api_key_here":
        return """
        <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 15px; margin: 10px 0; color: #155724;">
            <strong>🤖 Full AI Mode Active!</strong> OpenRouter API key detected - all features available.
        </div>
        """
    else:
        return """
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 10px 0; color: #856404;">
            <strong>⚠️ Retrieval-Only Mode</strong> - No API key found. You'll get document search results only.<br>
            <em>Configure OPENROUTER_API_KEY in .env file for full AI responses.</em>
        </div>
        """


def get_config_display_html():
    """Generate initial configuration display HTML."""
    model_default = get_rag_default("model", "gpt-4o-mini")
    temperature_default = get_rag_default("temperature", 0.1)
    chunk_size_default = get_rag_default("chunk_size", 512)
    chunk_overlap_default = get_rag_default("chunk_overlap", 50)
    topk_default = get_rag_default("similarity_top_k", 8)
    cutoff_default = get_rag_default("similarity_threshold", 0.3)
    post_enabled = bool(get_rag_default("postprocessor_enabled", True))
    synthesizer_default = get_rag_default("synthesizer", "TreeSummarize")
    post_text = "✅ Enabled" if post_enabled else "❌ Disabled"
    return """
    <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 15px; margin: 10px 0; color: #155724;">
        <strong>🤖 AI Model:</strong> {model} (Temperature: {temp}) &nbsp;&nbsp;
        <strong>📄 Chunking:</strong> Size={chunk}, Overlap={overlap}<br>
        <strong>🎯 Retrieval:</strong> Top-K={topk}, Cutoff={cutoff} &nbsp;&nbsp;
        <strong>🔧 Postprocessor:</strong> {post} &nbsp;&nbsp;
        <strong>🧠 Synthesizer:</strong> {synth}
    </div>
    """.format(
        model=model_default,
        temp=temperature_default,
        chunk=chunk_size_default,
        overlap=chunk_overlap_default,
        topk=topk_default,
        cutoff=cutoff_default,
        post=post_text,
        synth=synthesizer_default,
    )


def load_deep_source_preferences(default_sources: List[str]) -> List[str]:
    """
    Read deep-research source preferences from config/rag_ui_config.json.
    Falls back to the provided defaults when the file is missing or invalid.
    """
    configured = UI_CONFIG.get("deep_research", {}).get("external_sources")
    if isinstance(configured, list):
        filtered = [src for src in default_sources if src in configured]
        if filtered:
            return filtered
    return default_sources


def create_advanced_rag_interface_legacy():
    """Legacy UI (unused) kept for reference."""
    
    # No custom CSS; use Gradio defaults
    css = ""
    model_default = str(get_rag_default("model", "gpt-4o-mini"))
    temperature_default = float(get_rag_default("temperature", 0.1))
    chunk_size_default = int(get_rag_default("chunk_size", 512))
    chunk_overlap_default = int(get_rag_default("chunk_overlap", 50))
    topk_default = int(get_rag_default("similarity_top_k", 5))
    similarity_threshold_default = float(get_rag_default("similarity_threshold", 0.7))
    synthesizer_default = str(get_rag_default("synthesizer", "Default"))
    postprocessor_enabled_default = bool(get_rag_default("postprocessor_enabled", False))
    postprocessor_default_value = ["SimilarityPostprocessor"] if postprocessor_enabled_default else []
    
    # UI Event Handlers (separate from backend)
    def update_chunk_status(chunk_size, chunk_overlap):
        """Update chunk configuration status display."""
        return f"""
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 10px 0; color: #856404;">
            <strong>🎯 Current Configuration:</strong> chunk_size={chunk_size}, chunk_overlap={chunk_overlap}<br>
            <strong>⚠️ Status:</strong> Configuration changed - click "🚀 Initialize Database" to apply changes
        </div>
        """
    
    def update_config_display(model, temp, chunk_size, chunk_overlap, top_k, cutoff, postprocessor, synth):
        """Update real-time configuration display."""
        return f"""
        <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 15px; margin: 10px 0; color: #155724;">
            <strong>🤖 AI Model:</strong> {model} (Temperature: {temp}) &nbsp;&nbsp;
            <strong>📄 Chunking:</strong> Size={chunk_size}, Overlap={chunk_overlap}<br>
            <strong>🎯 Retrieval:</strong> Top-K={top_k}, Cutoff={cutoff} &nbsp;&nbsp;
            <strong>🔧 Postprocessor:</strong> {'✅ Enabled' if postprocessor else '❌ Disabled'} &nbsp;&nbsp;
            <strong>🧠 Synthesizer:</strong> {synth}
        </div>
        """
    
    # Backend Interface Handlers
    def initialize_db(chunk_size, chunk_overlap):
        
        """Handle database initialization with chunk configuration."""
        return rag_backend.initialize_database(chunk_size=int(chunk_size), chunk_overlap=int(chunk_overlap))
    
    def handle_advanced_query(question, model, temperature, chunk_size, chunk_overlap, 
                             similarity_top_k, use_postprocessor, similarity_cutoff, synthesizer):
        """Handle advanced RAG queries with all configuration options."""
        # Convert postprocessor boolean to list format expected by backend
        postprocessors = ["SimilarityPostprocessor"] if use_postprocessor else []
        
        result = rag_backend.advanced_query(
            question, model, temperature, int(chunk_size), int(chunk_overlap),
            int(similarity_top_k), postprocessors, similarity_cutoff, synthesizer
        )
        
        return result["response"]
    
    def clear_inputs():
        """Clear input fields."""
        return "", ""

    # System Configuration popup helpers (match rag_gui style)
    def build_config_html(model, temperature, chunk_size, overlap_size, top_k, similarity_threshold, postprocessor_enabled, synthesizer):
        post_text = "Enabled" if (postprocessor_enabled and len(postprocessor_enabled) > 0) else "Disabled"
        return f"""
        <div id='config_popup_box' style='position: fixed; top: 56px; right: 16px; width: 300px; max-width: 90vw; padding: 10px; border: 1px solid rgba(128,128,128,0.35); border-radius: 8px; box-shadow: 0 6px 18px rgba(0,0,0,0.12); z-index: 9999;'>
            <div style='font-weight: 600; margin-bottom: 6px; font-size: 13px;'>System Configuration</div>
            <div style='font-size: 13px; line-height: 1.4;'>
                <div><strong>Model:</strong> {model}</div>
                <div><strong>Temperature:</strong> {temperature}</div>
                <div><strong>Chunk Size:</strong> {int(chunk_size)}</div>
                <div><strong>Overlap:</strong> {int(overlap_size)}</div>
                <div><strong>Top-K:</strong> {int(top_k)}</div>
                <div><strong>Similarity Threshold:</strong> {similarity_threshold}</div>
                <div><strong>Postprocessor:</strong> {post_text}</div>
                <div><strong>Synthesizer:</strong> {synthesizer}</div>
            </div>
        </div>
        """

    def toggle_config(is_visible, model, temperature, chunk_size, overlap_size, top_k, similarity_threshold, postprocessor_enabled, synthesizer):
        new_visible = not bool(is_visible)
        html = build_config_html(model, temperature, chunk_size, overlap_size, top_k, similarity_threshold, postprocessor_enabled, synthesizer)
        return gr.update(value=html, visible=new_visible), new_visible, gr.update(visible=new_visible)
    
    # Create the Gradio Interface
    with gr.Blocks(css=css, title="🚀 NRI – Neural RAG Research Intelligence") as interface:
        # Header Section
        gr.HTML("""
        <div class="main-container">
            <h1 style="text-align: center; color: #2c3e50; margin-bottom: 10px; font-size: 2.5em;">
                🚀 NRI – Neural RAG Research Intelligence
            </h1>
            <p style="text-align: center; color: #7f8c8d; font-size: 18px; margin-bottom: 30px;">
                Professional-grade Retrieval-Augmented Generation with full configurability
            </p>
        </div>
        """)
        
        # System Configuration toggle and popup
        with gr.Row():
            with gr.Column(scale=5):
                pass
            with gr.Column(scale=1):
                config_button = gr.Button("System Configuration", variant="secondary", size="sm", elem_id="config_toggle_btn_a3b")
        config_popup = gr.HTML(value="", visible=False)
        config_visible = gr.State(False)
        close_config_button = gr.Button("×", variant="secondary", size="sm", visible=False, elem_id="config_close_btn_a3b")

        gr.HTML("""
        <style>
        #config_popup_box { background: #ffffff; color: #222; }
        @media (prefers-color-scheme: dark) {
          #config_popup_box { background: #2b2b2b; color: #f2f2f2; border-color: rgba(255,255,255,0.25); box-shadow: 0 6px 18px rgba(0,0,0,0.6); }
        }
        #config_toggle_btn_a3b { width: auto !important; display: inline-block; }
        #config_toggle_btn_a3b button { font-size: 12px; padding: 2px 8px; min-height: 26px; width: auto !important; min-width: 0 !important; display: inline-flex; }
        #config_close_btn_a3b { position: fixed; top: 15px; right: 12px; z-index: 10000; width: auto !important; }
        #config_close_btn_a3b button { font-size: 14px; padding: 2px 8px; min-height: 26px; width: auto !important; min-width: 0 !important; display: inline-flex; }
        </style>
        """)
        
        # API Status Display
        api_status = gr.HTML(get_api_status_html())

        # Top output display and unified question row
        response_output = gr.Markdown(
            value="Welcome! Enter your question below to get AI-powered insights from your documents.",
            elem_id="rag_response_panel"
        )
        gr.HTML("""
        <style>
        #rag_response_panel {
            border: 1px solid rgba(255,255,255,0.35);
            border-radius: 14px;
            padding: 24px;
            min-height: 45vh;
            max-height: 60vh;
            background: rgba(255,255,255,0.03);
            box-shadow: 0 12px 34px rgba(0,0,0,0.35);
            overflow-y: auto;
            font-size: 1rem;
            line-height: 1.5;
        }
        #rag_response_panel h1,
        #rag_response_panel h2,
        #rag_response_panel h3 {
            margin-top: 14px;
        }
        #legacy_upload_panel {
            border: 1px dashed rgba(0,0,0,0.2);
            border-radius: 12px;
            padding: 10px;
            margin-top: 18px;
            background: rgba(0,0,0,0.01);
        }
        #legacy_upload_panel label + div,
        #legacy_upload_panel label + div > div,
        #legacy_upload_panel label + div > div > div {
            min-height: 150px !important;
            max-height: 150px !important;
        }
        #legacy_upload_panel label + div {
            overflow-y: auto;
        }
        </style>
        """)

        deep_source_choices = ["ArXiv", "Wikipedia", "Tavily Search"]
        default_deep_sources = deep_source_choices.copy()
        configured_deep_sources = load_deep_source_preferences(default_deep_sources)
        deep_sources_state = gr.State(configured_deep_sources)

        with gr.Row():
            with gr.Column(scale=3):
                query_input = gr.Textbox(
                    label="",
                    placeholder="Ask your question here...",
                    lines=2,
                    show_label=False,
                    container=False
                )
            with gr.Column(scale=1, min_width=200):
                deep_research_checkbox = gr.Checkbox(
                    label="Enable Deep Research",
                    value=False,
                    info="Runs the multi-agent workflow with external sources.",
                )
                submit_btn = gr.Button("Submit", variant="primary", size="lg", scale=1)

        with gr.Group(elem_id="legacy_upload_panel"):
            gr.Markdown("### 📤 Upload Knowledge Files")
            upload_input = gr.File(
                label="Drop PDF, DOC/DOCX, TXT, RTF, or EPUB files",
                file_count="multiple",
                file_types=["file"],
            )
            upload_status = gr.Markdown(
                "Uploads are queued for verification before reaching the shared database."
            )

        # Database Initialization Section
        gr.Markdown("### 📁 Database Setup")
        with gr.Row():
            if not existing_loaded:
                init_btn = gr.Button("🔄 Initialize Vector Database", variant="primary", scale=1)
            status_output = gr.Textbox(
                label="Initialization Status", 
                value=existing_status,
                interactive=False,
                scale=2
            )
        
        if not existing_loaded:
            gr.Markdown("📥 Uploads are reviewed before being ingested. We'll notify you when it's time to initialize.")
        
        # Main layout with columns
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ RAG Configuration")
                
                # Model selection
                model_dropdown = gr.Dropdown(
                    choices=["gpt-4o", "gpt-4o-mini"],
                    value=model_default,
                    label="🤖 Language Model",
                    info="Choose your preferred model"
                )
                
                # Temperature control  
                temperature_slider = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    step=0.1,
                    value=temperature_default,
                    label="🌡️ Temperature",
                    info="Lower = more focused, Higher = more creative"
                )
                
                # Chunking parameters
                with gr.Row():
                    chunk_size_input = gr.Number(
                        value=chunk_size_default,
                        minimum=128,
                        maximum=2048,
                        step=64,
                        label="📄 Chunk Size",
                        info="Text chunk size for processing"
                    )
                    
                    chunk_overlap_input = gr.Number(
                        value=chunk_overlap_default,
                        minimum=0,
                        maximum=200,
                        step=10,
                        label="🔗 Chunk Overlap",
                        info="Overlap between chunks"
                    )
                
                if existing_loaded:
                    gr.Markdown("✅ Existing vector database detected automatically. You're ready to run queries.")
                    with gr.Accordion("Need to rebuild or refresh the database?", open=False):
                        rebuild_btn = gr.Button("♻️ Rebuild / Refresh Vector Database", variant="secondary")
                        rebuild_btn.click(
                            initialize_db,
                            inputs=[chunk_size_input, chunk_overlap_input],
                            outputs=[status_output]
                        )
                
                # Retrieval parameters
                similarity_topk_slider = gr.Slider(
                    minimum=1,
                    maximum=20,
                    step=1,
                    value=topk_default,
                    label="🎯 Similarity Top-K",
                    info="Number of similar documents to retrieve"
                )
                
                # Postprocessor selection
                postprocessor_checkbox = gr.CheckboxGroup(
                    choices=["SimilarityPostprocessor"],
                    value=postprocessor_default_value,
                    label="🔧 Node Postprocessors",
                    info="Additional result filtering"
                )
                
                # Similarity filtering
                similarity_cutoff_slider = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    step=0.1,
                    value=similarity_threshold_default,
                    label="✂️ Similarity Cutoff",
                    info="Minimum similarity score threshold"
                )
                
                # Response synthesizer
                synthesizer_dropdown = gr.Dropdown(
                    choices=["TreeSummarize", "Refine", "CompactAndRefine", "Default"],
                    value=synthesizer_default,
                    label="🧠 Response Synthesizer",
                    info="How to combine retrieved information"
                )
            
            with gr.Column(scale=2):
                gr.Markdown("### 💬 Query Interface")
                
                # Query input
                query_input2 = gr.Textbox(
                    label="❓ Ask a question",
                    placeholder="Enter your question here... (e.g., 'What are AI agents and their capabilities?')",
                    lines=3
                )
                
                # Submit button
                submit_btn2 = gr.Button(
                    "🚀 Ask Question", 
                    variant="primary",
                    size="lg"
                )
                
                # Response output
                response_output2 = gr.Textbox(
                    label="🤖 AI Response",
                    lines=12,
                    interactive=False,
                    placeholder="AI response will appear here..."
                )
                
                # Configuration display
                config_display_hidden = gr.Textbox(visible=False,
                    label="📋 Current Configuration",
                    lines=8,
                    interactive=False,
                    placeholder="Configuration details will appear here..."
                )
        
        # Connect functions to components
        if not existing_loaded:
            init_btn.click(
                initialize_db, 
                inputs=[chunk_size_input, chunk_overlap_input],
                outputs=[status_output]
            )
        
        upload_input.change(
            fn=handle_document_upload,
            inputs=[upload_input],
            outputs=[upload_status],
        )

        submit_btn.click(
            fn=_combined_loading_state,
            inputs=[deep_research_checkbox],
            outputs=[
                response_output,
                submit_btn,
            ],
        ).then(
            fn=run_unified_query,
            inputs=[
                query_input,
                model_dropdown,
                temperature_slider,
                chunk_size_input,
                chunk_overlap_input,
                similarity_topk_slider,
                postprocessor_checkbox,
                similarity_cutoff_slider,
                synthesizer_dropdown,
                deep_research_checkbox,
                deep_sources_state,
            ],
            outputs=[
                response_output,
                plan_output,
                context_output,
                analysis_output,
                insight_output,
                report_output,
                citations_output,
                notes_output,
            ],
        ).then(
            fn=_reset_run_button,
            outputs=[submit_btn],
        )

        # Toggle System Configuration popup
        config_button.click(
            fn=toggle_config,
            inputs=[
                config_visible,
                model_dropdown,
                temperature_slider,
                chunk_size_input,
                chunk_overlap_input,
                similarity_topk_slider,
                similarity_cutoff_slider,
                postprocessor_checkbox,
                synthesizer_dropdown,
            ],
            outputs=[config_popup, config_visible, close_config_button]
        )
        close_config_button.click(
            fn=toggle_config,
            inputs=[
                config_visible,
                model_dropdown,
                temperature_slider,
                chunk_size_input,
                chunk_overlap_input,
                similarity_topk_slider,
                similarity_cutoff_slider,
                postprocessor_checkbox,
                synthesizer_dropdown,
            ],
            outputs=[config_popup, config_visible, close_config_button]
        )
    
    return interface


def launch_application():
    """Launch the advanced RAG application."""
    print("🎉 Launching your Advanced RAG Assistant...")
    print("🔗 Your application will open in a new browser tab!")
    print("")
    print("⚠️  Make sure your OPENROUTER_API_KEY environment variable is set!")
    print("")
    print("📋 Testing Instructions:")
    print("1. If prompted, click 'Initialize Vector Database' (button only appears when needed)")
    print("2. Wait for the readiness message")
    print("3. Configure your RAG parameters:")
    print("   - Choose model (gpt-4o, gpt-4o-mini)")
    print("   - Adjust temperature (0.0 = deterministic, 1.0 = creative)")
    print("   - Set chunk size and overlap")
    print("   - Choose similarity top-k")
    print("   - Select postprocessors and synthesizer")
    print("4. Enter a question and click 'Ask Question'")
    print("5. Review both the response and configuration used")
    print("")
    print("🧪 Experiments to try:")
    print("- Compare different models with the same question")
    print("- Test temperature effects (0.1 vs 0.9)")
    print("- Try different chunk sizes (256 vs 1024)")
    print("- Compare synthesizers (TreeSummarize vs Refine)")
    print("- Adjust similarity cutoff to filter results")
    print("")
    print("🚀 Starting application server...")
    print("=" * 60)
    
    try:
        advanced_interface.launch(
            server_name="127.0.0.1",
            server_port=7862,  # Different port from A3a.py (7860) and previous A3b (7861)
            share=False,
            show_error=True
        )
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        print("💡 Try closing other Gradio applications and retry")


# Initialize the backend
rag_backend = AdvancedRAGBackend()
print("🚀 Advanced RAG Backend initialized and ready!")

# UI function rewritten to mirror rag_gui
def create_advanced_rag_interface():
    import gradio as gr

    stored_chunk_size, stored_chunk_overlap = read_existing_chunk_parameters()
    configured_chunk_size = int(get_rag_default("chunk_size", 512))
    configured_chunk_overlap = int(get_rag_default("chunk_overlap", 50))
    default_chunk_size = rag_backend.current_chunk_size or stored_chunk_size or configured_chunk_size
    default_chunk_overlap = rag_backend.current_chunk_overlap or stored_chunk_overlap or configured_chunk_overlap
    existing_loaded, existing_status = rag_backend.try_load_existing_database(
        chunk_size=default_chunk_size,
        chunk_overlap=default_chunk_overlap
    )
    if not existing_status:
        existing_status = "Uploads are reviewed automatically. Initialize once you receive the green light."

    deep_source_choices = ["ArXiv", "Wikipedia", "Tavily Search"]
    default_deep_sources = deep_source_choices.copy()
    configured_deep_sources = load_deep_source_preferences(default_deep_sources)
    model_default = str(get_rag_default("model", "gpt-4o-mini"))
    temperature_default = float(get_rag_default("temperature", 0.1))
    topk_default = int(get_rag_default("similarity_top_k", 5))
    similarity_threshold_default = float(get_rag_default("similarity_threshold", 0.7))
    synthesizer_default = str(get_rag_default("synthesizer", "Default"))
    postprocessor_enabled_default = bool(get_rag_default("postprocessor_enabled", False))
    postprocessor_default_value = ["SimilarityPostprocessor"] if postprocessor_enabled_default else []

    def build_config_html(model, temperature, chunk_size, overlap_size, top_k, similarity_threshold, postprocessor_enabled, synthesizer):
        post_text = "Enabled" if (postprocessor_enabled and len(postprocessor_enabled) > 0) else "Disabled"
        return f"""
        <div id='config_popup_box' style='position: fixed; top: 56px; right: 16px; width: 300px; max-width: 90vw; padding: 10px; border-radius: 8px; box-shadow: 0 6px 18px rgba(0,0,0,0.12); z-index: 9999;'>
            <div style='font-weight: 600; margin-bottom: 6px; font-size: 13px;'>System Configuration</div>
            <div style='font-size: 13px; line-height: 1.4;'>
                <div><strong>Model:</strong> {model}</div>
                <div><strong>Temperature:</strong> {temperature}</div>
                <div><strong>Chunk Size:</strong> {int(chunk_size)}</div>
                <div><strong>Overlap:</strong> {int(overlap_size)}</div>
                <div><strong>Top-K:</strong> {int(top_k)}</div>
                <div><strong>Similarity Threshold:</strong> {similarity_threshold}</div>
                <div><strong>Postprocessor:</strong> {post_text}</div>
                <div><strong>Synthesizer:</strong> {synthesizer}</div>
            </div>
        </div>
        """

    def toggle_config(is_visible, model, temperature, chunk_size, overlap_size, top_k, similarity_threshold, postprocessor_enabled, synthesizer):
        new_visible = not bool(is_visible)
        html = build_config_html(model, temperature, chunk_size, overlap_size, top_k, similarity_threshold, postprocessor_enabled, synthesizer)
        return gr.update(value=html, visible=new_visible), new_visible, gr.update(visible=new_visible)

    # Backend adapters (mirror legacy handlers but scoped to this UI)
    def initialize_db(chunk_size, chunk_overlap):
        return rag_backend.initialize_database(chunk_size=int(chunk_size), chunk_overlap=int(chunk_overlap))

    def handle_advanced_query(question, model, temperature, chunk_size, chunk_overlap,
                              similarity_top_k, use_postprocessor, similarity_cutoff, synthesizer):
        # Normalize postprocessor input from CheckboxGroup (list) or Checkbox (bool)
        enabled = False
        if isinstance(use_postprocessor, list):
            enabled = len(use_postprocessor) > 0
        else:
            enabled = bool(use_postprocessor)
        postprocessors = ["SimilarityPostprocessor"] if enabled else []

        result = rag_backend.advanced_query(
            question, model, float(temperature), int(chunk_size), int(chunk_overlap),
            int(similarity_top_k), postprocessors, float(similarity_cutoff), synthesizer
        )
        return result["response"]

    with gr.Blocks(title="🚀 NRI – Neural RAG Research Intelligence") as interface:
        with gr.Row():
            with gr.Column(scale=5):
                gr.Markdown("# 🚀 NRI – Neural RAG Research Intelligence")
            with gr.Column(scale=1):
                config_button = gr.Button("System Configuration", variant="secondary", size="sm", elem_id="config_toggle_btn_a3b")
        config_popup = gr.HTML(value="", visible=False)
        config_visible = gr.State(False)
        deep_sources_state = gr.State(configured_deep_sources)
        close_config_button = gr.Button("×", variant="secondary", size="sm", visible=False, elem_id="config_close_btn_a3b")

        gr.HTML("""
        <style>
        #panel_model, #panel_retrieval, #panel_advanced { border: 1px solid rgba(128,128,128,0.35); border-radius: 8px; padding: 12px; }
        /* Popup uses Gradio theme variables for background/text/border */
        #config_popup_box {
          background: var(--background-fill-primary, var(--color-background-primary, #ffffff));
          color: var(--body-text-color, var(--color-text, inherit));
          border: 1px solid var(--border-color-primary, rgba(128,128,128,0.35));
        }
        #config_toggle_btn_a3b { width: auto !important; display: inline-block; }
        #config_toggle_btn_a3b button { font-size: 12px; padding: 2px 8px; min-height: 26px; width: auto !important; min-width: 0 !important; display: inline-flex; }
        #config_close_btn_a3b { position: fixed; top: 15px; right: 12px; z-index: 10000; width: auto !important; }
        #config_close_btn_a3b button { font-size: 14px; padding: 2px 8px; min-height: 26px; width: auto !important; min-width: 0 !important; display: inline-flex; }
        .gr-accordion > summary {
          font-weight: 600;
          color: #ffa94d;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        </style>
        """)

        # Unified Chat Panel
        gr.Markdown("---")
        gr.Markdown("<h3 style='text-align:center; font-family: Georgia, \\\"Times New Roman\\\", serif; margin: 12px 0;'>Research Console</h3>")
        response_output = gr.Markdown(
            value="Welcome! Enter your question below to get AI-powered insights from your documents.",
            elem_id="rag_response_panel"
        )
        gr.HTML("""
        <style>
        #rag_response_panel {
            border: 1px solid rgba(255,255,255,0.35);
            border-radius: 14px;
            padding: 24px;
            min-height: 45vh;
            max-height: 60vh;
            background: rgba(255,255,255,0.03);
            box-shadow: 0 12px 34px rgba(0,0,0,0.35);
            overflow-y: auto;
            font-size: 1rem;
            line-height: 1.5;
        }
        #rag_response_panel h1,
        #rag_response_panel h2,
        #rag_response_panel h3 {
            margin-top: 14px;
        }
        #upload_panel {
            border: 1px dashed rgba(255,255,255,0.35);
            border-radius: 14px;
            padding: 11px;
            margin-top: 16px;
            background: rgba(255,255,255,0.02);
        }
        #upload_panel label + div,
        #upload_panel label + div > div,
        #upload_panel label + div > div > div {
            min-height: 150px !important;
            max-height: 150px !important;
        }
        #upload_panel label + div {
            overflow-y: auto;
        }
        </style>
        """)
        with gr.Row():
            with gr.Column(scale=4):
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g., Summarize the key AI research directions in logistics.",
                    lines=3,
                )
            with gr.Column(scale=1):
                deep_research_checkbox = gr.Checkbox(
                    label="Enable Deep Research",
                    value=False,
                    info="Runs the multi-agent workflow with external sources.",
                )
                submit_btn = gr.Button("Submit", variant="primary", size="lg")

        with gr.Group(elem_id="upload_panel"):
            gr.Markdown("### 📤 Upload Knowledge Files")
            upload_input = gr.File(
                label="Drop PDF, DOC/DOCX, TXT, RTF, or EPUB files",
                file_count="multiple",
                file_types=["file"],
            )
            upload_status = gr.Markdown(
                "Uploads are reviewed before being added to the production knowledge base."
            )

        # Database Configuration
        gr.Markdown("---")
        with gr.Accordion("Database Configuration", open=False):
            with gr.Row():
                chunk_size_input = gr.Number(label="Chunk Size", value=default_chunk_size, minimum=128, maximum=2048, step=64)
                chunk_overlap_input = gr.Number(label="Overlap Size", value=default_chunk_overlap, minimum=0, maximum=200, step=10)
            with gr.Row():
                gr.Markdown("**Chunk Size:** Controls how large each text segment should be (128-2048 characters)")
                gr.Markdown("**Overlap:** Amount of text shared between consecutive chunks (0-200 characters)")
            gr.HTML("<div style='height:6px'></div>")
            with gr.Row():
                init_btn = gr.Button("Initialize Database", variant="primary", size="lg", scale=1)
            status_output = gr.Textbox(label="System Status", value="Click 'Initialize Database' to get started...", interactive=False, lines=2)

        # Advanced Configuration panels
        gr.Markdown("---")
        with gr.Accordion("Advanced Configuration", open=False):
            with gr.Row():
                with gr.Column(scale=1, elem_id="panel_model"):
                    gr.Markdown("### Model Settings")
                    model_selection = gr.Textbox(label="AI Model", value=model_default, interactive=True, info="Current language model for response generation")
                    temperature_slider = gr.Slider(label="Temperature", minimum=0.0, maximum=1.0, value=temperature_default, step=0.1, info="Lower = focused, Higher = creative")
                    gr.Markdown("*gpt-4o-mini is faster and more cost-effective*")

                with gr.Column(scale=1, elem_id="panel_retrieval"):
                    gr.Markdown("### Retrieval Settings")
                    similarity_topk_slider = gr.Slider(label="Top-K Settings", minimum=1, maximum=20, value=topk_default, step=1, info="Controls how many top-ranked results to retrieve from vector database")
                    similarity_cutoff_slider = gr.Slider(label="Similarity Threshold", minimum=0.0, maximum=1.0, value=similarity_threshold_default, step=0.05, info="Minimum similarity score for result inclusion")

                with gr.Column(scale=1, elem_id="panel_advanced"):
                    gr.Markdown("### Advanced Options")
                    synthesizer_dropdown = gr.Dropdown(label="Response Synthesizer", choices=["TreeSummarize", "Refine", "CompactAndRefine", "Default"], value=synthesizer_default, info="How to combine retrieved information")
                    postprocessor_checkbox = gr.CheckboxGroup(choices=["SimilarityPostprocessor"], value=postprocessor_default_value, label="Enable Similarity Postprocessor", info="Enables/disables similarity-based result postprocessing")

        # Events
        upload_input.change(
            fn=handle_document_upload,
            inputs=[upload_input],
            outputs=[upload_status],
        )

        submit_btn.click(
            fn=_combined_loading_state,
            inputs=[deep_research_checkbox],
            outputs=[
                response_output,
                submit_btn,
            ],
        ).then(
            fn=run_unified_query,
            inputs=[
                query_input,
                model_selection,
                temperature_slider,
                chunk_size_input,
                chunk_overlap_input,
                similarity_topk_slider,
                postprocessor_checkbox,
                similarity_cutoff_slider,
                synthesizer_dropdown,
                deep_research_checkbox,
                deep_sources_state,
            ],
            outputs=[
                response_output,
            ],
        ).then(
            fn=_reset_run_button,
            outputs=[submit_btn],
        )

        init_btn.click(
            initialize_db,
            inputs=[chunk_size_input, chunk_overlap_input],
            outputs=[status_output]
        )

        config_button.click(
            fn=toggle_config,
            inputs=[
                config_visible,
                model_selection,
                temperature_slider,
                chunk_size_input,
                chunk_overlap_input,
                similarity_topk_slider,
                similarity_cutoff_slider,
                postprocessor_checkbox,
                synthesizer_dropdown,
            ],
            outputs=[config_popup, config_visible, close_config_button]
        )
        close_config_button.click(
            fn=toggle_config,
            inputs=[
                config_visible,
                model_selection,
                temperature_slider,
                chunk_size_input,
                chunk_overlap_input,
                similarity_topk_slider,
                similarity_cutoff_slider,
                postprocessor_checkbox,
                synthesizer_dropdown,
            ],
            outputs=[config_popup, config_visible, close_config_button]
        )

        return interface


def _repeat_deep_research_output(message: str) -> str:
    return message


def _format_plan_output(plan: Optional[PlannerOutput]) -> str:
    if not plan:
        return "⚠️ Planner did not return any structured plan."
    lines = ["### 🧭 Planner Output"]
    if plan.sub_questions:
        lines.append("**Sub-questions:**")
        for idx, task in enumerate(plan.sub_questions, 1):
            rationale = f" _(why: {task.rationale})_" if task.rationale else ""
            lines.append(f"{idx}. {task.question}{rationale}")
    if plan.key_entities:
        lines.append("\n**Key Entities:** " + ", ".join(plan.key_entities))
    if plan.priority_topics:
        lines.append("**Priority Topics:** " + ", ".join(plan.priority_topics))
    return "\n".join(lines)


def _format_context_output(contexts: Optional[List[RetrievedContext]]) -> str:
    if not contexts:
        return "⚠️ No supporting documents were retrieved."
    lines = ["### 📚 Retrieved Context"]
    for idx, ctx in enumerate(contexts[:5], 1):
        score_text = f" (score: {ctx.score:.3f})" if ctx.score is not None else ""
        lines.append(f"**Document {idx}:** {ctx.source}{score_text}\n{ctx.content[:400]}...")
    return "\n\n".join(lines)


def _format_analysis_output(analysis: Optional[CriticalAnalysisOutput], contexts: Optional[List[RetrievedContext]] = None) -> str:
    if not analysis:
        return "⚠️ Analysis agent did not return any results."
    lines = ["### 🧪 Critical Analysis", analysis.summary or "(No summary provided.)"]
    if analysis.key_points:
        lines.append("\n**Key Points:**")
        for point in analysis.key_points:
            sources = ", ".join(point.supporting_sources) or "context"
            lines.append(f"- {point.statement} _(sources: {sources})_")
    if analysis.contradictions:
        lines.append("\n**Contradictions:**")
        for item in analysis.contradictions:
            lines.append(f"- {item}")
    if analysis.validated_sources:
        lines.append("\n**Validated Sources:** " + ", ".join(analysis.validated_sources))
    return "\n".join(lines)


def _format_insight_output(insights: Optional[InsightOutput]) -> str:
    if not insights:
        return "⚠️ Insight agent did not return any hypotheses or trends."
    lines = ["### 💡 Insights"]
    if insights.hypotheses:
        lines.append("**Hypotheses:**")
        lines.extend([f"- {hyp}" for hyp in insights.hypotheses])
    if insights.trends:
        lines.append("\n**Trends:**")
        lines.extend([f"- {trend}" for trend in insights.trends])
    if insights.reasoning_steps:
        lines.append("\n**Reasoning Steps:**")
        lines.extend([f"- {step}" for step in insights.reasoning_steps])
    return "\n".join(lines)


def _format_report_output(report: Optional[ReportOutput]) -> str:
    if not report:
        return "⚠️ Report builder did not generate a final summary."
    lines = ["### 📄 Executive Summary", report.executive_summary or "(No summary returned.)"]
    if report.detailed_findings:
        lines.append("\n### 📌 Detailed Findings\n" + report.detailed_findings)
    return "\n".join(lines)


def _format_citations_output(report: Optional[ReportOutput]) -> str:
    if not report or not report.citations:
        return "⚠️ No citations were provided."
    return "### 📑 Citations\n" + "\n".join(report.citations)


def _format_notes_output(notes: Optional[List[str]]) -> str:
    if not notes:
        return "ℹ️ No special notes."
    return "### 📝 Notes\n" + "\n".join(f"- {note}" for note in notes if note)


def _combined_loading_state(deep_enabled: bool):
    placeholder = "🔄 Running deep research..." if deep_enabled else "🔄 Running advanced RAG query..."
    return placeholder, gr.update(value="Processing...", interactive=False)


def _reset_run_button():
    return gr.update(value="Submit", interactive=True)


def run_deep_research_workflow(query: str, model_name: str, temperature: float, similarity_cutoff: float, external_sources: Optional[List[str]]):
    query = (query or "").strip()
    if not query:
        return _repeat_deep_research_output("⚠️ Please enter a research question.")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key.strip() == "your_openrouter_api_key_here":
        return _repeat_deep_research_output("⚠️ Configure OPENROUTER_API_KEY to run the deep researcher.")

    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    try:
        llm = ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url, temperature=temperature)
    except Exception as exc:
        return _repeat_deep_research_output(f"❌ Could not initialize LLM: {exc}")

    external_sources = external_sources or []
    tavily_requested = "Tavily Search" in external_sources
    tavily_available = bool(os.getenv("TAVILY_API_KEY"))
    use_tavily = tavily_requested and tavily_available
    notes: List[str] = []
    if tavily_requested and not tavily_available:
        notes.append("Tavily Search selected but TAVILY_API_KEY is missing; skipping Tavily.")

    retriever_config = RetrieverConfig(
        similarity_top_k=5,
        similarity_cutoff=float(similarity_cutoff),
        use_database=True,
        use_tavily=use_tavily,
        use_arxiv="ArXiv" in external_sources,
        use_wikipedia="Wikipedia" in external_sources,
    )

    if not LANGGRAPH_AVAILABLE:
        return _repeat_deep_research_output(
            "⚠️ LangGraph is not installed in this environment, so the deep researcher cannot run."
        )

    try:
        agents = GraphAgents(
            planner=ResearchPlannerAgent(llm),
            retriever=ContextualRetrieverAgent(retriever_config),
            analyst=CriticalAnalysisAgent(llm),
            insight=InsightGenerationAgent(llm),
            reporter=ReportBuilderAgent(llm),
        )
        graph = build_research_graph(agents)
        result = run_research(graph, query)
    except Exception as exc:
        return _repeat_deep_research_output(f"❌ Deep researcher failed: {exc}")

    combined_notes = notes + result.get("notes", [])

    sections = [
        _format_plan_output(result.get("planner")),
        _format_context_output(result.get("contexts")),
        _format_analysis_output(result.get("analysis"), result.get("contexts")),
        _format_insight_output(result.get("insights")),
        _format_report_output(result.get("report")),
        _format_citations_output(result.get("report")),
        _format_notes_output(combined_notes),
    ]
    return "\n\n".join(section for section in sections if section)


def run_unified_query(
    question: str,
    model: str,
    temperature: float,
    chunk_size: float,
    chunk_overlap: float,
    similarity_top_k: float,
    use_postprocessor,
    similarity_cutoff: float,
    synthesizer: str,
    deep_enabled: bool,
    deep_sources: Optional[List[str]],
):
    # Normalize postprocessor input
    enabled = False
    if isinstance(use_postprocessor, list):
        enabled = len(use_postprocessor) > 0
    else:
        enabled = bool(use_postprocessor)
    postprocessors = ["SimilarityPostprocessor"] if enabled else []

    if not deep_enabled:
        result = rag_backend.advanced_query(
            question,
            model,
            float(temperature),
            int(chunk_size),
            int(chunk_overlap),
            int(similarity_top_k),
            postprocessors,
            float(similarity_cutoff),
            synthesizer,
        )
        return result["response"]

    deep_response = run_deep_research_workflow(
        question,
        model,
        float(temperature),
        float(similarity_cutoff),
        deep_sources,
    )
    return deep_response


def create_deep_research_interface():
    import gradio as gr

    tavily_available = bool(os.getenv("TAVILY_API_KEY"))
    default_sources = ["ArXiv", "Wikipedia"]
    if tavily_available:
        default_sources.append("Tavily Search")
    model_default = str(get_rag_default("model", "gpt-4o-mini"))
    temperature_default = float(get_rag_default("temperature", 0.1))
    similarity_threshold_default = float(get_rag_default("similarity_threshold", 0.7))

    with gr.Blocks(title="Multi-Agent Deep Researcher - Assignment 3b") as interface:
        gr.Markdown("## 🧠 Multi-Agent Deep Researcher")
        with gr.Row():
            with gr.Column(scale=1):
                query_box = gr.Textbox(label="Research Question", placeholder="e.g., How is AI used in military logistics?", lines=4)
                model_dropdown = gr.Dropdown(choices=["gpt-4o", "gpt-4o-mini"], value=model_default, label="LLM Model")
                temperature_slider = gr.Slider(minimum=0.0, maximum=1.0, step=0.05, value=temperature_default, label="Temperature")
                similarity_slider = gr.Slider(minimum=0.0, maximum=1.0, step=0.05, value=similarity_threshold_default, label="Similarity Cutoff")
                external_sources = gr.CheckboxGroup(
                    choices=["Tavily Search", "ArXiv", "Wikipedia"],
                    value=default_sources,
                    label="External Sources",
                    info="Toggle which connectors should supplement the local knowledge base"
                )
                run_button = gr.Button("Run Deep Research", variant="primary")
            with gr.Column(scale=1):
                gr.Markdown("### Results")
                plan_output = gr.Markdown()
                context_output = gr.Markdown()
                analysis_output = gr.Markdown()
                insight_output = gr.Markdown()
                report_output = gr.Markdown()
                citations_output = gr.Markdown()
                notes_output = gr.Markdown()

        run_button.click(
            fn=_deep_research_loading_state,
            outputs=[
                plan_output,
                context_output,
                analysis_output,
                insight_output,
                report_output,
                citations_output,
                notes_output,
                run_button,
            ],
        ).then(
            fn=run_deep_research_workflow,
            inputs=[query_box, model_dropdown, temperature_slider, similarity_slider, external_sources],
            outputs=[
                plan_output,
                context_output,
                analysis_output,
                insight_output,
                report_output,
                citations_output,
                notes_output,
            ],
        ).then(
            fn=_reset_deep_research_button,
            outputs=[run_button],
        )

        interface.queue()

        return interface

# Create the interface
advanced_interface = create_advanced_rag_interface()
print("✅ Advanced RAG interface (with Deep Research mode) created successfully!")


def launch_deep_research_application():
    print("ℹ️ Deep Research is now integrated into the main Advanced RAG interface.")
    print("   Launching the unified application...")
    launch_application()

# Environment check and launch info
print("")
print("🎯 Assignment 3b: Advanced Gradio RAG Frontend")
print("=" * 50)
print("🔍 Environment Check:")
api_key = os.getenv("OPENROUTER_API_KEY")
if api_key and api_key.strip() != "your_openrouter_api_key_here":
    print("   OpenRouter API: ✅ Found")
else:
    print("   OpenRouter API: ⚠️  Not configured (retrieval-only mode)")

print(f"   Data Path: {str(get_default_data_folder())}")
print(f"   Database Path: {os.getenv('ASSIGNMENT_3B_DB_PATH', './AssignmentDb/a3b_advanced_gradio_rag_vectordb')}")
print("")
print("🚀 Ready to launch Advanced RAG Assistant (with Deep Research mode)!")
print("   Run launch_application() to start the unified web interface")

# Auto-launch when script is run directly
if __name__ == "__main__":
    launch_application()
