from __future__ import annotations

from dataclasses import dataclass
import io
from typing import Tuple

from PIL import Image


@dataclass(frozen=True)
class TransformSpec:
    name: str = 'none'


def _parse_resolution(spec: str) -> Tuple[int, int] | None:
    if spec == 'max':
        return None
    if 'x' not in spec:
        raise ValueError(f'Invalid resolution: {spec}')
    w, h = spec.lower().split('x', 1)
    return int(w), int(h)


def normalize_resolution(img: Image.Image, spec: str) -> Image.Image:
    parsed = _parse_resolution(spec)
    if parsed is None:
        return img.copy()
    return img.resize(parsed, Image.Resampling.LANCZOS)


def apply_transform(img: Image.Image, spec: TransformSpec) -> Image.Image:
    name = (spec.name or 'none').lower()
    if name == 'none':
        return img.copy()
    if name.startswith('resize'):
        factor = float(name.replace('resize', ''))
        w = max(1, int(round(img.width * factor)))
        h = max(1, int(round(img.height * factor)))
        return img.resize((w, h), Image.Resampling.LANCZOS)
    if name.startswith('jpeg'):
        quality = int(name.replace('jpeg', ''))
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality)
        buf.seek(0)
        return Image.open(buf).convert('RGB')
    raise ValueError(f'Unsupported transform: {spec.name}')
