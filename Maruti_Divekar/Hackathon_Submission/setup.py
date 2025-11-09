from setuptools import setup, find_packages

setup(
    name="ai_deep_researcher",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langgraph",
        "gradio",
        "requests",
        "beautifulsoup4",
        "pyyaml",
        "scikit-learn",
        "faiss-cpu",
    ],
)