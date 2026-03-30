#!/usr/bin/env python3
"""
Pixel art animated sticker pack — ALL BULLISH DEGEN EDITION
Stickers: GM, LFG, WAGMI, SEND IT, DIAMOND HANDS, ATH, APE IN, 1000X, WEN MOON, HIGHER
12fps retro sprite style.
"""

import os, math, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_IMG = "/data/.openclaw/workspace/starfish-stickers/character_v2.png"
OUT = "/data/.openclaw/workspace/starfish-stickers/pixel_v2"
os.makedirs(OUT, exist_ok=True)

FPS = 12
SIZE = 512
GRID = 32  # pixel grid size

PALETTE = [
    (0, 0, 0, 0),
    (210, 60, 20, 255),
    (235, 90, 20, 255),
    (255, 130, 30, 255),
    (255, 170, 50, 255),
    (255, 210, 80, 255),
    (15, 15, 15, 255),
    (255, 255, 255, 255),
    (200, 30, 30, 255),
    (160, 40, 10, 255),
]

def pixelate(img, grid=GRID):
    small = img.resize((grid, grid), Image.LANCZOS)
    data = np.array(small)
    out = np.zeros_like(data)
    for y in range(grid):
        for x in range(grid):
            px = data[y, x]
            if px[3] < 30:
                out[y, x] = [0, 0, 0, 0]
                continue
            best, best_dist = None, float('inf')
            for col in PALETTE[1:]:
                dist = sum((int(px[i]) - int(col[i]))**2 for i in range(3))
                if dist < best_dist:
                    best_dist = dist
                    best = col
            out[y, x] = best
    return Image.fromarray(out.astype(np.uint8), 'RGBA')

def blank():
    return Image.new("RGBA", (SIZE, SIZE), (0,0,0,0))

def compose(pix_small, scale=1.0, tx=0, ty=0, flip=False, label=None, label_color=(255,220,0,255)):
    frame = blank()
    scaled_grid = max(4, int(GRID * scale))
    scaled_img = pix_small.resize((scaled_grid, scaled_grid), Image.NEAREST)
    if flip:
        scaled_img = scaled_img.transpose(Image.FLIP_LEFT_RIGHT)
    block = SIZE // GRID
    final_size = scaled_grid * block
    final = scaled_img.resize((final_size, final_size), Image.NEAREST)
    cx, cy = SIZE//2, SIZE//2
    x = cx - final_size//2 + int(tx)
    y = cy - final_size//2 + int(ty)
    frame.paste(final, (x, y), final)
    
    if label:
        draw = ImageDraw.Draw(frame)
        # Big bold pixel-style label at bottom
        font_size = 52
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0,0), label, font=font)
        tw = bbox[2] - bbox[0]
        lx = (SIZE - tw) // 2
        ly = SIZE - font_size - 20
        # Black shadow
        draw.text((lx+3, ly+3), label, font=font, fill=(0,0,0,200))
        # Main text
        draw.text((lx, ly), label, font=font, fill=label_color)
    
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
        "-b:v", "80k", "-crf", "40",
        "-auto-alt-ref", "0",
        "-t", str(duration),
        out_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.rmtree(d)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"  ✓ {name}.webm ({size_kb}KB)")

# Load + pixelate
base = Image.open(BASE_IMG).convert("RGBA")
pix = pixelate(base)

# ─── GM — Happy bob, "GM" text pulses in ─────────────────────────────────────
def make_gm(p):
    frames = []
    for i in range(24):
        phase = (i % 8) / 8
        ty = -8 if phase < 0.5 else 0
        sy = 0.95 if phase < 0.5 else 1.0
        show_label = i >= 8
        frames.append(compose(p, scale=sy, ty=ty, label="GM" if show_label else None, label_color=(255,220,0,255)))
    return frames

# ─── LFG — Shake + BLAST OFF with trail ──────────────────────────────────────
def make_lfg(p):
    frames = []
    # Shake anticipation
    for i in range(6):
        tx = ((-1)**i) * 8
        frames.append(compose(p, tx=tx, label="LFG!", label_color=(255,80,20,255)))
    # LAUNCH
    for i in range(18):
        progress = i / 18
        ty = -progress * progress * 420
        scale = 1.0 - progress * 0.7
        frames.append(compose(p, scale=max(0.05, scale), ty=ty))
    return frames

# ─── WAGMI — Victory jumps, gets BIGGER each jump ────────────────────────────
def make_wagmi(p):
    frames = []
    for jump in range(3):
        scale = 1.0 + jump * 0.1  # gets bigger each jump — confidence growing
        arc = [8, -15, -55, -90, -90, -55, -15, 8]
        for ty in arc:
            frames.append(compose(p, scale=scale, ty=ty, label="WAGMI", label_color=(0,255,120,255)))
    return frames

# ─── SEND IT — Wind up and YEET forward ──────────────────────────────────────
def make_sendit(p):
    frames = []
    # Lean back (wind up)
    for i in range(4):
        frames.append(compose(p, tx=-12, scale=0.95, label="SEND", label_color=(255,50,50,255)))
    # SEND IT — zoom right and grow
    for i in range(20):
        progress = i / 20
        tx = progress * progress * 300
        scale = 1.0 + progress * 0.4
        frames.append(compose(p, tx=tx, scale=min(scale, 1.4), label="IT!!!" if i > 5 else None, label_color=(255,50,50,255)))
    return frames

