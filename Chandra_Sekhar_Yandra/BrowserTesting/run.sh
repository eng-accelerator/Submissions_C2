#!/bin/bash

# Browser Automation AI Agent - Startup Script

echo "🧠 Browser Automation AI Agent"
echo "================================"
echo ""

# Check if OPENROUTER_API_KEY is set
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "⚠️  WARNING: OPENROUTER_API_KEY is not set"
    echo "   The AI agents will not work without this key."
    echo "   Set it in a .env file or export it:"
    echo "   export OPENROUTER_API_KEY='your_key_here'"
    echo ""
fi

# Load .env file if it exists
if [ -f .env ]; then
    echo "✓ Loading environment variables from .env file"
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "✓ Starting Streamlit application..."
echo ""
echo "The application will be available at:"
echo "  - Local: http://localhost:8501"
echo "  - Network: http://$(hostname -I | awk '{print $1}'):8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run main.py --server.port 8501 --server.headless true
