#!/usr/bin/env python3
"""
Final high-quality animated sticker pack.
30fps, proper cartoon principles per pose.
Each animation is unique to the character's scene.
"""

import os, math, subprocess, shutil
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

SRC = "/data/.openclaw/workspace/starfish-stickers/poses_cut"
OUT = "/data/.openclaw/workspace/starfish-stickers/final_animated"
os.makedirs(OUT, exist_ok=True)

FPS = 30
SIZE = 512
CX = SIZE // 2

def load(name):
    return Image.open(os.path.join(SRC, f"{name}.png")).convert("RGBA").resize((SIZE, SIZE), Image.LANCZOS)

def blank():
    return Image.new("RGBA", (SIZE, SIZE), (0,0,0,0))

def ease_out(t, power=3):
    return 1 - (1 - t) ** power

def ease_in(t, power=3):
    return t ** power

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def spring(t, freq=4, decay=6):
    return math.exp(-decay * t) * math.cos(freq * 2 * math.pi * t)

def compose(base, sx=1.0, sy=1.0, tx=0, ty=0, angle=0, alpha=255, blur=0):
    frame = blank()
    img = base.copy()

    if sx != 1.0 or sy != 1.0:
        w = max(1, int(SIZE * sx))
        h = max(1, int(SIZE * sy))
        img = img.resize((w, h), Image.LANCZOS)

    if angle != 0:
        img = img.rotate(angle, resample=Image.BICUBIC, expand=False)

    if blur > 0:
        img = img.filter(ImageFilter.GaussianBlur(blur))

    if alpha != 255:
        r, g, b, a = img.split()
        a = a.point(lambda x: int(x * max(0, alpha) / 255))
        img = Image.merge("RGBA", (r, g, b, a))

    w, h = img.size
    x = CX - w // 2 + int(tx)
    y = CX - h // 2 + int(ty)
    frame.paste(img, (x, y), img)
    return frame

def add_motion_blur(frame, dx=0, dy=0, strength=3):
    """Simulate motion blur by layering shifted semi-transparent copies."""
    if strength == 0 or (dx == 0 and dy == 0):
        return frame
    result = frame.copy()
    for i in range(1, strength + 1):
        ghost = blank()
        alpha = int(120 / (i * 2))
        shifted = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        shifted.paste(frame, (int(dx * i / strength), int(dy * i / strength)), frame)
        r, g, b, a = shifted.split()
        a = a.point(lambda x: int(x * alpha / 255))
        shifted = Image.merge("RGBA", (r, g, b, a))
        result = Image.alpha_composite(result, shifted)
    return result

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
        "-b:v", "0", "-crf", "28",
        "-auto-alt-ref", "0",
        "-t", str(duration),
        out_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.rmtree(d)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"  ✓ {name}.webm ({size_kb}KB)")
    return out_path

# ─── GM — Coffee sip: sleepy bob, steam rising, blink ────────────────────────
def make_gm():
    base = load("gm")
    frames = []
    n = FPS * 2  # 2s loop
    for i in range(n):
        t = i / n
        # Slow sleepy bob
        bob = math.sin(t * 2 * math.pi) * 10
        # Slight squash/stretch with bob
        sy = 1.0 + 0.025 * math.sin(t * 2 * math.pi)
        sx = 1.0 - 0.015 * math.sin(t * 2 * math.pi)
        # Slow blink at t=0.6
        blink_t = (t - 0.55) / 0.08
        if 0 < blink_t < 1:
            sy_blink = 1.0 - 0.08 * math.sin(blink_t * math.pi)
        else:
            sy_blink = 1.0
        frames.append(compose(base, sx=sx * sy_blink, sy=sy * sy_blink, ty=bob))
    return frames

# ─── LFG — Scream build → EXPLOSIVE launch ───────────────────────────────────
def make_lfg():
    base = load("lfg")
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        if t < 0.15:  # Vibrate with excitement
            shake = math.sin(t * 200) * 7
            sy = 1.0 + 0.05 * math.sin(t * 150)
            frames.append(compose(base, tx=shake, sy=sy))
        elif t < 0.3:  # SQUASH DOWN — anticipation
            p = (t - 0.15) / 0.15
            sy = 1.0 - ease_in(p) * 0.3
            sx = 1.0 + ease_in(p) * 0.25
            ty = ease_in(p) * 35
            frames.append(compose(base, sx=sx, sy=sy, ty=ty))
        else:  # BLAST OFF
            p = (t - 0.3) / 0.7
            p2 = ease_in(p, 2)
            ty = -p2 * 750
            sy = 1.0 + p * 0.5  # stretch tall as it launches
            sx = 1.0 - p * 0.35
            alpha = max(0, int(255 * (1 - max(0, p - 0.65) / 0.35)))
            blur = p * 3
            frames.append(compose(base, sx=sx, sy=sy, ty=ty, alpha=alpha, blur=blur))
    return frames

