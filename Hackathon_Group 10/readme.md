# 🤖 AI Financial Coach - Multi-Agent Financial Advisory System

> Your Personal Money Advisor with AI-Powered Analysis

A production-ready financial management platform powered by multiple AI agents working together to provide comprehensive financial insights, investment recommendations, and personalized advice.

---

## Loom Video
https://www.loom.com/share/22bdae5741a84e519f5cdae58064ef2e

## 🌟 Key Features

### Core Capabilities
- **📊 Real-time Financial Dashboard** - Track income, expenses, savings, and financial health score
- **💬 AI Financial Advisor** - Natural language queries with context-aware responses
- **📈 Spending Analysis** - Automatic categorization and visual breakdown of expenses
- **🎯 Goal Planning** - Create and track financial goals with investment strategies
- **💰 Investment Recommendations** - Personalized investment options based on risk profile and timeline
- **📥 Comprehensive Reports** - Generate detailed Excel reports with charts and insights
- **📚 Knowledge Base** - Curated financial information with web search fallback
- **👤 Guest Mode** - Try the app without signup, with optional account creation

---

## 🤖 Multi-Agent Architecture

### 1. **Query Understanding Agent**
**Purpose:** Analyzes user queries to extract intent and context

**Capabilities:**
- Detects time periods (last month, Q1 2024, etc.)
- Identifies query type (spending analysis, investment advice, tax optimization)
- Determines if knowledge base search or web search is needed
- Extracts topics for targeted information retrieval

**Example:**
```
User: "Analyze my spending patterns for last 3 months"
→ Extracts: time_period="3 months", intent="spending_analysis", needs_visualization=true
```

---

### 2. **Data Retrieval Agent**
**Purpose:** Fetches relevant financial data from database

**Capabilities:**
- SQL query generation based on time periods
- Aggregates transactions by category, month, or quarter
- Calculates financial metrics (income, expenses, savings rate)
- Retrieves specific date ranges or latest data

**Data Sources:**
- SQLite database with user transactions
- Supports CSV, Excel, PDF bank statements
- Smart parsing with automatic column detection

---

### 3. **Knowledge Agent**
**Purpose:** Searches for financial information to enhance responses

**Capabilities:**
- **Primary:** Vector database search (FAISS) for curated knowledge
- **Fallback:** Tavily web search for real-time information
- Semantic search for tax laws, investment strategies, insurance info
- Region-specific knowledge (India, USA, UK, etc.)

**Knowledge Categories:**
- Tax regulations and deductions
- Investment strategies and options
- Insurance policies and recommendations
- Loan and debt management
- Financial planning best practices

---

### 4. **Visualization Agent**
**Purpose:** Generates interactive charts and graphs

**Capabilities:**
- Trend analysis (line charts for income/expenses over time)
- Category breakdown (pie charts and horizontal bar charts)
- Savings rate tracking (bar charts)
- Dynamic chart generation based on query type

**Chart Types:**
- Line charts for time-series data
- Pie charts for category distribution
- Bar charts for comparisons and rankings

---

### 5. **Analysis Agent**
**Purpose:** Synthesizes data and generates insights

**Capabilities:**
- Combines user data with knowledge base information
- Generates personalized recommendations
- Provides actionable financial advice
- Cites sources (knowledge base or web search)
- Context-aware responses based on user's financial situation

**Example Output:**
```
"Based on your October 2023 data showing ₹58,293 in savings (50% rate), 
you're in an excellent position to optimize taxes. According to Section 80C, 
you can invest up to ₹1.5 lakh in tax-saving instruments..."
```

---

### 6. **Investment Options Agent**
**Purpose:** Recommends investment vehicles based on goals

**Capabilities:**
- Time horizon analysis (emergency, short-term, medium-term, long-term)
- Risk-based asset allocation (conservative, balanced, aggressive)
- India-specific investment options (PPF, ELSS, NPS, Mutual Funds, etc.)
- Expected returns calculation with compounding
- Liquidity and lock-in period analysis
- Tax benefit identification

**Investment Vehicles Supported:**
- High Yield Savings Accounts
- Liquid & Short-term Debt Funds
- Fixed Deposits & PPF
- Equity Mutual Funds & Index Funds
- ELSS (Tax-saving funds)
- NPS (National Pension System)
- Corporate Bonds & NCDs

---

### 7. **Custom Savings Strategy Agent**
**Purpose:** Creates comprehensive savings and goal allocation plans

**Capabilities:**
- Multi-goal prioritization and allocation
- Emergency fund calculation (3-6 months expenses)
- Monthly contribution optimization
- ETA calculation with compounding returns
- Due date feasibility analysis
- Budget and debt handoff coordination

**Features:**
- Goal upsert with priority management
- Time-to-achieve calculations
- Funding gap identification
- Leftover allocation suggestions

---

### 8. **Report Generation Agent**
**Purpose:** Creates comprehensive Excel reports

**Capabilities:**
- Multi-sheet Excel workbooks with professional formatting
- Embedded charts (pie, bar, line)
- Executive summary with key insights
- Category breakdown analysis
- Monthly trend analysis
- Tax optimization recommendations
- Goals tracking with progress indicators
- Investment strategy documentation

**Report Sections:**
1. Executive Summary
2. Category Breakdown (with pie chart)
3. Trend Analysis (with line chart)
4. Tax Optimization
5. Goals Tracker
6. Investment Options
7. Personalized Recommendations

---

## 🛠️ Technical Stack

