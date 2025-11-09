"""
Multi-Agent AI Pipeline with Memory & Structured Outputs
-----------------------------------------------------------------
Agents:
1. Contextual Retriever
2. Critical Analysis
3. Insight Generation
4. Report Builder

Features:
- Memory to store past runs
- Structured JSON outputs
- Prompt templates for consistency
- Data flow management between nodes
- Caching for LLM outputs
"""

import os, time, json, re, hashlib
from typing import List, Dict, Any

# Import Pydantic for state schema
from pydantic import BaseModel, Field

# LangGraph
# Try to import LangGraph; provide a minimal fallback if unavailable
try:
    from langgraph.graph import StateGraph, START, END
except Exception:
    # Minimal fallback implementation so the rest of the script can run without langgraph installed.
    class _FallbackStateGraph:
        def __init__(self, state_schema=None): # Added state_schema argument
            self.nodes = {}
            self.edges = []
            self.state_schema = state_schema # Store schema if provided

        def add_node(self, name, func):
            self.nodes[name] = func

        def add_edge(self, a, b):
            self.edges.append((a, b))

        # Add __class_getitem__ to support type hinting syntax
        def __class_getitem__(cls, item):
            return cls

        def compile(self): # Added a dummy compile method
            # In a real fallback, this would just return self or a simple executor
            print("Warning: Running with fallback StateGraph. Full LangGraph features unavailable.")
            return self

        def run(self, inputs, config=None, **kwargs): # Added a dummy run method
             print("Warning: Running dummy run method.")
             # In a real fallback, you would simulate the execution flow
             # For this minimal fallback, we'll just return the initial state with a log
             inputs.setdefault("logs", []).append("Dummy run executed with fallback StateGraph.")
             return inputs

    StateGraph = _FallbackStateGraph
    START = "__START__"
    END = "__END__"

# LangChain / LLM and related imports with safe fallbacks when packages are missing
try:
    from langchain_openai import ChatOpenAI
except Exception:
    try:
        # Newer langchain installs use chat_models
        from langchain.chat_models import ChatOpenAI  # type: ignore
    except Exception:
        # Minimal mock ChatOpenAI to allow offline runs / static analysis
        class ChatOpenAI:
            def __init__(self, model="gpt-4o", temperature=2.0):
                self.model = model
                self.temperature = temperature

            def invoke(self, prompt: str):
                # Return a simple object with a content attribute like the real client
                class _R:
                    pass
                r = _R()
                # Heuristic simple mock outputs to satisfy downstream JSON parsing attempts
                if "Critical Analysis Agent" in prompt or "Summarize the main findings" in prompt:
                    r.content = json.dumps({
                        "summary": "Mock summary (langchain not installed).",
                        "contradictions": [],
                        "source_evaluation": []
                    })
                elif "Insight Generation Agent" in prompt or "Identify trends" in prompt:
                    r.content = json.dumps([{
                        "insight": "Mock insight",
                        "reasoning_chain": "Generated from mock LLM",
                        "confidence": "low",
                        "supporting_evidence": []
                    }])
                elif "professional report writer" in prompt or "Compile the following" in prompt:
                    r.content = json.dumps({
                        "executive_summary": "Mock report generated because LangChain/OpenAI packages are not installed.",
                        "key_findings": [],
                        "contradictions": [],
                        "insights": [],
                        "recommendations": []
                    })
                else:
                    r.content = prompt  # fallback: echo
                return r

# Document class fallback (used in several places)
try:
    from langchain.schema import Document
except Exception:
    class Document:
        def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
            self.page_content = page_content
            self.metadata = metadata or {}

# Vectorstore / embeddings / text splitter fallbacks
try:
    from langchain.vectorstores import LanceDB
except Exception:
    class LanceDB:
        @staticmethod
        def from_documents(docs, embeddings, connection=None, table_name=None):
            # Very small wrapper that provides similarity_search by returning original docs
            class _VS:
                def __init__(self, docs):
                    self._docs = docs

                def similarity_search(self, query, k=5):
                    return self._docs[:k]
            return _VS(docs)