# ─── DIAMOND HANDS — Slow spin, never flinches ────────────────────────────────
def make_diamond(p):
    frames = []
    spin = [
        (1.0, False), (1.0, False), (1.0, False), (1.0, False),
        (0.6, False), (0.2, False), (0.2, True), (0.6, True),
        (1.0, True),  (1.0, True),  (1.0, True),  (1.0, True),
        (0.6, True),  (0.2, True),  (0.2, False), (0.6, False),
    ]
    for _ in range(3):
        for scale, flip in spin:
            frames.append(compose(p, scale=scale, flip=flip, label="💎 HOLD", label_color=(100,220,255,255)))
    return frames

# ─── ATH — Zooms in from tiny, stamp effect ───────────────────────────────────
def make_ath(p):
    frames = []
    scales = [0.05, 0.1, 0.18, 0.28, 0.4, 0.55, 0.7, 0.88, 1.0, 1.15, 1.05, 1.0]
    for s in scales:
        frames.append(compose(p, scale=s))
    # Victory pulse
    for i in range(12):
        pulse = 1.0 + 0.08 * ((i % 2) * 2 - 1)
        frames.append(compose(p, scale=pulse, label="ATH 📈", label_color=(0,255,100,255)))
    return frames

# ─── APE IN — Starts tiny (far away) runs toward camera getting huge ─────────
def make_apein(p):
    frames = []
    scales = [0.08, 0.12, 0.18, 0.25, 0.35, 0.46, 0.58, 0.7, 0.82, 0.94, 1.05, 1.15,
              1.22, 1.15, 1.22, 1.15, 1.22, 1.15, 1.22, 1.15, 1.22, 1.15, 1.22, 1.15]
    for i, s in enumerate(scales):
        label = "APE IN" if i >= 10 else None
        frames.append(compose(p, scale=min(s, 1.2), label=label, label_color=(255,165,0,255)))
    return frames

# ─── 1000X — Number flickers up, character spins in excitement ───────────────
def make_1000x(p):
    frames = []
    nums = ["1X","2X","5X","10X","25X","50X","100X","250X","500X","1000X"]
    colors = [
        (255,255,100,255),(255,220,80,255),(255,180,60,255),(255,140,40,255),
        (255,100,20,255),(255,60,20,255),(255,20,20,255),(200,0,200,255),
        (100,0,255,255),(255,215,0,255)
    ]
    for num, col in zip(nums, colors):
        scale = 0.7 + (nums.index(num) / len(nums)) * 0.5
        frames.append(compose(p, scale=min(scale,1.2), label=num, label_color=col))
        frames.append(compose(p, scale=min(scale,1.2), label=num, label_color=col))
    # Flash finale
    for _ in range(4):
        frames.append(compose(p, scale=1.2, label="1000X 🚀", label_color=(255,215,0,255)))
        frames.append(compose(p, scale=1.1, label="1000X 🚀", label_color=(255,100,100,255)))
    return frames

# ─── WEN MOON — Float dreamily up ────────────────────────────────────────────
def make_wenmoon(p):
    frames = []
    n = 36
    for i in range(n):
        progress = i / n
        ty = -progress * 230
        tx = math.sin(progress * 4 * math.pi) * 10
        show_label = i > 6
        frames.append(compose(p, ty=ty, tx=tx, label="WEN MOON? 🌙" if show_label else None, label_color=(200,200,255,255)))
    return frames

# ─── HIGHER — Hypnotic zoom, keeps going up ───────────────────────────────────
def make_higher(p):
    frames = []
    scales = [0.08, 0.12, 0.18, 0.26, 0.36, 0.48, 0.62, 0.78, 0.95, 1.1, 1.2, 1.1,
              1.2, 1.1, 1.2, 1.1, 1.2, 1.1, 1.2, 1.1, 1.2, 1.1, 1.2, 1.1]
    flips = [False]*9 + [True, False, True, False, True, False, True, False, True, False, True, False, True, False, True]
    for i, (s, flip) in enumerate(zip(scales, flips)):
        label = "HIGHER" if i >= 8 else None
        frames.append(compose(p, scale=min(s,1.2), flip=flip, label=label, label_color=(255,215,0,255)))
    return frames

STICKERS = [
    ("gm",            make_gm,      2),
    ("lfg",           make_lfg,     2),
    ("wagmi",         make_wagmi,   2),
    ("send_it",       make_sendit,  2),
    ("diamond_hands", make_diamond, 3),
    ("ath",           make_ath,     2),
    ("ape_in",        make_apein,   2),
    ("1000x",         make_1000x,   2),
    ("wen_moon",      make_wenmoon, 3),
    ("higher",        make_higher,  2),
]

for name, fn, dur in STICKERS:
    print(f"Generating {name}...")
    frames = fn(pix)
    save_and_render(frames, name, duration=dur)

print("\n✅ Bullish degen pack done!")
