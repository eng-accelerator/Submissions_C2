# 🧭 Fix Log – RAG LlamaIndex + LanceDB Integration (macOS / Python 3.12)

**Author:** Prasanna Neelavar  
**Environment:** macOS (Apple Silicon)  
**Stack:** Python 3.12, LlamaIndex, LanceDB, Hugging Face, Datasets  

---

## 1. PyArrow Compatibility Issue

**Error:**
```
AttributeError: module 'pyarrow' has no attribute 'PyExtensionType'. Did you mean: 'ExtensionType'?
```

**Cause:**  
Incompatible `pyarrow` version with `lancedb` or `pylance`.

**Fix:**
Pinned compatible versions:
```bash
pip install "lancedb==0.10.0" "pylance==0.14.1" "pyarrow<15.0.1,>=12"
```

---

## 2. Hugging Face Dataset Local Cache Error

**Error:**
```
NotImplementedError: Loading a dataset cached in a LocalFileSystem is not supported.
```

**Cause:**  
The dataset was being loaded using a local cache path with the `datasets` library expecting remote FS metadata.

**Fix:**
Bypassed reloading from local cache and saved raw dataset manually using:
```python
dataset.save_to_disk("data/personas_dataset")
```
and ensured `.cache/` cleanup before retry.

---

## 3. Dependency Conflict (pyarrow vs lancedb)

**Error:**
```
No solution found when resolving dependencies...
```

**Cause:**  
`lancedb==0.10.0` required `pyarrow<15.0.1`, but newer versions (e.g., 18.x) were installed.

**Fix:**
Removed all related libs, then reinstalled compatible ones:
```bash
pip uninstall lancedb pyarrow pylance -y
pip install "lancedb==0.10.0" "pylance==0.14.1" "pyarrow==14.0.2"
```

---

## 4. Hugging Face Hub Version Mismatch

**Error:**
```
ImportError: huggingface-hub>=0.34.0,<1.0 is required...
```

**Fix:**
Ensured the `transformers` and `huggingface-hub` libraries matched LlamaIndex’s range:
```bash
pip install "huggingface-hub==0.39.4" "transformers==4.44.2"
```

---

## 5. Coroutine Handling in LlamaIndex Pipeline

**Error:**
```
TypeError: cannot unpack non-iterable coroutine object
```
and
```
TypeError: object of type 'coroutine' has no len()
```

**Cause:**  
`.run()` method of `IngestionPipeline` in newer LlamaIndex builds returns a coroutine even in “sync” mode.

**Fix:**  
Wrapped the call safely:
```python
import asyncio

result = pipeline.run(documents=documents)
if asyncio.iscoroutine(result):
    nodes = asyncio.run(result)
else:
    nodes = result
```

---

## 6. Segmentation Fault (Multiprocessing / MPS)

**Cause:**  
Torch MPS backend instability on macOS + multiprocessing in embedding step.

**Fix:**  
Disable GPU fallback:
```python
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
```

---

## ✅ Final Working Setup

**`pyproject.toml` key dependencies:**
```toml
[tool.poetry.dependencies]
python = "^3.12"
lancedb = "0.10.0"
pyarrow = "14.0.2"
pylance = "0.14.1"
datasets = "3.0.1"
huggingface-hub = "0.39.4"
transformers = "4.44.2"
llama-index = "0.11.14"
```

**Command to run:**
```bash
python rag_llamaindex_lancedb.py
```

**Expected output:**
```
✅ Found 100 local persona files. Skipping dataset download.
Setting up LanceDB connection...
Connected to LanceDB, table: personas_rag
Creating embedding model and ingestion pipeline...
Processing documents and creating embeddings...
Successfully processed XXXX text chunks
```
