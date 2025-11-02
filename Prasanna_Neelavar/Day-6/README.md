# 🧠 Retrieval Augmented Generation (RAG) with LlamaIndex & LanceDB

## Project Overview
This repository demonstrates a complete RAG (Retrieval Augmented Generation) pipeline using **LlamaIndex** and **LanceDB**. The project is based on the C2 Engineering Accelerator session led by Dileep Karri (Outskill), focusing on reducing LLM hallucinations by leveraging external knowledge sources.

## What is RAG?
RAG combines retrieval of relevant information from external sources with generative AI models (LLMs) to produce more accurate and grounded responses. It works in two main phases:

1. **Offline Data Preparation**
   - Collect and extract data (documents, videos, audio, PDFs)
   - Chunk text into manageable pieces (512–1024 tokens, 100–200 token overlap)
   - Embed text as numerical vectors
   - Store vectors in a database (LanceDB, Pinecone, etc.)
2. **Online Retrieval & Generation**
   - Embed user query
   - Retrieve similar vectors/chunks
   - Combine retrieved info with query
   - Generate response using an LLM

## Features
- **Vector Search Only**: Fast retrieval, no LLM generation
- **HuggingFace API Integration**: Uses cloud-based LLMs (requires API key)
- **Local LLM with Ollama**: Fully offline, local inference
- **Flexible data ingestion and chunking**
- **Troubleshooting tips for common setup issues**

## Installation


### 1. Create a Python Environment (Recommended)
```bash
python -m venv rag_env
source rag_env/bin/activate       # macOS/Linux
rag_env\Scripts\activate         # Windows
```

Alternatively, you can use [uv](https://github.com/astral-sh/uv) for fast environment management:
```bash
uv venv rag_env
source rag_env/bin/activate       # macOS/Linux
rag_env\Scripts\activate         # Windows
```

### 2. Install Dependencies
Using pip:
```bash
pip install llama-index llama-index-vector-stores-lancedb \
   llama-index-embeddings-huggingface llama-index-llms-huggingface-api \
   lancedb datasets requests
```

Or using uv:
```bash
uv pip install llama-index llama-index-vector-stores-lancedb \
   llama-index-embeddings-huggingface llama-index-llms-huggingface-api \
   lancedb datasets requests
```

### 3. For Local LLM (Ollama) Support
Using pip:
```bash
pip install llama-index-llms-ollama
```
Or using uv:
```bash
uv pip install llama-index-llms-ollama
```

## Usage

### Run the Main Script
```bash
python rag_llamaindex_lancedb.py
```

### Modes
| Mode                 | Description                | Requires                 |
| -------------------- | -------------------------- | ------------------------ |
| Vector Search        | Fast, no LLM used          | None                     |
| HuggingFace RAG      | Uses HuggingFace cloud LLM | HuggingFace API key      |
| Local LLM (Ollama)   | Fully offline              | Ollama installed locally |

#### HuggingFace API Setup
1. Get your API key from [HuggingFace Tokens](https://huggingface.co/settings/tokens)
2. Set it as an environment variable:
   ```bash
   export HUGGINGFACE_API_KEY="your_token_here"
   ```
3. Uncomment the HuggingFace RAG section in the script.

#### Local LLM (Ollama) Setup
- Download and install Ollama: [Ollama Download](https://ollama.com/download)
- Pull a model (example):
  ```bash
  ollama pull llama3.2:1b
  ollama serve
  ```
- Uncomment the Ollama section in the script.

## Troubleshooting & Tips
- **Python version conflicts**: Use virtual environments and ensure correct kernel selection in VS Code/Jupyter
- **Library installation issues**: Reinstall dependencies in a clean environment
- **HuggingFace API errors**: Check API key and internet connectivity
- **Ollama not working in Colab**: Use local setup for Ollama
- **Recommended Python versions**: 3.14 and 3.11 (3.13.1 and 3.12.0 may have issues)

## Scripts & Documentation
- `rag_llamaindex_lancedb.py`: Main RAG pipeline implementation
- `rag_llamaindex_lancedb.md`: Step-by-step guide and usage instructions
- `summary-RAG.md`: Session summary and conceptual background
- `version-check.py`, `datasets-check.py`: Environment and dataset checks

## References & Further Reading
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [LanceDB Documentation](https://lancedb.com/docs/)
- [HuggingFace Datasets](https://huggingface.co/docs/datasets/)
- [Ollama](https://ollama.com/)

## Contact & Next Steps
- For questions, refer to the session notes in `summary-RAG.md`
- Next session: MCP workflows, Cursor, and Cloud code (see summary for details)

---

*This project is for educational and experimental purposes.*
