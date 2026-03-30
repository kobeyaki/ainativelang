#!/usr/bin/env python3
"""
Pixel art animated sticker pack.
Approach: downscale character to 32x32, quantize to limited palette,
upscale back to 512x512 with nearest-neighbor (chunky pixels).
Animate with 8-frame choppy motion — retro game feel.
"""

import os, math, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImagePalette

BASE_IMG = "/data/.openclaw/workspace/starfish-stickers/character_v2.png"
OUT = "/data/.openclaw/workspace/starfish-stickers/pixel"
os.makedirs(OUT, exist_ok=True)

FPS = 12   # intentionally choppy — 12fps like old game sprites
SIZE = 512
PIXEL_SIZE = 16  # each "pixel" = 16x16 block → 32x32 grid

# Starfish palette — locked colors
PALETTE = [
    (0, 0, 0, 0),           # transparent
    (210, 60, 20, 255),     # dark red
    (235, 90, 20, 255),     # medium orange-red
    (255, 130, 30, 255),    # bright orange
    (255, 170, 50, 255),    # light orange
    (255, 210, 80, 255),    # yellow-orange (spots)
    (15, 15, 15, 255),      # near-black (eyes, outline)
    (255, 255, 255, 255),   # white (eye shine)
    (200, 30, 30, 255),     # mouth/tongue
    (160, 40, 10, 255),     # dark outline
]

def pixelate(img, grid=32):
    """Downscale to grid, quantize to palette, upscale to 512."""
    small = img.resize((grid, grid), Image.LANCZOS)
    data = np.array(small)
    
    out = np.zeros_like(data)
    for y in range(grid):
        for x in range(grid):
            px = data[y, x]
            if px[3] < 30:
                out[y, x] = [0, 0, 0, 0]
                continue
            # Find nearest palette color
            best = None
            best_dist = float('inf')
            for col in PALETTE[1:]:  # skip transparent
                dist = sum((int(px[i]) - int(col[i]))**2 for i in range(3))
                if dist < best_dist:
                    best_dist = dist
                    best = col
            out[y, x] = best
    
    pixelated = Image.fromarray(out.astype(np.uint8), 'RGBA')
    # Scale up with NEAREST for blocky pixel look
    big = pixelated.resize((SIZE, SIZE), Image.NEAREST)
    return big, pixelated  # full size + small grid

def blank():
    return Image.new("RGBA", (SIZE, SIZE), (0,0,0,0))

def compose_pixel(pix_small, scale=1.0, tx=0, ty=0, flip=False):
    """Scale up pixel art and compose on frame."""
    frame = blank()
    scaled_grid = max(8, int(32 * scale))
    scaled_img = pix_small.resize((scaled_grid, scaled_grid), Image.NEAREST)
    if flip:
        scaled_img = scaled_img.transpose(Image.FLIP_LEFT_RIGHT)
    # Upscale to pixel block size
    block = SIZE // 32
    final_size = scaled_grid * block
    final = scaled_img.resize((final_size, final_size), Image.NEAREST)
    
    cx, cy = SIZE//2, SIZE//2
    x = cx - final_size//2 + int(tx)
    y = cy - final_size//2 + int(ty)
    frame.paste(final, (x, y), final)
    return frame

def save_and_render(frames, name, fps=FPS, duration=2):
    d = os.path.join(OUT, f"frames_{name}")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    for i, f in enumerate(frames):
        f.save(os.path.join(d, f"f{i:04d}.png"))
    
    out_path = os.path.join(OUT, f"{name}.webm")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(d, "f%04d.png"),
        "-c:v", "libvpx-vp9",
        "-pix_fmt", "yuva420p",
        "-b:v", "60k", "-crf", "42",
        "-auto-alt-ref", "0",
        "-t", str(duration),
        out_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.rmtree(d)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"  ✓ {name}.webm ({size_kb}KB)")
    return out_path

