from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw

from generators._common import RenderConfig, _load_font, write_render_manifest


def render_typography_only(text: str, cfg: RenderConfig) -> Image.Image:
    img = Image.new("RGB", (cfg.width, cfg.height), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    font = _load_font(size=cfg.font_size)

    max_width = cfg.width - 2 * cfg.margin
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    y = cfg.margin
    for line in lines[:18]:
        draw.text((cfg.margin, y), line, fill=(0, 0, 0), font=font)
        y += int(cfg.font_size * cfg.line_spacing)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_csv", required=True, help="CSV with column prompt_redacted")
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--width", type=int, default=800)
    ap.add_argument("--height", type=int, default=400)
    ap.add_argument("--font_size", type=int, default=16)
    ap.add_argument("--line_spacing", type=float, default=1.25)
    args = ap.parse_args()

    cfg = RenderConfig(width=args.width, height=args.height, font_size=args.font_size, line_spacing=args.line_spacing)
    df = pd.read_csv(args.data_csv)
    assert "prompt_redacted" in df.columns, "CSV must contain prompt_redacted"

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []

    for i, row in df.iterrows():
        img = render_typography_only(str(row["prompt_redacted"]), cfg)
        img.save(out_dir / f"{i:04d}.png")
        manifest.append({"id": int(i), "template_family": "typography_only", "render_config": cfg.to_dict()})

    write_render_manifest(out_dir / "render_manifest.jsonl", manifest)
    print(f"Wrote {len(df)} images to {out_dir}")


if __name__ == "__main__":
    main()
