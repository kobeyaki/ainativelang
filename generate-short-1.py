#!/usr/bin/env python3

"""
YouTube Short #1: "90% Cheaper"
Generates vertical video (9:16) with cost comparison
"""

import os
from PIL import Image, ImageDraw, ImageFont
import subprocess
from pathlib import Path

# Vertical dimensions (YouTube Shorts)
WIDTH, HEIGHT = 1080, 1920
VIDEO_DIR = Path("/tmp/ainl-short-1")
OUTPUT_FILE = Path("/data/.openclaw/workspace/ainl-videos/short-1-90-cheaper.mp4")

# Colors
BG_DARK = "#0d1117"
TEXT_WHITE = "#ffffff"
TEXT_RED = "#ff4444"
TEXT_GREEN = "#00dd00"
TEXT_ACCENT = "#4ec9b0"

def create_blank(width, height, color=BG_DARK):
    return Image.new("RGB", (width, height), color)

def slide_1():
    """Hook: $1,183"""
    img = create_blank(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    
    try:
        font_huge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 200)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    except:
        font_huge = font_small = ImageFont.load_default()
    
    draw.text((WIDTH//2, HEIGHT//2 - 200), "$1,183", 
              fill=TEXT_RED, font=font_huge, anchor="mm")
    draw.text((WIDTH//2, HEIGHT//2 + 100), "Your AI framework costs this per year",
              fill=TEXT_WHITE, font=font_small, anchor="mm")
    
    return img

def slide_2():
    """Problem: Orchestration"""
    img = create_blank(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        font_metric = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 60)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    except:
        font_title = font_metric = font_label = ImageFont.load_default()
    
    draw.text((WIDTH//2, 200), "Traditional", fill=TEXT_RED, font=font_title, anchor="mm")
    draw.text((WIDTH//2, 500), "4,500 tokens", fill=TEXT_WHITE, font=font_metric, anchor="mm")
    draw.text((WIDTH//2, 700), "per run", fill=TEXT_WHITE, font=font_label, anchor="mm")
    draw.text((WIDTH//2, 1000), "$6/day", fill=TEXT_RED, font=font_metric, anchor="mm")
    draw.text((WIDTH//2, 1600), "Orchestration loops", fill=TEXT_WHITE, font=font_label, anchor="mm")
    
    return img

def slide_3():
    """Solution: AINL"""
    img = create_blank(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        font_metric = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 60)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    except:
        font_title = font_metric = font_label = ImageFont.load_default()
    
    draw.text((WIDTH//2, 200), "AINL Compiled", fill=TEXT_GREEN, font=font_title, anchor="mm")
    draw.text((WIDTH//2, 500), "487 tokens", fill=TEXT_GREEN, font=font_metric, anchor="mm")
    draw.text((WIDTH//2, 700), "per run", fill=TEXT_WHITE, font=font_label, anchor="mm")
    draw.text((WIDTH//2, 1000), "$0.35/day", fill=TEXT_GREEN, font=font_metric, anchor="mm")
    draw.text((WIDTH//2, 1600), "Deterministic execution", fill=TEXT_WHITE, font=font_label, anchor="mm")
    
    return img

def slide_4():
    """CTA"""
    img = create_blank(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    
    try:
        font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
        font_percent = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
        font_link = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 48)
    except:
        font_cta = font_percent = font_link = ImageFont.load_default()
    
    draw.text((WIDTH//2, HEIGHT//2 - 300), "90%", fill=TEXT_GREEN, font=font_cta, anchor="mm")
    draw.text((WIDTH//2, HEIGHT//2 - 100), "Cheaper", fill=TEXT_WHITE, font=font_percent, anchor="mm")
    draw.text((WIDTH//2, HEIGHT//2 + 200), "github.com/sbhooley/", fill=TEXT_ACCENT, font=font_link, anchor="mm")
    draw.text((WIDTH//2, HEIGHT//2 + 320), "ainativelang", fill=TEXT_ACCENT, font=font_link, anchor="mm")
    
    return img

def main():
    print("🎬 Generating YouTube Short #1: 90% Cheaper")
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    slides = [
        ("slide_1_hook", slide_1(), 5),
        ("slide_2_problem", slide_2(), 10),
        ("slide_3_solution", slide_3(), 10),
        ("slide_4_cta", slide_4(), 5),
    ]
    
    print("📸 Generating slides...")
    mp4_files = []
    
    for name, img, duration in slides:
        print(f"  {name}...")
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
    
    # Concatenate
    print("🎬 Concatenating slides...")
    concat_file = VIDEO_DIR / "concat.txt"
    with open(concat_file, "w") as f:
        for mp4_path in mp4_files:
            f.write(f"file '{mp4_path}'\n")
    
    cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c", "copy", "-y", str(OUTPUT_FILE)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"✅ Short generated!")
    print(f"   File: {OUTPUT_FILE}")
    print(f"   Duration: 30 seconds")
    print(f"   Format: 1080x1920 (vertical)")

if __name__ == "__main__":
    main()
