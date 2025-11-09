"""Lightweight captioning helper leveraging basic image statistics."""

from __future__ import annotations

import statistics
from pathlib import Path
from typing import List

try:
    from PIL import Image
except ImportError:  # pragma: no cover - optional dependency
    Image = None  # type: ignore[assignment]


def _format_rgb(rgb: List[int]) -> str:
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"


def generate_caption(path: str) -> List[str]:
    """Return descriptive snippets for the image at ``path``."""

    image_path = Path(path)
    if Image is None or not image_path.exists():
        return ["Unable to inspect image content."]

    try:
        with Image.open(image_path) as img:
            width, height = img.size
            mode = img.mode
            pixels = list(img.getdata())

            sample = pixels[:: max(1, len(pixels) // 500)]
            avg = [int(statistics.mean(channel)) for channel in zip(*sample)]
            caption = [
                f"Image size {width}x{height} ({mode}).",
                f"Dominant colour around {_format_rgb(avg)}.",
            ]
            if width > height:
                caption.append("Layout appears horizontal / landscape.")
            elif height > width:
                caption.append("Layout appears vertical / portrait.")
            else:
                caption.append("Layout appears square.")
            return caption
    except Exception:
        return ["Failed to inspect image."]


