# 🧠 RAG Implementation with LlamaIndex and LanceDB

This guide and Python script demonstrate a **complete RAG (Retrieval-Augmented Generation)** pipeline using **LlamaIndex** and **LanceDB**, featuring three different approaches:

1. **Vector Search Only** — Fast retrieval, no LLM generation.  
2. **HuggingFace API Integration** — Uses cloud-based LLMs.  
3. **Local LLM with Ollama** — Runs fully offline with local inference.

---

## 📦 1. Installation Instructions

### 1️⃣ Create a new Python environment (recommended)
```bash
python -m venv rag_env
source rag_env/bin/activate       # For macOS/Linux
rag_env\Scripts\activate          # For Windows
```

### 2. Install required dependencies
```bash
pip install llama-index llama-index-vector-stores-lancedb \
    llama-index-embeddings-huggingface llama-index-llms-huggingface-api \
    lancedb datasets requests
```

### 3. For local LLM (Ollama) support, also install:
```bash
pip install llama-index-llms-ollama
```

## 🧰 2. Usage Overview

You can use this script to test:

| Mode                 | Description                | Requires                 |
| -------------------- | -------------------------- | ------------------------ |
| `Vector Search`      | Fast, no LLM used          | None                     |
| `HuggingFace RAG`    | Uses HuggingFace cloud LLM | HuggingFace API key      |
| `Local LLM (Ollama)` | Fully offline              | Ollama installed locally |


## ⚙️ 3. Run Instructions

Use `rag_llamaindex_lancedb.py` in your VS Code workspace.

## ▶️ 4. Run the Script
```bash
python rag_llamaindex_lancedb.py
```

### ☁️ HuggingFace API Setup

1. Get your API key from
    🔗 https://huggingface.co/settings/tokens

2. Set it as an environment variable before running:
```bash
export HUGGINGFACE_API_KEY="your_token_here"
```

3. Uncomment the HuggingFace RAG section in the main code block.

💻 Local LLM (Ollama) Setup

Download and install Ollama from:
🔗 https://ollama.com/download

Pull the small model (example):

ollama pull llama3.2:1b


Start the service:

ollama serve


Uncomment the Ollama section in the script, then re-run.

🧭 Summary
Mode	Use Case	Pros	Cons
Vector Search	Fast search	No API cost, very fast	No text generation
HuggingFace RAG	Cloud LLMs	High quality, scalable	Needs API key, cost per call
Local Ollama RAG	Offline LLM	Private, cost-free	Requires local setup