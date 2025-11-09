# Virtual Environment Setup Guide

## Step-by-Step Setup Instructions

### Step 1: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
```

**macOS/Linux:**
```bash
python3 -m venv venv
```

This creates a `venv` folder in your project directory.

---

### Step 2: Activate Virtual Environment

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Verify activation:**
You should see `(venv)` at the beginning of your command prompt:
```
(venv) C:\Users\gengi\OneDrive\Desktop\hackathon>
```

---

### Step 3: Upgrade pip (Recommended)

```bash
python -m pip install --upgrade pip
```

---

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- langchain
- langchain-core
- langchain-openai
- langchain-community
- langgraph
- streamlit
- And other dependencies

**Expected output:**
```
Collecting langchain>=0.1.0
Collecting langchain-core>=0.1.0
...
Successfully installed ...
```

---

### Step 5: Configure Environment Variables

**5.1. Create `.env` file:**

**Windows:**
```bash
copy env.example .env
```

**macOS/Linux:**
```bash
cp env.example .env
```

**5.2. Edit `.env` file:**

Open `.env` in a text editor and add your OpenRouter API key:

```env
OPEN_ROUTER_KEY=sk-or-your-key-here
```

**Get your key from:** https://openrouter.ai/keys

---

### Step 6: Verify Installation

Run the test script:

```bash
python test_system.py
```

**Expected output:**
```
🧪 Testing Multi-Agent AI Deep Researcher System

==================================================
Testing imports...
✅ All imports successful

Testing agent initialization...
✅ All agents initialized successfully

Testing workflow initialization...
✅ Workflow initialized successfully

Checking API key...
✅ OpenRouter API key configured
   Using OpenRouter endpoint: https://openrouter.ai/api/v1

==================================================

Test Results:
  Imports: ✅ PASS
  Agents: ✅ PASS
  Workflow: ✅ PASS
  API Key: ✅ PASS

✅ All tests passed! System is ready.
```

---

### Step 7: Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## Deactivating Virtual Environment

When you're done working, deactivate the virtual environment:

```bash
deactivate
```

The `(venv)` prefix will disappear from your prompt.

---

## Troubleshooting

### Virtual Environment Not Activating (Windows PowerShell)

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again:
```powershell
venv\Scripts\Activate.ps1
```

### Python Not Found

**Windows:**
- Make sure Python is installed and added to PATH
- Try `py` instead of `python`:
  ```bash
  py -m venv venv
  ```

**macOS/Linux:**
- Use `python3` instead of `python`:
  ```bash
  python3 -m venv venv
  ```

### pip Install Fails

1. **Upgrade pip first:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Install packages individually if needed:**
   ```bash
   pip install langchain
   pip install langchain-core
   pip install langchain-openai
   ```

3. **Check Python version:**
   ```bash
   python --version
   ```
   Should be Python 3.8 or higher.

### Module Not Found After Installation

1. **Verify virtual environment is activated** (should see `(venv)` in prompt)
2. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

### Import Errors

If you see `ModuleNotFoundError`:
- Make sure virtual environment is activated
- Reinstall: `pip install -r requirements.txt`
- Check that `langchain-core` is installed: `pip list | findstr langchain`

---

## Quick Reference

### Complete Setup (Copy-Paste)

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy env.example .env
# Edit .env and add your OPEN_ROUTER_KEY

# Test
python test_system.py

# Run app
streamlit run app.py
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp env.example .env
# Edit .env and add your OPEN_ROUTER_KEY

# Test
python test_system.py

# Run app
streamlit run app.py
```

---

## Next Steps

After setup is complete:
1. ✅ Virtual environment activated
2. ✅ Dependencies installed
3. ✅ API key configured
4. ✅ System tested
5. 🚀 Ready to run: `streamlit run app.py`

---

**Need Help?** Check the main `README.md` or `QUICK_START.md` for more details.

