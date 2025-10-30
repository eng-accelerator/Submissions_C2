@echo off
REM Streamlit Chatbot Launcher Script for Windows

echo 🚀 Starting Streamlit Chatbot Assistant...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo 📦 Streamlit not found. Installing dependencies...
    pip install -r requirements.txt
) else (
    echo ✅ Streamlit is installed
)

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🌐 Launching application...
echo 📝 Press Ctrl+C to stop the server
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REM Run Streamlit app
streamlit run app.py

