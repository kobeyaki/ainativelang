#!/usr/bin/env python3
"""
Overlay laser-writes-text effect on top of Vidu video.
Arch's laser beams sweep left to right and write "NEW BUY" letter by letter.
"""
import cv2
import numpy as np
import math

INPUT = '/data/.openclaw/workspace/ainl-mascot-upgrades/arch_buybot_v2.mp4'
OUTPUT = '/data/.openclaw/workspace/ainl-mascot-upgrades/arch_buybot_v2_text.mp4'

cap = cv2.VideoCapture(INPUT)
FPS = cap.get(cv2.CAP_PROP_FPS)
TOTAL_FRAMES = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(OUTPUT, fourcc, FPS, (W, H))

TEXT = "NEW BUY"
# Text area: center bottom third
TEXT_Y = int(H * 0.80)
TEXT_X_START = int(W * 0.12)
TEXT_X_END = int(W * 0.88)
FONT = cv2.FONT_HERSHEY_DUPLEX
FONT_SCALE = W / 320  # scale to video size
THICKNESS = max(3, int(W / 160))

# Measure full text width
(tw, th), _ = cv2.getTextSize(TEXT, FONT, FONT_SCALE, THICKNESS)
TEXT_X = (W - tw) // 2  # center
TEXT_TOP = TEXT_Y - th - 10
TEXT_BOT = TEXT_Y + 10

# Animation timing
SWEEP_START_F = int(FPS * 0.4)   # start sweep at 0.4s
SWEEP_END_F = int(FPS * 2.0)     # finish writing by 2.0s
PULSE_END_F = int(FPS * 2.8)
HOLD_END_F = TOTAL_FRAMES

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def draw_glow_text(frame, text, x, y, alpha_frac, color=(255, 255, 255), glow_color=(180, 0, 255)):
    """Draw text with purple glow using addWeighted blending."""
    overlay = frame.copy()
    
    # Glow layers (blurred)
    for blur_size, glow_alpha in [(31, 0.5), (15, 0.4), (7, 0.3)]:
        glow_layer = np.zeros_like(frame)
        cv2.putText(glow_layer, text, (x, y), FONT, FONT_SCALE, glow_color, THICKNESS + 8)
        glow_layer = cv2.GaussianBlur(glow_layer, (blur_size, blur_size), 0)
        cv2.addWeighted(overlay, 1.0, glow_layer, glow_alpha * alpha_frac, 0, overlay)
        frame = overlay.copy()
    
    # Sharp white text on top
    cv2.putText(frame, text, (x, y), FONT, FONT_SCALE, 
                tuple(int(c * alpha_frac) for c in color), THICKNESS)
    return frame

def draw_laser_beam(frame, x1, y1, x2, y2, progress):
    """Draw purple laser beam from eye to text, only up to progress."""
    ex = int(x1 + (x2 - x1) * progress)
    ey = int(y1 + (y2 - y1) * progress)
    
    overlay = frame.copy()
    # Outer glow
    cv2.line(overlay, (x1, y1), (ex, ey), (180, 0, 255), max(2, THICKNESS * 3))
    cv2.addWeighted(frame, 0.7, overlay, 0.3, 0, frame)
    
    overlay2 = frame.copy()
    cv2.line(overlay2, (x1, y1), (ex, ey), (220, 100, 255), max(1, THICKNESS))
    cv2.addWeighted(frame, 0.8, overlay2, 0.2, 0, frame)
    
    # Bright core
    cv2.line(frame, (x1, y1), (ex, ey), (255, 200, 255), max(1, THICKNESS // 2))
    return frame

# Arch eye positions (approximate for 960x960 — eyes in upper center area)
LEFT_EYE = (int(W * 0.38), int(H * 0.42))
RIGHT_EYE = (int(W * 0.62), int(H * 0.42))

# Where lasers converge to (left and right of text)
LASER_LEFT_TARGET = (TEXT_X - 20, TEXT_Y - th // 2)
LASER_RIGHT_TARGET = (TEXT_X + tw + 20, TEXT_Y - th // 2)

frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    if frame_idx >= SWEEP_START_F and frame_idx < SWEEP_END_F:
        # Sweep phase
        t = (frame_idx - SWEEP_START_F) / (SWEEP_END_F - SWEEP_START_F)
        t = ease_in_out(t)
        
        # Reveal text progressively
        num_chars = int(t * len(TEXT))
        partial_text = TEXT[:num_chars]
        
        if partial_text:
            frame = draw_glow_text(frame, partial_text, TEXT_X, TEXT_Y, min(1.0, t * 2))
        
        # Laser beams sweeping
        # Left eye laser goes to current write position
        if t > 0:
            current_x = TEXT_X + int(t * tw)
            frame = draw_laser_beam(frame, LEFT_EYE[0], LEFT_EYE[1], current_x, TEXT_Y - th//2, 1.0)
            frame = draw_laser_beam(frame, RIGHT_EYE[0], RIGHT_EYE[1], current_x, TEXT_Y - th//2, 1.0)
    
    elif frame_idx >= SWEEP_END_F and frame_idx < PULSE_END_F:
        # Pulse phase — full text + lasers off + pulse glow
        pulse_t = (frame_idx - SWEEP_END_F) / (PULSE_END_F - SWEEP_END_F)
        pulse_alpha = 0.8 + 0.2 * math.sin(pulse_t * math.pi * 3)
        frame = draw_glow_text(frame, TEXT, TEXT_X, TEXT_Y, pulse_alpha)
        
        # Scatter particles
        rng = np.random.default_rng(frame_idx)
        n_particles = 25
        fade = 1 - pulse_t
        for _ in range(n_particles):
            px = TEXT_X + tw // 2 + int(rng.integers(-tw//2, tw//2)) + int(rng.integers(-1,2) * pulse_t * 80)
            py = TEXT_Y - th // 2 + int(rng.integers(-th, th)) + int(rng.integers(-1,2) * pulse_t * 40)
            radius = int(rng.integers(3, 8))
            alpha = int(fade * 200)
            overlay = frame.copy()
            cv2.circle(overlay, (px, py), radius, (180, 0, 255), -1)
            cv2.addWeighted(frame, 1.0, overlay, alpha/255.0, 0, frame)
    
    elif frame_idx >= PULSE_END_F:
        # Hold / fade out
        hold_t = (frame_idx - PULSE_END_F) / max(1, TOTAL_FRAMES - PULSE_END_F)
        alpha = max(0.0, 1.0 - hold_t * 1.5)
        if alpha > 0:
            frame = draw_glow_text(frame, TEXT, TEXT_X, TEXT_Y, alpha)
    
    out.write(frame)
    frame_idx += 1

cap.release()
out.release()
print(f"Done! {frame_idx} frames -> {OUTPUT}")