def add_scanlines(frame):
    """Optional: add subtle scanline overlay for retro CRT feel."""
    overlay = Image.new("RGBA", (SIZE, SIZE), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    for y in range(0, SIZE, 4):
        draw.line([(0, y), (SIZE, y)], fill=(0, 0, 0, 30))
    return Image.alpha_composite(frame, overlay)

# Load and pixelate base
base = Image.open(BASE_IMG).convert("RGBA")
_, pix = pixelate(base, grid=32)

# ─── GM — 2-frame idle bob (game idle animation) ─────────────────────────────
def make_gm(p):
    frames = []
    # Frame sequence: up, up, neutral, neutral, down-squish, down-squish, neutral, neutral
    poses = [
        (1.0, 1.0, 0, -6),    # neutral up
        (1.0, 1.0, 0, -6),
        (1.0, 1.0, 0, 0),     # neutral
        (1.0, 1.0, 0, 0),
        (1.05, 0.95, 0, 4),   # squish down
        (1.05, 0.95, 0, 4),
        (1.0, 1.0, 0, 0),     # back
        (1.0, 1.0, 0, 0),
    ]
    # Repeat 3x for 2s at 12fps = 24 frames total
    for _ in range(3):
        for sx, sy, tx, ty in poses:
            frames.append(compose_pixel(p, scale=min(sx, sy)))
    return frames

# ─── LFG — Run cycle then launch ─────────────────────────────────────────────
def make_lfg(p):
    frames = []
    # Running frames (tilt alternating + bounce)
    run = [
        (1.0, -4), (1.0, 0), (1.0, -4), (1.0, 0),
        (1.0, -4), (1.0, 0), (1.0, -4), (1.0, 0),
    ]
    for scale, ty in run:
        frames.append(compose_pixel(p, scale=scale, ty=ty))
    # LAUNCH — shrink (distance) + move up fast
    for i in range(16):
        progress = i / 16
        scale = 1.0 - progress * 0.85
        ty = -progress * progress * 350
        frames.append(compose_pixel(p, scale=max(0.1, scale), ty=ty))
    return frames

# ─── WAGMI — Classic jump arc ─────────────────────────────────────────────────
def make_wagmi(p):
    frames = []
    arc = [
        (0.95, 1.05, 8),    # crouch
        (0.95, 1.05, 8),
        (1.0, 1.0, -20),    # leaving ground
        (0.95, 1.05, -60),  # rising
        (0.9, 1.1, -90),    # peak
        (0.9, 1.1, -90),    # peak hold
        (0.95, 1.05, -60),  # falling
        (1.0, 1.0, -20),    # landing approach
        (1.1, 0.9, 10),     # land squash
        (1.1, 0.9, 10),
        (1.0, 1.0, 0),      # recover
        (1.0, 1.0, 0),
    ]
    for _ in range(2):
        for sx, sy, ty in arc:
            frames.append(compose_pixel(p, scale=min(sx,sy), ty=ty))
    return frames

# ─── NGMI — Shake head, slump ────────────────────────────────────────────────
def make_ngmi(p):
    frames = []
    # Shake left/right rapidly
    shakes = [(-12,0),(12,0),(-10,0),(10,0),(-8,0),(8,0),(-4,0),(4,0),(0,0),(0,0)]
    for tx, ty in shakes:
        frames.append(compose_pixel(p, tx=tx, ty=ty))
    # Slow slump down
    for i in range(14):
        progress = i / 14
        ty = progress * 40
        scale = 1.0 - progress * 0.2
        frames.append(compose_pixel(p, scale=scale, ty=ty))
    return frames

# ─── DIAMOND HANDS — Idle sparkle spin ───────────────────────────────────────
def make_diamond(p):
    frames = []
    # Pixel art "spin" = flip trick: normal, squash thin (turning), flip, thin, normal
    spin_seq = [
        (1.0, False),  # normal
        (1.0, False),
        (1.0, False),
        (0.6, False),  # squish (turning)
        (0.2, False),  # nearly edge-on
        (0.2, True),   # flip
        (0.6, True),   # expanding flip side
        (1.0, True),   # full flip
        (1.0, True),
        (1.0, True),
        (0.6, True),
        (0.2, True),
        (0.2, False),
        (0.6, False),
    ]
    for _ in range(3):
        for scale, flip in spin_seq:
            frames.append(compose_pixel(p, scale=scale, flip=flip))
    return frames

# ─── ATH — NUMBER GO UP zoom in ──────────────────────────────────────────────
def make_ath(p):
    frames = []
    # Start tiny, grow each frame
    scales = [0.1, 0.15, 0.2, 0.28, 0.38, 0.5, 0.62, 0.75, 0.85, 0.93, 1.0, 1.0,
              1.05, 1.0, 1.05, 1.0, 1.05, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    for s in scales:
        frames.append(compose_pixel(p, scale=s))
    return frames

# ─── BIG BUY — GROW BIG pixel by pixel ───────────────────────────────────────
def make_bigbuy(p):
    frames = []
    # Grow and pulse
    grow = [0.5, 0.6, 0.7, 0.85, 1.0, 1.15, 1.3, 1.4, 1.45, 1.4, 1.45, 1.4,
            1.45, 1.4, 1.45, 1.4, 1.45, 1.4, 1.45, 1.4, 1.45, 1.4, 1.45, 1.4]
    for s in grow:
        frames.append(compose_pixel(p, scale=min(s, 1.4)))
    return frames

# ─── REKT — Pixelated death animation ────────────────────────────────────────
def make_rekt(p):
    frames = []
    # Hold, shake, fall off screen
    for _ in range(4):
        frames.append(compose_pixel(p))
    shake_seq = [(-10,0),(10,0),(-10,0),(10,0),(-8,0),(8,0),(0,0),(0,0)]
    for tx, ty in shake_seq:
        frames.append(compose_pixel(p, tx=tx))
    # Fall + shrink
    for i in range(12):
        progress = (i+1)/12
        ty = progress * progress * 400
        scale = 1.0 - progress * 0.6
        frames.append(compose_pixel(p, scale=max(0.1,scale), ty=ty))
    return frames

# ─── WEN MOON — Float up dreamy ──────────────────────────────────────────────
def make_wenmoon(p):
    frames = []
    n = 36  # 3s at 12fps
    for i in range(n):
        progress = i / n
        ty = -progress * 250
        # Gentle sway
        tx = math.sin(progress * 4 * math.pi) * 10
        frames.append(compose_pixel(p, ty=ty, tx=tx))
    return frames

# ─── HIGHER — Zoom spin, pixel style ─────────────────────────────────────────
def make_higher(p):
    frames = []
    scales = [0.1, 0.15, 0.22, 0.3, 0.4, 0.5, 0.62, 0.75, 0.88, 1.0, 1.1, 1.2,
              1.1, 1.2, 1.1, 1.2, 1.1, 1.2, 1.1, 1.2, 1.1, 1.2, 1.1, 1.2]
    flips = [False]*6 + [True]*6 + [False]*6 + [True]*6
    for s, flip in zip(scales, flips):
        frames.append(compose_pixel(p, scale=min(s, 1.2), flip=flip))
    return frames

STICKERS = [
    ("gm",            make_gm,      2),
    ("lfg",           make_lfg,     2),
    ("wagmi",         make_wagmi,   2),
    ("ngmi",          make_ngmi,    2),
    ("diamond_hands", make_diamond, 3),
    ("ath",           make_ath,     2),
    ("big_buy",       make_bigbuy,  2),
    ("rekt",          make_rekt,    2),
    ("wen_moon",      make_wenmoon, 3),
    ("higher",        make_higher,  2),
]

for name, fn, dur in STICKERS:
    print(f"Generating {name}...")
    frames = fn(pix)
    save_and_render(frames, name, duration=dur)

print("\n✅ All pixel art done!")