# ─── WAGMI — Jump → peak → land with spring settle ───────────────────────────
def make_wagmi():
    base = load("wagmi")
    frames = []
    n = FPS * 2
    jump_seq = [
        # (progress_start, progress_end, func) → describes arc phases
    ]
    for i in range(n):
        t = (i / n) * 1.5  # 1.5 jumps per 2s
        phase = t % 1.0

        if phase < 0.15:  # Crouch
            p = phase / 0.15
            sy = 1.0 - ease_in_out(p) * 0.2
            sx = 1.0 + ease_in_out(p) * 0.15
            ty = ease_in_out(p) * 25
            angle = 0
        elif phase < 0.45:  # Rise
            p = (phase - 0.15) / 0.30
            sy = 0.8 + ease_out(p) * 0.35  # stretch on rise
            sx = 0.85 + ease_out(p) * 0.2
            ty = 25 - ease_out(p) * 120
            angle = ease_out(p) * 8
        elif phase < 0.55:  # Peak float
            p = (phase - 0.45) / 0.10
            sy = 1.15 - p * 0.05
            sx = 0.9 + p * 0.05
            ty = -95 + p * 5
            angle = 8 - p * 16
        elif phase < 0.75:  # Fall
            p = (phase - 0.55) / 0.20
            sy = 1.1 - p * 0.2
            sx = 0.95 + p * 0.1
            ty = -90 + ease_in(p) * 95
            angle = -8 + p * 8
        else:  # Land + spring
            p = (phase - 0.75) / 0.25
            sp = spring(p, freq=3, decay=8)
            sy = 0.85 + ease_out(p) * 0.18 + sp * 0.05
            sx = 1.15 - ease_out(p) * 0.18 - sp * 0.03
            ty = sp * 15
            angle = 0

        frames.append(compose(base, sx=sx, sy=sy, ty=ty, angle=angle))
    return frames

# ─── SEND IT — Lean back → YEET forward with speed blur ─────────────────────
def make_sendit():
    base = load("send_it")
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        if t < 0.25:  # Lean back — wind up
            p = t / 0.25
            tx = -ease_in_out(p) * 40
            angle = ease_in_out(p) * -15
            sy = 1.0 - p * 0.05
            frames.append(compose(base, tx=tx, sy=sy, angle=angle))
        elif t < 0.45:  # SEND — explosive forward
            p = (t - 0.25) / 0.20
            tx = -40 + ease_out(p, 4) * 580
            angle = -15 + p * 15
            sy = 1.0 + p * 0.2
            sx = 0.7 + p * 0.5  # squish on launch then stretch
            alpha = max(0, int(255 * (1 - max(0, p - 0.5) / 0.5)))
            blur = p * 4
            frames.append(compose(base, sx=sx, sy=sy, tx=tx, angle=angle, alpha=alpha, blur=blur))
        else:  # Gone — blank then reappear for loop
            p = (t - 0.45) / 0.55
            if p > 0.7:  # Reappear at start for seamless loop
                rp = (p - 0.7) / 0.3
                tx = -40 * ease_out(rp)
                frames.append(compose(base, tx=-40, alpha=int(255 * ease_out(rp) * 0.8)))
            else:
                frames.append(blank())
    return frames

# ─── DIAMOND HANDS — Slow proud orbit + pulse glow ───────────────────────────
def make_diamond():
    base = load("diamond_hands")
    frames = []
    n = FPS * 3  # 3s for slow majestic feel
    for i in range(n):
        t = i / n
        # Slow orbit rotation
        angle = t * 360 * 0.6
        # Breathing scale pulse
        pulse = 1.0 + 0.06 * math.sin(t * 4 * math.pi)
        # Slight vertical float
        ty = math.sin(t * 2 * math.pi) * 12
        frames.append(compose(base, sx=pulse, sy=pulse, ty=ty, angle=angle))
    return frames

