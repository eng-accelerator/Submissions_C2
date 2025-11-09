# 🔬 Multi-Agent AI Deep Researcher

**C2 | Hackathon Group 1**

A sophisticated multi-agent research system built with Gradio that performs deep research investigations using RAG (Retrieval-Augmented Generation), vector similarity search, critical analysis, and automated report generation.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [Multi-Agent Pipeline](#-multi-agent-pipeline)
- [UI Features](#-ui-features)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

### Core Capabilities
- **Multi-Agent Research Pipeline**: Coordinated agents for planning, retrieval, analysis, insights, and reporting
- **Hybrid Search**: Combines vector similarity (FAISS) with keyword-based fallback retrieval
- **Intelligent Document Processing**: PDF, HTML, and text file support with smart chunking (180 words, 30-word overlap)
- **Source Attribution**: Tracks and validates source credibility with detailed metadata
- **LLM-Powered Insights**: OpenAI/OpenRouter integration for pattern extraction and hypothesis generation
- **Automated Report Generation**: Professional markdown reports with executive summaries
- **Web Search Integration**: Optional Tavily API support for live web searches

### UI & UX Features
- **Timestamped Status Updates**: Real-time progress tracking with HH:MM:SS timestamps
- **Animated Progress Spinner**: Visual feedback during long-running operations
- **Analysis Depth Presets**: Quick/Standard/Deep modes with customizable parameters
- **Advanced Settings**: JSON configuration editor with preset reset functionality
- **Multi-Tab Output**: Separate views for Retrieved Context, Analysis, Insights, and Final Report
- **Download Functionality**: Export all stage outputs as markdown files
- **Persistent State**: Tab data remains available across stages and switches
- **Responsive Design**: Centered layout with proper scrolling (max-width 1400px)

---

## 🏗️ Architecture

### Multi-Agent System

```
┌─────────────┐
│   Planner   │ ─── Task decomposition, constraint enforcement
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Retriever  │ ─── Document indexing, vector search, chunking
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Analyst   │ ─── Source validation, credibility scoring, conflict detection
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Insights   │ ─── Pattern extraction, hypothesis generation (LLM-powered)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Reporter   │ ─── Markdown report generation with executive summary
└─────────────┘
```

### Key Components

#### 1. **PlannerAgent** (`src/agents/planner.py`)
- Creates research plan based on query and constraints
- Enforces depth limits (quick/standard/deep)
- Tracks costs and resource usage

#### 2. **ContextualRetrieverAgent** (`src/agents/context_retriever.py`)
- **Document Loaders**: PDF (PyMuPDF), HTML (BeautifulSoup), file uploads
- **Vector Store**: FAISS with L2-normalized embeddings (384-dim local fallback, 1536-dim OpenAI)
- **Chunking**: 180-word chunks with 30-word overlap for context preservation
- **Hybrid Search**: Vector similarity + keyword fallback for robustness
- **Deduplication**: SHA256 hashing prevents duplicate document indexing

#### 3. **CriticalAnalysisAgent** (`src/agents/critical_analyst.py`)
- **Source Credibility Scoring**: Domain-based scoring (0-1 scale)
- **Evidence Mapping**: Extracts and categorizes claims with supporting evidence
- **Conflict Detection**: Identifies contradictions across sources
- **Structured Output**: Line-separated format for easy scanning

#### 4. **InsightGenerationAgent** (`src/agents/insight_generator.py`)
- **Pattern Extraction**: LLM-powered identification of recurring themes
- **Hypothesis Generation**: Generates research hypotheses from analysis
- **Keyword Extraction**: TF-IDF based topic extraction
- **Fallback Mode**: Extractive summarization when LLM unavailable

#### 5. **ReportBuilderAgent** (`src/agents/report_builder.py`)
- **Executive Summary**: LLM-generated high-level overview
- **Structured Sections**: Key findings, insights, patterns, recommendations
- **Source Citations**: Inline references with credibility indicators
- **Markdown Output**: Professional formatting with metadata

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- (Optional) OpenAI API key or OpenRouter API key
- (Optional) Tavily API key for web search

### Setup Steps

1. **Clone the repository**:
```powershell
git clone <repository-url>
cd AI_Deep_Researcher
```

2. **Create and activate virtual environment**:
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Windows Command Prompt
python -m venv .venv
.venv\Scripts\activate.bat

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**:
```powershell
pip install -r requirements.txt
```

4. **Configure environment variables**:
```powershell
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
# OPENAI_API_KEY=sk-...
# OPENROUTER_API_KEY=sk-or-...
# TAVILY_API_KEY=tvly-...
```

---

## ⚡ Quick Start

### Running the Application

**Recommended method** (ensures proper package resolution):
```powershell
python -m src.app
```

**Alternative** (direct script execution):
```powershell
python src/app.py
```

The application will:
1. Auto-select an available port (7860-7870)
2. Launch Gradio interface at `http://localhost:<port>`
3. Display "Running on local URL" in terminal

### Basic Workflow

1. **Enter Research Query**: Type your research question
2. **Upload Documents** (optional): Add PDFs, text files, or HTML
3. **Add URLs** (optional): Comma-separated web URLs
4. **Select Depth**: Quick (8 sources), Standard (20 sources), or Deep (40 sources)
5. **Click "🚀 Start Research"**: Full pipeline runs automatically
6. **View Results**: Switch between tabs to see Retrieved Context, Analysis, Insights, and Final Report
7. **Download**: Use download buttons to export results as markdown

---

## ⚙️ Configuration

### Analysis Depth Presets

| Preset | Max Sources | Min Credibility | Min Score | Top K | Best For |
|--------|-------------|-----------------|-----------|-------|----------|
| **Quick** | 8 | 0.6 | 0.6 | 3 | Fast overview, high-quality sources only |
| **Standard** | 20 | 0.7 | 0.6 | 5 | Balanced research with moderate coverage |
| **Deep** | 40 | 0.5 | 0.5 | 12 | Comprehensive analysis, includes varied sources |

### Advanced Settings (JSON)

Expand "Advanced Settings" to customize:

```json
{
  "depth": "standard",
  "max_sources": 20,
  "min_credibility": 0.7,
  "min_score": 0.6,
  "top_k": 5
}
```

**Reset Button**: Click "🔁 Reset Advanced Settings to Depth Preset" to restore preset values.

### Environment Variables

Create `.env` file with:

```env
# LLM Configuration (at least one required)
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...

# Web Search (optional)
TAVILY_API_KEY=tvly-...

# Embeddings Mode (optional, defaults to 'remote')
EMBEDDINGS_MODE=remote  # or 'local' for offline hash-based embeddings

# Logging (optional)
LOG_LEVEL=INFO
```

---

## 📖 Usage Guide

### Individual Stage Buttons

Run stages independently for debugging or iterative research:

- **📥 Index Files**: Index documents and URLs into vector store
- **🔍 Retrieve**: Search indexed documents for relevant passages
- **📊 Analyze**: Perform critical analysis on retrieved content
- **💡 Insights**: Generate patterns and hypotheses
- **📄 Report**: Build final markdown report

### Tab Navigation

#### 📋 Retrieved Context
- Total passages retrieved
- Source count and types
- Relevance scores (0-1)
- Snippet previews (600 chars)
- Full metadata per passage

#### 🔍 Analysis
**Structured line format:**
```
Analyzed: 3 source(s)
Average credibility: 0.75/1.0
Key finding: [Primary discovery from sources]
Additional finding: [Secondary discovery if available]
Credibility assessment: High overall reliability; sources largely authoritative.
Conflicts detected: None identified across analyzed sources.
```

#### 💡 Insights
- **Patterns**: Recurring themes across sources
- **Hypotheses**: Research questions and potential explanations
- **Keywords**: Top extracted terms with relevance scores
- **LLM vs Fallback**: Indicator shows generation method

#### 📄 Final Report
- **Executive Summary**: High-level overview (LLM-generated)
- **Key Findings**: Structured list of discoveries
- **Insights**: Detailed patterns and hypotheses
- **Recommendations**: Next steps and further research areas
- **Metadata**: Query, timestamp, source count

### Status Bar Features

Real-time progress with timestamps:
```
14:32:15 | 🔄 [1/6] Planning
14:32:16 | 🔄 [2/6] Indexing
14:32:20 | 🔄 [3/6] Retrieving
14:32:25 | 🔄 [4/6] Analyzing
14:32:30 | 🔄 [5/6] Generating Insights
14:32:35 | 🔄 [6/6] Building Report
14:32:40 | ✅ Research Completed (6/6 stages)
```

**Spinner**: Animated indicator shows during pipeline execution, hides on completion.

---

## 🔄 Multi-Agent Pipeline

### Full Pipeline Flow

```
User Query + Documents
        │
        ▼
   [Planning] ─────────────► Create research plan
        │                    Validate constraints
        ▼
   [Indexing] ─────────────► Load & chunk documents
        │                    Generate embeddings
        │                    Build FAISS index
        ▼
  [Retrieval] ─────────────► Vector similarity search
        │                    Keyword fallback
        │                    Re-rank by score
        ▼
   [Analysis] ─────────────► Score source credibility
        │                    Extract key findings
        │                    Detect conflicts
        ▼
   [Insights] ─────────────► Extract patterns (LLM)
        │                    Generate hypotheses (LLM)
        │                    Identify topics (TF-IDF)
        ▼
    [Report] ─────────────► Generate executive summary (LLM)
                             Compile markdown report
                             Add metadata & citations
```

### Stage Details

#### Stage 1: Planning
- Parses query intent
- Sets resource limits based on depth preset
- Creates structured research plan

#### Stage 2: Indexing
- **Document Loading**: PDFs (PyMuPDF), HTML (BeautifulSoup), files
- **Chunking**: 180-word segments, 30-word overlap
- **Embedding Generation**: 
  - Remote: OpenAI/OpenRouter (1536-dim)
  - Local fallback: Hash-based (384-dim, padded)
- **L2 Normalization**: Ensures unit vectors for cosine similarity
- **Deduplication**: SHA256 prevents re-indexing

#### Stage 3: Retrieval
- **Primary**: FAISS IndexFlatIP (inner product after L2 norm = cosine)
- **Fallback**: Keyword matching with punctuation handling
- **Filtering**: Min score threshold, max source limits
- **Metadata Preservation**: Source, title, type, timestamps

#### Stage 4: Analysis
- **Credibility Scoring**:
  - Nature/JAMA/NEJM: 0.95 (peer-reviewed journals)
  - arXiv/Springer: 0.85 (preprints/academic)
  - DOI references: 0.7 (published)
  - Blogs/Medium: 0.4 (informal)
  - Default: 0.5
- **Evidence Mapping**: Claims → Support
- **Conflict Detection**: Cross-source contradiction identification

#### Stage 5: Insights
- **LLM Integration**: OpenAI/OpenRouter for pattern extraction
- **Prompt Engineering**: Structured prompts for consistent output
- **Hypothesis Generation**: Research questions from findings
- **Validation**: Rejects prompt echoes, requires substantive content

#### Stage 6: Report Building
- **Executive Summary**: LLM-generated overview (max 400 tokens)
- **Structured Sections**: Findings, Insights, Recommendations
- **Citation Format**: Inline source references with credibility
- **Markdown Export**: Clean, readable format
- **File Output**: Saved to `outputs/` directory with timestamp

---

## 🎨 UI Features

### Layout & Design
- **Centered Container**: Max-width 1400px, auto-margin
- **Scrollable Tabs**: 450px max-height with overflow-y
- **Responsive**: Adapts to different screen sizes
- **Custom CSS**: Professional styling with #e8f4f8 status bar

### Interactive Elements
- **Depth Radio**: Updates JSON config on change
- **Reset Button**: Reverts JSON to selected preset
- **Spinner**: CSS animation (0.9s rotation, #3498db border)
- **Download Files**: Auto-generate on content change

### Accessibility
- **Keyboard Navigation**: Full tab support
- **Screen Reader Friendly**: ARIA labels on components
- **High Contrast**: Clear visual hierarchy

---

## 📁 Project Structure

```
AI_Deep_Researcher/
├── src/
│   ├── __init__.py
│   ├── app.py                      # Main Gradio application
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner.py              # Research planning agent
│   │   ├── context_retriever.py    # Document indexing & retrieval
│   │   ├── critical_analyst.py     # Source analysis & validation
│   │   ├── insight_generator.py    # Pattern & hypothesis generation
│   │   ├── report_builder.py       # Markdown report assembly
│   │   └── keywords.py             # TF-IDF keyword extraction
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── loaders.py              # Document loaders (PDF, HTML, File)
│   │   ├── pdf_loader.py           # PyMuPDF wrapper
│   │   ├── vectorstore_new.py      # FAISS vector store
│   │   ├── websearch.py            # Tavily API integration
│   │   └── http.py                 # HTTP utilities
│   └── utils/
│       ├── __init__.py
│       ├── config.py               # YAML/env configuration
│       ├── llm.py                  # OpenAI/OpenRouter wrapper
│       ├── costs.py                # Cost tracking
│       └── logging.py              # Structured logging
├── data/
│   └── faiss.index                 # Persisted vector store
├── outputs/
│   └── *.md                        # Generated reports
├── config/
│   └── settings.yaml               # Application settings
├── .env                            # Environment variables (not in git)
├── .env.example                    # Example environment file
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── ENHANCEMENTS_SUMMARY.md         # Recent feature additions
```

---

## 🛠️ Development

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agents.py

# Run with verbose output
pytest -v
```

### Code Quality

```powershell
# Linting with Ruff
ruff check src/

# Type checking with mypy
mypy src/

# Format code
ruff format src/
```

### Adding New Agents

1. Create agent class in `src/agents/your_agent.py`
2. Implement required methods (typically `process()` or similar)
3. Import in `src/app.py`
4. Add to pipeline in `run_pipeline()` function
5. Update status messages in `on_run()` function

### Debugging Tips

- **Enable verbose logging**: Set `LOG_LEVEL=DEBUG` in `.env`
- **Check vector store**: Inspect `data/faiss.index` size and metadata
- **Monitor LLM calls**: Watch for "LLM error:" messages in console
- **Test individual stages**: Use stage buttons instead of full pipeline
- **Examine outputs**: Check `outputs/` directory for generated files

---

## 🐛 Troubleshooting

### Common Issues

#### "Import 'gradio' could not be resolved"
- **Cause**: Gradio not installed or wrong Python environment
- **Fix**: 
  ```powershell
  pip install gradio>=4.0.0
  # Or reinstall all dependencies
  pip install -r requirements.txt
  ```

#### "No passages retrieved" with uploaded files
- **Cause**: 
  - Files not properly indexed
  - Min score threshold too high
  - Empty/corrupted documents
- **Fix**:
  1. Click "📥 Index Files" first
  2. Lower `min_score` in Advanced Settings (try 0.4)
  3. Check console for indexing errors
  4. Verify file formats (PDF, TXT, HTML supported)

#### LLM generates placeholder text or echoes prompt
- **Cause**: 
  - Missing API keys
  - API rate limits
  - Network issues
- **Fix**:
  1. Verify `.env` has valid `OPENAI_API_KEY` or `OPENROUTER_API_KEY`
  2. Check API key permissions and billing
  3. System falls back to extractive summarization automatically

#### Vector store index corrupted
- **Cause**: Interrupted indexing or version mismatch
- **Fix**:
  ```powershell
  # Delete and rebuild index
  rm data/faiss.index
  # Re-run indexing in UI
  ```

#### Port already in use
- **Cause**: Previous instance still running or port conflict
- **Fix**: App auto-tries ports 7860-7870, or manually:
  ```powershell
  # Find process using port
  netstat -ano | findstr :7860
  # Kill process by PID
  taskkill /PID <pid> /F
  ```

### Performance Issues

#### Slow indexing
- **Reduce document size**: Use shorter documents or limit pages
- **Use local embeddings**: Set `EMBEDDINGS_MODE=local` in `.env`
- **Increase chunking size**: Modify `chunk_size` in `context_retriever.py`

#### Slow retrieval
- **Reduce `top_k`**: Lower value in Advanced Settings (try 3 for quick)
- **Increase `min_score`**: Filter out low-relevance results (try 0.7)
- **Use Quick preset**: Limits max_sources to 8

### Getting Help

1. **Check logs**: Console output shows detailed error traces
2. **Review ENHANCEMENTS_SUMMARY.md**: Recent changes and known issues
3. **Inspect outputs**: Check `outputs/` for partial results
4. **Test components individually**: Use stage buttons to isolate issues

---

## 📝 License
Free to use

## 🙏 Acknowledgments

- **C2 | Hackathon Group 1** team members
- **Gradio**: UI framework
- **FAISS**: Vector similarity search
- **OpenAI/OpenRouter**: LLM integration
- **PyMuPDF**: PDF processing

---

## Created By

[Maruti Divekar, Vivek, Shabbir, Saumya, KEP62F]

---

**Version**: 2.0  
**Last Updated**: November 2025  
**Status**: Production Ready
