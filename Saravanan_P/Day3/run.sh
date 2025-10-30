#!/bin/bash

# Streamlit Chatbot Launcher Script

echo "🚀 Starting Streamlit Chatbot Assistant..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if Streamlit is installed
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "📦 Streamlit not found. Installing dependencies..."
    pip3 install -r requirements.txt
else
    echo "✅ Streamlit is installed"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Launching application..."
echo "📝 Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Run Streamlit app
streamlit run app.py

