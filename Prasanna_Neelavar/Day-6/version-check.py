# test_env.py
from datasets import load_dataset
import pyarrow
import lancedb
import huggingface_hub

print("pyarrow:", pyarrow.__version__)
print("datasets:", __import__("datasets").__version__)
print("lancedb:", lancedb.__version__)
print("huggingface_hub:", huggingface_hub.__version__)

ds = load_dataset("dvilasuero/finepersonas-v0.1-tiny", split="train")
print("Loaded dataset rows:", len(ds))
print("Sample:", ds[0])
