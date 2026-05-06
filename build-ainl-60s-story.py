#!/usr/bin/env python3
"""
AINL 60-Second Story Commercial
- Human-centric, ChatGPT vibes
- Story-driven narrative
- Star as hero
- Problem → Solution → Outcome
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import subprocess
import math

WIDTH, HEIGHT = 1920, 1080
FPS = 30
OUTPUT_DIR = "/data/.openclaw/workspace/ainl-videos"
TEMP_DIR = "/tmp/ainl-60s-story"

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load star
star_img = Image.open("/data/.openclaw/workspace/ainl-star-v2.png").convert('RGBA')
star_width = 300
aspect = star_img.height / star_img.width
star_height = int(star_width * aspect)
star_img = star_img.resize((star_width, star_height), Image.Resampling.LANCZOS)

def create_slide(bg_color=(10, 10, 20), elements=None, frame_num=0):
    """Create slide with flexible element system"""
    img = Image.new('RGBA', (WIDTH, HEIGHT), bg_color + (255,))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Subtle gradient
    for y in range(HEIGHT):
        alpha = int(10 * (y / HEIGHT))
        draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, alpha))
    
    # Cyan scan lines (subtle)
    for y in range(0, HEIGHT, 6):
        opacity = int(8 * (math.sin(frame_num / 8 + y / 150) * 0.5 + 0.5))
        draw.line([(0, y), (WIDTH, y)], fill=(0, 255, 200, opacity))
    
    # Apply elements
    if elements:
        for elem in elements:
            if elem['type'] == 'star':
                star = star_img.copy()
                scale = elem.get('scale', 1.0)
                alpha = elem.get('alpha', 255)
                
                if scale != 1.0:
                    new_size = (int(star_img.width * scale), int(star_img.height * scale))
                    star = star.resize(new_size, Image.Resampling.LANCZOS)
                
                if alpha < 255:
                    alpha_ch = star.split()[3]
                    alpha_ch = ImageEnhance.Brightness(alpha_ch).enhance(alpha / 255.0)
                    star.putalpha(alpha_ch)
                
                x = elem.get('x', (WIDTH - star.width) // 2)
                y = elem.get('y', (HEIGHT - star.height) // 2)
                img.paste(star, (x, y), star)
                
                # Glow
                glow = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
                glow_draw = ImageDraw.Draw(glow, 'RGBA')
                radius = int(star.width / 2 + 20)
                center = (x + star.width // 2, y + star.height // 2)
                for r in range(radius, 0, -4):
                    glow_alpha = int(25 * (1 - r / radius))
                    glow_draw.ellipse(
                        [(center[0] - r, center[1] - r), (center[0] + r, center[1] + r)],
                        outline=(0, 255, 200, glow_alpha)
                    )
                img = Image.alpha_composite(img, glow)
            
            elif elem['type'] == 'text':
                draw = ImageDraw.Draw(img, 'RGBA')
                text = elem['text']
                font_size = elem.get('size', 60)
                color = elem.get('color', (200, 200, 200, 220))
                
                try:
                    if elem.get('bold'):
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                    else:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                x = elem.get('x', (WIDTH - text_width) // 2)
                y = elem.get('y', HEIGHT // 2)
                
                draw.text((x, y), text, font=font, fill=color)
    
    return img.convert('RGB')

# ============================================================================
# Build 60-Second Story
# ============================================================================

print("🎬 Building AINL 60s Story Commercial")
print("=" * 50)

slides = []

# ACT 1: Problem (12s = 360 frames / 30fps)
print("1️⃣  Act 1: Problem (12s)...")
for i in range(360):
    progress = i / 360.0
    opacity = int(150 + (50 * math.sin(progress * math.pi * 4)))
    
    slide = create_slide(
        bg_color=(20, 15, 25),
        elements=[
            {
                'type': 'text',
                'text': 'Building agents is broken',
                'size': 70,
                'bold': True,
                'color': (200, 100, 100, 180),
                'y': HEIGHT // 2 - 100
            },
            {
                'type': 'text',
                'text': 'Complex. Slow. Expensive.',
                'size': 45,
                'color': (150, 150, 150, opacity),
                'y': HEIGHT // 2 + 50
            }
        ],
        frame_num=i
    )
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

# ACT 2: Discovery (10s = 300 frames)
print("2️⃣  Act 2: Discovery (10s)...")
for i in range(300):
    progress = i / 300.0
    star_alpha = int(255 * progress)
    star_scale = 0.3 + (0.4 * progress)
    
    slide = create_slide(
        elements=[
            {
                'type': 'star',
                'alpha': star_alpha,
                'scale': star_scale,
                'x': (WIDTH - int(star_img.width * star_scale)) // 2,
                'y': HEIGHT // 2 - 150
            },
            {
                'type': 'text',
                'text': 'There\'s a better way',
                'size': 65,
                'bold': True,
                'color': (0, 255, 200, int(200 * progress)),
                'y': HEIGHT // 2 + 150
            }
        ],
        frame_num=360 + i
    )
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

# ACT 3: Magic (20s = 600 frames)
print("3️⃣  Act 3: Magic (20s)...")
for i in range(600):
    progress = i / 600.0
    
    # Rotating text snippets showing solution
    if progress < 0.33:
        text = "Deterministic compilation"
        color = (0, 200, 150, int(200 * (progress / 0.33)))
    elif progress < 0.66:
        text = "$29/month for 100+ agents"
        color = (0, 255, 100, 200)
    else:
        text = "99.7% uptime. Zero overhead."
        color = (200, 255, 100, int(200 * ((progress - 0.66) / 0.34)))
    
    pulse = 1.0 + (0.08 * math.sin(progress * math.pi * 4))
    
    slide = create_slide(
        elements=[
            {
                'type': 'star',
                'scale': pulse,
                'x': (WIDTH - int(star_img.width * pulse)) // 2,
                'y': HEIGHT // 2 - 200
            },
            {
                'type': 'text',
                'text': text,
                'size': 55,
                'bold': True,
                'color': color,
                'y': HEIGHT // 2 + 100
            }
        ],
        frame_num=660 + i
    )
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

# ACT 4: Outcome (10s = 300 frames)
print("4️⃣  Act 4: Outcome (10s)...")
for i in range(300):
    progress = i / 300.0
    
    slide = create_slide(
        elements=[
            {
                'type': 'star',
                'scale': 1.0 + (0.1 * math.sin(progress * math.pi * 2)),
                'x': WIDTH // 2 - int(star_img.width * 1.05) // 2,
                'y': HEIGHT // 2 - 150
            },
            {
                'type': 'text',
                'text': 'You built something real',
                'size': 60,
                'bold': True,
                'color': (0, 255, 200, 200),
                'y': HEIGHT // 2 + 150
            }
        ],
        frame_num=1260 + i
    )
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

# ACT 5: CTA (8s = 240 frames)
print("5️⃣  Act 5: CTA (8s)...")
for i in range(240):
    progress = i / 240.0
    opacity = int(100 + (100 * progress))
    
    slide = create_slide(
        elements=[
            {
                'type': 'star',
                'scale': 0.8,
                'x': WIDTH // 2 - int(star_img.width * 0.8) // 2,
                'y': HEIGHT // 2 - 150
            },
            {
                'type': 'text',
                'text': 'github.com/sbhooley',
                'size': 50,
                'bold': True,
                'color': (0, 255, 200, opacity),
                'y': HEIGHT // 2 + 150
            },
            {
                'type': 'text',
                'text': '/ainativelang',
                'size': 50,
                'bold': True,
                'color': (0, 255, 200, opacity),
                'y': HEIGHT // 2 + 220
            }
        ],
        frame_num=1560 + i
    )
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

print(f"✅ Generated {len(slides)} slides ({len(slides)/30:.1f} seconds)")

# ============================================================================
# Assemble video
# ============================================================================

print("\n🎥 Assembling video...")

concat_file = f"{TEMP_DIR}/concat.txt"
with open(concat_file, "w") as f:
    for slide in slides:
        f.write(f"file '{slide}'\n")
        f.write(f"duration 0.033\n")

cmd = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", concat_file,
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
    f"{TEMP_DIR}/ainl-60s-silent.mp4"
]

subprocess.run(cmd, capture_output=True)
print("✅ Silent video ready")

# Add audio
print("\n🎙️ Adding voiceover...")
cmd = [
    "ffmpeg", "-y",
    "-i", f"{TEMP_DIR}/ainl-60s-silent.mp4",
    "-i", "/tmp/commercial-voiceover.mp3",
    "-c:v", "copy", "-c:a", "aac",
    "-map", "0:v:0", "-map", "1:a:0",
    "-shortest",
    f"{OUTPUT_DIR}/AINL-60s-Story-FINAL.mp4"
]

subprocess.run(cmd, capture_output=True)
print("✅ Audio mixed")

print("\n" + "=" * 50)
print("🎬 AINL 60s Story Complete!")
print(f"📹 File: {OUTPUT_DIR}/AINL-60s-Story-FINAL.mp4")
print("=" * 50)
