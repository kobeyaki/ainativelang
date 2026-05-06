#!/usr/bin/env python3
"""
AINL Star Commercial
- Star as hero
- Cyan scan lines (signature AINL aesthetic)
- Warm star vs cool cyan contrast
- Premium motion
- Cute + institutional
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import subprocess
import math

WIDTH, HEIGHT = 1920, 1080
FPS = 30
OUTPUT_DIR = "/data/.openclaw/workspace/ainl-videos"
TEMP_DIR = "/tmp/ainl-star-commercial"

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load star image
star_img = Image.open("/data/.openclaw/workspace/ainl-star-v2.png")
star_img = star_img.convert('RGBA')
# Resize star to reasonable size
star_width = 400
aspect = star_img.height / star_img.width
star_height = int(star_width * aspect)
star_img = star_img.resize((star_width, star_height), Image.Resampling.LANCZOS)

def create_star_slide(title_text="", subtitle_text="", star_alpha=255, star_scale=1.0, bg_color=(10, 10, 20), accent=(0, 255, 200), frame_num=0):
    """Create a slide with star as centerpiece"""
    img = Image.new('RGBA', (WIDTH, HEIGHT), bg_color + (255,))
    
    # Subtle gradient overlay
    draw = ImageDraw.Draw(img, 'RGBA')
    for y in range(HEIGHT):
        alpha = int(15 * (y / HEIGHT))
        draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, alpha))
    
    # Cyan scan lines (signature AINL look)
    line_spacing = 4
    for y in range(0, HEIGHT, line_spacing):
        opacity = int(20 * (math.sin(frame_num / 10 + y / 100) * 0.5 + 0.5))
        draw.line([(0, y), (WIDTH, y)], fill=(0, 255, 200, opacity))
    
    # Star (center, with scale/alpha animation)
    star_scaled = star_img.copy()
    if star_scale != 1.0:
        new_size = (int(star_img.width * star_scale), int(star_img.height * star_scale))
        star_scaled = star_scaled.resize(new_size, Image.Resampling.LANCZOS)
    
    # Apply alpha to star
    if star_alpha < 255:
        alpha_channel = star_scaled.split()[3]
        alpha_channel = ImageEnhance.Brightness(alpha_channel).enhance(star_alpha / 255.0)
        star_scaled.putalpha(alpha_channel)
    
    # Center star
    star_x = (WIDTH - star_scaled.width) // 2
    star_y = (HEIGHT - star_scaled.height) // 2 - 100
    img.paste(star_scaled, (star_x, star_y), star_scaled)
    
    # Star glow (cyan neon)
    glow_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img, 'RGBA')
    glow_radius = int(star_scaled.width / 2 + 30)
    glow_center = (star_x + star_scaled.width // 2, star_y + star_scaled.height // 2)
    
    # Radial glow effect
    for r in range(glow_radius, 0, -5):
        glow_alpha = int(40 * (1 - r / glow_radius))
        glow_draw.ellipse(
            [(glow_center[0] - r, glow_center[1] - r), (glow_center[0] + r, glow_center[1] + r)],
            outline=(0, 255, 200, glow_alpha)
        )
    
    img = Image.alpha_composite(img, glow_img)
    
    # Title
    if title_text:
        font_size = 140
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        draw = ImageDraw.Draw(img, 'RGBA')
        bbox = draw.textbbox((0, 0), title_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (WIDTH - text_width) // 2
        text_y = star_y + star_scaled.height + 80
        
        # Shadow
        draw.text((text_x + 3, text_y + 3), title_text, font=font, fill=(0, 0, 0, 100))
        # Main text
        draw.text((text_x, text_y), title_text, font=font, fill=accent)
    
    # Subtitle
    if subtitle_text:
        font_size = 50
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        draw = ImageDraw.Draw(img, 'RGBA')
        bbox = draw.textbbox((0, 0), subtitle_text, font=font)
        text_width = bbox[2] - bbox[0]
        sub_x = (WIDTH - text_width) // 2
        sub_y = text_y + 100 if title_text else HEIGHT - 150
        
        draw.text((sub_x, sub_y), subtitle_text, font=font, fill=(180, 180, 180, 200))
    
    return img.convert('RGB')

# ============================================================================
# Build Slides
# ============================================================================

print("🎬 Building AINL Star Commercial")
print("=" * 50)

slides = []

# Act 1: Star materializes (45 frames = 1.5s)
print("1️⃣  Act 1: Star materializes...")
for i in range(45):
    progress = i / 45.0
    alpha = int(255 * progress)
    scale = 0.5 + (0.5 * progress)  # Zoom in
    
    slide = create_star_slide(
        star_alpha=alpha,
        star_scale=scale,
        frame_num=i
    )
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

# Act 2: The problem ($210) - red text
print("2️⃣  Act 2: The Problem ($210)...")
for i in range(60):
    slide = create_star_slide(
        title_text="$210/month",
        subtitle_text="Traditional orchestration",
        accent=(255, 100, 100),
        frame_num=45 + i
    )
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

# Act 3: The solution ($29) - green text
print("3️⃣  Act 3: The Solution ($29)...")
for i in range(60):
    progress = i / 60.0
    pulse = 1.0 + (0.1 * math.sin(progress * math.pi * 2))
    
    slide = create_star_slide(
        title_text="$29/month",
        subtitle_text="AINL",
        star_scale=pulse,
        accent=(0, 255, 100),
        frame_num=105 + i
    )
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

# Act 4: The proof
print("4️⃣  Act 4: The Proof...")
for i in range(60):
    slide = create_star_slide(
        title_text="90-95% Cheaper",
        subtitle_text="100+ agents. 99.7% uptime.",
        accent=(255, 200, 0),
        frame_num=165 + i
    )
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

# Act 5: CTA
print("5️⃣  Act 5: CTA...")
for i in range(45):
    slide = create_star_slide(
        title_text="github.com/sbhooley",
        subtitle_text="/ainativelang",
        accent=(0, 255, 200),
        frame_num=225 + i
    )
    slide.save(f"{TEMP_DIR}/slide_{len(slides):04d}.png")
    slides.append(f"{TEMP_DIR}/slide_{len(slides)-1:04d}.png")

print(f"✅ Generated {len(slides)} slides ({len(slides)/30:.1f} seconds)")

# ============================================================================
# Assemble video
# ============================================================================

print("\n🎥 Assembling video...")

# Create concat list using Python
concat_file = f"{TEMP_DIR}/concat.txt"
with open(concat_file, "w") as f:
    for slide in slides:
        f.write(f"file '{slide}'\n")
        f.write(f"duration 0.033\n")

cmd = [
    "ffmpeg",
    "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", concat_file,
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "medium",
    f"{TEMP_DIR}/ainl-star-silent.mp4"
]

result = subprocess.run(cmd, capture_output=True, text=True)
if "muxing overhead" in result.stderr:
    print("✅ Video assembled (silent)")
else:
    print("⚠️  Check assembly")

# ============================================================================
# Add audio
# ============================================================================

print("\n🎙️ Adding audio...")

if os.path.exists("/tmp/commercial-voiceover.mp3"):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", f"{TEMP_DIR}/ainl-star-silent.mp4",
        "-i", "/tmp/commercial-voiceover.mp3",
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        f"{OUTPUT_DIR}/AINL-Star-90sec-FINAL.mp4"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("✅ Audio mixed")
else:
    print("⚠️  No voiceover")

print("\n" + "=" * 50)
print("🎬 AINL Star Commercial Complete!")
print(f"📹 File: {OUTPUT_DIR}/AINL-Star-90sec-FINAL.mp4")
print("=" * 50)
