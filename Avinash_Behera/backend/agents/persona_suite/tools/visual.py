"""Extract lightweight visual heuristics from design artifacts."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List

try:
    from PIL import Image, ImageStat
except ImportError:  # pragma: no cover - optional dependency
    Image = None  # type: ignore[assignment]
    ImageStat = None  # type: ignore[assignment]


def analyze_visual_features(path: str) -> Dict[str, object]:
    """Return a dictionary with simple visual measurements."""

    image_path = Path(path)
    if Image is None or ImageStat is None or not image_path.exists():
        return {
            "dimensions": None,
            "aspect_ratio": None,
            "contrast": None,
            "notes": ["Image analysis unavailable."],
        }

    try:
        with Image.open(image_path) as img:
            width, height = img.size
            aspect_ratio = round(width / height, 3) if height else None

            stat = ImageStat.Stat(img.convert("L"))
            contrast = round(stat.stddev[0], 3) if stat.stddev else None

            palette_notes: List[str] = []
            if aspect_ratio:
                if aspect_ratio > 1.4:
                    palette_notes.append("Wide layout suggests desktop or web screen.")
                elif aspect_ratio < 0.8:
                    palette_notes.append("Tall layout suggests mobile screen.")

            if contrast is not None:
                if contrast < 20:
                    palette_notes.append("Low contrast; text legibility may suffer.")
                elif contrast > 60:
                    palette_notes.append("High contrast; hierarchy likely clear.")

            diag = round(math.hypot(width, height), 1) if width and height else None

            return {
                "dimensions": {"width": width, "height": height, "diagonal": diag},
                "aspect_ratio": aspect_ratio,
                "contrast": contrast,
                "notes": palette_notes,
            }
    except Exception:
        return {
            "dimensions": None,
            "aspect_ratio": None,
            "contrast": None,
            "notes": ["Failed to evaluate image."],
        }


