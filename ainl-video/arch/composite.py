#!/usr/bin/env python3
"""
Arch Compositor — place Arch on any background without touching his design.
Usage: python3 composite.py <background.png> <output.png> [--scale 0.6] [--x 0.5] [--y 0.65]
"""

import sys
from PIL import Image, ImageFilter
import argparse

def remove_dark_background(img, threshold=40):
    """Remove the circular dark background from Arch, keep just the character."""
    img = img.convert("RGBA")
    data = img.getdata()
    new_data = []
    w, h = img.size
    cx, cy = w // 2, h // 2
    radius = min(w, h) // 2 - 10

    for i, pixel in enumerate(data):
        x = i % w
        y = i // w
        r, g, b, a = pixel
        # Remove pixels that are very dark (the circular background)
        dist = ((x - cx)**2 + (y - cy)**2) ** 0.5
        if r < threshold and g < threshold and b < threshold:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append((r, g, b, a))

    img.putdata(new_data)
    return img

def composite(bg_path, arch_path, output_path, scale=0.62, pos_x=0.5, pos_y=0.68):
    bg = Image.open(bg_path).convert("RGBA")
    arch = Image.open(arch_path).convert("RGBA")

    # Remove dark background from Arch
    arch = remove_dark_background(arch, threshold=35)

    # Resize Arch to scale relative to background
    bg_w, bg_h = bg.size
    arch_w = int(bg_w * scale)
    arch_ratio = arch.size[1] / arch.size[0]
    arch_h = int(arch_w * arch_ratio)
    arch = arch.resize((arch_w, arch_h), Image.LANCZOS)

    # Position: center horizontally, lower third vertically
    paste_x = int(bg_w * pos_x - arch_w / 2)
    paste_y = int(bg_h * pos_y - arch_h / 2)

    # Add subtle drop shadow
    shadow = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", (arch_w, arch_h), (0, 0, 0, 0))
    # Use arch alpha as shadow shape
    r, g, b, a = arch.split()
    shadow_shape = Image.merge("RGBA", [Image.new("L", arch.size, 0),
                                         Image.new("L", arch.size, 0),
                                         Image.new("L", arch.size, 0), a])
    shadow.paste(shadow_shape, (paste_x + 12, paste_y + 16), shadow_shape)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=18))

    # Composite: bg → shadow → arch
    result = Image.alpha_composite(bg, shadow)
    result.paste(arch, (paste_x, paste_y), arch)

    result = result.convert("RGB")
    result.save(output_path, quality=95)
    print(f"Saved: {output_path} ({bg_w}x{bg_h})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("background")
    parser.add_argument("output")
    parser.add_argument("--scale", type=float, default=0.62)
    parser.add_argument("--x", type=float, default=0.5)
    parser.add_argument("--y", type=float, default=0.68)
    args = parser.parse_args()

    composite(args.background, "/data/.openclaw/workspace/ainl-video/arch/arch-canonical.jpg",
              args.output, args.scale, args.x, args.y)
