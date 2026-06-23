from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw

from generators._common import RenderConfig, _load_font, write_render_manifest


def render_diagram(text: str, cfg: RenderConfig) -> Image.Image:
    img = Image.new("RGB", (cfg.width, cfg.height), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)
    font = _load_font(preferred="DejaVuSans.ttf", size=cfg.font_size)

    box_w, box_h = int(cfg.width * 0.35), int(cfg.height * 0.20)
    x1, y1 = cfg.margin, int(cfg.height * 0.20)
    x2, y2 = x1 + box_w, y1 + box_h
    draw.rectangle([x1, y1, x2, y2], outline=(0, 0, 0), width=2)
    draw.text((x1 + 8, y1 + 8), "Step A", fill=(0, 0, 0), font=font)

    x3, y3 = int(cfg.width * 0.55), int(cfg.height * 0.20)
    x4, y4 = x3 + box_w, y3 + box_h
    draw.rectangle([x3, y3, x4, y4], outline=(0, 0, 0), width=2)
    draw.text((x3 + 8, y3 + 8), "Step B", fill=(0, 0, 0), font=font)
    draw.line([x2, y1 + box_h // 2, x3, y3 + box_h // 2], fill=(0, 0, 0), width=2)
    draw.polygon([(x3, y3 + box_h // 2), (x3 - 10, y3 + box_h // 2 - 6), (x3 - 10, y3 + box_h // 2 + 6)], fill=(0, 0, 0))

    cap_y = int(cfg.height * 0.60)
    draw.rectangle([cfg.margin, cap_y, cfg.width - cfg.margin, cfg.height - cfg.margin], outline=(120, 120, 120), width=1)
    draw.text((cfg.margin + 8, cap_y + 6), "Legend / Notes:", fill=(80, 80, 80), font=font)

    max_width = cfg.width - 2 * cfg.margin - 16
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

    y = cap_y + int(cfg.font_size * 1.7)
    for line in lines[:7]:
        draw.text((cfg.margin + 8, y), line, fill=(0, 0, 0), font=font)
        y += int(cfg.font_size * cfg.line_spacing)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_csv", required=True)
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
        img = render_diagram(str(row["prompt_redacted"]), cfg)
        img.save(out_dir / f"{i:04d}.png")
        manifest.append({"id": int(i), "template_family": "diagram", "render_config": cfg.to_dict()})

    write_render_manifest(out_dir / "render_manifest.jsonl", manifest)
    print(f"Wrote {len(df)} images to {out_dir}")


if __name__ == "__main__":
    main()
