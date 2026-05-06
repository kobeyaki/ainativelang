#!/usr/bin/env python3
"""
Arch Buybot Animation
- Arch hovers with jetpack flames flickering
- Purple laser beams sweep left to right
- Lasers progressively reveal "NEW BUY" text in glowing neon purple
- Text pulses, particles scatter, then loop
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os

BASE_IMAGE = "/data/.openclaw/media/inbound/file_159---d6f6508c-d37d-4ea4-bc91-4f9675158617.jpg"
OUT_DIR = "/data/.openclaw/workspace/ainl-mascot-upgrades"
OUT_GIF = os.path.join(OUT_DIR, "arch_buybot.gif")
OUT_WEBP = os.path.join(OUT_DIR, "arch_buybot.webp")

# Animation settings
FPS = 24
TOTAL_SECONDS = 3.0
TOTAL_FRAMES = int(FPS * TOTAL_SECONDS)

# Phases (in seconds)
HOVER_INTRO = 0.3       # just hovering
LASER_SWEEP = 1.2       # lasers sweep and reveal text
TEXT_PULSE = 0.5        # text pulses with energy + particles
HOLD = 0.5              # hold before loop
# rest is fade for loop


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def make_glow(draw, text, x, y, font, color, glow_color, glow_radius=12, alpha=255):
    """Draw glowing text"""
    # Draw glow layers
    for r in range(glow_radius, 0, -3):
        gc = (*glow_color, int(alpha * 0.3 * (1 - r/glow_radius)))
        # We'll do this via separate overlay
        pass
    draw.text((x, y), text, font=font, fill=(*color, alpha), anchor="mm")


def create_glow_text_image(size, text, font, x, y, text_color, glow_color, glow_strength=20, alpha=255):
    """Create a separate image with glowing text"""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    
    # Glow layers
    for radius in [glow_strength, glow_strength//2, glow_strength//4]:
        glow_layer = Image.new("RGBA", size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_layer)
        gd.text((x, y), text, font=font, fill=(*glow_color, int(alpha * 0.6)), anchor="mm")
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius))
        img = Image.alpha_composite(img, glow_layer)
    
    # Sharp text on top
    d = ImageDraw.Draw(img)
    d.text((x, y), text, font=font, fill=(*text_color, alpha), anchor="mm")
    
    return img


def draw_laser_beam(draw, x1, y1, x2, y2, progress, width=6):
    """Draw a purple laser beam with glow effect"""
    # Only draw up to progress point
    ex = lerp(x1, x2, progress)
    ey = lerp(y1, y2, progress)
    
    # Outer glow
    for w in [width*4, width*2, width]:
        alpha = int(180 * (w == width) + 80 * (w == width*2) + 40 * (w == width*4))
        draw.line([(x1, y1), (ex, ey)], fill=(180, 0, 255, alpha), width=w)
    # Core bright
    draw.line([(x1, y1), (ex, ey)], fill=(230, 180, 255, 255), width=max(2, width//3))


def hover_offset(frame):
    """Subtle vertical hover oscillation"""
    return math.sin(frame * 2 * math.pi / (FPS * 1.5)) * 4


def flame_flicker(frame, base_alpha=180):
    """Flickering flame intensity"""
    return int(base_alpha + math.sin(frame * 0.7) * 30 + math.sin(frame * 1.3) * 20)


def main():
    base = Image.open(BASE_IMAGE).convert("RGBA")
    W, H = base.size
    
    # Scale down to 512x512 for GIF size
    TARGET = 512
    base = base.resize((TARGET, TARGET), Image.LANCZOS)
    W, H = TARGET, TARGET
    
    # Try to load a bold font, fall back to default
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if not os.path.exists(font_path):
            # Try brew fonts
            font_path = "/home/linuxbrew/.linuxbrew/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_large = ImageFont.truetype(font_path, 72)
        font_med = ImageFont.truetype(font_path, 48)
    except Exception:
        font_large = ImageFont.load_default()
        font_med = font_large
    
    # Key coordinates (relative to 512x512)
    # Arch center is roughly at center-top area
    arch_center_x = W // 2
    arch_center_y = H // 2 - 30
    
    # Eye positions (approximate for 512x512 image)
    left_eye_x = int(W * 0.35)
    left_eye_y = int(H * 0.52)
    right_eye_x = int(W * 0.65)
    right_eye_y = int(H * 0.52)
    
    # Laser endpoints (sweep across screen)
    laser_end_y = int(H * 0.75)
    laser_left_end_x = -20
    laser_right_end_x = W + 20
    
    # Text position
    text_x = W // 2
    text_y = int(H * 0.82)
    
    # Phase frame boundaries
    f_hover_end = int(HOVER_INTRO * FPS)
    f_sweep_end = f_hover_end + int(LASER_SWEEP * FPS)
    f_pulse_end = f_sweep_end + int(TEXT_PULSE * FPS)
    f_hold_end = f_pulse_end + int(HOLD * FPS)
    f_total = TOTAL_FRAMES
    
    frames = []
    
    for f in range(f_total):
        # Start with base image
        frame_img = base.copy()
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        vy = hover_offset(f)
        
        # --- Phase logic ---
        if f < f_hover_end:
            # Just hovering, subtle flame
            pass
        
        elif f < f_sweep_end:
            # Laser sweep phase
            sweep_t = (f - f_hover_end) / (f_sweep_end - f_hover_end)
            sweep_t = ease_in_out(sweep_t)
            
            # Left eye laser sweeps LEFT
            draw_laser_beam(draw,
                left_eye_x, left_eye_y + int(vy),
                laser_left_end_x, laser_end_y,
                min(1.0, sweep_t * 1.5), width=5)
            
            # Right eye laser sweeps RIGHT
            draw_laser_beam(draw,
                right_eye_x, right_eye_y + int(vy),
                laser_right_end_x, laser_end_y,
                min(1.0, sweep_t * 1.5), width=5)
            
            # Text reveals progressively as sweep passes center
            text_reveal = max(0, (sweep_t - 0.3) / 0.7)
            if text_reveal > 0:
                text_alpha = int(text_reveal * 255)
                text_img = create_glow_text_image(
                    (W, H), "NEW BUY", font_large,
                    text_x, text_y,
                    (255, 255, 255), (160, 0, 255),
                    glow_strength=18, alpha=text_alpha
                )
                overlay = Image.alpha_composite(overlay, text_img)
                draw = ImageDraw.Draw(overlay)
        
        elif f < f_pulse_end:
            # Text pulse + particles
            pulse_t = (f - f_sweep_end) / (f_pulse_end - f_sweep_end)
            pulse_scale = 1.0 + 0.15 * math.sin(pulse_t * math.pi * 2)
            pulse_alpha = int(200 + 55 * math.sin(pulse_t * math.pi * 3))
            
            # Lasers stay at full
            draw_laser_beam(draw, left_eye_x, left_eye_y + int(vy), laser_left_end_x, laser_end_y, 1.0, width=5)
            draw_laser_beam(draw, right_eye_x, right_eye_y + int(vy), laser_right_end_x, laser_end_y, 1.0, width=5)
            
            text_img = create_glow_text_image(
                (W, H), "NEW BUY", font_large,
                text_x, text_y,
                (255, 255, 255), (180, 0, 255),
                glow_strength=int(18 + 10 * math.sin(pulse_t * math.pi * 2)),
                alpha=pulse_alpha
            )
            overlay = Image.alpha_composite(overlay, text_img)
            draw = ImageDraw.Draw(overlay)
            
            # Scatter particles
            import random
            random.seed(f)
            for _ in range(20):
                px = text_x + random.randint(-120, 120)
                py = text_y + random.randint(-30, 30)
                spread = pulse_t * 60
                px += int(random.choice([-1, 1]) * spread)
                py += int(random.choice([-1, 1]) * spread * 0.5)
                size = random.randint(2, 5)
                palpha = int((1 - pulse_t) * 200)
                draw.ellipse([px-size, py-size, px+size, py+size],
                             fill=(200, 100, 255, palpha))
        
        elif f < f_hold_end:
            # Hold — everything visible, lasers on
            draw_laser_beam(draw, left_eye_x, left_eye_y + int(vy), laser_left_end_x, laser_end_y, 1.0, width=5)
            draw_laser_beam(draw, right_eye_x, right_eye_y + int(vy), laser_right_end_x, laser_end_y, 1.0, width=5)
            
            text_img = create_glow_text_image(
                (W, H), "NEW BUY", font_large,
                text_x, text_y,
                (255, 255, 255), (160, 0, 255),
                glow_strength=18, alpha=220
            )
            overlay = Image.alpha_composite(overlay, text_img)
        
        else:
            # Fade out for loop
            fade_t = (f - f_hold_end) / max(1, f_total - f_hold_end)
            fade_alpha = int((1 - fade_t) * 220)
            if fade_alpha > 0:
                text_img = create_glow_text_image(
                    (W, H), "NEW BUY", font_large,
                    text_x, text_y,
                    (255, 255, 255), (160, 0, 255),
                    glow_strength=18, alpha=fade_alpha
                )
                overlay = Image.alpha_composite(overlay, text_img)
        
        # Composite overlay onto base
        result = Image.alpha_composite(frame_img, overlay).convert("RGB")
        frames.append(result)
    
    # Save as GIF
    print(f"Saving {len(frames)} frames as GIF...")
    frame_duration_ms = int(1000 / FPS)
    frames[0].save(
        OUT_GIF,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration_ms,
        loop=0,
        optimize=False
    )
    print(f"Saved: {OUT_GIF}")
    
    # Also save as WEBP (better quality animated)
    frames_rgba = [f.convert("RGBA") for f in frames]
    frames_rgba[0].save(
        OUT_WEBP,
        save_all=True,
        append_images=frames_rgba[1:],
        duration=frame_duration_ms,
        loop=0
    )
    print(f"Saved: {OUT_WEBP}")
    print("Done!")


if __name__ == "__main__":
    main()
