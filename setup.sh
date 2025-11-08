#!/bin/bash

# Medical MCP Server Setup Script
# Run this script to set up the environment

echo "=========================================="
echo "Medical MCP Server Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - PERPLEXITY_API_KEY"
else
    echo ""
    echo "✅ .env file already exists"
fi

# Verify installation
echo ""
echo "Verifying installation..."
python3 << 'EOF'
import sys
required = ['mcp', 'duckduckgo_search', 'geopy', 'openai', 'dotenv']
missing = []
for pkg in required:
    try:
        __import__(pkg)
        print(f"✅ {pkg}")
    except ImportError:
        print(f"❌ {pkg} - NOT INSTALLED")
        missing.append(pkg)

if missing:
    print(f"\n❌ Missing packages: {', '.join(missing)}")
    sys.exit(1)
else:
    print("\n✅ All dependencies installed!")
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your API keys"
    echo "2. Test the server: python3 test_mcp_server.py"
    echo "3. Run the server: python3 locationservice.py"
else
    echo ""
    echo "=========================================="
    echo "Setup Failed!"
    echo "=========================================="
    echo "Please check the errors above and try again."
    exit 1
fi

