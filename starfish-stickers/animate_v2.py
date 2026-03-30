#!/usr/bin/env python3
"""
Animate the canonical starfish character.
Each sticker: 512x512 RGBA frames → VP9 WebM with alpha.

Character: kawaii orange starfish, 5 legs, big black eyes, smile.
Design principle: the CHARACTER moves, not just the image. 
Squash/stretch, anticipation, follow-through — cartoon principles.
"""

import os, math, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE_IMG = "/data/.openclaw/workspace/starfish-stickers/character_base.png"
OUT = "/data/.openclaw/workspace/starfish-stickers/animated_v2"
os.makedirs(OUT, exist_ok=True)

FPS = 30
SIZE = 512
CX = SIZE // 2

def load():
    return Image.open(BASE_IMG).convert("RGBA")

def blank():
    return Image.new("RGBA", (SIZE, SIZE), (0,0,0,0))

def compose(base, scale_x=1.0, scale_y=1.0, tx=0, ty=0, angle=0, alpha=255):
    """Transform base image and paste onto transparent frame."""
    frame = blank()
    img = base.copy()
    
    if scale_x != 1.0 or scale_y != 1.0:
        new_w = max(1, int(SIZE * scale_x))
        new_h = max(1, int(SIZE * scale_y))
        img = img.resize((new_w, new_h), Image.LANCZOS)
    
    if angle != 0:
        img = img.rotate(angle, resample=Image.BICUBIC, expand=False)
    
    if alpha != 255:
        r,g,b,a = img.split()
        a = a.point(lambda x: int(x * alpha / 255))
        img = Image.merge("RGBA", (r,g,b,a))
    
    w, h = img.size
    x = CX - w//2 + int(tx)
    y = CX - h//2 + int(ty)
    frame.paste(img, (x, y), img)
    return frame

def easing_out(t):
    return 1 - (1-t)**3

def easing_in_out(t):
    return t*t*(3-2*t)

def spring(t, freq=3, decay=5):
    """Springy oscillation that dampens."""
    return math.sin(t * freq * 2 * math.pi) * math.exp(-decay * t)

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
        "-b:v", "80k", "-crf", "38",
        "-auto-alt-ref", "0",
        "-t", str(duration),
        out_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.rmtree(d)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"  ✓ {name}.webm ({size_kb}KB)")
    return out_path

# ─── GM — Happy morning bounce with squash & stretch ─────────────────────────
def make_gm(base):
    frames = []
    n = FPS * 2
    for i in range(n):
        t = (i / n) * 2  # 2 bounces per loop
        phase = t % 1.0
        
        # Squash on land, stretch on rise — cartoon bounce physics
        if phase < 0.3:  # going up
            p = phase / 0.3
            sy = 1.0 + 0.15 * p          # stretch tall
            sx = 1.0 - 0.1 * p
            ty = -60 * easing_out(p)
        elif phase < 0.5:  # peak
            p = (phase - 0.3) / 0.2
            sy = 1.15 - 0.15 * p
            sx = 0.9 + 0.1 * p
            ty = -60 + 10 * p
        elif phase < 0.8:  # falling
            p = (phase - 0.5) / 0.3
            sy = 1.0 - 0.1 * p           # squash on approach
            sx = 1.0 + 0.05 * p
            ty = -50 + 50 * p
        else:  # land squash + recover
            p = (phase - 0.8) / 0.2
            sy = 0.9 + 0.1 * easing_out(p)
            sx = 1.1 - 0.1 * easing_out(p)
            ty = 0
        
        frames.append(compose(base, scale_x=sx, scale_y=sy, ty=ty))
    return frames

# ─── LFG — Rumble → BLAST OFF ─────────────────────────────────────────────────
def make_lfg(base):
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        if t < 0.3:  # Anticipation — squish down
            p = t / 0.3
            sy = 1.0 - 0.25 * math.sin(p * math.pi)
            sx = 1.0 + 0.2 * math.sin(p * math.pi)
            ty = 30 * math.sin(p * math.pi) + math.sin(t * 80) * 5
            frames.append(compose(base, scale_x=sx, scale_y=sy, ty=ty))
        else:  # LAUNCH — accelerate upward
            p = (t - 0.3) / 0.7
            p2 = p * p * p  # cubic acceleration
            ty = -p2 * 700
            sy = 1.0 + p * 0.4  # stretch as it launches
            sx = 1.0 - p * 0.3
            alpha = max(0, int(255 * (1 - max(0, p - 0.7) / 0.3)))
            frames.append(compose(base, scale_x=sx, scale_y=sy, ty=ty, alpha=alpha))
    return frames

