#!/usr/bin/env python3
"""
Starfish Sticker Pack Processor
- Removes background using rembg (AI-powered)
- Formats to Telegram spec: 512x512 PNG, transparent bg
- Adds optional white outline for visibility
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("rembg not available, using fallback")

INPUT_DIR = Path("/data/.openclaw/workspace/starfish-stickers/output")
OUTPUT_DIR = Path("/data/.openclaw/workspace/starfish-stickers/stickers")
OUTPUT_DIR.mkdir(exist_ok=True)

TARGET_SIZE = 512


def add_white_outline(img: Image.Image, thickness: int = 8) -> Image.Image:
    """Add a white outline around the subject for better visibility."""
    # Get alpha channel
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    r, g, b, alpha = img.split()
    alpha_arr = np.array(alpha)
    
    # Dilate the alpha to create outline mask
    from PIL import ImageFilter
    outline_mask = Image.fromarray(alpha_arr)
    for _ in range(thickness // 2):
        outline_mask = outline_mask.filter(ImageFilter.MaxFilter(3))
    
    # Create white layer same size
    white = Image.new("RGBA", img.size, (255, 255, 255, 255))
    white.putalpha(outline_mask)
    
    # Composite: white behind original
    result = Image.new("RGBA", img.size, (0, 0, 0, 0))
    result.paste(white, (0, 0))
    result.paste(img, (0, 0), img)
    return result


def fit_to_512(img: Image.Image) -> Image.Image:
    """Fit image into 512x512 canvas preserving aspect ratio."""
    img.thumbnail((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
    canvas = Image.new("RGBA", (TARGET_SIZE, TARGET_SIZE), (0, 0, 0, 0))
    x = (TARGET_SIZE - img.width) // 2
    y = (TARGET_SIZE - img.height) // 2
    canvas.paste(img, (x, y), img if img.mode == "RGBA" else None)
    return canvas


def process_sticker(src: Path, add_outline: bool = True) -> Path:
    name = src.stem
    out_path = OUTPUT_DIR / f"{name}.png"
    
    print(f"Processing: {name}...", end=" ", flush=True)
    
    with open(src, "rb") as f:
        input_bytes = f.read()
    
    if REMBG_AVAILABLE:
        # AI background removal
        output_bytes = remove(input_bytes)
        img = Image.open(__import__("io").BytesIO(output_bytes)).convert("RGBA")
    else:
        # Fallback: open and hope it already has transparency
        img = Image.open(src).convert("RGBA")
    
    if add_outline:
        img = add_white_outline(img, thickness=12)
    
    img = fit_to_512(img)
    img.save(out_path, "PNG", optimize=True)
    
    size_kb = out_path.stat().st_size / 1024
    print(f"✓ ({size_kb:.0f}KB)")
    return out_path


if __name__ == "__main__":
    sources = sorted(INPUT_DIR.glob("*.webp"))
    print(f"Found {len(sources)} stickers to process\n")
    
    processed = []
    for src in sources:
        try:
            out = process_sticker(src, add_outline=True)
            processed.append(out)
        except Exception as e:
            print(f"✗ ERROR on {src.name}: {e}")
    
    print(f"\n✅ Done! {len(processed)}/{len(sources)} stickers saved to:")
    print(f"   {OUTPUT_DIR}")
    print(f"\nFiles:")
    for p in sorted(OUTPUT_DIR.glob("*.png")):
        print(f"  - {p.name} ({p.stat().st_size//1024}KB)")
