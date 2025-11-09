# 🏦 AI Financial Coach

Your Personal Money Advisor with AI-Powered Multi-Agent Analysis

## 🌟 Features

### 1. Transaction Analysis Dashboard
- Upload bank statements (CSV, Excel, PDF)
- Automatic column detection (NO LLM needed)
- Financial health scoring
- Spending breakdown by category
- Month-over-month trends

### 2. Financial Knowledge Base
- Upload tax documents, insurance policies, loan agreements
- Autonomous AI crawler for financial information
- Semantic search across documents
- Region-specific knowledge (India, USA, UK, etc.)

### 3. Multi-Agent Financial Planner
- **Analysis Agent**: Examines your transaction data
- **Planning Agent**: Creates personalized financial strategies
- **Advisory Agent**: Provides expert recommendations
- Natural language conversation interface

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key
- (Optional) Tavily API key for web search

### Installation

1. **Clone/Extract the project**
```bash
cd ai_financial_coach
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up API keys**

Create `.streamlit/secrets.toml`:
```toml
openai_api_key = "your-openai-api-key"
tavily_api_key = "your-tavily-api-key"  # Optional
```

Or set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export TAVILY_API_KEY="your-tavily-api-key"  # Optional
```

4. **Run the application**
```bash
streamlit run app.py
```

5. **Access the app**
Open your browser to `http://localhost:8501`

## 📁 Project Structure

```
ai_financial_coach/
├── app.py                      # Main dashboard
├── pages/
│   ├── 1_📚_Knowledge_Base.py # Knowledge management
│   └── 2_🤖_AI_Financial_Planner.py # Multi-agent planner
├── core/
│   ├── transaction_parser.py  # CSV/Excel parser (NO LLM)
│   ├── transaction_store.py   # SQLite/PostgreSQL wrapper
│   ├── knowledge_store.py     # Vector DB for knowledge
│   ├── knowledge_crawler.py   # Autonomous crawler
│   └── financial_planner_agent.py # Multi-agent system
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 💡 Usage Guide

### 1. Upload Bank Statements
1. Sign up / Sign in
2. Use sidebar to upload CSV/Excel files
3. Click "Process & Store"
4. View dashboard with financial metrics

### 2. Build Knowledge Base
1. Go to "Knowledge Base" page
2. **Option A**: Manually upload PDFs
3. **Option B**: Use AI Crawler (select region & categories)
4. Wait for processing

### 3. Ask AI Financial Planner
1. Go to "AI Financial Planner" page
2. Ask questions like:
   - "Analyze my spending patterns"
   - "Should I prepay my loan or invest?"
   - "Create a retirement plan for me"
3. Get personalized advice based on your data

## 🎯 Key Features Explained

### Intelligent Column Detection
- **NO LLM required** for parsing bank statements
- Automatic detection of date, amount, type, balance columns
- Supports multiple bank formats (HDFC, ICICI, SBI, etc.)
- Handles DrCr indicators, separate debit/credit columns

### Dual-Track Architecture
- **Track 1**: Transaction data → PostgreSQL/SQLite (structured)
- **Track 2**: Knowledge docs → Vector DB (unstructured)
- Optimized for speed and accuracy

### Multi-Agent System
```
User Query
    ↓
Analysis Agent → Examines transaction data
    ↓
Knowledge Agent → Searches relevant docs
    ↓
Planning Agent → Generates personalized advice
    ↓
Response to User
```

## 🔧 Configuration

### Database
Default: SQLite (for demo)
```python
# config.py
DATABASE_CONFIG = {
    'connection_string': 'sqlite:///./financial_data.db'
}
```

For production, use PostgreSQL:
```python
DATABASE_CONFIG = {
    'connection_string': 'postgresql://user:pass@localhost:5432/financedb'
}
```

### API Keys
Set in `.streamlit/secrets.toml` or environment variables:
- `OPENAI_API_KEY` (required)
- `TAVILY_API_KEY` (optional, for web crawler)

## 📊 Database Schema

### Users Table
- user_id, username, email, country, currency

### Transactions Table
- transaction_id, user_id, date, amount, type, balance
- description, category, mode, reference

### Indexes
- user_id + date (for fast queries)
- user_id + type
- user_id + category

## 🤖 AI Components

### Column Detection (NO LLM)
- Regex-based pattern matching
- Data type validation
- Heuristic scoring
- 95%+ accuracy on common formats

### Knowledge Crawler
- Autonomous web search
- Content extraction
- Vectorization
- Region-specific information

### Multi-Agent Planner
- LangChain-based orchestration
- GPT-4o-mini for reasoning
- Context-aware responses
- Actionable recommendations

## 🚧 Roadmap

- [ ] Advanced budget tracking
- [ ] Goal setting and tracking
- [ ] Bill payment reminders
- [ ] Investment portfolio analysis
- [ ] Tax filing assistance
- [ ] Multi-currency support
- [ ] Mobile app

## 📝 Example Bank Statement Format

```csv
date,DrCr,amount,balance,mode,description
01-01-2024,Dr,10000,90000,ATM,ATM Withdrawal
02-01-2024,Cr,50000,140000,SALARY,Salary Credit
03-01-2024,Dr,500,139500,UPI,UPI/SWIGGY
```

The parser automatically detects:
- `date` → Transaction date
- `DrCr` → Debit/Credit indicator
- `amount` → Transaction amount
- `balance` → Account balance
- `mode` → Payment mode
- `description` → Transaction details

## 🔐 Security Notes

- Passwords are hashed (SHA-256)
- User data is isolated
- No external data sharing (except OpenAI API for embeddings)
- Use environment variables for API keys
- For production: Use PostgreSQL with proper authentication

## 🐛 Troubleshooting

### "No module named 'langchain'"
```bash
pip install langchain langchain-community langchain-openai
```

### "Database connection error"
Check `config.py` and ensure database path is correct

### "OpenAI API error"
Verify your API key in `.streamlit/secrets.toml`

### "Crawler not working"
Ensure TAVILY_API_KEY is set (or use manual upload)

## 📄 License

MIT License - Feel free to use and modify

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Email: support@example.com

## 🎉 Credits

Built with:
- Streamlit
- LangChain
- OpenAI
- FAISS
- Plotly

---

**Made with ❤️ for better financial wellness**
