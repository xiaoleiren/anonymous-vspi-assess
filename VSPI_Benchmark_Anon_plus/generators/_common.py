from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Iterable, List, Dict, Any
import json

from PIL import ImageFont


@dataclass(frozen=True)
class RenderConfig:
    width: int = 800
    height: int = 400
    font_size: int = 16
    margin: int = 16
    line_spacing: float = 1.25
    opacity: int = 255
    placement: str = "default"
    mild_artifact: str = "none"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_font(preferred: Optional[str] = None, size: int = 16):
    candidates = []
    if preferred:
        candidates.append(preferred)
    candidates.extend([
        "DejaVuSansMono.ttf",
        "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ])
    for cand in candidates:
        try:
            return ImageFont.truetype(cand, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def write_render_manifest(path: str | Path, rows: Iterable[Dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def parse_bin_grid(value: str, cast_fn=int) -> List[Any]:
    return [cast_fn(v.strip()) for v in value.split(",") if v.strip()]
