# Multi-Agent Deep Researcher Roadmap

## 1. Scope & Architecture
- Define end-to-end flow: ingestion → retrieval → multi-agent reasoning → reporting.
- Choose core stack (LangChain/LangGraph orchestrator, LanceDB/FAISS vectors, OpenRouter LLMs, Gradio UI).
- Decide how the new system coexists with the existing A3b RAG app (shared services vs. separate module).

## 2. Data & Retrieval Layer
- Extend current document ingestion so both interfaces reuse the same vector index; document schema & metadata contract.
- Determine external source connectors (ArXiv, news APIs, DuckDuckGo, etc.) with throttling/caching and mapping into a unified Document format.
- Define evaluation datasets and logging to measure retrieval quality.
  - Create a small seed set of "gold" questions (e.g., 10 covering local PDFs + external topics) with expected supporting sources.
  - Add a retrieval log (CSV/JSONL) recording query, timestamp, source name, doc id/path, similarity score, and whether it passed the cutoff.
  - Instrument the new connectors to emit structured events (possibly via Python `logging` or a lightweight `logs/retrieval.log`).

## 3. Agent Design
- Draft specs for each agent (Contextual Retriever, Critical Analyst, Insight Generator, Report Builder; optional Planner/Fact Checker).
- For every agent: prompts/system messages, expected inputs/outputs, memory requirements, and validation checks.
- Plan shared state structure so agents can append findings without clobbering one another.

## 4. LangGraph Orchestration
- Model the state graph connecting agents (branching/looping for multi-hop retrieval, retry & timeout strategy).
- Implement guardrails: error handling, fallback paths, rate-limit backoffs, and telemetry hooks.
- Add configuration toggles (max depth, model choices, temperature) to make experiments reproducible.

## 5. Evaluation & UX
- Create a test harness with seed queries, golden expectations, and metrics (coverage, contradiction detection, cost/time).
- Design the new Gradio page: query input, agent status timeline, retrieved sources panel, final report viewer/download.
- Integrate provenance tracking and user-adjustable parameters (e.g., # of agents, external sources to enable).

## 6. Iterative Enhancements
- Layer in advanced skills: contradiction detection, citation validation, hypothesis ranking, trend analysis.
- Optimize performance/cost via batching, selective LLM usage, streaming updates, and adaptive memory.
- Document deployment steps and monitoring to support continuous improvements.