# ─── ATH — Zoom in from tiny, overshoot, victory jiggle ─────────────────────
def make_ath():
    base = load("ath")
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        if t < 0.5:  # ZOOM IN
            p = ease_out(t / 0.5, 4)
            scale = 0.05 + p * 1.05  # overshoot slightly
            frames.append(compose(base, sx=scale, sy=scale))
        elif t < 0.65:  # Overshoot settle
            p = (t - 0.5) / 0.15
            scale = 1.1 - ease_in_out(p) * 0.1
            frames.append(compose(base, sx=scale, sy=scale))
        else:  # Victory jiggle
            p = (t - 0.65) / 0.35
            jiggle = math.sin(p * 10 * math.pi) * 6 * (1 - p)
            bob = math.sin(p * 4 * math.pi) * 8
            frames.append(compose(base, sx=1.0, sy=1.0, angle=jiggle, ty=bob))
    return frames

# ─── APE IN — Dive in: fall from top, splash landing ────────────────────────
def make_apein():
    base = load("ape_in")
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        if t < 0.1:  # Enter from top
            p = t / 0.1
            ty = -SIZE * (1 - ease_in(p))
            frames.append(compose(base, ty=ty))
        elif t < 0.25:  # IMPACT — massive squash
            p = (t - 0.1) / 0.15
            sy = 1.0 - ease_in_out(p) * 0.45
            sx = 1.0 + ease_in_out(p) * 0.4
            ty = ease_in_out(p) * 40
            frames.append(compose(base, sx=sx, sy=sy, ty=ty))
        elif t < 0.45:  # Spring back up
            p = (t - 0.25) / 0.20
            sp = spring(p, freq=2.5, decay=5)
            sy = 0.55 + ease_out(p) * 0.5 + sp * 0.08
            sx = 1.4 - ease_out(p) * 0.4 - sp * 0.05
            ty = 40 - sp * 30
            frames.append(compose(base, sx=sx, sy=sy, ty=ty))
        else:  # Settled, happy bounce
            p = (t - 0.45) / 0.55
            bob = math.sin(p * 4 * math.pi) * 10
            frames.append(compose(base, ty=bob))
    return frames

# ─── 1000X — Flex pulse: grows stronger with each pump ───────────────────────
def make_1000x():
    base = load("1000x")
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        # 4 flex pumps, each bigger than the last
        pumps = 4
        phase = (t * pumps) % 1.0
        pump_num = int(t * pumps)
        base_scale = 0.85 + pump_num * 0.06  # grows each pump

        if phase < 0.4:  # flex out
            p = ease_out(phase / 0.4)
            scale = base_scale + p * 0.12
        else:  # relax back
            p = ease_in_out((phase - 0.4) / 0.6)
            scale = base_scale + 0.12 - p * 0.12

        frames.append(compose(base, sx=scale, sy=scale))
    return frames

# ─── WEN MOON — Float dreamily, stars twinkle, fade up ──────────────────────
def make_wenmoon():
    base = load("wen_moon")
    frames = []
    n = FPS * 3
    for i in range(n):
        t = i / n
        # Gentle float upward
        ty = -t * 130
        # Dreamy sway
        tx = math.sin(t * 2.5 * math.pi) * 18
        # Slow rotate
        angle = math.sin(t * 1.5 * math.pi) * 7
        # Pulse
        pulse = 1.0 + 0.04 * math.sin(t * 6 * math.pi)
        # Fade near end
        alpha = int(255 * (1 - max(0, t - 0.75) / 0.25))
        frames.append(compose(base, sx=pulse, sy=pulse, tx=tx, ty=ty, angle=angle, alpha=alpha))
    return frames

# ─── HIGHER — Hypnotic approach: zooms at you, fills frame ───────────────────
def make_higher():
    base = load("higher")
    frames = []
    n = FPS * 2
    for i in range(n):
        t = i / n
        if t < 0.7:  # Accelerating zoom
            p = ease_in(t / 0.7, 2)
            scale = 0.08 + p * 1.05
            # Slight wobble while approaching
            angle = math.sin(t * 8 * math.pi) * 3 * (1 - p)
            frames.append(compose(base, sx=scale, sy=scale, angle=angle))
        else:  # Fill frame + pulse
            p = (t - 0.7) / 0.3
            scale = 1.13 + math.sin(p * 6 * math.pi) * 0.05
            frames.append(compose(base, sx=scale, sy=scale))
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
    print(f"Animating {name}...")
    frames = fn()
    save_and_render(frames, name, duration=dur)

print("\n✅ Final pack ready!")
