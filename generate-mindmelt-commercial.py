#!/usr/bin/env python3

"""
AINL Mind-Melting Commercial
Psychedelic, hypnotic, overwhelming visual spectacle
90 seconds of pure visual chaos with AINL message underneath
"""

import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import subprocess
from pathlib import Path
import math

WIDTH, HEIGHT = 1920, 1080
VIDEO_DIR = Path("/tmp/ainl-mindmelt")
OUTPUT_FILE = Path("/data/.openclaw/workspace/ainl-videos/AINL-Mindmelt-90sec.mp4")

# Neon colors
NEON_PINK = "#ff00ff"
NEON_CYAN = "#00ffff"
NEON_GREEN = "#00ff00"
NEON_PURPLE = "#8800ff"
NEON_ORANGE = "#ff6600"
BG_BLACK = "#000000"

def create_blank(width, height, color=BG_BLACK):
    return Image.new("RGB", (width, height), color)

def apply_glitch(img, intensity=5):
    """Apply chromatic aberration + glitch effect"""
    r, g, b = img.split()
    
    # Shift channels by random amounts
    offset = random.randint(-intensity, intensity)
    r = r.transform((WIDTH, HEIGHT), Image.AFFINE, (1, 0, offset, 0, 1, 0))
    b = b.transform((WIDTH, HEIGHT), Image.AFFINE, (1, 0, -offset, 0, 1, 0))
    
    return Image.merge('RGB', (r, g, b))

def apply_distortion(img):
    """Apply lens distortion"""
    pixels = img.load()
    
    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Radial distortion formula
            cx, cy = WIDTH // 2, HEIGHT // 2
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx**2 + dy**2)
            
            # Swirl effect
            angle = dist * 0.05 + random.random() * 0.1
            new_x = int(cx + dist * math.cos(angle) * 1.1)
            new_y = int(cy + dist * math.sin(angle) * 1.1)
            
            if 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT:
                try:
                    pixels[x, y] = img.getpixel((new_x, new_y))
                except:
                    pass
    
    return img

def cascade_code(img, color, density=50):
    """Add cascading code/data streams"""
    draw = ImageDraw.Draw(img, 'RGBA')
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    chars = "01[](){}|><><|AI@hashmark%andmore"
    
    for _ in range(density):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        char = random.choice(chars)
        opacity = random.randint(50, 200)
        
        # Add glow effect
        for i in range(3, 0, -1):
            glow_color = (*ImageDraw.ImageDraw(img, 'RGBA')._get_color(color)[:3], max(0, opacity - i*30))
            # Simplified glow
        
        draw.text((x, y), char, fill=(*ImageDraw.ImageDraw(img, 'RGBA')._get_color(color)[:3], opacity), font=font)
    
    return img

