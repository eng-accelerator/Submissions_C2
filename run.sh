#!/bin/bash
# Launch script for Multi-Agent DevOps Incident Suite

echo "🚨 Multi-Agent DevOps Incident Analysis Suite"
echo "=============================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating .env from example..."
    cp env.example .env
    echo ""
    echo "⚙️  Please edit .env and add your OpenAI API key:"
    echo "   nano .env"
    echo ""
    read -p "Press Enter to continue after adding your API key..."
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if dependencies are installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Create necessary directories
mkdir -p uploaded_logs
mkdir -p knowledge_base
mkdir -p vector_stores
mkdir -p cookbooks

echo ""
echo "🚀 Launching application..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 The app will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Launch Streamlit
streamlit run app.py --server.port 8501 --server.headless false

