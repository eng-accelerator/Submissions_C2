# Distribution Guide - Medical MCP Server

## How to Distribute This Code to Your Team

### Option 1: Git Repository (Recommended)

#### 1. Create a Git Repository

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create .gitignore
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".chromadb/" >> .gitignore
echo "*.txt" >> .gitignore
echo "test_*.py" >> .gitignore

# Commit
git commit -m "Initial commit: Medical MCP Server"

# Add remote repository
git remote add origin <your-repo-url>

# Push to repository
git push -u origin main
```

#### 2. Team Members Clone and Setup

```bash
# Clone repository
git clone <your-repo-url>
cd ailearn

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Test installation
python3 test_mcp_server.py
```

### Option 2: Zip Archive Distribution

#### 1. Create Distribution Package

```bash
# Create distribution directory
mkdir medical-mcp-server-dist
cd medical-mcp-server-dist

# Copy essential files
cp ../locationservice.py .
cp ../requirements.txt .
cp ../README.md .
cp ../MCP_SERVER_SETUP.md .
cp ../mcp_config_example.json .

# Create .env.example
cat > .env.example << EOF
OPENAI_API_KEY=your-openai-api-key-here
PERPLEXITY_API_KEY=your-perplexity-api-key-here
EOF

# Create setup script
cat > setup.sh << 'EOF'
#!/bin/bash
echo "Setting up Medical MCP Server..."
pip install -r requirements.txt
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please add your API keys."
fi
echo "Setup complete!"
EOF

chmod +x setup.sh

# Create zip archive
cd ..
zip -r medical-mcp-server.zip medical-mcp-server-dist/
```

#### 2. Team Members Extract and Setup

```bash
# Extract archive
unzip medical-mcp-server.zip
cd medical-mcp-server-dist

# Run setup script
./setup.sh

# Edit .env with API keys
nano .env

# Test installation
python3 -c "from locationservice import openai_client, perplexity_client; print('OpenAI:', '✅' if openai_client else '❌'); print('Perplexity:', '✅' if perplexity_client else '❌')"
```

### Option 3: Package as Python Package

#### 1. Create Package Structure

```bash
mkdir medical_mcp_server
cd medical_mcp_server

# Create package structure
mkdir -p medical_mcp_server
cp ../locationservice.py medical_mcp_server/__init__.py
cp ../requirements.txt .
cp ../README.md .

# Create setup.py
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="medical-mcp-server",
    version="1.0.0",
    description="Medical Service Provider Finder MCP Server",
    author="Your Team",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.21.0",
        "duckduckgo-search>=8.1.1",
        "geopy>=2.4.1",
        "openai>=2.7.1",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "medical-mcp-server=medical_mcp_server:main",
        ],
    },
)
EOF
```

#### 2. Build and Distribute

```bash
# Build package
python3 setup.py sdist bdist_wheel

# Distribute dist/medical_mcp_server-1.0.0.tar.gz
```

#### 3. Team Members Install

```bash
# Install from package
pip install medical_mcp_server-1.0.0.tar.gz

# Or install from git
pip install git+https://github.com/your-org/medical-mcp-server.git
```

## Essential Files for Distribution

### Required Files

1. **locationservice.py** - Main MCP server code
2. **requirements.txt** - Python dependencies
3. **README.md** - Setup and usage instructions
4. **.env.example** - Environment variable template

### Optional Files (Recommended)

1. **MCP_SERVER_SETUP.md** - Detailed setup guide
2. **mcp_config_example.json** - MCP client configuration example
3. **test_mcp_server.py** - Test script
4. **DISTRIBUTION_GUIDE.md** - This file

### Files to Exclude

- `.env` - Contains sensitive API keys (never commit!)
- `__pycache__/` - Python cache files
- `*.pyc` - Compiled Python files
- Test output files
- Personal configuration files

## Team Setup Checklist

### For Each Team Member

- [ ] Clone/download the code
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` file with API keys
- [ ] Test installation: `python3 test_mcp_server.py`
- [ ] Configure MCP client (if using)
- [ ] Verify Perplexity API access

## Integration with Main Codebase

### Option 1: Standalone MCP Server

Run as separate service:

```bash
python3 locationservice.py
```

Connect via MCP protocol from your main application.

### Option 2: Import as Module

```python
# In your main code
from locationservice import (
    search_medical_providers,
    search_with_progressive_radius,
    recommend_provider
)

# Use the functions directly
providers = search_medical_providers(
    patient_address="123 Main St, Denver, CO",
    service_type="Cardiology",
    num_results=10
)
```

### Option 3: API Wrapper

Create a REST API wrapper:

```python
from flask import Flask, request, jsonify
from locationservice import search_with_progressive_radius, geocode_address, recommend_provider

app = Flask(__name__)

@app.route('/api/find-providers', methods=['POST'])
def find_providers():
    data = request.json
    # Use MCP server functions
    # Return JSON response
    pass
```

## Environment Variables Setup

### Required

- `OPENAI_API_KEY` - For parsing search results
- `PERPLEXITY_API_KEY` - For primary search (recommended)

### Optional

- `GEOCODING_SERVICE` - Alternative geocoding service
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

## Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Solution: Create `.env` file with API keys

2. **Import Errors**
   - Solution: Install dependencies: `pip install -r requirements.txt`

3. **Perplexity API Errors**
   - Solution: Verify API key is correct and has credits

4. **Geocoding Failures**
   - Solution: Check internet connection and Nominatim service status

## Support

For questions or issues:
1. Check [MCP_SERVER_SETUP.md](MCP_SERVER_SETUP.md)
2. Review [TESTING_GUIDE.md](TESTING_GUIDE.md)
3. Check logs for error messages
4. Contact the team lead

## Version History

- **v1.0.0** - Initial release with Perplexity API integration