### Core Technologies
- **Framework:** Streamlit (Python web framework)
- **AI/ML:** LangChain, OpenAI GPT-4o-mini
- **Database:** SQLite (easily upgradable to PostgreSQL)
- **Vector DB:** FAISS (Facebook AI Similarity Search)
- **Embeddings:** OpenAI text-embedding-3-small

### Key Libraries
```python
langchain-openai          # LLM orchestration
langchain-community       # Tools and utilities
faiss-cpu                 # Vector search
streamlit                 # Web interface
pandas                    # Data manipulation
plotly                    # Interactive charts
openpyxl                  # Excel generation
pydantic                  # Data validation
tavily-python             # Web search fallback
```

### Architecture Patterns
- **Multi-agent coordination** - Agents work together in sequence
- **Stateless design** - Each agent is independent and reusable
- **Vector search** - Semantic similarity for knowledge retrieval
- **Streaming responses** - Real-time agent reasoning display
- **Session management** - Streamlit session state for data persistence

---

## 📊 Data Flow
```
User Query
    ↓
Query Understanding Agent → Extract intent, time, topics
    ↓
Data Retrieval Agent → Fetch transactions, calculate metrics
    ↓
Knowledge Agent → Search knowledge base OR web (fallback)
    ↓
Visualization Agent → Generate charts (if needed)
    ↓
Analysis Agent → Synthesize insights + recommendations
    ↓
Response to User (with citations and visualizations)
```

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.9+
pip install -r requirements.txt
```

### Environment Variables
Create `.streamlit/secrets.toml`:
```toml
openai_api_key = "your-openai-key"
openai_base_url = "https://openrouter.ai/api/v1"  # Optional
tavily_api_key = "your-tavily-key"  # For web search fallback
```

### Run Application
```bash
streamlit run app.py
```

### Upload Data
1. Use sidebar to upload bank statements (CSV, Excel, PDF)
2. System automatically parses and categorizes transactions
3. Start chatting with AI Financial Coach

---

## 🔧 Configuration

### Guest Mode (Default)
```python
GUEST_MODE_ENABLED = True  # Allow users to try without signup
CLEAR_GUEST_DATA_ON_STARTUP = True  # Fresh start each session
```

### Database
```python
# SQLite (default)
connection_string = "sqlite:///./financial_data.db"

# PostgreSQL (production)
connection_string = "postgresql://user:pass@localhost:5432/dbname"
```

---

## 📁 Project Structure
```
ai_financial_coach/
├── app.py                              # Main dashboard
├── core/
│   ├── financial_planner_agent.py      # Main multi-agent orchestrator
│   ├── investment_options_agent.py     # Investment recommendations
│   ├── custom_savings_strategy_agent.py # Goal planning & allocation
│   ├── knowledge_store.py              # Vector DB for knowledge
│   ├── transaction_store.py            # SQL database wrapper
│   ├── transaction_parser.py           # Smart CSV/Excel/PDF parser
│   ├── visualization_builder.py        # Chart generation
│   └── report_generator.py             # Excel report creation
├── pages/
│   ├── AI_Financial_Planner.py         # Chat interface
│   ├── Create_Goal.py                  # Goal creation with investments
│   └── Knowledge_Base.py               # Knowledge management
└── requirements.txt
```

---

## 🎯 Use Cases

### 1. Spending Analysis
```
"Analyze my spending patterns"
→ Shows trends, categories, insights with charts
```

### 2. Tax Optimization
```
"How can I save tax?"
→ Searches knowledge base + web for Section 80C, 80D, etc.
```

### 3. Goal Planning
```
Create New Goal → Car Purchase (₹8L in 2 years)
→ Recommends investment mix, calculates SIP amount
```

### 4. Investment Advice
```
"Best investment options for me"
→ Analyzes risk profile, timeline, suggests vehicles
```

### 5. Financial Reports
```
Download Report → Generates Excel with all insights
```

---

## 🔒 Security & Privacy

- **Guest Mode:** Temporary data, cleared on app restart
- **User Accounts:** Optional signup with hashed passwords
- **Data Isolation:** Each user has separate database records
- **No Data Sharing:** All processing happens locally
- **Session Security:** Streamlit session management

---

## 🚦 Limitations

- Emergency fund calculation assumes 3-6 months of expenses
- Investment returns are estimates, not guarantees
- Tax information is general guidance, not professional advice
- Web search limited by Tavily API rate limits
- SQLite suitable for demo; use PostgreSQL for production

---

## 🔮 Future Enhancements

- [ ] Goal tracking with automatic rebalancing
- [ ] Budget management and alerts
- [ ] Receipt OCR and automatic categorization
- [ ] Multi-currency support
- [ ] Expense prediction using ML
- [ ] Integration with bank APIs
- [ ] Mobile app (React Native)
- [ ] Real-time portfolio tracking

---

## 📄 License

MIT License - Free for personal and commercial use

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

---

## 📧 Support

For issues, questions, or suggestions:
- Open a GitHub issue
- Email: support@aifinancialcoach.com

---

**⚠️ Disclaimer:** This tool provides general financial information and estimates only. It does not constitute professional financial, investment, or tax advice. Always consult with qualified financial advisors before making investment decisions.

---

Contributors ❤️
Vibha T S (visa2023@gmail.com)
Pawel Labuz (Labuz.Courses@gmail.com)
Rahul Sharma (rahulsharma91a@gmail.com)
Sunil Garg (grag.linus@gmail)
Prerna

