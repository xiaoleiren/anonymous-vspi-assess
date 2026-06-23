from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw

from generators._common import RenderConfig, _load_font, write_render_manifest


def render_terminal(text: str, cfg: RenderConfig) -> Image.Image:
    img = Image.new("RGB", (cfg.width, cfg.height), color=(18, 18, 18))
    draw = ImageDraw.Draw(img)
    font = _load_font(size=cfg.font_size)

    bar_h = int(cfg.font_size * 2)
    draw.rectangle([0, 0, cfg.width, bar_h], fill=(35, 35, 35))
    draw.text((cfg.margin, int(bar_h * 0.25)), "terminal.log — read-only", fill=(200, 200, 200), font=font)

    max_width = cfg.width - 2 * cfg.margin
    words = text.split()
    lines, cur = [], ""
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

    y = bar_h + cfg.margin
    prefix = "[INFO] "
    for line in lines[:16]:
        draw.text((cfg.margin, y), prefix + line, fill=(210, 210, 210), font=font)
        y += int(cfg.font_size * cfg.line_spacing)

    draw.text((cfg.margin, min(cfg.height - cfg.margin - cfg.font_size, y + cfg.font_size)), "$", fill=(120, 220, 120), font=font)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_csv", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--width", type=int, default=800)
    ap.add_argument("--height", type=int, default=400)
    ap.add_argument("--font_size", type=int, default=16)
    ap.add_argument("--line_spacing", type=float, default=1.30)
    args = ap.parse_args()

    cfg = RenderConfig(width=args.width, height=args.height, font_size=args.font_size, line_spacing=args.line_spacing)
    df = pd.read_csv(args.data_csv)
    assert "prompt_redacted" in df.columns, "CSV must contain prompt_redacted"

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []

    for i, row in df.iterrows():
        img = render_terminal(str(row["prompt_redacted"]), cfg)
        img.save(out_dir / f"{i:04d}.png")
        manifest.append({"id": int(i), "template_family": "terminal", "render_config": cfg.to_dict()})

    write_render_manifest(out_dir / "render_manifest.jsonl", manifest)
    print(f"Wrote {len(df)} images to {out_dir}")


if __name__ == "__main__":
    main()
