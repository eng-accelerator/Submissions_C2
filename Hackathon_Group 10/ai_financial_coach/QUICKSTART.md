# 🚀 Quick Start Guide

Get up and running in 5 minutes!

## 1. Extract the Project
```bash
unzip ai_financial_coach.zip
cd ai_financial_coach
```

## 2. Install Dependencies

### Option A: Using setup script (Linux/Mac)
```bash
chmod +x setup.sh
./setup.sh
```

### Option B: Manual installation
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

## 3. Configure API Keys

Edit `.streamlit/secrets.toml`:
```toml
openai_api_key = "sk-YOUR-KEY-HERE"
tavily_api_key = "tvly-YOUR-KEY-HERE"  # Optional
```

Get API keys:
- OpenAI: https://platform.openai.com/api-keys
- Tavily (optional): https://tavily.com

## 4. Run the App
```bash
streamlit run app.py
```

Open browser to: http://localhost:8501

## 5. First Steps

1. **Sign Up**: Create an account
2. **Upload Bank Statement**: Use sidebar to upload CSV/Excel
3. **View Dashboard**: See your financial overview
4. **Build Knowledge Base**: Go to Knowledge Base page
5. **Ask AI**: Go to AI Financial Planner page

## 📊 Example Bank Statement Format

Your CSV should look like this:
```csv
date,DrCr,amount,balance,description
01-01-2024,Dr,10000,90000,ATM Withdrawal
02-01-2024,Cr,50000,140000,Salary Credit
```

The parser automatically detects columns!

## ❓ Common Issues

### "No module named 'streamlit'"
```bash
pip install streamlit
```

### "OpenAI API key not found"
Edit `.streamlit/secrets.toml` and add your key

### "Database error"
The app uses SQLite by default (no setup needed)

## 🎯 What to Try

1. Upload a bank statement
2. Ask AI: "Analyze my spending patterns"
3. Ask AI: "How can I save money?"
4. Upload knowledge docs (tax PDFs, etc.)
5. Ask AI: "Should I prepay my loan?"

## 📚 Full Documentation

See `README.md` for complete documentation

## 🆘 Need Help?

Check the troubleshooting section in README.md

---

**That's it! You're ready to go! 🎉**
