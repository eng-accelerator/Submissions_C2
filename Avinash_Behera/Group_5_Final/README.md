# Hackathon project submission doc

# 🧠 **Multimodal UI/UX Analysis Agent Suite — Submission Package**

---

## 📹 Project Demo Video Link: https://drive.google.com/file/d/1glLEIVay_GB-sVtGv1E6fXPfV_iQTZcF/view?usp=drive_link

---

## 🚀 Project Philosophy

Our north star is to help product teams answer one question:

> “Is this experience ready for real people?” — in minutes, not weeks.
> 

The suite fuses multimodal analysis, persona-driven simulations, and rapid iteration loops so designers, PMs, and researchers can **ship with confidence**.

By pairing **human-centered heuristics** with **defensible AI reasoning**, we deliver:

- Rapid, repeatable evaluation of **visual**, **UX**, and **accessibility** quality — without losing nuance.
- Insight-rich reports that ground recommendations in **personas, goals, and measurable scores**.
- A workflow that fits naturally into existing contexts — **Figma links, Supabase history, PDFs, and stored screens** — so adoption feels effortless.

---

## 🧩 Build Journey

1. **Foundations & Data Flow** — Scaffolded FastAPI services, Supabase persistence, and storage pipelines; wired a React + Vite frontend for uploads, project management, and live polling.
2. **Multimodal Agent Core** — Implemented LangGraph orchestration (`agents/orchestrator.py`) to run visual, UX, and accessibility agents in parallel, maintaining shared state through reducers and ensuring deterministic aggregation.
3. **Observability & Performance** — Upgraded agents to LangChain `ChatOpenAI` with callback telemetry, halved runtime through batch processing, and surfaced token/cost metrics for every request (`ENHANCEMENTS_COMPLETE.md`).
4. **Persona Suite Expansion** — Built the persona pipeline (`agents/persona_suite/`) to normalize artifacts, derive personas, simulate journeys, score friction, and render Markdown / JSON reports for downstream export.
5. **Polish & Integrations** — Added Figma ingestion, append-mode analysis, PDF export, and UI refinements so the platform supports real-world design workflows end-to-end.

---

## ⚙️ Tech Stack (and Why LangGraph)

| Layer | Technology | Purpose |
| --- | --- | --- |
| **Frontend** | React 18 + Vite 6, TailwindCSS, Shadcn UI, Framer Motion | Responsive uploads, real-time progress, and interactive dashboards (`src/App.tsx`, `ProjectsDashboard.tsx`). |
| **Backend API** | FastAPI + BackgroundTasks + Supabase SDK | Handles uploads, Figma imports, job scheduling, and result persistence (`main.py`). |
| **Agent Runtime** | LangChain + LangGraph | Powers the visual (`visual_agent.py`), UX (`ux_agent.py`), accessibility (`accessibility_agent.py`), and persona pipelines. |
| **Data & Reports** | Supabase tables + ReportLab PDF + Markdown renderer | Stores project data and generates human-friendly reports. |

### 🧠 Why LangGraph

- Executes multimodal agents **in parallel** while maintaining shared context through typed reducers (`AnalysisState`).
- Encodes the full pipeline declaratively (START ➜ agents ➜ aggregate) for **reproducibility and auditability**.
- Enables **conditional routing** — e.g., entering the persona suite only when toggled — to avoid wasted tokens.
- Interoperates cleanly with LangChain’s callbacks, retries, and structured outputs for reliable orchestration.

---

## 🧱 Architecture Diagrams

---

## 🧩 **System Architecture (Markdown-only View)**

```markdown
───────────────────────────────────────────────────────────────────────────────
                    🧠  MULTIMODAL UI/UX ANALYSIS AGENT SUITE
───────────────────────────────────────────────────────────────────────────────

👩‍💻  Design Team
   │
   ├── uploads design files / Figma links
   │
   ▼
🖥️  Frontend  —  React + Vite + Tailwind + Shadcn UI
   │
   ├── Real-time upload progress
   ├── Project dashboards & analysis views
   └── Communicates via REST / WebSockets
        │
        ▼
⚙️  Backend API  —  FastAPI
   │
   ├── Handles uploads & job scheduling
   ├── Manages Figma imports (via MCP)
   ├── Triggers LangGraph orchestration
   │
   ├───► 🗄️  Supabase DB
   │         • Stores project metadata
   │         • Historical results
   │         • Persona & market records
   │
   ├───► 💾  Object Storage
   │         • Uploaded screenshots
   │         • Figma exports
   │
   └───► 🧮  LangGraph Orchestrator
            │
            ├── Runs all AI agents in parallel
            ├── Shares typed state (AnalysisState)
            └── Aggregates structured outputs
                 │
                 ├── 👁️  Visual Agent
                 ├── 🧭  UX Heuristics Agent
                 ├── ♿  Accessibility Agent
                 └── 👥  Persona Suite (sub-graph)
                        │
                        ├─ Derive personas
                        ├─ Simulate user journeys
                        ├─ Score frustration & task flow
                        └─ Generate reports
                             │
                             ▼
📄  Reports & Exports
   ├── Markdown + JSON payloads → Frontend
   ├── PDF summaries via ReportLab
   └── Supabase archival for history

───────────────────────────────────────────────────────────────────────────────
✨  Frontend pulls results → displays dashboards → enables fast iteration loops
───────────────────────────────────────────────────────────────────────────────

```

