"""
RAG Implementation with LlamaIndex and LanceDB
----------------------------------------------
This script demonstrates a complete RAG pipeline using LlamaIndex and LanceDB.

It provides three modes:
1. Vector Search Only
2. HuggingFace API Integration
3. Local LLM with Ollama
"""

import os
import time
import subprocess
import asyncio
from pathlib import Path
import requests

import lancedb
from datasets import load_dataset

# LlamaIndex core components
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline

# Embedding and vector store
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.lancedb import LanceDBVectorStore

# LLM integrations
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from llama_index.llms.ollama import Ollama

# -------------------------------------------------------
# 1. Data Preparation
# -------------------------------------------------------
def prepare_data(num_samples=100):
    """Load dataset and create document files."""
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    existing_files = list(data_dir.glob("persona_*.txt"))
    if existing_files:
        print(f"✅ Found {len(existing_files)} local persona files. Skipping dataset download.")
        documents = [
            Document(
                text=open(f, "r", encoding="utf-8").read(),
                metadata={"persona_id": i, "source": "local-cache"},
            )
            for i, f in enumerate(existing_files)
        ]
        return documents

    # If not found, download and save
    print(f"📥 Downloading {num_samples} personas from Hugging Face...")
    dataset = load_dataset("dvilasuero/finepersonas-v0.1-tiny", split="train")

    documents = []
    for i, persona in enumerate(dataset.select(range(min(num_samples, len(dataset))))):
        text = persona["persona"]
        file_path = data_dir / f"persona_{i}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        documents.append(Document(text=text, metadata={"persona_id": i, "source": "finepersonas-dataset"}))

    print(f"✅ Prepared and cached {len(documents)} documents in {data_dir}")
    return documents


# -------------------------------------------------------
# 2. LanceDB Setup
# -------------------------------------------------------
def setup_lancedb_store(table_name="personas_rag"):
    print("Setting up LanceDB connection...")
    db = lancedb.connect("./lancedb_data")
    print(f"Connected to LanceDB, table: {table_name}")
    return db, table_name


# -------------------------------------------------------
# 3. Embedding and Vector Store
# -------------------------------------------------------
# async def create_and_populate_index(documents, db, table_name):
def create_and_populate_index(documents, db, table_name):
    print("Creating embedding model and ingestion pipeline...")

    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    vector_store = LanceDBVectorStore(
        uri="./lancedb_data", table_name=table_name, mode="overwrite"
    )

    pipeline = IngestionPipeline(
        transformations=[SentenceSplitter(chunk_size=512, chunk_overlap=20), embed_model],
        vector_store=vector_store,
    )

    print("Processing documents and creating embeddings...")
    # multi processing
    # nodes = await pipeline.arun(documents=documents)

    # single threaded non-async
    # nodes = pipeline.arun(documents=documents)

    result = pipeline.run(documents=documents)
    if asyncio.iscoroutine(result):
        nodes = asyncio.run(result)
    else:
        nodes = result

    print(f"Successfully processed {len(nodes)} text chunks")
    return vector_store, embed_model


# -------------------------------------------------------
# 4. Vector Search
# -------------------------------------------------------
def perform_vector_search(db, table_name, query_text, embed_model, top_k=5):
    query_embedding = embed_model.get_text_embedding(query_text)
    table = db.open_table(table_name)
    results = table.search(query_embedding).limit(top_k).to_pandas()
    return results


def test_vector_search(db, table_name, embed_model):
    print("Testing Vector Search (No LLM needed)")
    print("=" * 50)

    queries = [
        "technology and artificial intelligence expert",
        "teacher educator professor",
        "environment climate sustainability",
        "art culture heritage creative",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 30)
        results = perform_vector_search(db, table_name, query, embed_model, top_k=3)
        for idx, row in results.iterrows():
            score = row.get("_distance", "N/A")
            text = row.get("text", "N/A")
            score_str = f"{score:.3f}" if isinstance(score, (int, float)) else str(score)
            print(f"\nResult {idx + 1} (Score: {score_str}):")
            print(f"{text[:200]}...")


