#!/bin/bash
# setup.sh - Setup script for AI Financial Coach

echo "🏦 AI Financial Coach - Setup Script"
echo "===================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip
echo "✓ pip upgraded"
echo ""

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .streamlit directory
echo "🔧 Setting up Streamlit configuration..."
mkdir -p .streamlit

# Copy secrets template if not exists
if [ ! -f .streamlit/secrets.toml ]; then
    cp .streamlit/secrets.toml.example .streamlit/secrets.toml
    echo "✓ Created .streamlit/secrets.toml from template"
    echo "⚠️  IMPORTANT: Edit .streamlit/secrets.toml and add your API keys!"
else
    echo "✓ .streamlit/secrets.toml already exists"
fi
echo ""

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p knowledge_db
mkdir -p uploads
echo "✓ Directories created"
echo ""

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .streamlit/secrets.toml and add your OpenAI API key"
echo "2. (Optional) Add Tavily API key for knowledge crawler"
echo "3. Run: streamlit run app.py"
echo ""
echo "🚀 To start the app:"
echo "   streamlit run app.py"
echo ""
