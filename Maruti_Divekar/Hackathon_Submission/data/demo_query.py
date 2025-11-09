# Sample demo query and constraints for validating the research pipeline

QUERY = """
What are the latest developments and potential impacts of Retrieval-Augmented Generation (RAG) 
in healthcare applications, focusing on studies from 2023-2025? Consider both technical 
innovations and real-world implementation challenges.
"""

CONSTRAINTS = {
    "time_window": "2023-01-01..2025-12-31",
    "domains": [
        "nature.com",
        "who.int",
        "arxiv.org",
        "pubmed.ncbi.nlm.nih.gov"
    ],
    "max_budget_usd": 2.00,
    "max_tokens": 100000,
    "depth": "deep",
    "disallowed_sources": [
        "twitter.com",
        "reddit.com",
        "medium.com"
    ]
}