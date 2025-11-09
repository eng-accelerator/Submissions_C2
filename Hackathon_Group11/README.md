# Multi-Agent AI Deep Researcher

A hackathon demo showcasing a multi-agent AI system for comprehensive research using specialized AI agents that collaborate to conduct deep, multi-source investigations.

## 🤖 System Overview

This system uses four specialized agents working in collaboration:

1. **🔍 Contextual Retriever Agent** - Pulls data from research papers, news articles, reports, and APIs
2. **📊 Critical Analysis Agent** - Summarizes findings, highlights contradictions, and validates sources
3. **💡 Insight Generation Agent** - Suggests hypotheses or trends using reasoning chains
4. **📄 Report Builder Agent** - Compiles all insights into a structured report

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenRouter API key (get from https://openrouter.ai/keys)

### Installation

1. **Clone or download this repository**

2. **Create and activate virtual environment:**

   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Windows
   copy env.example .env
   
   # macOS/Linux
   cp env.example .env
   
   # Edit .env and add your OPEN_ROUTER_KEY
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`

**📖 For detailed setup instructions, see `VIRTUAL_ENV_SETUP.md`**

## 📋 Features

- **Multi-Source Retrieval**: Searches web, research papers (ArXiv), and news articles
  - **Tavily Search API**: AI-optimized web search with structured results, relevance scores, and AI-generated answers
  - **ArXiv Integration**: Research paper search for academic sources
- **Critical Analysis**: Identifies contradictions and assesses source credibility
- **Insight Generation**: Creates hypotheses, trends, and reasoning chains
- **Structured Reports**: Generates professional markdown reports with citations
- **Demo Mode**: Cached results for reliable hackathon demonstrations

## 🏗️ Architecture

### Tech Stack

- **LangChain**: Agent framework and LLM integration
- **LangGraph**: Workflow orchestration
- **Streamlit**: Web UI
- **OpenRouter**: Unified LLM API (supports OpenAI, Anthropic, Google, Meta, and more)

### Project Structure

```
multi-agent-researcher/
├── agents/
│   ├── retriever.py          # Contextual Retriever Agent
│   ├── analyzer.py            # Critical Analysis Agent
│   ├── insight_generator.py  # Insight Generation Agent
│   └── report_builder.py     # Report Builder Agent
├── orchestration/
│   └── coordinator.py        # LangGraph workflow
├── utils/
│   └── demo_cache.py         # Demo caching utilities
├── app.py                    # Streamlit UI
├── requirements.txt
└── README.md
```

### Workflow

```
Query → Retriever → Analyzer → Insight Generator → Report Builder → Final Report
```

## 🎯 Demo Mode

For hackathon presentations, use Demo Mode to show cached results:

1. Check "Use Demo Mode" in the sidebar
2. Click a demo query button
3. System will use cached results for instant display

To cache new results:
- Run a query normally (without demo mode)
- Results are automatically cached for future demo use

## 🔧 Configuration

### LLM Settings

Edit model configuration in `utils/llm_config.py`:
- `DEFAULT_MODEL` - Default model for all agents
- `ANALYZER_MODEL` - Model for analysis agent
- `INSIGHT_MODEL` - Model for insight generation
- `REPORT_MODEL` - Model for report building

**OpenRouter Model Format:**
- `openai/gpt-4-turbo-preview` - OpenAI GPT-4 Turbo
- `anthropic/claude-3-opus` - Anthropic Claude 3 Opus
- `google/gemini-pro` - Google Gemini Pro
- `meta-llama/llama-2-70b-chat` - Meta Llama 2
- See https://openrouter.ai/models for full list

### API Keys

Required:
- `OPEN_ROUTER_KEY` - OpenRouter API key (get from https://openrouter.ai/keys)
- `TAVILY_API_KEY` - Tavily Search API key (get from https://tavily.com/)

Optional:
- `NEWS_API_KEY` - Enhanced news search (if not using Tavily)

## 📝 Usage Example

1. Enter a research query: "Latest developments in quantum computing 2024"
2. Click "Start Research"
3. Watch agents work sequentially:
   - Retriever searches multiple sources
   - Analyzer processes findings
   - Insight Generator creates hypotheses
   - Report Builder compiles final report
4. View results in tabs: Report, Sources, Analysis, Insights
5. Download report as markdown file

## 🐛 Troubleshooting

### API Key Issues
- Ensure `.env` file exists with `OPEN_ROUTER_KEY`
- Get your key from https://openrouter.ai/keys
- Check API key is valid and has credits
- Verify model name format (e.g., `openai/gpt-4-turbo-preview`)

### Search Failures
- DuckDuckGo search may be rate-limited
- ArXiv API is free but may have delays
- System will continue with available sources

### LLM Errors
- Check API rate limits
- Verify model name is correct
- System falls back to template-based reports if LLM fails

## 🎨 Customization

### Add New Agents

1. Create new agent file in `agents/`
2. Implement agent class with required methods
3. Add node to workflow in `orchestration/coordinator.py`
4. Update UI in `app.py` to display results

### Modify Workflow

Edit `orchestration/coordinator.py` to:
- Add conditional routing
- Implement parallel agent execution
- Add error recovery logic

## 📊 Demo Queries

Pre-configured demo queries:
- "Latest developments in quantum computing 2024"
- "Current state of AI safety research and regulations"
- "Emerging climate technology solutions 2024"

## 🏆 Hackathon Notes

This MVP demonstrates:
- ✅ Multi-agent collaboration
- ✅ LangGraph orchestration
- ✅ RAG (Retrieval-Augmented Generation)
- ✅ Long-context synthesis
- ✅ Professional UI/UX

Built in ~10-12 hours following optimized hackathon timeline.

## 📄 License

MIT License - Hackathon Project

## 🙏 Acknowledgments

- LangChain/LangGraph team for excellent frameworks
- Streamlit for rapid UI development
- OpenAI for LLM APIs

---

**Built for Hackathon Demo** | Multi-Agent AI Deep Researcher

