# MediScout - AI Medical Research Assistant

**Group 3 Project | AI Accelerator Programme (C2 Cohort)**

MediScout is a multi-agent AI system for medical research that combines local document analysis with external database searches (PubMed) to provide comprehensive critical analysis and automated report generation.

[Video Demo](https://youtu.be/0h-VQgeT-hw)

## 🚀 Quick Start

### For Anaconda Users
See [SETUP.md](SETUP.md) for detailed instructions.

### For Non-Anaconda Users  
See [SETUP-NON-ANACONDA.md](SETUP-NON-ANACONDA.md) for standard Python/pip setup.

### Basic Setup (5 minutes)
```bash
# 1. Clone repository
git clone https://github.com/neelavar/AI-Accelerator-C2-Hackathon-Group-3.git
cd AI-Accelerator-C2-Hackathon-Group-3

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -e .

# 4. Configure environment
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY and PUBMED_EMAIL

# 5. Run application
streamlit run main.py
```

## 📋 Prerequisites

- **Python:** 3.11, 3.12, or 3.13 (NOT 3.14+)
- **API Keys:**
  - OpenRouter API key (required) - Get from [openrouter.ai](https://openrouter.ai/keys)
  - LangSmith API key (optional) - Get from [smith.langchain.com](https://smith.langchain.com/)
- **Email:** Valid email for PubMed API access (no registration needed)

## 🏗️ Architecture

MediScout uses a **multi-agent orchestration** pattern with LangGraph:

```
User Query → Validator → Retriever → Analyzer → Report Builder → User
                ↓           ↓
           Local KB    PubMed API
```

See [docs/architecture-diagram.html](docs/architecture-diagram.html) for the complete architecture diagram.

## 📚 About This Repository

This repository contains the Group 3 project for the AI Accelerator Programme (C2 cohort). The goal is to rapidly prototype and iterate on AI agents and agentic systems using an AI-augmented design & development process. Project documentation, architecture notes, templates, and persona definitions live under the `docs/` directory.

Key points
- Primary workspace for Group 3 in the AI Accelerator C2 cohort.
- Project documentation and templates are stored under `docs/` (see `docs/templates` and `docs/ai-personas`).
- The project follows an AI-augmented workflow: teams should leverage the included AI personas to speed up planning, design, and implementation.

NOTE: As development progresses, all project-specific documentation should live in `docs/project-docs/`.

Why this repo exists
- Provide a shared, structured place to develop agentic prototypes during the hackathon.
- Encourage disciplined documentation with templates for PRDs, project plans, architecture and technical designs.
- Promote an AI-augmented workflow by providing curated AI personas that act as role-based assistants (Product Analyst, Project Manager, UX Designer, Solution Architect, Python AI Developer, etc.).

Getting started (high-level)
- Read the AI persona descriptions in `docs/ai-personas/` and the templates in `docs/templates/`.
- Use the PRD template (`docs/templates/10_prd-template.md`) to capture product requirements for small agent projects.
- Use the Project Plan template (`docs/templates/20_project-plan-template.md`) to break work into phases and AI-ready tasks.
- Use the Architecture template (`docs/templates/40_architecture-template.md`) for high-level system design and the Technical Design Document template (`docs/templates/41_technical-design-template.md`) for implementation-level details.
- A rudimentary Python project scaffold is included as a reference (using `uv` as a minimal example). Developers can use it as a starting point for service components.

Leveraging AI Personas
- The `docs/ai-personas/` folder contains role-based persona files. Treat these as virtual collaborators:
	- Use the Product Analyst persona to craft clear PRDs and user stories.
	- Use the Project Manager persona to decompose epics into AI-ready tasks and maintain the project log.
	- Use the Solution Architect persona when creating the architecture document and making system-level trade-offs.
	- Use the Python AI Developer persona for coding, model integration, and implementation guidance.
- Personas are intended to be used interactively: copy suggested prompts or ask tailored questions when planning, designing, reviewing, or coding.

Documentation best-practices
- Keep docs concise but actionable. Use the templates under `docs/templates/` as the single source of truth.
- Update the relevant template for each new feature or component (PRD → Project Plan → Architecture → Technical Design → Runbooks).
- Store examples, payloads, and small fixtures under `docs/examples/` (create as needed).

Contribution guidelines
- Branches & workflow:
	- Work from the `develop` branch for development. Direct commits to `develop` are prohibited.
	- Create feature branches named `feat/<short-name>` or `fix/<short-name>`.
	- Open a pull request against `develop` when your change is ready for review.
- Issues & PRs:
	- Open issues for bugs, tasks, or docs you plan to work on. Tag PRs with the relevant issue number where appropriate.
	- Keep PRs small and focused. Link to the relevant template (PRD, architecture, etc.) when changing design decisions.
- Code style & tests:
	- Follow existing code style in the repo. Add unit tests for new logic where feasible.
	- For Python services, prefer small, fast unit tests and one integration test for critical flows.
- Documentation & templates:
	- Use templates in `docs/templates/` for PRDs, project plans, architecture and technical designs.
	- Update `docs/ai-personas/` if you create a new persona or improve an existing one.
- Communication:
	- If you need clarifications or want to discuss architecture choices, contact the repo owner (see below) or open a discussion issue.

Repository structure (important folders)
- `docs/ai-personas/` — AI persona definitions and prompts.
- `docs/templates/` — Documentation templates (PRD, project plan, architecture, TDD).
- `docs/project-docs/` — Project-specific documentation (use this as your main doc area as the project progresses).
- `main.py`, `pyproject.toml` — Minimal Python project scaffold (reference).

Contact
- Project Members: 
- Maintainer: Prasanna Neelavar — prasanna.neelavar@gmail.com
- Ashish Saha
- Saravanan K (Saro)
- Manohar Negi
- Srinivas K

License
- See `LICENSE` for license details.

Thanks for contributing — use the personas, stick to the templates, and keep docs actionable. Let's build something useful and iteratively improve it.

