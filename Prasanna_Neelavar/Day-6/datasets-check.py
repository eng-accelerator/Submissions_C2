from datasets import load_dataset
dataset = load_dataset("dvilasuero/finepersonas-v0.1-tiny", split="train")
print(len(dataset))
