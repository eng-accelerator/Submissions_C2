# Complete code for Assignment 3b - Cell 1 (Part 1: Setup and Imports)
# Replace Cell 1 content with this:

# Import all required libraries
import gradio as gr
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

# LlamaIndex core components
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter

# Advanced RAG components
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import TreeSummarize, Refine, CompactAndRefine
from llama_index.core.retrievers import VectorIndexRetriever

print("✅ All libraries imported successfully!")