# ─── WAGMI — Double fist pump jump ────────────────────────────────────────────
def make_wagmi(base):
    frames = []
    n = FPS * 2
    for i in range(n):
        t = (i / n) * 2  # 2 pumps
        phase = t % 1.0
        
        jump_h = abs(math.sin(phase * math.pi)) * 90
        sy = 1.0 + 0.12 * abs(math.sin(phase * math.pi))
        sx = 1.0 - 0.08 * abs(math.sin(phase * math.pi))
        
        # Slight tilt on each jump alternating
        angle = math.sin(phase * math.pi) * 8 * (1 if t < 1 else -1)
        
        frames.append(compose(base, scale_x=sx, scale_y=sy, ty=-jump_h, angle=angle))
    return frames

# ─── NGMI — Sad droop + tears ─────────────────────────────────────────────────
def make_ngmi(base):
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        if t < 0.2:  # Hold upright
            frames.append(compose(base))
        elif t < 0.5:  # Slow sad droop
            p = (t - 0.2) / 0.3
            angle = -p * 20
            sy = 1.0 - p * 0.1
            ty = p * 20
            frames.append(compose(base, scale_y=sy, ty=ty, angle=angle))
        else:  # Slumped, slight shake of despair
            p = (t - 0.5) / 0.5
            shake = math.sin(p * 20) * 4 * (1 - p)
            frames.append(compose(base, scale_y=0.9, ty=20, angle=-20 + shake))
    return frames

# ─── DIAMOND HANDS — Pulse glow + slow proud spin ────────────────────────────
def make_diamond(base):
    frames = []
    n = FPS * 3
    for i in range(n):
        t = i / n
        # Majestic slow rotation with pulsing scale
        angle = t * 360 * 0.4  # slow almost-full rotation
        pulse = 1.0 + 0.08 * math.sin(t * 6 * math.pi)
        frames.append(compose(base, scale_x=pulse, scale_y=pulse, angle=angle))
    return frames

# ─── ATH — Start tiny, ZOOM to full, victory wiggle ──────────────────────────
def make_ath(base):
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        if t < 0.5:  # zoom in
            p = easing_out(t / 0.5)
            scale = 0.1 + p * 0.95
            frames.append(compose(base, scale_x=scale, scale_y=scale))
        else:  # victory wiggle
            p = (t - 0.5) / 0.5
            wiggle = math.sin(p * 8 * math.pi) * 8 * (1 - p)
            scale = 1.05 - p * 0.05
            frames.append(compose(base, scale_x=scale, scale_y=scale, angle=wiggle))
    return frames

# ─── BIG BUY — SWELL UP huge, settle with satisfaction ───────────────────────
def make_bigbuy(base):
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        if t < 0.4:  # GROW
            p = easing_out(t / 0.4)
            scale = 1.0 + p * 0.55
        elif t < 0.6:  # overshoot settle
            p = (t - 0.4) / 0.2
            scale = 1.55 - p * 0.1
        else:  # happy satisfied bob
            p = (t - 0.6) / 0.4
            scale = 1.45 + math.sin(p * 4 * math.pi) * 0.04
        bob = math.sin(t * 5 * math.pi) * 6
        frames.append(compose(base, scale_x=min(scale, 1.55), scale_y=min(scale, 1.55), ty=bob))
    return frames

# ─── REKT — Dramatic spin-crash fall ─────────────────────────────────────────
def make_rekt(base):
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        if t < 0.15:  # freeze of horror
            shake = math.sin(t * 100) * 6
            frames.append(compose(base, tx=shake))
        else:
            p = (t - 0.15) / 0.85
            angle = -p * p * 540  # accelerating spin
            ty = p * p * 600
            scale = 1.0 - p * 0.5
            alpha = max(0, int(255 * (1 - max(0, p - 0.6) / 0.4)))
            frames.append(compose(base, scale_x=scale, scale_y=scale, ty=ty, angle=angle, alpha=alpha))
    return frames

# ─── WEN MOON — Float upward dreamily, stars twinkle ─────────────────────────
def make_wenmoon(base):
    frames = []
    n = FPS * 3
    for i in range(n):
        t = i / n
        # Dreamy float up with gentle sway
        ty = -t * 120
        sway = math.sin(t * 3 * math.pi) * 12
        scale = 1.0 + 0.04 * math.sin(t * 5 * math.pi)
        angle = math.sin(t * 2 * math.pi) * 6
        alpha = int(255 * (1 - max(0, t - 0.75) / 0.25))  # fade at top
        frames.append(compose(base, scale_x=scale, scale_y=scale, tx=sway, ty=ty, angle=angle, alpha=alpha))
    return frames

# ─── HIGHER — Hypnotic zoom spin (gets big, fills screen) ────────────────────
def make_higher(base):
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        # Zoom from far to fill + spin
        scale = 0.2 + easing_in_out(t) * 1.1
        angle = t * 540  # 1.5 spins
        frames.append(compose(base, scale_x=min(scale,1.3), scale_y=min(scale,1.3), angle=angle))
    return frames

# ─── Run all ──────────────────────────────────────────────────────────────────
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

base = load()
for name, fn, dur in STICKERS:
    print(f"Generating {name}...")
    frames = fn(base)
    save_and_render(frames, name, duration=dur)

print("\n✅ All done!")
