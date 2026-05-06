#!/usr/bin/env python3
"""
AINL Cinema Commercial v2
- Crystal clear typography
- Locked numbers: $29, $210, 90-95%, 99.7%, 100+
- Cinematic color grading
- Professional visual hierarchy
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import subprocess
import math

WIDTH, HEIGHT = 1920, 1080
FPS = 30
OUTPUT_DIR = "/data/.openclaw/workspace/ainl-videos"
TEMP_DIR = "/tmp/ainl-cinema"

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_slide(text, subtext="", color_bg=(10, 10, 20), accent_color=(0, 255, 200), slide_num=0):
    """Create a cinematic slide with professional typography"""
    img = Image.new('RGB', (WIDTH, HEIGHT), color_bg)
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Gradient overlay (subtle, professional)
    for y in range(HEIGHT):
        alpha = int(20 * (y / HEIGHT))
        draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, alpha))
    
    # Main text
    if text:
        font_size = 180
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Shadow effect (professional depth)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (WIDTH - text_width) // 2
        text_y = HEIGHT // 2 - 150
        
        # Drop shadow
        draw.text((text_x + 4, text_y + 4), text, font=font, fill=(0, 0, 0, 100))
        # Main text with glow
        draw.text((text_x, text_y), text, font=font, fill=accent_color)
        
        # Glow effect
        blurred = img.filter(ImageFilter.GaussianBlur(8))
        alpha_blurred = Image.new('RGBA', img.size)
        for x in range(WIDTH):
            for y in range(HEIGHT):
                px = blurred.getpixel((x, y))
                alpha_blurred.putpixel((x, y), (px[0], px[1], px[2], 30))
        img = Image.alpha_composite(img.convert('RGBA'), alpha_blurred).convert('RGB')
        draw = ImageDraw.Draw(img, 'RGBA')
    
    # Subtext
    if subtext:
        font_size = 60
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), subtext, font=font)
        text_width = bbox[2] - bbox[0]
        sub_x = (WIDTH - text_width) // 2
        sub_y = text_y + 250
        
        draw.text((sub_x, sub_y), subtext, font=font, fill=(200, 200, 200, 220))
    
    return img

def apply_color_grade(img, grade='cool'):
    """Apply cinematic color grading"""
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.1)  # Slight saturation boost
    
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.05)  # Slight brightness
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)  # Contrast punch
    
    return img

# ============================================================================
# Build Slides
# ============================================================================

print("🎬 Building AINL Cinema Commercial")
print("=" * 50)

slides = []

# Act 1: Problem ($210)
print("1️⃣  Act 1: The Problem...")
for i in range(45):  # 1.5 seconds
    slide = create_slide(
        "$210/month",
        "Traditional agent orchestration",
        color_bg=(40, 20, 20),
        accent_color=(255, 80, 80)
    )
    slide = apply_color_grade(slide)
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

# Act 2: Solution intro
print("2️⃣  Act 2: Introducing AINL...")
for i in range(45):  # 1.5 seconds
    slide = create_slide(
        "AINL",
        "Deterministic agent compiler",
        color_bg=(10, 10, 20),
        accent_color=(0, 255, 200)
    )
    slide = apply_color_grade(slide)
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

# Act 3: The revelation ($29)
print("3️⃣  Act 3: The Numbers...")
for i in range(60):  # 2 seconds
    slide = create_slide(
        "$29/month",
        "100+ agents. 99.7% uptime.",
        color_bg=(10, 10, 20),
        accent_color=(0, 255, 100)
    )
    slide = apply_color_grade(slide)
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

# Act 4: The comparison
print("4️⃣  Act 4: Comparison...")
for i in range(60):  # 2 seconds
    slide = create_slide(
        "90-95% Cheaper",
        "Zero orchestration overhead",
        color_bg=(10, 10, 20),
        accent_color=(255, 200, 0)
    )
    slide = apply_color_grade(slide)
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

# Act 5: CTA
print("5️⃣  Act 5: CTA...")
for i in range(45):  # 1.5 seconds
    slide = create_slide(
        "github.com/sbhooley",
        "/ainativelang",
        color_bg=(10, 10, 20),
        accent_color=(0, 255, 200)
    )
    slide = apply_color_grade(slide)
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

print(f"✅ Generated {len(slides)} slides")

# ============================================================================
# Assemble video
# ============================================================================

print("\n🎥 Assembling video...")

# Create concat file for ffmpeg
with open(f"{TEMP_DIR}/concat.txt", "w") as f:
    for slide in slides:
        f.write(f"file '{slide}'\n")
        f.write(f"duration 0.033\n")  # ~30 fps

cmd = [
    "ffmpeg",
    "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", f"{TEMP_DIR}/concat.txt",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "medium",
    f"{TEMP_DIR}/ainl-cinema-silent.mp4"
]

subprocess.run(cmd, capture_output=True)
print("✅ Video assembled (silent)")

# ============================================================================
# Add voiceover + audio design
# ============================================================================

print("\n🎙️ Adding audio...")

# Check for voiceover
voiceover_path = "/tmp/commercial-voiceover.mp3"
if not os.path.exists(voiceover_path):
    print("⚠️  Voiceover not found. Using video-only.")
    output_path = f"{OUTPUT_DIR}/AINL-Cinema-90sec-FINAL.mp4"
    import shutil
    shutil.copy(f"{TEMP_DIR}/ainl-cinema-silent.mp4", output_path)
else:
    # Add voiceover + audio design (basic ffmpeg mixer)
    cmd = [
        "ffmpeg",
        "-y",
        "-i", f"{TEMP_DIR}/ainl-cinema-silent.mp4",
        "-i", voiceover_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        f"{OUTPUT_DIR}/AINL-Cinema-90sec-FINAL.mp4"
    ]
    
    subprocess.run(cmd, capture_output=True)
    print("✅ Audio mixed")

print("\n" + "=" * 50)
print("🎬 AINL Cinema Commercial Complete!")
print(f"📹 File: {OUTPUT_DIR}/AINL-Cinema-90sec-FINAL.mp4")
print("=" * 50)