try:
    from langchain.embeddings.openai import OpenAIEmbeddings
except Exception:
    class OpenAIEmbeddings:
        def __init__(self, *args, **kwargs):
            pass

        def embed_documents(self, docs: List[str]):
            # return dummy vectors
            return [[0.0] * 1 for _ in docs]

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except Exception:
    class RecursiveCharacterTextSplitter:
        def __init__(self, chunk_size=1000, chunk_overlap=150):
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap

        def split_documents(self, docs: List[Document]):
            # naive splitter: return docs unchanged (safe fallback)
            return docs

# lancedb lightweight fallback
try:
    import lancedb
except Exception:
    class _FakeConn:
        def __init__(self, path):
            self._tables = {}

        def table_names(self):
            return list(self._tables.keys())

        def drop_table(self, name):
            if name in self._tables:
                del self._tables[name]

    class lancedb:
        @staticmethod
        def connect(path):
            return _FakeConn(path)

# requests fallback for environments without requests installed
try:
    import requests
except Exception:
    class _FakeResponse:
        def __init__(self, data=None):
            self._data = data or {}

        def json(self):
            return self._data

    class requests:
        @staticmethod
        def get(*args, **kwargs):
            return _FakeResponse({"articles": []})

import pickle

# ----------------------------
# Shared Pipeline State
# ----------------------------
# ----------------------------
# Shared Pipeline State
# ----------------------------
class PipelineState(BaseModel):
    """
    Pydantic model that holds the pipeline state.

    Note: we allow arbitrary types (like the custom `Document` class used
    by the pipeline) by setting model_config.arbitrary_types_allowed = True.
    This avoids PydanticSchemaGenerationError when Pydantic attempts to
    generate a schema for custom types.
    """
    model_config = {"arbitrary_types_allowed": True}

    query: str = Field(default="")
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    # Document is a custom class; keep the annotation but allow arbitrary types
    raw_docs: List[Any] = Field(default_factory=list)
    chunks: List[Any] = Field(default_factory=list)
    vectorstore: Any = Field(default=None)
    critical_analysis: Dict[str, Any] = Field(default_factory=dict)
    insights: List[Dict[str, Any]] = Field(default_factory=list)
    report_text: str = Field(default="")
    report_json: Dict[str, Any] = Field(default_factory=dict)
    logs: List[str] = Field(default_factory=list)
    memory: Dict[str, Any] = Field(default_factory=dict)


def log(state: Dict[str, Any], msg: str):
    state.setdefault("logs", []).append(f"{time.strftime('%H:%M:%S')} {msg}")

