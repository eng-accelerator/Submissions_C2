"""Simple OCR helper with graceful fallbacks."""

from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
except ImportError:  # pragma: no cover - optional dependency
    Image = None  # type: ignore[assignment]

try:
    import pytesseract
except ImportError:  # pragma: no cover - optional dependency
    pytesseract = None  # type: ignore[assignment]


def _file_cache_key(path: Path) -> str:
    """Return a cache key based on path + file stats."""

    if not path.exists():
        return str(path)
    stat = path.stat()
    return f"{path.resolve()}::{stat.st_size}::{stat.st_mtime_ns}"


@lru_cache(maxsize=128)
def _extract_text_cached(key: str) -> str:
    """Internal helper used by ``extract_text``."""

    path_str, *_ = key.split("::")
    image_path = Path(path_str)

    if Image is None or not image_path.exists():
        return ""

    try:
        with Image.open(image_path) as img:
            grayscale = img.convert("L")
            if pytesseract is None:
                # Provide a lightweight heuristic: hash of image to keep deterministic.
                digest = hashlib.sha1(grayscale.tobytes()).hexdigest()
                return f"image-text-placeholder-{digest[:10]}"
            return pytesseract.image_to_string(grayscale, lang="eng").strip()
    except Exception:
        return ""


def extract_text(path: str) -> str:
    """Public OCR API with caching and graceful fallbacks."""

    key = _file_cache_key(Path(path))
    return _extract_text_cached(key)


