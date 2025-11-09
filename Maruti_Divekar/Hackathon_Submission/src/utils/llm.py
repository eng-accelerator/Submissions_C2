"""Lightweight LLM helper with a robust extractive fallback.

This module exposes generate_text(...) which will try to use an attached LLM
and, if unavailable, will return a concise extractive summary. The module
also records the source of the last generation so callers (UI) can show a
visible indicator ("llm" vs "fallback").
"""
from __future__ import annotations
import re
from typing import List
import math
import hashlib

_LAST_GENERATION_SOURCE: str = 'unknown'


def _extractive_summarize(text: str, n_sentences: int = 4) -> str:
    """Simple extractive summarizer using TF-IDF sentence scoring.

    Selects the top n_sentences by TF-IDF weight and returns them in the
    original order. Falls back to the first N sentences when scoring fails.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
    except Exception:
        # If sklearn is not available, fall back to naive first-sentences approach
        sents = re.split(r'(?<=[\.!?])\s+', text.strip())
        return ' '.join(sents[:n_sentences]).strip()

    # Split into sentences
    sents = [s.strip() for s in re.split(r'(?<=[\.!?])\s+', text.strip()) if s.strip()]
    if not sents:
        return ''
    if len(sents) <= n_sentences:
        return ' '.join(sents)

    try:
        vec = TfidfVectorizer(stop_words='english')
        X = vec.fit_transform(sents)
        # Score sentences by sum of TF-IDF weights
        scores = X.sum(axis=1).A1
        # Pick top sentence indices
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n_sentences]
        top_idx_sorted = sorted(top_idx)
        summary = ' '.join(sents[i] for i in top_idx_sorted)
        return summary
    except Exception:
        # On any failure, return first n sentences
        return ' '.join(sents[:n_sentences])


def generate_text(prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
    """Generate text using an LLM if available; otherwise return an extractive summary.

    This function prefers to call an attached LLM (OpenAI/OpenRouter API). If the
    LLM call fails for any reason (missing credentials, API error,
    runtime error), it returns a concise extractive summary of the prompt so
    downstream agents always receive usable, plain-English text.
    """
    global _LAST_GENERATION_SOURCE
    try:
        # Try to use OpenAI/OpenRouter with new API
        import os
        from openai import OpenAI
        
        # Try OpenAI first, then OpenRouter
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("Neither OPENAI_API_KEY nor OPENROUTER_API_KEY environment variable is set")
        
        # Use OpenRouter if that's the key we have
        if api_key.startswith('sk-or-'):
            base_url = "https://openrouter.ai/api/v1"
            client = OpenAI(api_key=api_key, base_url=base_url)
            model = 'openai/gpt-4o-mini'  # OpenRouter model
        else:
            client = OpenAI(api_key=api_key)
            model = 'gpt-4o-mini'
        
        response = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        out = response.choices[0].message.content
        if out and isinstance(out, str) and out.strip():
            _LAST_GENERATION_SOURCE = 'llm'
            return out.strip()
    except Exception as e:
        print(f"LLM error: {e}")
        # Silent fallback to extractive summarizer below
        pass
    
    # Last-resort: extractive summarize into short plain-English
    _LAST_GENERATION_SOURCE = 'fallback'
    return _extractive_summarize(prompt, n_sentences=4)


def get_last_generation_source() -> str:
    """Return the source of the last generation: 'llm' or 'fallback' (or 'unknown')."""
    return _LAST_GENERATION_SOURCE


def _local_embed(text: str, dim: int = 384) -> List[float]:
    """Deterministic lightweight embedding: hash tokens -> bucket frequencies -> L2 normalize.

    We purposely keep dim smaller (384) and later pad to the target 1536 size used elsewhere.
    This allows offline retrieval with approximate semantic grouping while avoiding external calls.
    """
    # Basic tokenization
    tokens = [t.lower() for t in re.findall(r"[A-Za-z0-9_]+", text)]
    if not tokens:
        return [0.0] * dim
    buckets = [0.0] * dim
    for tok in tokens:
        h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
        idx = h % dim
        buckets[idx] += 1.0
    # TF weighting
    total = len(tokens)
    if total:
        buckets = [v / total for v in buckets]
    # Simple log scaling
    buckets = [math.log1p(v) for v in buckets]
    # L2 norm
    norm = math.sqrt(sum(v * v for v in buckets)) or 1.0
    buckets = [v / norm for v in buckets]
    return buckets

def get_embeddings(texts: List[str], model: str = 'text-embedding-3-small', **kwargs) -> List[List[float]]:
    """Get embeddings for a list of texts.

    Order of strategies:
    1. If EMBEDDINGS_MODE=local -> use deterministic local embed
    2. Try remote (OpenAI/OpenRouter) API
    3. On failure -> local embed padded to 1536 dims
    """
    import os
    mode = os.getenv('EMBEDDINGS_MODE', 'auto').lower()
    TARGET_DIM = 1536

    # Local only mode
    if mode == 'local':
        local_vecs = []
        for t in texts:
            base = _local_embed(t, dim=384)
            # Pad to TARGET_DIM for FAISS consistency
            padded = base + [0.0] * (TARGET_DIM - len(base))
            local_vecs.append(padded)
        return local_vecs

    # Attempt remote embeddings
    try:
        from openai import OpenAI
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("No embedding API key found; falling back to local embeddings")
        if api_key.startswith('sk-or-'):
            base_url = "https://openrouter.ai/api/v1"
            client = OpenAI(api_key=api_key, base_url=base_url)
            model = 'openai/text-embedding-3-small'
        else:
            client = OpenAI(api_key=api_key)
        resp = client.embeddings.create(model=model, input=texts, **kwargs)
        vecs = [d.embedding for d in resp.data]
        # If dimension differs, pad/trim
        fixed = []
        for v in vecs:
            if len(v) < TARGET_DIM:
                v = v + [0.0] * (TARGET_DIM - len(v))
            elif len(v) > TARGET_DIM:
                v = v[:TARGET_DIM]
            fixed.append(v)
        return fixed
    except Exception as e:
        print(f"Error getting embeddings remotely, using local fallback: {e}")
        local_vecs = []
        for t in texts:
            base = _local_embed(t, dim=384)
            padded = base + [0.0] * (TARGET_DIM - len(base))
            local_vecs.append(padded)
        return local_vecs