def create_psychedelic_slide(act, slide_num):
    """Create increasingly intense psychedelic slides"""
    img = create_blank(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    
    try:
        font_huge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 200)
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except:
        font_huge = font_big = font_small = ImageFont.load_default()
    
    # Pick random intense colors
    colors = [NEON_PINK, NEON_CYAN, NEON_GREEN, NEON_PURPLE, NEON_ORANGE]
    primary_color = random.choice(colors)
    secondary_color = random.choice([c for c in colors if c != primary_color])
    
    # ACT 1: Problem - Chaos
    if act == 1:
        draw.text((WIDTH//2, 200), "$1,183", fill=NEON_PINK, font=font_huge, anchor="mm")
        draw.text((WIDTH//2, 500), "/year", fill=NEON_CYAN, font=font_big, anchor="mm")
        draw.text((WIDTH//2, 800), "WASTED", fill=NEON_ORANGE, font=font_big, anchor="mm")
        
        # Add cascading code
        for _ in range(100):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            char = random.choice("01whileloop")
            draw.text((x, y), char, fill=random.choice(colors), font=font_small)
    
    # ACT 2: Solution - Compilation
    elif act == 2:
        draw.text((WIDTH//2, HEIGHT//2 - 150), "COMPILE", fill=NEON_GREEN, font=font_huge, anchor="mm")
        draw.text((WIDTH//2, HEIGHT//2 + 100), "NOT LOOP", fill=NEON_CYAN, font=font_big, anchor="mm")
        
        # Animated grid
        for i in range(0, WIDTH, 100):
            draw.line([(i, 0), (i, HEIGHT)], fill=NEON_PURPLE, width=2)
        for i in range(0, HEIGHT, 100):
            draw.line([(0, i), (WIDTH, i)], fill=NEON_PURPLE, width=2)
    
    # ACT 3: Proof - Intensity
    elif act == 3:
        draw.text((WIDTH//2, 300), "17", fill=NEON_GREEN, font=font_huge, anchor="mm")
        draw.text((WIDTH//2, 600), "$29", fill=NEON_CYAN, font=font_huge, anchor="mm")
        draw.text((WIDTH//2, 900), "99.7%", fill=NEON_PINK, font=font_big, anchor="mm")
        
        # Chaotic numbers
        for _ in range(200):
            num = str(random.randint(0, 999))
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            draw.text((x, y), num, fill=random.choice(colors), font=font_small)
    
    # ACT 4: CTA - Pure Energy
    elif act == 4:
        draw.text((WIDTH//2, HEIGHT//2 - 200), "AINL", fill=NEON_CYAN, font=font_huge, anchor="mm")
        draw.text((WIDTH//2, HEIGHT//2 + 100), "github.com/sbhooley/ainativelang", fill=NEON_GREEN, font=font_small, anchor="mm")
        
        # Radiating lines
        for angle in range(0, 360, 15):
            x1, y1 = WIDTH//2, HEIGHT//2
            x2 = x1 + 500 * math.cos(math.radians(angle))
            y2 = y1 + 500 * math.sin(math.radians(angle))
            draw.line([(x1, y1), (x2, y2)], fill=random.choice(colors), width=3)
    
    # Apply glitch + distortion
    img = apply_glitch(img, intensity=8)
    
    return img

def main():
    print("🫠 Generating MIND-MELTING AINL Commercial")
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Rapid cuts - lots of short slides for chaotic feel
    slides = []
    
    # Act 1: Problem (10 rapid cuts, 15 sec total)
    for i in range(10):
        slides.append((f"act1_chaos_{i}", 1, create_psychedelic_slide(1, i)))
    slides.append((f"act1_final", 5, create_psychedelic_slide(1, 10)))
    
    # Act 2: Solution (12 rapid cuts, 25 sec total)
    for i in range(12):
        slides.append((f"act2_compile_{i}", 1, create_psychedelic_slide(2, i)))
    slides.append((f"act2_final", 13, create_psychedelic_slide(2, 12)))
    
    # Act 3: Proof (15 rapid cuts, 30 sec total)
    for i in range(15):
        slides.append((f"act3_proof_{i}", 1, create_psychedelic_slide(3, i)))
    slides.append((f"act3_final", 15, create_psychedelic_slide(3, 15)))
    
    # Act 4: CTA (10 rapid cuts, 20 sec total)
    for i in range(10):
        slides.append((f"act4_cta_{i}", 1, create_psychedelic_slide(4, i)))
    slides.append((f"act4_final", 10, create_psychedelic_slide(4, 10)))
    
    print(f"📸 Generating {len(slides)} slides...")
    mp4_files = []
    
    for idx, (name, duration, img) in enumerate(slides):
        if idx % 10 == 0:
            print(f"  {idx}/{len(slides)}...")
        
        img_path = VIDEO_DIR / f"{name}.png"
        img.save(img_path)
        
        mp4_path = VIDEO_DIR / f"{name}.mp4"
        cmd = [
            "ffmpeg", "-loop", "1", "-i", str(img_path),
            "-c:v", "libx264", "-t", str(duration),
            "-pix_fmt", "yuv420p", "-y", str(mp4_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        mp4_files.append(mp4_path)
    
    print("🎬 Assembling mind-melt...")
    concat_file = VIDEO_DIR / "concat.txt"
    with open(concat_file, "w") as f:
        for mp4_path in mp4_files:
            f.write(f"file '{mp4_path}'\n")
    
    cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c", "copy", "-y", str(OUTPUT_FILE)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"🫠 Mind-melt generated!")
    print(f"   File: {OUTPUT_FILE}")
    print(f"   Duration: 90 seconds")
    print(f"   Slides: {len(slides)} (rapid cuts for chaos)")
    print(f"   Vibe: PSYCHEDELIC OVERLOAD 🤯")

if __name__ == "__main__":
    main()
