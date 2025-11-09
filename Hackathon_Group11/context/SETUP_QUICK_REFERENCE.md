# Setup Quick Reference Card

## 🚀 Complete Setup (Copy-Paste)

### Windows (Command Prompt)

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
copy env.example .env

# 6. Edit .env and add your OPEN_ROUTER_KEY
# (Open .env in notepad or your editor)

# 7. Test installation
python test_system.py

# 8. Run application
streamlit run app.py
```

### Windows (PowerShell)

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\Activate.ps1
# If you get execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
Copy-Item env.example .env

# 6. Edit .env and add your OPEN_ROUTER_KEY
# (Open .env in notepad or your editor)

# 7. Test installation
python test_system.py

# 8. Run application
streamlit run app.py
```

### macOS/Linux

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
cp env.example .env

# 6. Edit .env and add your OPEN_ROUTER_KEY
nano .env
# or
vim .env

# 7. Test installation
python test_system.py

# 8. Run application
streamlit run app.py
```

---

## ✅ Verification Checklist

- [ ] Virtual environment created (`venv/` folder exists)
- [ ] Virtual environment activated (see `(venv)` in prompt)
- [ ] Dependencies installed (`pip list` shows packages)
- [ ] `.env` file created with `OPEN_ROUTER_KEY`
- [ ] Test script passes (`python test_system.py`)
- [ ] Application runs (`streamlit run app.py`)

---

## 🔧 Common Commands

### Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Deactivate Virtual Environment
```bash
deactivate
```

### Check if Virtual Environment is Active
Look for `(venv)` at the start of your command prompt.

### Install/Update Dependencies
```bash
pip install -r requirements.txt
```

### Check Installed Packages
```bash
pip list
```

### Test System
```bash
python test_system.py
```

### Run Application
```bash
streamlit run app.py
```

---

## 🐛 Quick Troubleshooting

**Virtual environment not activating?**
- Windows PowerShell: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Check Python is installed: `python --version`

**Module not found?**
- Verify venv is activated: `(venv)` should be in prompt
- Reinstall: `pip install -r requirements.txt`

**API key not working?**
- Check `.env` file exists
- Verify key format: `OPEN_ROUTER_KEY=sk-or-...`
- Get key from: https://openrouter.ai/keys

---

**For detailed instructions, see `VIRTUAL_ENV_SETUP.md`**

