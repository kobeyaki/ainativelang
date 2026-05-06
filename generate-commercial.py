#!/usr/bin/env python3

"""
AINL Viral Commercial Generator
90-second cinematic brand video
"""

import os
from PIL import Image, ImageDraw, ImageFont
import subprocess
from pathlib import Path

WIDTH, HEIGHT = 1920, 1080
VIDEO_DIR = Path("/tmp/ainl-commercial")
OUTPUT_FILE = Path("/data/.openclaw/workspace/ainl-videos/AINL-Commercial-90sec.mp4")

# Colors
BG_DARK = "#0d1117"
BG_PROBLEM = "#2a0000"
BG_SOLUTION = "#001a2a"
TEXT_WHITE = "#ffffff"
TEXT_RED = "#ff4444"
TEXT_GREEN = "#00dd00"
TEXT_CYAN = "#4ec9b0"
TEXT_GRAY = "#888888"

def create_blank(width, height, color=BG_DARK):
    return Image.new("RGB", (width, height), color)

# ACT 1: Problem (0-15 sec = 15 frames at 1fps equiv)

def act1_slide1():
    """Problem state - frustrated engineer"""
    img = create_blank(WIDTH, HEIGHT, BG_PROBLEM)
    draw = ImageDraw.Draw(img)
    
    try:
        font_headline = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        font_subtext = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    except:
        font_headline = font_subtext = ImageFont.load_default()
    
    draw.text((WIDTH//2, HEIGHT//2 - 150), "$1,183/year", 
              fill=TEXT_RED, font=font_headline, anchor="mm")
    draw.text((WIDTH//2, HEIGHT//2 + 100), "Orchestration you don't need",
              fill=TEXT_GRAY, font=font_subtext, anchor="mm")
    
    return img

def act1_slide2():
    """Code loops - the problem"""
    img = create_blank(WIDTH, HEIGHT, BG_PROBLEM)
    draw = ImageDraw.Draw(img)
    
    try:
        font_code = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 32)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    except:
        font_code = font_label = ImageFont.load_default()
    
    code = """while True:
    llm_call()
    decision()
    llm_call()
    execute()
    llm_call()"""
    
    draw.text((100, 200), code, fill=TEXT_RED, font=font_code)
    draw.text((WIDTH//2, HEIGHT - 150), "Every decision loops through the LLM",
              fill=TEXT_RED, font=font_label, anchor="mm")
    
    return img

# ACT 2: Solution (15-40 sec)

def act2_slide1():
    """Clean AINL code"""
    img = create_blank(WIDTH, HEIGHT, BG_SOLUTION)
    draw = ImageDraw.Draw(img)
    
    try:
        font_code = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 36)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    except:
        font_code = font_label = ImageFont.load_default()
    
    code = """graph MarketMonitor {
  node FetchPrices { type: external }
  node Analyze { type: compute }
  node Decide { type: llm }
  node Execute { type: external }
}"""
    
    draw.text((100, 200), code, fill=TEXT_CYAN, font=font_code)
    draw.text((WIDTH//2, HEIGHT - 150), "Compile once. Run deterministically.",
              fill=TEXT_CYAN, font=font_label, anchor="mm")
    
    return img

def act2_slide2():
    """Compilation success"""
    img = create_blank(WIDTH, HEIGHT, BG_SOLUTION)
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        font_check = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    except:
        font_title = font_check = ImageFont.load_default()
    
    draw.text((WIDTH//2, 200), "Compiling...", fill=TEXT_CYAN, font=font_title, anchor="mm")
    draw.text((WIDTH//2, 500), "✓ Parsing", fill=TEXT_GREEN, font=font_check, anchor="mm")
    draw.text((WIDTH//2, 650), "✓ Validating", fill=TEXT_GREEN, font=font_check, anchor="mm")
    draw.text((WIDTH//2, 800), "✓ Done", fill=TEXT_GREEN, font=font_check, anchor="mm")
    
    return img

# ACT 3: Proof (40-70 sec)

def act3_slide1():
    """Production metrics"""
    img = create_blank(WIDTH, HEIGHT, BG_DARK)
    draw = ImageDraw.Draw(img)
    
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except:
        font_big = font_label = font_small = ImageFont.load_default()
    
    draw.text((WIDTH//2, 200), "17 Agents", fill=TEXT_GREEN, font=font_big, anchor="mm")
    draw.text((WIDTH//2, 400), "$29/month", fill=TEXT_GREEN, font=font_big, anchor="mm")
    draw.text((WIDTH//2, 650), "99.7% uptime • 0 errors", fill=TEXT_CYAN, font=font_label, anchor="mm")
    
    return img

def act3_slide2():
    """Cost comparison"""
    img = create_blank(WIDTH, HEIGHT, BG_DARK)
    draw = ImageDraw.Draw(img)
    
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 56)
    except:
        font_big = font_label = ImageFont.load_default()
    
    draw.text((WIDTH//4, HEIGHT//2), "$1,183", fill=TEXT_RED, font=font_big, anchor="mm")
    draw.text((WIDTH//4, HEIGHT//2 + 150), "Traditional", fill=TEXT_GRAY, font=font_label, anchor="mm")
    
    draw.text((3*WIDTH//4, HEIGHT//2), "$130", fill=TEXT_GREEN, font=font_big, anchor="mm")
    draw.text((3*WIDTH//4, HEIGHT//2 + 150), "AINL", fill=TEXT_GREEN, font=font_label, anchor="mm")
    
    # Arrow
    draw.line([(WIDTH//2 - 100, HEIGHT//2), (WIDTH//2 + 100, HEIGHT//2)], fill=TEXT_CYAN, width=8)
    
    return img

# ACT 4: CTA (70-90 sec)

def act4_slide1():
    """Brand + GitHub"""
    img = create_blank(WIDTH, HEIGHT, BG_DARK)
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 56)
        font_link = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 48)
    except:
        font_title = font_subtitle = font_link = ImageFont.load_default()
    
    draw.text((WIDTH//2, 200), "AINL", fill=TEXT_CYAN, font=font_title, anchor="mm")
    draw.text((WIDTH//2, 450), "The Orchestration Compiler", fill=TEXT_WHITE, font=font_subtitle, anchor="mm")
    draw.text((WIDTH//2, 700), "github.com/sbhooley/ainativelang", fill=TEXT_CYAN, font=font_link, anchor="mm")
    draw.text((WIDTH//2, 900), "Apache 2.0 • Open Source", fill=TEXT_GRAY, font=font_subtitle, anchor="mm")
    
    return img

def main():
    print("🎬 Generating AINL Commercial (90 seconds)")
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Each slide duration in seconds
    slides = [
        # Act 1: Problem (15 sec)
        ("act1_problem_hook", act1_slide1(), 8),
        ("act1_loops", act1_slide2(), 7),
        
        # Act 2: Solution (25 sec)
        ("act2_code", act2_slide1(), 12),
        ("act2_compile", act2_slide2(), 13),
        
        # Act 3: Proof (30 sec)
        ("act3_metrics", act3_slide1(), 15),
        ("act3_comparison", act3_slide2(), 15),
        
        # Act 4: CTA (20 sec)
        ("act4_brand", act4_slide1(), 20),
    ]
    
    print("📸 Generating slides...")
    mp4_files = []
    
    for name, img, duration in slides:
        print(f"  {name} ({duration}s)...")
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
    print("🎬 Assembling commercial...")
    concat_file = VIDEO_DIR / "concat.txt"
    with open(concat_file, "w") as f:
        for mp4_path in mp4_files:
            f.write(f"file '{mp4_path}'\n")
    
    cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c", "copy", "-y", str(OUTPUT_FILE)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"✅ Commercial generated!")
    print(f"   File: {OUTPUT_FILE}")
    print(f"   Duration: 90 seconds")
    print(f"   Format: 1920x1080 (cinema)")

if __name__ == "__main__":
    main()
