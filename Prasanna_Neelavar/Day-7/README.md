# Day 7 - RAG Implementation Assignments

This directory contains four Jupyter notebooks that demonstrate various aspects of Retrieval-Augmented Generation (RAG) implementation, from basic vector databases to advanced RAG techniques with Gradio interfaces.

## Setup Instructions

### 1. Google Colab Setup

1. Upload the notebooks to Google Colab:
   - Open [Google Colab](https://colab.research.google.com)
   - File → Upload Notebook → Select the `.ipynb` files
   - Or use "Open in Colab" button if viewing on GitHub

2. Mount Google Drive:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```

3. Configure OpenRouter API Key:
   - Click on the 🔑 icon in the left sidebar
   - Add a new secret named `OPENROUTER_API_KEY`
   - Paste your OpenRouter API key
   - Access in code:
   ```python
   from google.colab import userdata
   import os
   os.environ["OPENROUTER_API_KEY"] = userdata.get('OPENROUTER_API_KEY')
   ```

4. Content Directory Structure:
   ```
   MyDrive/
   └── Outskill-RAG/
       ├── requirements.txt
       └── content/
           └── papers/
               └── agents/
                   └── [research papers...]
   ```

## Assignments Overview

### 1. Vector Database Basics (`assignment_1_vector_db_basics.ipynb`)
Implementation of fundamental vector database operations:
- Document loading with SimpleDirectoryReader
- Vector store setup using LanceDB
- Vector index creation
- Basic semantic search and retrieval
- Local embeddings using BAAI/bge-small-en-v1.5

### 2. Advanced RAG Techniques (`assignment_2_advanced_rag.ipynb`)
Exploration of sophisticated RAG features:
- Node postprocessors for filtering and reranking
- Response synthesizers (TreeSummarize, Refine)
- Structured outputs using Pydantic models
- Advanced retrieval pipelines
- Multiple processing stages

### 3. Basic Gradio RAG Interface (`assignment_3a_basic_gradio_rag.ipynb`)
Creating a user interface for RAG:
- Simple Gradio web interface
- Document upload functionality
- Basic RAG query processing
- Result visualization
- Real-time responses

### 4. Advanced Gradio RAG Interface (`assignment_3b_advanced_gradio_rag.ipynb`)
Enhanced RAG interface with advanced features:
- Advanced retrieval options
- Result filtering and ranking
- Response synthesis methods
- Enhanced visualization
- Performance metrics

## Requirements

1. **Python Libraries:**
   - Install from requirements.txt:
   ```python
   !pip install -r "/content/drive/MyDrive/Outskill-RAG/requirements.txt"
   ```

2. **API Keys:**
   - OpenRouter API key (for LLM operations)
   - Free models available through OpenRouter

3. **Data:**
   - Research papers in the agents domain
   - Stored in Google Drive under Outskill-RAG/content/papers/agents/

## Usage Tips

1. **Running the Notebooks:**
   - Execute cells in sequence
   - Wait for each cell to complete before proceeding
   - Check for successful completion indicators (✅)

2. **Troubleshooting:**
   - Verify Google Drive mounting
   - Confirm OpenRouter API key setup
   - Check file paths match your Drive structure
   - Ensure all requirements are installed

3. **Best Practices:**
   - Save notebooks periodically
   - Monitor resource usage
   - Clear output if notebook becomes too large
   - Use provided test functions to verify implementations

## Performance Considerations

1. **Embeddings:**
   - Using local embeddings (BAAI/bge-small-en-v1.5)
   - Efficient and cost-effective
   - No external API calls needed

2. **Vector Store:**
   - LanceDB for efficient vector storage
   - Persistent storage in Google Drive
   - Optimized for retrieval operations

3. **Memory Management:**
   - Clear variables when not needed
   - Restart kernel if memory usage is high
   - Use batch processing for large datasets

## Error Handling

Common issues and solutions:
1. **Drive Mount Errors:**
   - Remount drive
   - Check permissions
   - Verify path structure

2. **API Key Issues:**
   - Verify secret is set
   - Check environment variable
   - Confirm key validity

3. **Resource Limits:**
   - Reduce batch sizes
   - Clear notebook outputs
   - Restart runtime if needed
