# 🛠️ Setup Guide

> **Complete Installation Instructions** for Text Summarization MVP
> Beginner-friendly guide for all platforms

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Platform-Specific Guides](#platform-specific-guides)
4. [HuggingFace Token Setup](#huggingface-token-setup)
5. [First Run](#first-run)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 4GB available
- **Storage**: 3GB free space (for models)
- **Internet**: Required for first run (model downloads)

### Recommended Requirements
- **RAM**: 8GB+ (for faster processing)
- **GPU**: NVIDIA GPU with 4GB+ VRAM (optional, 3-5x speedup)
- **Storage**: SSD for better model loading
- **Internet**: Stable connection (downloads ~500MB-2GB)

### Check Your Python Version
```bash
python --version
# Should show: Python 3.8.x or higher

# If you see Python 2.x, try:
python3 --version
```

---

## 🚀 Installation Methods

### Method 1: **Quick Start** (Google Colab) ⭐ EASIEST

**Best for**: Quick testing, no local setup

1. Open [Google Colab](https://colab.research.google.com/)
2. Upload `text_summarization_mvp_enhanced.ipynb`
3. Click **Runtime → Run All**
4. Wait for public URL to appear (~5 minutes)

**Pros**:
- ✅ No installation required
- ✅ Free GPU access
- ✅ Works from any device

**Cons**:
- ⏰ Session expires after 72 hours
- 🔗 Public link expires in 7 days

---

### Method 2: **Local Jupyter** (Recommended for Development)

**Best for**: Long-term use, offline capability

#### Step 1: Clone Repository
```bash
# Download the project
git clone https://github.com/YOUR_USERNAME/day2-text-summarization-mvp.git
cd day2-text-summarization-mvp
```

#### Step 2: Create Virtual Environment (Recommended)
```bash
# Create isolated environment
python -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# You should see (venv) in your terminal
```

#### Step 3: Install Dependencies
```bash
# Install all packages
pip install -r requirements.txt

# This will take 5-10 minutes
# Downloads ~200MB of packages
```

#### Step 4: Launch Jupyter
```bash
# Start Jupyter Notebook
jupyter notebook

# Browser will open automatically
# Navigate to: text_summarization_mvp_enhanced.ipynb
```

#### Step 5: Run the Notebook
1. Click **Cell → Run All**
2. Wait for models to download (~5 minutes first run)
3. Access at `http://localhost:8888`

---

### Method 3: **Standalone Python Script** (Coming Soon)

For production deployment without Jupyter.

---

## 🖥️ Platform-Specific Guides

### Windows 10/11

#### Install Python
1. Download from [python.org](https://www.python.org/downloads/)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify: Open Command Prompt and type `python --version`

#### Install Git (Optional)
1. Download from [git-scm.com](https://git-scm.com/)
2. Use default settings during installation

#### Install ffmpeg (For Audio Export)
```powershell
# Using Chocolatey (package manager)
choco install ffmpeg

# OR download manually from:
# https://ffmpeg.org/download.html
```

#### Common Issues
- **"python not recognized"**: Restart terminal after installation
- **Permission errors**: Run Command Prompt as Administrator
- **SSL errors**: `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package>`

---

### macOS

#### Install Python
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Verify installation
python3 --version
```

#### Install Git
```bash
# Using Homebrew
brew install git
```

#### Install ffmpeg
```bash
# Using Homebrew
brew install ffmpeg
```

#### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Common Issues
- **"command not found: python"**: Use `python3` instead
- **Permission denied**: Use `sudo` or check file permissions
- **SSL certificate error**: Update certificates via `/Applications/Python 3.x/Install Certificates.command`

---

### Linux (Ubuntu/Debian)

#### Install Python & Dependencies
```bash
# Update package list
sudo apt update

# Install Python 3.8+
sudo apt install python3 python3-pip python3-venv

# Install ffmpeg for audio
sudo apt install ffmpeg

# Install Git
sudo apt install git
```

#### Setup Project
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/day2-text-summarization-mvp.git
cd day2-text-summarization-mvp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Common Issues
- **"No module named 'pip'"**: `sudo apt install python3-pip`
- **"python3-dev required"**: `sudo apt install python3-dev`
- **CUDA errors**: Ensure NVIDIA drivers installed: `nvidia-smi`

---

## 🔑 HuggingFace Token Setup (Optional)

**Required for**:
- Gated models (Llama, Mistral, etc.)
- Private repositories
- Higher API rate limits

**Not required for this project** (we use public models only)

### Get Your Token

1. Go to [HuggingFace Settings](https://huggingface.co/settings/tokens)
2. Click **"New token"**
3. Name: `text-summarization-mvp`
4. Type: **Read**
5. Click **"Generate"**
6. Copy the token (starts with `hf_...`)

### Add to Environment

**Option A: Environment File**
```bash
# Copy template
cp .env.example .env

# Edit .env file
# Add: HF_TOKEN=hf_your_token_here
```

**Option B: System Environment Variable**

**Windows**:
```powershell
setx HF_TOKEN "hf_your_token_here"
# Restart terminal
```

**macOS/Linux**:
```bash
# Add to ~/.bashrc or ~/.zshrc
export HF_TOKEN="hf_your_token_here"

# Apply changes
source ~/.bashrc
```

**Option C: In Notebook** (Not Recommended - Security Risk)
```python
import os
os.environ['HF_TOKEN'] = 'hf_your_token_here'
```

---

## 🎬 First Run

### What Happens on First Launch?

```
1. Dependencies load          [5 seconds]
2. Models download            [3-5 minutes, one-time]
   - t5-small: ~242MB
   - t5-base: ~892MB
   - BART: ~1.6GB
   - Pegasus: ~2.2GB
3. Gradio interface starts    [10 seconds]
4. Public URL generated       [5 seconds]
```

### Step-by-Step First Run

1. **Open Jupyter Notebook**
   ```bash
   jupyter notebook text_summarization_mvp_enhanced.ipynb
   ```

2. **Run Cell 1** (Installation)
   - Installs all packages
   - Takes ~5-10 minutes
   - You'll see progress bars

3. **Run Cell 2** (Import Libraries)
   - Loads dependencies
   - Takes ~10 seconds
   - Shows version information

4. **Run Cells 3-16** (Setup)
   - Initializes components
   - Each takes ~1-2 seconds

5. **Run Cell 25** (Launch Interface)
   - Downloads models (first time only)
   - Creates Gradio interface
   - Displays public URL

6. **Access the App**
   - Click the Gradio URL
   - Try the sample text
   - Test export features

### Verify Installation

```python
# Run this in a notebook cell
import gradio as gr
import transformers
import torch

print(f"Gradio: {gr.__version__}")        # Should be 5.0+
print(f"Transformers: {transformers.__version__}")  # Should be 4.57+
print(f"PyTorch: {torch.__version__}")    # Should be 2.0+
print(f"CUDA: {torch.cuda.is_available()}")  # True if GPU available
```

---

## 🐛 Troubleshooting

### Common Errors & Solutions

#### 1. **"No module named 'gradio'"**

**Problem**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt

# If that fails, install individually:
pip install gradio transformers torch
```

---

#### 2. **"CUDA out of memory"**

**Problem**: GPU doesn't have enough VRAM

**Solution**:
```python
# In Config class, force CPU:
DEVICE = "cpu"  # Instead of auto-detect

# Or use smaller model:
# Use t5-small instead of BART
```

---

#### 3. **"Connection timeout" during model download**

**Problem**: Slow/unstable internet

**Solution**:
```python
# Increase timeout
os.environ['HF_HUB_TIMEOUT'] = '300'  # 5 minutes

# Or download manually:
from huggingface_hub import snapshot_download
snapshot_download("t5-small", cache_dir="./model_cache")
```

---

#### 4. **"Address already in use" (Port conflict)**

**Problem**: Port 7860 is occupied

**Solution**:
```python
# Change port in launch command:
interface.launch(server_port=7861, share=True)

# Or find which process is using it:
# Windows: netstat -ano | findstr :7860
# macOS/Linux: lsof -i :7860
```

---

#### 5. **"ImportError: cannot import name 'Audio'"**

**Problem**: Gradio version mismatch

**Solution**:
```bash
pip install --upgrade gradio
# Restart Jupyter kernel
```

---

#### 6. **"ffmpeg not found" (Audio export fails)**

**Problem**: ffmpeg not installed

**Solution**:
```bash
# Windows (with Chocolatey):
choco install ffmpeg

# macOS:
brew install ffmpeg

# Linux:
sudo apt install ffmpeg

# Verify:
ffmpeg -version
```

---

#### 7. **"Permission denied" when writing exports**

**Problem**: No write access to export directory

**Solution**:
```bash
# Create directory with proper permissions
mkdir -p exports
chmod 755 exports

# Or change export directory in Config:
EXPORT_DIR = "/tmp/exports"  # Use temp directory
```

---

### Getting Help

If you encounter issues not listed here:

1. **Check Logs**: Look for error messages in terminal
2. **Google Error**: Search exact error message
3. **GitHub Issues**: Check if others have same problem
4. **Ask Instructor**: Bootcamp support channels
5. **Create Issue**: Open GitHub issue with:
   - Error message
   - Operating system
   - Python version
   - Steps to reproduce

---

## ⚙️ Advanced Configuration

### GPU Acceleration (NVIDIA)

**Check GPU Availability**:
```bash
nvidia-smi
```

**Install CUDA PyTorch**:
```bash
# Uninstall CPU version
pip uninstall torch

# Install GPU version (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

**Expected Speedup**:
- T5-Small: 3-4x faster
- BART: 5-7x faster

---

### Apple Silicon (M1/M2) Optimization

**Use MPS Backend** (Metal Performance Shaders):
```python
# In Config class:
if torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"
```

**Expected Speedup**: 2-3x faster than CPU

---

### Custom Model Cache Location

**Why**: Share models across projects

```bash
# Set environment variable
export TRANSFORMERS_CACHE="/path/to/shared/cache"

# Or in code:
Config.CACHE_DIR = "/path/to/shared/cache"
```

---

### Batch Processing (Future Enhancement)

```python
# Process multiple texts at once
texts = ["Text 1", "Text 2", "Text 3"]

summaries = []
for text in texts:
    summary, _, _ = engine.summarize(text, "t5-small")
    summaries.append(summary)
```

---

## 📦 Deployment Options

See [README.md - Deployment Options](README.md#deployment-options) for:
- HuggingFace Spaces
- Streamlit Cloud
- Railway
- Render
- AWS/GCP

---

## ✅ Verification Checklist

Before considering setup complete, verify:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip list`)
- [ ] Jupyter launches successfully
- [ ] Notebook runs without errors
- [ ] At least one model downloads
- [ ] Gradio interface appears
- [ ] Sample text summarizes correctly
- [ ] Export to markdown works
- [ ] Cache system working (check `./model_cache/`)
- [ ] Exports saved to `./exports/`

---

## 🎓 Next Steps

After successful setup:

1. **Try Different Models**: Compare BART vs T5 vs Pegasus
2. **Test Export Formats**: Try Markdown, JSON, Audio, PDF
3. **Experiment with Length**: Adjust summary length slider
4. **Check Cache**: Notice speedup on repeated texts
5. **Deploy**: Try HuggingFace Spaces for permanent URL

---

**Need Help?** See [Troubleshooting](#troubleshooting) or contact maintainer.

**Ready to Use?** Return to [README.md](README.md) for usage guide.
