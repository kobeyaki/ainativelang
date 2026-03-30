#!/usr/bin/env python3
"""
Generate animated WebM sticker frames for Telegram animated stickers.
Each sticker: 512x512 RGBA PNG frames → ffmpeg → VP9 WebM with alpha.
"""

import os, math, subprocess, shutil
from PIL import Image, ImageDraw

SRC = "/data/.openclaw/workspace/starfish-stickers/stickers"
OUT = "/data/.openclaw/workspace/starfish-stickers/animated"
os.makedirs(OUT, exist_ok=True)

FPS = 30
SIZE = 512
CENTER = SIZE // 2

def load(name):
    return Image.open(os.path.join(SRC, name)).convert("RGBA").resize((SIZE, SIZE), Image.LANCZOS)

def save_frames(frames, name):
    d = os.path.join(OUT, f"frames_{name}")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    for i, f in enumerate(frames):
        f.save(os.path.join(d, f"frame_{i:04d}.png"))
    return d

def render_webm(frames_dir, out_path, fps=FPS):
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(frames_dir, "frame_%04d.png"),
        "-c:v", "libvpx-vp9",
        "-pix_fmt", "yuva420p",
        "-b:v", "0",
        "-crf", "24",
        "-auto-alt-ref", "0",
        "-t", "3",        # max 3 seconds for TG stickers
        out_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.rmtree(frames_dir)
    print(f"  ✓ {out_path}")

def compose(base, scale=1.0, tx=0, ty=0, angle=0):
    """Return a 512x512 RGBA frame with base transformed."""
    frame = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    img = base.copy()
    if scale != 1.0:
        new_s = max(1, int(SIZE * scale))
        img = img.resize((new_s, new_s), Image.LANCZOS)
    if angle != 0:
        img = img.rotate(angle, resample=Image.BICUBIC, expand=False)
    w, h = img.size
    x = CENTER - w // 2 + int(tx)
    y = CENTER - h // 2 + int(ty)
    frame.paste(img, (x, y), img)
    return frame

# ─── GM — Happy bouncing sunrise bob ───────────────────────────────────────────
def make_gm():
    base = load("gm.png")
    frames = []
    n = FPS * 2  # 2s loop
    for i in range(n):
        t = i / n
        # gentle bob up/down + slight scale pulse
        bob = math.sin(t * 2 * math.pi) * 18
        scale = 1.0 + 0.04 * math.sin(t * 4 * math.pi)
        frames.append(compose(base, scale=scale, ty=bob))
    return frames

# ─── LFG — ROCKET LAUNCH ────────────────────────────────────────────────────
def make_lfg():
    base = load("lfg.png")
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        # shake at start, then blast off upward
        if t < 0.25:
            shake = math.sin(t * 80) * 8
            frames.append(compose(base, tx=shake, scale=1.0))
        else:
            progress = (t - 0.25) / 0.75
            ty = -progress * progress * 600  # accelerating launch
            scale = 1.0 - progress * 0.3
            frames.append(compose(base, ty=ty, scale=scale))
    return frames

# ─── WAGMI — FIST PUMP / JUMP JOY ────────────────────────────────────────────
def make_wagmi():
    base = load("wagmi.png")
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        # jump: fast up, gravity down, repeat twice
        phase = (t * 2) % 1.0
        jump = -abs(math.sin(phase * math.pi)) * 80
        scale = 1.0 + 0.06 * abs(math.sin(phase * math.pi))
        frames.append(compose(base, ty=jump, scale=scale))
    return frames

# ─── NGMI — COLLAPSE / CRUMPLE ────────────────────────────────────────────────
def make_ngmi():
    base = load("ngmi.png")
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        # wobble then droops sadly down
        if t < 0.3:
            wobble = math.sin(t * 60) * 6
            frames.append(compose(base, tx=wobble))
        else:
            progress = (t - 0.3) / 0.7
            ty = progress * progress * 120
            scale = 1.0 - progress * 0.15
            angle = math.sin(progress * math.pi) * -15
            frames.append(compose(base, ty=ty, scale=scale, angle=angle))
    return frames

# ─── DIAMOND HANDS — SLOW GLOWING PULSE + SPIN ────────────────────────────────
def make_diamond():
    base = load("diamond_hands.png")
    frames = []
    n = FPS * 3
    for i in range(n):
        t = i / n
        # slow majestic rotation + pulsing scale
        angle = t * 360 * 0.5  # half rotation over 3s
        scale = 1.0 + 0.07 * math.sin(t * 4 * math.pi)
        frames.append(compose(base, scale=scale, angle=angle))
    return frames

# ─── ATH — GREEN STREAK / ZOOM IN ────────────────────────────────────────────
def make_ath():
    base = load("ath.png")
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        # zoom from small to big then hold
        if t < 0.5:
            scale = 0.3 + (t / 0.5) * 0.8
            frames.append(compose(base, scale=scale))
        else:
            pulse = 1.0 + 0.04 * math.sin((t - 0.5) * 8 * math.pi)
            frames.append(compose(base, scale=pulse))
    return frames

# ─── BIG BUY — MONEY BOUNCE / GROW ───────────────────────────────────────────
def make_bigbuy():
    base = load("big_buy.png")
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        # grow large like "ITS HUGE" then settle
        if t < 0.4:
            scale = 1.0 + (t / 0.4) * 0.5  # grow to 1.5x
        else:
            progress = (t - 0.4) / 0.6
            scale = 1.5 - math.sin(progress * math.pi * 3) * 0.1  # oscillate settle
        bob = math.sin(t * 4 * math.pi) * 10
        frames.append(compose(base, scale=min(scale, 1.45), ty=bob))
    return frames

# ─── REKT — FALL + SPIN DOWN ──────────────────────────────────────────────────
def make_rekt():
    base = load("rekt.png")
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        # spin and fall off screen downward
        angle = t * -180
        ty = t * t * 400
        scale = 1.0 - t * 0.4
        frames.append(compose(base, ty=ty, scale=scale, angle=angle))
    return frames

# ─── WEN MOON — FLOAT UP WITH STARS ──────────────────────────────────────────
def make_wenmoon():
    base = load("wen_moon.png")
    frames = []
    n = FPS * 3
    for i in range(n):
        t = i / n
        # gentle float upward, dreamy
        ty = -t * 80
        scale = 1.0 + 0.03 * math.sin(t * 6 * math.pi)
        angle = math.sin(t * 2 * math.pi) * 5
        frames.append(compose(base, ty=ty, scale=scale, angle=angle))
    return frames

# ─── HIGHER — HYPNOTIC SPIN ZOOM ─────────────────────────────────────────────
def make_higher():
    base = load("higher.png")
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        angle = t * 720  # 2 full spins
        scale = 0.5 + t * 0.7
        frames.append(compose(base, scale=min(scale, 1.1), angle=angle))
    return frames

STICKERS = [
    ("gm",            make_gm),
    ("lfg",           make_lfg),
    ("wagmi",         make_wagmi),
    ("ngmi",          make_ngmi),
    ("diamond_hands", make_diamond),
    ("ath",           make_ath),
    ("big_buy",       make_bigbuy),
    ("rekt",          make_rekt),
    ("wen_moon",      make_wenmoon),
    ("higher",        make_higher),
]

for name, fn in STICKERS:
    print(f"Generating {name}...")
    frames = fn()
    fd = save_frames(frames, name)
    render_webm(fd, os.path.join(OUT, f"{name}.webm"))

print("\nAll done!")