---

## 🤖 **Agentic Flow (Markdown-only LangGraph View)**

```markdown
──────────────────────────────────────────────────────────────
              ⚙️  LANGGRAPH ORCHESTRATOR  —  NODE FLOW
──────────────────────────────────────────────────────────────

[START]
   │
   ├─▶ 👁️  Visual Analysis Node
   │       • Detects layout balance, spacing, composition
   │
   ├─▶ 🧭  UX Heuristics Node
   │       • Runs Nielsen + accessibility checks
   │
   ├─▶ ♿  Accessibility Node
   │       • Color contrast, text readability
   │
   ▼
 ┌─────────────────────────────────────────────┐
 │  Aggregation Node                           │
 │  • Merges visual, UX, and accessibility data│
 │  • Computes composite design scores          │
 └─────────────────────────────────────────────┘
   │
   ├──▶ (if personaFit enabled)
   │       👥  Persona Suite Sub-Graph
   │
   │       ┌────────────────────────────────────────┐
   │       │ Persona Suite Flow                     │
   │       │ ├─ Ingest design context               │
   │       │ ├─ Understand design intent            │
   │       │ ├─ Generate personas                   │
   │       │ ├─ Simulate interactions               │
   │       │ ├─ Evaluate frustration / friction     │
   │       │ ├─ Score task completion               │
   │       │ └─ Produce report (JSON + Markdown)    │
   │       └────────────────────────────────────────┘
   │
   ▼
 [END]  →  Final Results
          • `final_results.json`
          • `report.md`
          • Optional `report.pdf`

──────────────────────────────────────────────────────────────
🏁  Output streamed to frontend dashboard and Supabase archive
──────────────────────────────────────────────────────────────

```

---

## 🌐 **Data & Integration Map**

```markdown
──────────────────────────────────────────────────────────────
                🌍  INTEGRATION LAYER OVERVIEW
──────────────────────────────────────────────────────────────

        ┌───────────────────────────────┐
        │        External Sources        │
        ├───────────────────────────────┤
        │ 🎨  Figma MCP  →  design frames│
        │ 🔎  Exa MCP    →  competitor URLs│
        │ 🌐  Apify MCP  →  structured scrape│
        └───────────────────────────────┘
                     │
                     ▼
        ┌───────────────────────────────┐
        │    LangGraph Orchestrator      │
        ├───────────────────────────────┤
        │  • fetch + parse inputs        │
        │  • run agents in parallel      │
        │  • maintain AnalysisState      │
        │  • aggregate structured results│
        └───────────────────────────────┘
                     │
                     ▼
        ┌───────────────────────────────┐
        │   FastAPI Backend Services     │
        ├───────────────────────────────┤
        │  • stores data → Supabase      │
        │  • saves assets → Storage       │
        │  • exposes REST endpoints       │
        │  • generates PDF / Markdown     │
        └───────────────────────────────┘
                     │
                     ▼
        ┌───────────────────────────────┐
        │     React / Vite Frontend      │
        ├───────────────────────────────┤
        │  • uploads & progress UI       │
        │  • persona + market dashboards │
        │  • report viewer               │
        │  • iteration feedback loops    │
        └───────────────────────────────┘
──────────────────────────────────────────────────────────────

```

---

---

## ✅ Success Criteria Achieved

- **Speed & Scale** — 2× faster end-to-end analysis through concurrent agent execution and multimodal batch prompting.
- **Depth of Insight** — Unified visual, UX, accessibility, and persona storytelling in a single JSON + Markdown + PDF result set.
- **Workflow Coverage** — Supports Figma imports, incremental updates, Supabase history, and background job tracking — ready for production.
- **Observability** — Automatic token/cost telemetry and structured logging (`[LANGCHAIN]`, `[LANGGRAPH]`) for every pipeline run.
- **Reliability** — Graceful error handling maintains project state and prevents data loss during pipeline interruptions.

---

## 🧠 Skills Demonstrated & Learned

- Architecting complex **LangGraph state machines** and persona pipelines using typed reducers and caching.
- Prompting **multimodal GPT-4o/4o-mini** agents for consistent JSON outputs across visual, UX, and accessibility heuristics.
- Integrating **Figma API, Supabase, and ReportLab** into a cohesive FastAPI backend with background task execution.
- Instrumenting AI workloads via **LangChain callbacks** to monitor latency, token usage, and cost.
- Designing polished **React UIs** that clearly communicate system status (uploads, polling, notifications) in real time.

---

## 🙏 Gratitude

Huge thanks to all of the Outskill **course mentors** and **course co-ordinators** for encouraging us to go beyond single-agent demos.

Your emphasis on **modularity, evaluation rigor, and shipping polish** directly shaped this submission.

We’re deeply grateful for the **feedback loops, office hours, and collective enthusiasm** that kept our team pushing forward throughout the hackathon.

> “We set out to build a demo — and ended up architecting a design-intelligence ecosystem.”
> 
> 
> — *Team @hackathon Group 5*
>
