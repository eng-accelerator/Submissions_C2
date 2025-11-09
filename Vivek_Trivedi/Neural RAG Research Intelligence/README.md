# 🚀 NRI – Neural RAG Research Intelligence

NRI is an advanced Retrieval-Augmented Generation (RAG) workspace that combines a configurable Gradio UI, a LanceDB vector store, and a multi-agent deep-research backend. The project started as Assignment 3B and has grown into a full research assistant that can answer complex questions using local documents plus optional external connectors.

---

## ✨ Key Capabilities

- **Rich Gradio Frontend**
  - Advanced RAG console with configurable model, temperature, chunk size/overlap, similarity cutoffs, synthesizer, and post-processors.
  - Upload widget (PDF/DOC/DOCX/TXT/RTF/EPUB) that stages files for manual review before ingestion.
  - System configuration popup mirrors all runtime settings for transparency.

- **Document Ingestion & Tracking**
  - Canonical ingest pipeline powered by `LlamaIndex` + LanceDB.
  - Persists metadata to `AssignmentDb/a3b_processed_manifest.json`, allowing the app to compare the manifest with the current `DataSource/` contents to detect new or modified files.
  - Full rebuild pathway ensures the vector database always stays in sync with approved files.

- **Deep Research Mode (LangGraph-ready)**
  - Planner, Retriever, Analysis, Insight, and Report agents (see `deep_research/`) orchestrated through LangGraph/LangChain.
  - Optional external connectors (ArXiv, Wikipedia, Tavily, web search) configurable through UI defaults in `config/rag_ui_config.json`.

- **Auditable Outputs**
  - Markdown panels for plans, retrieved context, analyses, insights, final report, citations, and notes.
  - Similarity cutoff feedback (“No retrieved chunks met the similarity threshold…”) to explain missing context.

---

## 🧱 Project Structure

```
.
├── A3b.py                     # Main Gradio + backend entrypoint
├── AssignmentDb/              # LanceDB vector store + ingest manifest
├── DataSource/                # Approved source documents (ingested)
├── uploads/                   # User uploads awaiting review
├── agents/                    # LangChain agent definitions
├── deep_research/             # LangGraph graph + helpers
├── config/
│   └── rag_ui_config.json     # UI default values (model, chunking, etc.)
├── logs/                      # Optional runtime logs
├── README.md                  # You are here
└── requirements.txt           # Python dependencies
```

---

## ⚙️ Requirements

- Python 3.10+ (tested on 3.12)
- `pip install -r requirements.txt`
- External services as needed:
  - `OPENROUTER_API_KEY` for LLM calls (set via `.env` or system env).
  - Optional `TAVILY_API_KEY`, `DATA_PATH`, etc.

---

## 🚀 Getting Started

1. **Install dependencies**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Seed local documents**
   - Drop approved PDFs/TXTs into `DataSource/`.
   - Uploads from the UI go to `uploads/` and should be moved into `DataSource/` after review.

3. **Configure defaults**
   - Adjust `config/rag_ui_config.json` for model, chunking, retrieval, synthesizer, post-processor, and default external sources.

4. **Run the app**
   ```bash
   python3 A3b.py
   ```
   - The console prints instructions plus the host/port (by default `http://127.0.0.1:7862`).

5. **Initialize the database**
   - After the Gradio UI loads, click **“Initialize Database”** once.
   - The backend compares `AssignmentDb/a3b_processed_manifest.json` with `DataSource/`:
     - If new/changed files exist, it triggers a full rebuild.
     - Otherwise it reports “No new files detected”.

---

## 📥 Upload & Ingestion Workflow

| Step | Description |
| --- | --- |
| 1 | User uploads files via the “Upload Knowledge Files” widget. |
| 2 | Files are copied into `uploads/` and marked “pending review.” |
| 3 | After manual verification, move the files into `DataSource/`. |
| 4 | Click **Initialize Database** – the app rechecks the manifest and rebuilds if necessary. |
| 5 | `AssignmentDb/a3b_processed_manifest.json` is updated with the latest metadata. |

> **Note:** We intentionally avoid ingesting directly from `uploads/` to prevent unreviewed content from reaching the shared knowledge base.

---

## 🧠 Configuring Retrieval & Models

- **UI defaults** (`config/rag_ui_config.json`)
  ```json
  {
    "rag_defaults": {
      "model": "gpt-4o-mini",
      "temperature": 0.1,
      "chunk_size": 512,
      "chunk_overlap": 50,
      "similarity_top_k": 5,
      "similarity_threshold": 0.7,
      "synthesizer": "Default",
      "postprocessor_enabled": false
    },
    "deep_research": {
      "external_sources": ["ArXiv", "Wikipedia", "Tavily Search"]
    }
  }
  ```
- Update this file to change the Gradio defaults; no code changes required.
- Environment variables override certain settings (`DATA_PATH`, `OPENROUTER_API_KEY`, etc.).

---

## 🔧 Troubleshooting

| Issue | Fix |
| --- | --- |
| `Unable to append new documents automatically...` | We now rebuild on any detected change; ensure reviewed files are in `DataSource/` and rerun **Initialize Database**. |
| “No API key found” banner | Set `OPENROUTER_API_KEY` in `.env` or export it before running. |
| Upload not appearing | Files stay in `uploads/` until manually moved to `DataSource/`. |
| Need to start over | Delete `AssignmentDb/` and re-click “Initialize Database” to rebuild from scratch. |

---

## 🗺️ Roadmap Highlights

See `RoadMap.md` for the full multi-agent plan. Upcoming priorities:
- Finalize LangGraph orchestration with Planner → Retriever → Analyst → Insight → Report agents.
- External connector hardening (caching, throttling, provenance logging).
- Expanded evaluation harness with golden questions and contradiction tests.

---

## 🤝 Contributing

1. Create a feature branch.
2. Update/extend tests or manifests where applicable.
3. Submit a PR summarizing:
   - UI/backend changes
   - Impact on ingestion and manifest
   - Testing performed

---

## 📄 License

This project is developed for the “Assignment 3B” research initiative. Adapt or redistribute per your course/company policy.

Happy researching! 🧠✨

---

## 🧑‍💻 How to Use the App

1. **Launch**  
   Run `python3 A3b.py` (after installing dependencies) and open the printed `http://127.0.0.1:7862` link in your browser.

2. **Upload Files (optional)**  
   Drag PDFs/TXTs/DOCs into the “Upload Knowledge Files” panel. They are copied to `uploads/` for review; move approved files into `DataSource/`.

3. **Initialize Database**  
   Click **“Initialize Database”**. The app scans `DataSource/`, compares it with `AssignmentDb/a3b_processed_manifest.json`, and rebuilds the LanceDB vector store if new or changed files are found. Otherwise it reports that everything is already indexed.

4. **Configure RAG Settings**  
   Adjust model, temperature, chunk size/overlap, top-K, similarity threshold, post-processor, and synthesizer in the left configuration column. Use the “System Configuration” button to view the active settings.

5. **Ask Questions**  
   Type your prompt in the “Your Question” box and click **Submit**. Results appear in the “Research Console” panel. Optional deep-research mode and external sources can be toggled via the advanced settings.

6. **Review Outputs**  
   Scroll through the plan, context, analysis, insight, report, citation, and notes tabs for full provenance. Adjust settings and rerun as needed.

7. **Iterate / Maintain**  
   - After reviewing new documents, move them from `uploads/` to `DataSource/` and rerun **Initialize Database**.  
   - Keep `config/rag_ui_config.json` in sync with your preferred default configuration.

That’s it—you’re ready to explore documents with NRI!