# -------------------------------------------------------
# 5. RAG with HuggingFace API
# -------------------------------------------------------
def create_query_engine(vector_store, embed_model, llm=None):
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)
    query_engine_kwargs = {"response_mode": "tree_summarize"}
    if llm:
        query_engine_kwargs["llm"] = llm
    query_engine = index.as_query_engine(**query_engine_kwargs)
    return query_engine


def query_rag(query_engine, question):
    return query_engine.query(question)


async def test_huggingface_rag(vector_store, embed_model):
    print("Testing RAG with HuggingFace API")
    print("=" * 40)
    try:
        llm = HuggingFaceInferenceAPI(
            model_name="HuggingFaceH4/zephyr-7b-beta",
            token=os.environ.get("HUGGINGFACE_API_KEY"),
        )
        query_engine = create_query_engine(vector_store, embed_model, llm)
        queries = [
            "Find personas interested in technology and AI",
            "Who are the educators or teachers in the dataset?",
            "Describe personas working with environmental topics",
        ]
        for query in queries:
            print(f"\nQuery: {query}")
            print("-" * 30)
            response = query_rag(query_engine, query)
            print(f"Response: {response}")
    except Exception as e:
        print(f"Error during HuggingFace RAG: {e}")


# -------------------------------------------------------
# 6. Local LLM (Ollama)
# -------------------------------------------------------
def check_ollama_installed():
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"Ollama is installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("Ollama is not installed or not in PATH")
    return False


def start_ollama_service():
    try:
        print("Starting Ollama service...")
        subprocess.Popen(["ollama", "serve"], shell=True)
        time.sleep(3)
        print("Ollama service started!")
        return True
    except Exception as e:
        print(f"Failed to start Ollama: {e}")
        return False


def pull_ollama_model(model_name="llama3.2:1b"):
    print(f"Pulling model: {model_name}")
    result = subprocess.run(["ollama", "pull", model_name], capture_output=True, text=True, shell=True)
    if result.returncode == 0:
        print(f"Model {model_name} pulled successfully!")
        return True
    else:
        print(f"Failed to pull model: {result.stderr}")
        return False


async def test_local_llm_rag(vector_store, embed_model):
    print("Testing RAG with Local LLM (Ollama)")
    print("=" * 40)
    try:
        llm = Ollama(model="llama3.2:1b", base_url="http://localhost:11434", request_timeout=60.0)
        query_engine = create_query_engine(vector_store, embed_model, llm)
        queries = [
            "Find personas interested in technology and AI",
            "Who are the educators or teachers in the dataset?",
            "Describe personas working with environmental topics",
        ]
        for query in queries:
            print(f"\nQuery: {query}")
            print("-" * 30)
            response = query_rag(query_engine, query)
            print(f"Response: {response}")
    except Exception as e:
        print(f"Error during local LLM RAG: {e}")


# -------------------------------------------------------
# 7. Utilities
# -------------------------------------------------------
def explore_lancedb_table(db, table_name):
    try:
        table = db.open_table(table_name)
        print("Table Schema:")
        print(table.schema)
        print(f"\nTotal records: {table.count_rows()}")
        df = table.to_pandas().head()
        print("\nSample records:")
        print(df)
    except Exception as e:
        print(f"Error exploring table: {e}")


# -------------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------------
if __name__ == "__main__":
    print("=== RAG Implementation with LlamaIndex + LanceDB ===")

    # 1. Prepare Data
    documents = prepare_data(num_samples=100)

    # 2. Setup LanceDB
    db, table_name = setup_lancedb_store()

    # 3. Create Vector Store and Embeddings
    # vector_store, embed_model = asyncio.run(create_and_populate_index(documents, db, table_name))
    vector_store, embed_model = create_and_populate_index(documents, db, table_name)

    # 4. Test Vector Search
    test_vector_search(db, table_name, embed_model)

    # 5. Optionally test HuggingFace or Local LLM RAG:
    # os.environ["HUGGINGFACE_API_KEY"] = "your_token_here"
    # asyncio.run(test_huggingface_rag(vector_store, embed_model))

    check_ollama_installed()
    asyncio.run(test_local_llm_rag(vector_store, embed_model))

    # 6. Explore table
    explore_lancedb_table(db, table_name)

    print("\n=== Script Completed ===")
