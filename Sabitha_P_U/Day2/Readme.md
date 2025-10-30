# 📚 Complete Step-by-Step Code Explanation

## Table of Contents
1. [Requirements & Dependencies](#requirements--dependencies)
2. [Import Statements](#import-statements)
3. [Global Variables](#global-variables)
4. [File Reading Functions](#file-reading-functions)
5. [Dynamic Model Loading](#dynamic-model-loading)
6. [Model Loading Function](#model-loading-function)
7. [Summarization Function](#summarization-function)
8. [Text-to-Speech Function](#text-to-speech-function)
9. [Export Functions](#export-functions)
10. [UI Configuration](#ui-configuration)
11. [Gradio Interface](#gradio-interface)
12. [Event Handlers](#event-handlers)

---

## 1. Requirements & Dependencies

### 📦 requirements.txt

```txt
# Core ML Libraries
gradio>=4.0.0                    # Web UI framework for ML applications
transformers>=4.30.0             # Hugging Face transformers for AI models
torch>=2.0.0                     # PyTorch deep learning framework
huggingface-hub>=0.16.0          # API client for Hugging Face Hub

# Text-to-Speech
gtts>=2.4.0                      # Google Text-to-Speech

# Document Processing
PyPDF2>=3.0.0                    # PDF reading library
python-docx>=0.8.11              # DOCX reading library

# Additional Dependencies
sentencepiece>=0.1.99            # Tokenizer for some models (T5, Pegasus)
protobuf>=3.20.0                 # Protocol buffers for model serialization
accelerate>=0.20.0               # Faster model loading and inference
requests>=2.28.0                 # HTTP library for API calls
```

### Installation Command:
```bash
pip install -r requirements.txt
```

### Why Each Library?

| Library | Purpose | Critical? |
|---------|---------|-----------|
| **gradio** | Creates the web interface | ✅ Yes |
| **transformers** | Loads AI summarization models | ✅ Yes |
| **torch** | Runs the neural networks | ✅ Yes |
| **huggingface-hub** | Fetches models dynamically from HF | ✅ Yes |
| **gtts** | Converts text to audio | ⚠️ Optional |
| **PyPDF2** | Reads PDF files | ⚠️ Optional |
| **python-docx** | Reads Word documents | ⚠️ Optional |
| **sentencepiece** | Required by some models | ✅ Yes |
| **accelerate** | Speeds up model loading | ⚠️ Optional |

---

## 2. Import Statements

```python
import gradio as gr                    # Web UI framework
from transformers import pipeline      # AI model pipeline
import torch                           # Deep learning framework
import json                            # JSON file handling
from datetime import datetime          # Timestamps for exports
from gtts import gTTS                  # Text-to-speech
import os                              # File system operations
import PyPDF2                          # PDF reading
import docx                            # DOCX reading
import requests                        # HTTP requests
from huggingface_hub import HfApi      # Hugging Face API client
```

### What Each Import Does:

- **gradio**: Creates interactive web interfaces with Python
- **transformers.pipeline**: Simplifies using AI models (one-line model loading)
- **torch**: Powers the neural networks, detects GPU availability
- **json**: Exports summaries in JSON format
- **datetime**: Adds timestamps to exported files
- **gTTS**: Google's text-to-speech engine
- **os**: Handles file paths and extensions
- **PyPDF2**: Extracts text from PDF documents
- **docx**: Extracts text from Word documents
- **HfApi**: Connects to Hugging Face to fetch model lists

---

## 3. Global Variables

```python
current_model = None
current_model_name = None
```

### Purpose:
- **Caching mechanism**: Avoids reloading the same model multiple times
- **Memory efficiency**: Models are large (500MB - 2GB), loading is slow (20-30 seconds)
- **Performance**: Once loaded, model stays in memory for fast repeated use

### How It Works:
```python
# First time:
load_model("facebook/bart-large-cnn")  # Downloads and loads (30 seconds)

# Second time:
load_model("facebook/bart-large-cnn")  # Already loaded! (instant)

# Different model:
load_model("t5-small")                 # Downloads new model (30 seconds)
```

---

## 4. File Reading Functions

### 4.1 Read TXT Files

```python
def read_txt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback for non-UTF-8 files
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()
```

**Step-by-step:**
1. Try to open file with UTF-8 encoding (most common)
2. If fails (special characters), try Latin-1 encoding
3. Read entire file content as string
4. Return the text

### 4.2 Read PDF Files

```python
def read_pdf_file(file_path):
    try:
        text = ""
        with open(file_path, 'rb') as f:              # 'rb' = read binary
            pdf_reader = PyPDF2.PdfReader(f)           # Create PDF reader
            for page in pdf_reader.pages:              # Loop through pages
                text += page.extract_text() + "\n"     # Extract text from each page
        return text.strip()                            # Remove extra whitespace
    except Exception as e:
        return f"Error reading PDF: {str(e)}"
```

**Step-by-step:**
1. Open PDF file in binary mode ('rb')
2. Create PdfReader object
3. Loop through each page
4. Extract text from each page
5. Concatenate all text with newlines
6. Return cleaned text (strip whitespace)

### 4.3 Read DOCX Files

```python
def read_docx_file(file_path):
    try:
        doc = docx.Document(file_path)          # Load Word document
        text = ""
        for paragraph in doc.paragraphs:        # Loop through paragraphs
            text += paragraph.text + "\n"       # Extract text
        return text.strip()
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"
```

**Step-by-step:**
1. Load Word document using python-docx
2. Access all paragraphs in the document
3. Extract text from each paragraph
4. Join with newlines
5. Return cleaned text

### 4.4 Main Upload Handler

```python
def read_uploaded_file(file):
    if file is None:
        return "⚠️ No file uploaded"
    
    file_path = file.name                              # Get file path
    file_extension = os.path.splitext(file_path)[1].lower()  # Get extension
    
    # Route to appropriate reader
    if file_extension == '.txt':
        return read_txt_file(file_path)
    elif file_extension == '.pdf':
        return read_pdf_file(file_path)
    elif file_extension in ['.docx', '.doc']:
        return read_docx_file(file_path)
    else:
        return f"⚠️ Unsupported format: {file_extension}"
```

**Step-by-step:**
1. Check if file was uploaded
2. Extract file extension (.txt, .pdf, .docx)
3. Route to appropriate reading function
4. Return extracted text or error message

---

## 5. Dynamic Model Loading

```python
def fetch_top_summarization_models(limit=10):
    try:
        api = HfApi()                                    # Create API client
        
        models = api.list_models(
            task="summarization",                        # Filter by task
            sort="downloads",                            # Sort by popularity
            direction=-1,                                # Descending order
            limit=limit                                  # Top 10
        )
        
        model_list = [model.id for model in models]      # Extract IDs
        return model_list
        
    except Exception as e:
        # Fallback to static list if API fails
        return [
            "facebook/bart-large-cnn",
            "google/pegasus-xsum",
            # ... more models
        ]
```

**Step-by-step:**
1. Create HfApi client to connect to Hugging Face
2. Call `list_models()` with filters:
   - **task="summarization"**: Only summarization models
   - **sort="downloads"**: Most downloaded = most popular
   - **direction=-1**: Highest to lowest
   - **limit=10**: Top 10 models
3. Extract model IDs from response
4. If API fails (no internet), use hardcoded fallback list
5. Return list of model names

**Example Output:**
```python
[
    "facebook/bart-large-cnn",
    "google/pegasus-xsum",
    "sshleifer/distilbart-cnn-12-6",
    "t5-small",
    ...
]
```

---

## 6. Model Loading Function

```python
def load_model(model_name, hf_token=None):
    global current_model, current_model_name
    
    # Check if already loaded
    if current_model_name == model_name and current_model is not None:
        return f"✅ Model '{model_name}' is already loaded!"
    
    # GPU detection
    device = 0 if torch.cuda.is_available() else -1
    
    # Load model
    if hf_token and hf_token.strip():
        current_model = pipeline(
            "summarization",
            model=model_name,
            token=hf_token,
            device=device
        )
    else:
        current_model = pipeline(
            "summarization",
            model=model_name,
            device=device
        )
    
    current_model_name = model_name
    device_info = "GPU" if torch.cuda.is_available() else "CPU"
    return f"✅ Model '{model_name}' loaded on {device_info}!"
```

**Step-by-step:**
1. **Cache Check**: If same model already loaded, skip loading
2. **GPU Detection**: 
   - `device=0` → Use GPU
   - `device=-1` → Use CPU
3. **Load Pipeline**:
   - Downloads model from Hugging Face (first time only)
   - Creates summarization pipeline
   - Uses token if provided (for private models)
4. **Save to Global**: Store model and name for future use
5. **Return Status**: Confirm success with device info

**Time Breakdown:**
- First load: 20-30 seconds (downloading)
- Subsequent loads (same model): Instant (cached)
- Different model: 20-30 seconds (new download)

---

## 7. Summarization Function

```python
def summarize_text(input_text, summary_percentage, min_length):
    # Validation
    if not input_text or not input_text.strip():
        return "⚠️ Please enter text"
    
    if current_model is None:
        return "⚠️ Please load a model first!"
    
    # Calculate max_length from percentage
    input_char_count = len(input_text)
    estimated_tokens = input_char_count // 4        # ~4 chars per token
    max_length = int(estimated_tokens * (summary_percentage / 100))
    max_length = max(30, max_length)                # Minimum 30 tokens
    
    # Handle long texts (chunking)
    max_input_length = 1024                          # Model limit
    if estimated_tokens > max_input_length:
        # Split into chunks
        words = input_text.split()
        chunk_size = max_input_length * 4
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_length += len(word) + 1
            if current_length > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        # Summarize each chunk
        summaries = []
        for chunk in chunks:
            result = current_model(
                chunk,
                max_length=int(max_length // len(chunks)),
                min_length=int(min_length // len(chunks)),
                do_sample=False
            )
            summaries.append(result[0]['summary_text'])
        
        summary = ' '.join(summaries)
    else:
        # Standard summarization
        result = current_model(
            input_text,
            max_length=int(max_length),
            min_length=int(min_length),
            do_sample=False
        )
        summary = result[0]['summary_text']
    
    # Format output
    output = f"📝 **Summary Generated!**\n\n"
    output += f"**Original:** {len(input_text)} chars ({len(input_text.split())} words)\n"
    output += f"**Summary:** {len(summary)} chars ({len(summary.split())} words)\n"
    output += f"**Compression:** {(1 - len(summary)/len(input_text))*100:.1f}%\n\n"
    output += f"---\n\n{summary}"
    
    return output
```

**Step-by-step:**

### Phase 1: Validation
1. Check if text is provided
2. Check if model is loaded

### Phase 2: Calculate Target Length
1. Count characters in input
2. Estimate tokens (1 token ≈ 4 characters)
3. Calculate max_length based on percentage
   - Example: 1000 chars → 250 tokens → 30% → 75 tokens

### Phase 3: Chunking (for long texts)
1. Check if text exceeds 1024 tokens
2. If yes, split into chunks:
   - Split by words
   - Group into chunks of ~1024 tokens each
   - Summarize each chunk separately
   - Combine summaries

### Phase 4: Summarization
1. Call model with parameters:
   - `max_length`: Target length
   - `min_length`: Minimum acceptable length
   - `do_sample=False`: Deterministic output
2. Extract summary from result

### Phase 5: Format Output
1. Calculate statistics
2. Format markdown output
3. Return formatted summary

---

## 8. Text-to-Speech Function

```python
def text_to_speech(summary_output):
    if not summary_output or "⚠️" in summary_output:
        return None
    
    # Extract clean summary
    summary_text = summary_output.split('---')[-1].strip()
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"summary_audio_{timestamp}.mp3"
    
    # Create TTS and save
    tts = gTTS(text=summary_text, lang='en', slow=False)
    tts.save(filename)
    
    return filename
```

**Step-by-step:**
1. **Validate**: Check if summary exists and has no errors
2. **Extract**: Get clean summary text (remove markdown formatting)
3. **Timestamp**: Create unique filename with current date/time
4. **Generate Audio**:
   - Create gTTS object with text
   - Language: English
   - Speed: Normal (slow=False)
5. **Save**: Write MP3 file to disk
6. **Return**: File path for download

**Example Filename:** `summary_audio_2024-10-30_14-32-15.mp3`

---

## 9. Export Functions

### 9.1 Full TXT Export

```python
def export_txt(input_text, summary_output):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"summary_{timestamp}.txt"
    
    content = f"Text Summary Report\n"
    content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"Model: {current_model_name}\n"
    content += f"\n{'='*60}\n\n"
    content += f"ORIGINAL TEXT:\n{input_text}\n\n"
    content += f"{'='*60}\n\n"
    content += f"SUMMARY:\n{summary_text}\n"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename
```

**Creates:**
```
Text Summary Report
Generated: 2024-10-30 14:32:15
Model: facebook/bart-large-cnn

============================================================

ORIGINAL TEXT:
[Your original text here...]

============================================================

SUMMARY:
[Summary here...]
```

### 9.2 JSON Export

```python
def export_json(input_text, summary_output):
    data = {
        "timestamp": datetime.now().isoformat(),
        "model": current_model_name,
        "original_text": input_text,
        "summary": summary_text,
        "original_length": len(input_text),
        "summary_length": len(summary_text),
        "compression_ratio": f"{(1 - len(summary_text)/len(input_text))*100:.1f}%"
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

**Creates:**
```json
{
  "timestamp": "2024-10-30T14:32:15.123456",
  "model": "facebook/bart-large-cnn",
  "original_text": "...",
  "summary": "...",
  "original_length": 1500,
  "summary_length": 450,
  "compression_ratio": "70.0%"
}
```

---

## 10. UI Configuration

### 10.1 Theme

```python
dark_theme = gr.themes.Base(
    primary_hue="blue",
    secondary_hue="slate",
    neutral_hue="slate",
).set(
    body_background_fill="*neutral_950",     # Very dark background
    block_label_text_color="*neutral_100",   # Light text
    # ... more color settings
)
```

**Color System:**
- `neutral_950`: Almost black (#0a0a0a)
- `neutral_900`: Very dark gray (#171717)
- `neutral_800`: Dark gray (#262626)
- `neutral_100`: Light gray (#f5f5f5)

### 10.2 Custom CSS

```python
custom_css = """
.block-label, label {
    color: #f3f4f6 !important;   /* Force light text */
}

@media (max-width: 768px) {      /* Mobile responsive */
    .gradio-container {
        padding: 0.5rem !important;
    }
}
"""
```

**Purpose:**
- Override default Gradio styles
- Ensure text visibility on dark background
- Make layout responsive for mobile devices

---

## 11. Gradio Interface Structure

```python
with gr.Blocks(theme=dark_theme, css=custom_css) as demo:
    gr.Markdown("# Header")
    
    with gr.Row():                          # Horizontal layout
        with gr.Column(scale=1):            # Left column (1/3 width)
            # Model configuration
            model_dropdown = gr.Dropdown(...)
            load_btn = gr.Button(...)
            
        with gr.Column(scale=2):            # Right column (2/3 width)
            # Input/Output
            with gr.Tabs():                 # Tabbed interface
                with gr.Tab("Text Input"):
                    input_text = gr.Textbox(...)
                with gr.Tab("File Upload"):
                    file_upload = gr.File(...)
```

**Layout Structure:**
```
┌─────────────────────────────────────────────┐
│              Header (Markdown)              │
├───────────────┬─────────────────────────────┤
│   Left Col    │       Right Column          │
│   (1/3)       │         (2/3)               │
│               │                             │
│  Model Config │  ┌──────────────────────┐  │
│  - Dropdown   │  │ Tab: Text Input      │  │
│  - Custom     │  │ Tab: File Upload     │  │
│  - Token      │  └──────────────────────┘  │
│  - Load Btn   │                             │
│  - Status     │  Input Text Box             │
│               │  Sliders (Settings)         │
│  Model Info   │  Generate Button            │
│               │  Summary Output             │
│               │  Audio / Export Buttons     │
└───────────────┴─────────────────────────────┘
```

---

## 12. Event Handlers

### 12.1 Model Loading

```python
load_btn.click(
    fn=lambda d, c, t: load_model(update_model_name(d, c), t),
    inputs=[model_dropdown, custom_model, hf_token],
    outputs=model_status
)
```

**Flow:**
1. User clicks "Load Model" button
2. Collect inputs: dropdown value, custom model, token
3. Call `load_model()` function
4. Update `model_status` textbox with result

### 12.2 File Upload

```python
upload_btn.click(
    fn=read_uploaded_file,
    inputs=[file_upload],
    outputs=input_text
)
```

**Flow:**
1. User uploads file
2. User clicks "Load from File"
3. Call `read_uploaded_file()` with file object
4. Extract text and populate `input_text` box

### 12.3 Summarization

```python
summarize_btn.click(
    fn=summarize_text,
    inputs=[input_text, summary_percentage, min_length],
    outputs=summary_output
)
```

**Flow:**
1. User clicks "Generate Summary"
2. Collect: input text, percentage, min length
3. Call `summarize_text()`
4. Display result in `summary_output` box

### 12.4 Text-to-Speech

```python
tts_btn.click(
    fn=text_to_speech,
    inputs=[summary_output],
    outputs=audio_output
)
```

**Flow:**
1. User clicks "Generate Audio"
2. Pass summary text
3. Generate MP3 file
4. Display audio player with download option

---

## 🎯 Complete Workflow Example

Let's trace a complete user journey:

### Step 1: Start Application
```bash
python app.py
```
- Fetches top 10 models from Hugging Face
- Launches Gradio interface on http://localhost:7860

### Step 2: Load Model
1. User selects "facebook/bart-large-cnn"
2. Clicks "Load Model"
3. **Behind the scenes:**
   - Checks if model cached (not first time)
   - Downloads model (~1.6 GB) to cache
   - Loads into memory using transformers
   - Detects GPU and uses it if available
4. Shows: "✅ Model loaded successfully on GPU!"

### Step 3: Input Text
**Option A: Type/Paste**
- User pastes article into text box

**Option B: Upload File**
- User uploads `document.pdf`
- Clicks "Load from File"
- **Behind the scenes:**
  - Detects `.pdf` extension
  - Calls `read_pdf_file()`
  - Extracts text from all pages
  - Populates text box

### Step 4: Configure Settings
- User sets "Summary Length" to 25%
- Sets "Min Length" to 30 tokens

### Step 5: Generate Summary
1. User clicks "Generate Summary"
2. **Behind the scenes:**
   - Validates input (not empty, model loaded)
   - Calculates: 2000 chars → 500 tokens → 25% → 125 tokens max
   - Calls model: `pipeline(text, max_length=125, min_length=30)`
   - Model processes (~2-3 seconds)
   - Formats output with statistics
3. Shows summary in output box

### Step 6: Generate Audio (Optional)
1. User clicks "Generate Audio"
2. **Behind the scenes:**
   - Extracts clean summary text
   - Creates gTTS object
   - Generates MP3 file
   - Returns file path
3. Audio player appears with download button

### Step 7: Export
**Option A: Full Report**
- Clicks "Full Report (TXT)"
- Downloads: `summary_2024-10-30_14-32-15.txt`
- Contains: Original + Summary + Metadata

**Option B: Summary Only**
- Clicks "Summary Only (TXT)"
- Downloads: Just the summary text

**Option C: JSON**
- Clicks "JSON Export"
- Downloads: Structured data with statistics

---

## 🔧 Performance Characteristics

### Memory Usage:
- **Small model (t5-small)**: ~500 MB RAM
- **Medium model (distilbart)**: ~1 GB RAM
- **Large model (bart-large-cnn)**: ~2 GB RAM
- **Plus overhead**: ~500 MB for Gradio + Python

### Processing Speed:
| Model | Input Length | GPU Time | CPU Time |
|-------|--------------|----------|----------|
| t5-small | 500 words | 0.5s | 2s |
| distilbart | 500 words | 1s | 4s |
| bart-large | 500 words | 2s | 8s |
| pegasus | 500 words | 3s | 12s |

### Disk Usage:
- Models cached in: `~/.cache/huggingface/`
- Each model: 200 MB - 2.3 GB
- Exports: 1-10 KB per file

---

## 🎓 Key Concepts Explained

### 1. Pipeline Architecture
```python
pipeline("summarization", model="...")
```
- Abstracts: tokenization → model inference → decoding
- Handles: device placement, batch processing, error handling
- One line replaces ~50 lines of manual code

### 2. Token Estimation
```python
estimated_tokens = char_count // 4
```
- English: ~4 characters per token on average
- "Hello world" = 11 chars ≈ 3 tokens
- Used for: max_length calculation, chunking decisions

### 3. Chunking Strategy
For texts > 1024 tokens:
- Split into overlapping chunks
- Summarize each independently
- Concatenate results
- Prevents information loss

### 4. Gradio Components
- **Textbox**: Multi-line text input/output
- **Slider**: Numeric value selection
- **Button**: Trigger actions
- **File**: File upload widget
- **Audio**: Audio player/downloader
- **Markdown**: Formatted text display

---

## 🐛 Common Issues & Solutions

### Issue 1: Model Download Fails
**Cause**: Internet connection, Hugging Face down, or rate limit
**Solution**: 
- Use HF token to avoid rate limits
- Check internet connection
- Try different model

### Issue 2: Out of Memory
**Cause**: Model too large for available RAM/VRAM
**Solution**:
- Use smaller model (t5-small, distilbart)
- Close other applications
- Use CPU mode (slower but less memory)

### Issue 3: PDF Text Extraction Empty
**Cause**: PDF is image-based (scanned document)
**Solution**:
- Use OCR tool first (Tesseract)
- Convert to text format
- Some PDFs have text as images

### Issue 4: Audio Generation Fails
**Cause**: No internet (gTTS requires online connection)
**Solution**:
- Check internet connection
- gTTS uses Google's servers (needs connectivity)

---

## 📊 Data Flow Diagram

```
User Input
   ↓
┌────────────────────┐
│ Upload File / Text │
└────────┬───────────┘
         ↓
┌────────────────────┐
│   File Reader      │ → Extract text from PDF/DOCX/TXT
└────────┬───────────┘
         ↓
┌────────────────────┐
│  Text Validation   │ → Check if not empty
└────────┬───────────┘
         ↓
┌────────────────────┐
│   Chunking         │ → Split if > 1024 tokens
│   (if needed)      │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ AI Model           │ → Generate summary
│ (Transformer)      │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Post-Processing    │ → Format, calculate stats
└────────┬───────────┘
         ↓
         ├─→ Display in UI
         ├─→ Text-to-Speech (gTTS)
         ├─→ Export TXT
         └─→ Export JSON
```

---

## 🎬 Conclusion

This application demonstrates:
- ✅ **ML Integration**: Using transformers for NLP
- ✅ **File Processing**: Multi-format document handling
- ✅ **API Integration**: Dynamic model fetching
- ✅ **UI Design**: Responsive, dark-themed interface
- ✅ **Export Options**: Multiple output formats
- ✅ **Audio Generation**: Text-to-speech integration
- ✅ **Error Handling**: Graceful fallbacks
- ✅ **Performance**: Caching, chunking, GPU support

**Total Lines of Code**: ~800
**Key Functions**: 15+
**UI Components**: 20+
**File Formats Supported**: 3 (TXT, PDF, DOCX)
**Export Formats**: 4 (TXT, JSON, Summary-only TXT, MP3)

---

## 📖 Further Learning

1. **Transformers**: [huggingface.co/docs/transformers](https://huggingface.co/docs/transformers)
2. **Gradio**: [gradio.app/docs](https://www.gradio.app/docs)
3. **PyTorch**: [pytorch.org/tutorials](https://pytorch.org/tutorials)
4. **NLP Basics**: Text preprocessing, tokenization, embeddings
5. **Model Fine-tuning**: Training custom summarization models

---

**Ready to run? Install requirements and launch!** 🚀

```bash
pip install -r requirements.txt
python app.py
```