# ----------------------------
# Simple caching utility
# ----------------------------
def llm_cache(llm_func, prompt: str, cache_dir="./cache"):
    os.makedirs(cache_dir, exist_ok=True)
    key = hashlib.sha256(prompt.encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{key}.pkl")
    if os.path.exists(cache_path):
        return pickle.load(open(cache_path, "rb"))
    res = llm_func(prompt)
    pickle.dump(res, open(cache_path, "wb"))
    return res

# ===============================================================
# 1️⃣ Contextual Retriever
# ===============================================================
def retrieve_data(state: PipelineState) -> PipelineState:
    # Create a mutable copy of the state
    state_dict = state.model_dump()
    log(state_dict, "Starting data retrieval...")
    all_docs = []

    for src in (state_dict.get("sources") or []):
        if src["type"] == "research":
            try:
                from langchain.document_loaders import ArxivLoader
                loader = ArxivLoader(search_query=src["query"], max_results=3)
                all_docs.extend(loader.load())
                log(state_dict, f"Fetched {len(all_docs)} research docs for '{src['query']}'")
            except Exception as e:
                log(state_dict, f"[ERROR] ArxivLoader: {e}")
        elif src["type"] == "news":
            NEWS_KEY = os.getenv("NEWS_API_KEY")
            if not NEWS_KEY:
                log(state_dict, "NEWS_API_KEY missing; skipping news source.")
                continue
            try:
                r = requests.get("https://newsapi.org/v2/everything",
                                 params={"q": src["query"], "pageSize": 5, "apiKey": NEWS_KEY})
                for art in r.json().get("articles", []):
                    text = f"{art['title']} - {art['description']} - {art['content']}"
                    all_docs.append(Document(page_content=text, metadata={"source": "news", "url": art["url"]}))
                log(state_dict, f"Fetched {len(all_docs)} news docs for '{src['query']}'")
            except Exception as e:
                log(state_dict, f"[ERROR] News fetch failed: {e}")

    if not all_docs:
        log(state_dict, "No documents retrieved.")
        # Return the updated state dictionary
        return PipelineState(**state_dict)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(all_docs)
    state_dict["chunks"] = chunks

    # LanceDB vector store
    os.makedirs("./vector_db", exist_ok=True)
    conn = lancedb.connect("./vector_db")
    if "retriever_data" in conn.table_names():
        conn.drop_table("retriever_data")
    vs = LanceDB.from_documents(chunks, OpenAIEmbeddings(), connection=conn, table_name="retriever_data")
    state_dict["vectorstore"] = vs
    log(state_dict, "Contextual retrieval complete.")
    # Return the updated state dictionary
    return PipelineState(**state_dict)

# ===============================================================
# 2️⃣ Critical Analysis Agent
# ===============================================================
CRIT_ANALYSIS_PROMPT = """
You are a Critical Analysis Agent.
Summarize the main findings, highlight contradictions, and validate sources.

Context:
{context}

Return structured JSON:
{{
  "summary": "...",
  "contradictions": [...],
  "source_evaluation": [...]
}}
"""

def critical_analysis(state: PipelineState) -> PipelineState:
    # Create a mutable copy of the state
    state_dict = state.model_dump()
    vs = state_dict.get("vectorstore")
    query = state_dict.get("query", "")
    log(state_dict, "Starting critical analysis...")

    if not vs:
        log(state_dict, "Vectorstore missing; skipping critical analysis.")
        # Return the updated state dictionary
        return PipelineState(**state_dict)

    docs = vs.similarity_search(query, k=5)
    context_text = "\n\n".join([d.page_content for d in docs])
    prompt = CRIT_ANALYSIS_PROMPT.format(context=context_text)

    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    try:
        result_text = llm_cache(lambda p: getattr(llm.invoke(p), "content", str(llm.invoke(p))), prompt)
        state_dict["critical_analysis"] = json.loads(result_text)
        log(state_dict, "Critical analysis complete.")
    except Exception as e:
        log(state_dict, f"[ERROR] Critical analysis failed: {e}")
        state_dict["critical_analysis"] = {}

    # Return the updated state dictionary
    return PipelineState(**state_dict)

# ===============================================================
# 3️⃣ Insight Generation Agent
# ===============================================================
INSIGHT_PROMPT = """
You are an Insight Generation Agent.
Analyze the critical analysis and identify trends, hypotheses, or implications.

Critical Analysis JSON:
{crit_analysis}

Return a list of insights in JSON:
[
  {{
    "insight": "...",
    "reasoning_chain": "...",
    "confidence": "low | medium | high",
    "supporting_evidence": ["...", "..."]
  }}
]
"""

def generate_insights(state: PipelineState) -> PipelineState:
    # Create a mutable copy of the state
    state_dict = state.model_dump()
    crit_analysis = state_dict.get("critical_analysis") or {}
    if not crit_analysis:
        log(state_dict, "No critical analysis data; skipping insight generation.")
        # Return the updated state dictionary
        return PipelineState(**state_dict)

    prompt = INSIGHT_PROMPT.format(crit_analysis=json.dumps(crit_analysis, indent=2))
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    try:
        result_text = llm_cache(lambda p: getattr(llm.invoke(p), "content", str(llm.invoke(p))), prompt)
        match = re.search(r"\[.*\]", result_text, re.S)
        insights = json.loads(match.group(0)) if match else []
        state_dict["insights"] = insights
        log(state_dict, f"Generated {len(insights)} insights.")
    except Exception as e:
        log(state_dict, f"[ERROR] Insight generation failed: {e}")
        state_dict["insights"] = []

    # Store in memory
    state_dict.setdefault("memory", {})["last_insights"] = state_dict["insights"]
    # Return the updated state dictionary
    return PipelineState(**state_dict)

# ===============================================================
# 4️⃣ Report Builder Agent
# ===============================================================
REPORT_PROMPT = """
You are a professional report writer.
Compile the following into a structured report with sections:
- Executive Summary
- Key Findings
- Contradictions
- Insights
- Recommendations

Critical Analysis JSON:
{crit_analysis}

Insights JSON:
{insights}

Return both TEXT and JSON.
"""

def build_report(state: PipelineState) -> PipelineState:
    # Create a mutable copy of the state
    state_dict = state.model_dump()
    crit_analysis = state_dict.get("critical_analysis") or {}
    insights = state_dict.get("insights") or []

    prompt = REPORT_PROMPT.format(
        crit_analysis=json.dumps(crit_analysis, indent=2),
        insights=json.dumps(insights, indent=2)
    )

    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    try:
        result_text = llm_cache(lambda p: getattr(llm.invoke(p), "content", str(llm.invoke(p))), prompt)
        match = re.search(r"\{.*\}", result_text, re.S)
        report_json = json.loads(match.group(0)) if match else {}
        state_dict["report_text"] = result_text
        state_dict["report_json"] = report_json
        state_dict.setdefault("memory", {})["last_report"] = state_dict["report_json"]
        log(state_dict, "Report built successfully.")
    except Exception as e:
        log(state_dict, f"[ERROR] Report building failed: {e}")
        state_dict["report_text"] = str(e)
        state_dict["report_json"] = {}

    # Return the updated state dictionary
    return PipelineState(**state_dict)

# ===============================================================
# LangGraph Pipeline Setup
# ===============================================================
# ===============================================================
# LangGraph Pipeline Setup (unified run() wrapper)
# ===============================================================
def build_pipeline():
    graph = StateGraph(PipelineState)
    graph.add_node("retrieve_data", retrieve_data)
    graph.add_node("critical_analysis", critical_analysis)
    graph.add_node("generate_insights", generate_insights)
    graph.add_node("report_builder", build_report)

    graph.add_edge(START, "retrieve_data")
    graph.add_edge("retrieve_data", "critical_analysis")
    graph.add_edge("critical_analysis", "generate_insights")
    graph.add_edge("generate_insights", "report_builder")
    graph.add_edge("report_builder", END)

    compiled = graph.compile()

    # --- Wrapper to expose a consistent .run() ---
    class PipelineWrapper:
        def __init__(self, compiled_graph):
            self.compiled = compiled_graph

        def run(self, state):
            """Unified run() that calls invoke() when available."""
            if hasattr(self.compiled, "invoke"):
                return self.compiled.invoke(state)
            elif hasattr(self.compiled, "run"):
                return self.compiled.run(state)
            else:
                raise AttributeError("Compiled graph has neither run() nor invoke()")

    return PipelineWrapper(compiled)


# ===============================================================
# Example Run
# ===============================================================
if __name__ == "__main__":
    pipeline = build_pipeline().compile()

    state: PipelineState = PipelineState( # Instantiate the Pydantic model
        query="Latest developments and ethical concerns in AI governance",
        sources=[
            {"type": "research", "query": "AI ethics and governance"},
            {"type": "news", "query": "AI regulation policy updates"}
        ]
    )

    result = pipeline.invoke(state)

    print("\n=== CRITICAL ANALYSIS ===\n", result.get("critical_analysis", "N/A"))
    print("\n=== INSIGHTS ===")
    for i, insight in enumerate(result.get("insights", []), 1):
        print(f"\nInsight {i}: {insight.get('insight')}")
        print(f"Reasoning: {insight.get('reasoning_chain')}")
        print(f"Confidence: {insight.get('confidence')}")
    print("\n=== REPORT TEXT ===\n", result.get("report_text"))
    print("\n=== REPORT JSON ===\n", json.dumps(result.get("report_json", {}), indent=2))
    print("\n=== LOGS ===\n")
    for l in result.get("logs", []):
        print(l)

