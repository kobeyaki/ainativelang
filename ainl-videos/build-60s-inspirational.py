#!/usr/bin/env python3
"""
AINL 60-Second Inspirational Commercial
Full pipeline: Replicate images → ElevenLabs VO → Kling animation → FFmpeg assembly
"""

import os
import sys
import json
import time
import math
import urllib.request
import urllib.error
import subprocess
import requests
import tempfile

sys.path.insert(0, '/data/.local/lib/python3.13/site-packages')

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# ============================================================================
# CONFIG
# ============================================================================

OUTPUT_DIR = "/data/.openclaw/workspace/ainl-videos"
TEMP_DIR = "/tmp/ainl-60s-inspirational"
FINAL_OUTPUT = f"{OUTPUT_DIR}/AINL-60s-Inspirational-FINAL.mp4"

REPLICATE_API_KEY = "r8_9yHTJQDKZfwyhm4LlU1hhg1RZcXjXEr3uUekA"
ELEVENLABS_API_KEY = "sk_7cc746ee0346a8ce5e5cf912870fe291783252a0e8a1a929"
SHORTAPI_KEY = "ak-27f236fc371511f1bc0caaba74064af8"
FLUX_VERSION = "c846a69991daf4c0e5d016514849d14ee5b2e6846ce6b9d6f21369e564cfe51e"

WIDTH, HEIGHT = 1920, 1080
FPS = 30

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# VOICEOVER SCRIPT
# ============================================================================

FULL_VOICEOVER = """What if building agents didn't have to be expensive?
What if you could ship faster, cheaper, with complete control?
What if the future of AI was deterministic, not chaotic?

There's a better way.
AINL is the compiler for the future.
Turn reasoning into structure. Turn ideas into systems.

This isn't theoretical. It's real.
One hundred agents running at scale.
Twenty-nine dollars a month. Ninety-nine point seven percent uptime.
Ninety percent cheaper than traditional orchestration.
The cost problem is solved. The speed problem is solved. The reliability problem is solved.

You can build this.
You already have the tools. You already have the vision.
AINL gives you the infrastructure.

Join the future.
github dot com slash sbhooley slash ainativelang.
Build something real."""

# ============================================================================
# STEP 1: GENERATE ELEVENLABS VOICEOVER
# ============================================================================

def generate_voiceover():
    print("\n🎙️ Generating ElevenLabs voiceover...")
    
    # Use Brian voice - deep, resonant, inspirational
    voice_id = "nPczCjzI2devNBz1zQrb"  # Brian - Deep, Resonant and Comforting
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    data = {
        "text": FULL_VOICEOVER,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.8,
            "style": 0.3,
            "use_speaker_boost": True
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        vo_path = f"{TEMP_DIR}/voiceover.mp3"
        with open(vo_path, 'wb') as f:
            f.write(response.content)
        print(f"   ✅ Voiceover saved: {vo_path} ({len(response.content)//1024}KB)")
        return vo_path
    else:
        print(f"   ❌ ElevenLabs error: {response.status_code} {response.text[:200]}")
        return None

# ============================================================================
# STEP 2: GENERATE IMAGES WITH REPLICATE
# ============================================================================

SCENE_PROMPTS = [
    # ACT 1: The Dream (12s)
    "Vast cosmic nebula, deep space, glowing stars scattered across infinite darkness, purple and cyan light rays, cinematic wide angle, 4K ultra-realistic, awe-inspiring, dreamlike, photorealistic space photography",
    
    # ACT 2: The Vision (10s)  
    "Glowing neural network visualization, neon cyan connections, nodes pulsing with energy, dark background, futuristic AI compilation, graph nodes forming organized structures, clean and elegant, inspiring technology",
    
    # ACT 3: The Proof (20s)
    "Sleek holographic dashboard floating in dark space, green glowing metrics: 100+ agents, $29/month, 99.7% uptime, data streams, cinematic lighting, clean minimalist tech UI, success metrics glowing",
    
    # ACT 4: The Call (10s)
    "Human silhouette at sunset, arms raised in triumph on mountain peak, golden hour light, cosmic background with stars visible, photorealistic, cinematic, empowering, infinite horizon, inspirational",
    
    # ACT 5: The Momentum (8s)
    "Abstract AINL logo concept, glowing star symbol, clean black background, neon cyan light emanating from center, minimalist futuristic branding, cinematic, high contrast",
]

def submit_replicate_image(prompt, scene_num):
    """Submit image generation to Replicate"""
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Bearer {REPLICATE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "version": FLUX_VERSION,
        "input": {
            "prompt": prompt,
            "width": 1920,
            "height": 1080
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        pred = response.json()
        print(f"   Scene {scene_num+1}: {pred['id']}")
        return pred['id']
    else:
        print(f"   Scene {scene_num+1} ERROR: {response.status_code} {response.text[:100]}")
        return None

def poll_replicate(pred_id, max_wait=120):
    """Poll until prediction complete, return image URL"""
    url = f"https://api.replicate.com/v1/predictions/{pred_id}"
    headers = {"Authorization": f"Bearer {REPLICATE_API_KEY}"}
    
    for i in range(max_wait // 5):
        time.sleep(5)
        response = requests.get(url, headers=headers)
        pred = response.json()
        status = pred.get('status', '')
        
        if status == 'succeeded':
            output = pred.get('output', [])
            if output:
                img_url = output[0] if isinstance(output, list) else output
                return img_url
        elif status == 'failed':
            print(f"   ❌ Prediction {pred_id} failed: {pred.get('error')}")
            return None
        
        if i % 4 == 0:
            print(f"   ... still generating ({i*5}s)")
    
    return None

def download_image(url, path):
    """Download image from URL"""
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as f:
            f.write(response.content)
        return True
    return False

# ============================================================================
# STEP 3: ANIMATE WITH KLING (image-to-video)
# ============================================================================

KLING_ANIMATION_PROMPTS = [
    # Scene 1: nebula - slow drift
    "Slow cinematic drift through cosmic nebula, stars twinkling, nebula clouds gently shifting, parallax depth, awe-inspiring motion",
    # Scene 2: neural network - energy flowing
    "Neural network connections lighting up one by one, energy flowing through nodes, compilation process, organized and satisfying",
    # Scene 3: dashboard - numbers rising
    "Holographic dashboard metrics rising, data streams flowing upward, green success indicators glowing, satisfying revelation",
    # Scene 4: human triumph - uplifting
    "Person raising arms in triumph, camera slowly pulls back revealing vast landscape, golden light intensifying, cinematic",
    # Scene 5: logo - reveal
    "Logo glowing and pulsing, light radiating outward, zoom slowly pulling back, cinematic reveal, triumphant",
]

def submit_kling_video(image_url, prompt, scene_num):
    """Submit image-to-video to Kling via ShortAPI"""
    url = "https://api.shortapi.ai/api/v1/job/create"
    headers = {
        "Authorization": f"Bearer {SHORTAPI_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "kwaivgi/kling-3.0/image-to-video",
        "args": {
            "mode": "std",
            "duration": "5",
            "prompt": prompt,
            "image": image_url
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    if result.get('code') == 0:
        job_id = result.get('data', {}).get('job_id') or result.get('job_id')
        print(f"   Scene {scene_num+1}: Kling job {job_id}")
        return job_id
    else:
        print(f"   Scene {scene_num+1} Kling error: {result}")
        return None

def poll_kling(job_id, max_wait=300):
    """Poll Kling job until complete"""
    url = f"https://api.shortapi.ai/api/v1/job/{job_id}"
    headers = {"Authorization": f"Bearer {SHORTAPI_KEY}"}
    
    for i in range(max_wait // 10):
        time.sleep(10)
        response = requests.get(url, headers=headers)
        result = response.json()
        
        status = result.get('data', {}).get('status') or result.get('status')
        code = result.get('code', -1)
        
        if code == 0 and status in (2, 'completed', 'succeed', 'succeeded'):
            # Extract video URL
            data = result.get('data', {})
            vid_url = (data.get('result', {}).get('videos', [{}])[0].get('url') or
                      data.get('url') or
                      None)
            if not vid_url:
                # Try regex
                import re
                match = re.search(r'https?://[^"]+\.mp4', json.dumps(result))
                if match:
                    vid_url = match.group(0)
            return vid_url
        elif code == 0 and status in (3, 'failed'):
            print(f"   ❌ Kling job {job_id} failed")
            return None
        
        if i % 3 == 0:
            print(f"   ... Kling generating ({i*10}s) status={status}")
    
    return None

# ============================================================================
# STEP 4: CREATE ANIMATED SLIDES (fallback if Kling fails)
# ============================================================================

def load_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        try:
            if bold:
                return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", size)
            return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", size)
        except:
            return ImageFont.load_default()

def create_animated_slide(base_img, texts, frame_num, total_frames, progress):
    """Create an animated slide from a base image with text overlays"""
    
    # Start from base image
    img = base_img.copy().convert('RGB')
    img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    
    # Subtle darkening overlay for text readability
    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 80))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # Cinematic letterbox bars
    draw = ImageDraw.Draw(img)
    bar_h = 80
    draw.rectangle([(0, 0), (WIDTH, bar_h)], fill=(0, 0, 0, 255))
    draw.rectangle([(0, HEIGHT - bar_h), (WIDTH, HEIGHT)], fill=(0, 0, 0, 255))
    
    # Ken Burns zoom effect
    zoom = 1.0 + (0.03 * progress)
    if zoom > 1.0:
        new_w = int(WIDTH * zoom)
        new_h = int(HEIGHT * zoom)
        img_zoomed = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        x_offset = (new_w - WIDTH) // 2
        y_offset = (new_h - HEIGHT) // 2
        img = img_zoomed.crop((x_offset, y_offset, x_offset + WIDTH, y_offset + HEIGHT))
        draw = ImageDraw.Draw(img)
    
    # Scanline effect (subtle)
    for y in range(bar_h, HEIGHT - bar_h, 4):
        scanline_alpha = int(5 * (math.sin(frame_num / 10 + y / 100) * 0.5 + 0.5))
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, scanline_alpha))
    
    # Draw text
    for text_cfg in texts:
        text = text_cfg['text']
        y_pos = text_cfg.get('y', HEIGHT // 2)
        font_size = text_cfg.get('size', 64)
        color = text_cfg.get('color', (255, 255, 255))
        bold = text_cfg.get('bold', False)
        fade_in = text_cfg.get('fade_in', 0.0)  # 0..1 progress to fade in
        
        # Fade in effect
        if progress < fade_in:
            alpha_mult = progress / fade_in
        else:
            alpha_mult = 1.0
        
        color_with_alpha = tuple(int(c * alpha_mult) for c in color)
        
        font = load_font(font_size, bold)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (WIDTH - text_w) // 2
        
        # Shadow for legibility
        shadow_col = tuple(int(c * 0.2 * alpha_mult) for c in color)
        draw.text((x + 2, y_pos + 2), text, font=font, fill=shadow_col)
        draw.text((x, y_pos), text, font=font, fill=color_with_alpha)
    
    return img

def generate_slide_sequence(base_img, texts, duration_sec, start_frame):
    """Generate frames for a slide sequence"""
    n_frames = int(duration_sec * FPS)
    paths = []
    
    for i in range(n_frames):
        progress = i / n_frames
        frame = create_animated_slide(base_img, texts, start_frame + i, n_frames, progress)
        path = f"{TEMP_DIR}/frame_{start_frame + i:05d}.png"
        frame.save(path)
        paths.append(path)
    
    return paths

def create_placeholder_image(color_top, color_bottom):
    """Create a gradient placeholder image"""
    img = Image.new('RGB', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    
    for y in range(HEIGHT):
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * y / HEIGHT)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * y / HEIGHT)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * y / HEIGHT)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    
    # Add some star dots
    import random
    random.seed(42)
    for _ in range(200):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        bright = random.randint(150, 255)
        size = random.choice([1, 1, 1, 2])
        draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=(bright, bright, bright))
    
    return img

# ============================================================================
# STEP 5: CONVERT VIDEO TO FRAMES
# ============================================================================

def video_to_frames(video_path, output_dir, start_frame, duration_sec):
    """Extract frames from a video file"""
    n_frames = int(duration_sec * FPS)
    
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"fps={FPS},scale={WIDTH}:{HEIGHT}",
        "-frames:v", str(n_frames),
        f"{output_dir}/frame_%05d_kling.png"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"   ffmpeg error: {result.stderr[-200:]}")
        return []
    
    # Rename frames to continuous sequence
    frames = []
    for i in range(1, n_frames + 1):
        src = f"{output_dir}/frame_{i:05d}_kling.png"
        dst = f"{output_dir}/frame_{start_frame + i - 1:05d}.png"
        if os.path.exists(src):
            os.rename(src, dst)
            frames.append(dst)
    
    return frames

# ============================================================================
# MAIN BUILD
# ============================================================================

def main():
    print("=" * 60)
    print("🎬 AINL 60s Inspirational Commercial")
    print("=" * 60)
    
    # ---- STEP 1: VOICEOVER ----
    vo_path = generate_voiceover()
    if not vo_path:
        print("⚠️  Voiceover failed - will build silent version")
    
    # ---- STEP 2: SUBMIT IMAGE GENERATION ----
    print("\n🎨 Submitting image generation...")
    pred_ids = []
    for i, prompt in enumerate(SCENE_PROMPTS):
        pid = submit_replicate_image(prompt, i)
        pred_ids.append(pid)
        time.sleep(0.5)  # rate limit courtesy
    
    print(f"   Submitted {len([p for p in pred_ids if p])} predictions")
    
    # ---- STEP 3: POLL FOR IMAGES ----
    print("\n⏳ Waiting for images (up to 2 minutes)...")
    image_urls = {}
    image_paths = {}
    
    for i, pid in enumerate(pred_ids):
        if not pid:
            continue
        print(f"   Polling scene {i+1}...")
        url = poll_replicate(pid, max_wait=120)
        if url:
            img_path = f"{TEMP_DIR}/scene_{i+1:02d}.png"
            if download_image(url, img_path):
                image_urls[i] = url
                image_paths[i] = img_path
                print(f"   ✅ Scene {i+1} image ready")
            else:
                print(f"   ❌ Scene {i+1} download failed")
        else:
            print(f"   ❌ Scene {i+1} generation failed")
    
    # Load images (or create placeholders)
    scene_images = []
    placeholders = [
        ((5, 0, 20), (30, 0, 60)),    # Deep space purple
        ((0, 10, 30), (0, 50, 80)),   # Cyan blue
        ((0, 20, 10), (0, 60, 30)),   # Green success
        ((80, 40, 0), (120, 60, 0)),  # Golden hour
        ((0, 0, 0), (10, 10, 10)),    # Black for logo
    ]
    
    for i in range(5):
        if i in image_paths and os.path.exists(image_paths[i]):
            img = Image.open(image_paths[i]).convert('RGB')
        else:
            print(f"   Using placeholder for scene {i+1}")
            img = create_placeholder_image(*placeholders[i])
        scene_images.append(img)
    
    # ---- STEP 4: SUBMIT KLING ANIMATIONS ----
    print("\n🎬 Submitting Kling animation jobs...")
    kling_jobs = {}
    
    # Animate scenes 1, 4, 5 with Kling (most impactful)
    kling_scenes = [0, 3, 4]  # indices
    
    for idx in kling_scenes:
        if idx in image_urls:
            job_id = submit_kling_video(image_urls[idx], KLING_ANIMATION_PROMPTS[idx], idx)
            if job_id:
                kling_jobs[idx] = job_id
            time.sleep(1)
    
    print(f"   Submitted {len(kling_jobs)} Kling jobs")
    
    # ---- STEP 5: BUILD PIL SLIDE SEQUENCES (for non-Kling scenes) ----
    print("\n🖼️  Building animated slide sequences...")
    
    SCENE_CONFIG = [
        # (duration_sec, texts)
        (12, [
            {'text': 'What if building agents', 'y': HEIGHT//2 - 100, 'size': 72, 'bold': True, 'color': (200, 200, 255), 'fade_in': 0.1},
            {'text': "didn't have to be expensive?", 'y': HEIGHT//2 - 10, 'size': 72, 'bold': True, 'color': (200, 200, 255), 'fade_in': 0.15},
            {'text': 'Faster. Cheaper. In complete control.', 'y': HEIGHT//2 + 90, 'size': 44, 'color': (150, 200, 255), 'fade_in': 0.4},
        ]),
        (10, [
            {'text': "There's a better way.", 'y': HEIGHT//2 - 80, 'size': 80, 'bold': True, 'color': (0, 220, 200), 'fade_in': 0.1},
            {'text': 'AINL is the compiler for the future.', 'y': HEIGHT//2 + 30, 'size': 52, 'bold': True, 'color': (100, 255, 220), 'fade_in': 0.3},
            {'text': 'Turn reasoning into structure.', 'y': HEIGHT//2 + 110, 'size': 40, 'color': (150, 255, 200), 'fade_in': 0.6},
        ]),
        (20, [
            {'text': "This isn't theoretical. It's real.", 'y': HEIGHT//2 - 180, 'size': 64, 'bold': True, 'color': (0, 255, 150), 'fade_in': 0.05},
            {'text': '100+ agents running at scale', 'y': HEIGHT//2 - 80, 'size': 52, 'bold': True, 'color': (100, 255, 180), 'fade_in': 0.15},
            {'text': '$29 / month  ·  99.7% uptime', 'y': HEIGHT//2 + 20, 'size': 64, 'bold': True, 'color': (50, 255, 120), 'fade_in': 0.3},
            {'text': '90% cheaper than traditional orchestration', 'y': HEIGHT//2 + 110, 'size': 40, 'color': (150, 255, 180), 'fade_in': 0.5},
            {'text': '✓ Cost solved  ✓ Speed solved  ✓ Reliability solved', 'y': HEIGHT//2 + 180, 'size': 36, 'color': (0, 220, 100), 'fade_in': 0.7},
        ]),
        (10, [
            {'text': 'You can build this.', 'y': HEIGHT//2 - 100, 'size': 80, 'bold': True, 'color': (255, 200, 100), 'fade_in': 0.1},
            {'text': 'You already have the vision.', 'y': HEIGHT//2, 'size': 52, 'color': (255, 220, 150), 'fade_in': 0.3},
            {'text': 'AINL gives you the infrastructure.', 'y': HEIGHT//2 + 80, 'size': 48, 'bold': True, 'color': (255, 240, 180), 'fade_in': 0.5},
        ]),
        (8, [
            {'text': 'Join the future.', 'y': HEIGHT//2 - 120, 'size': 88, 'bold': True, 'color': (0, 240, 220), 'fade_in': 0.1},
            {'text': 'github.com/sbhooley/ainativelang', 'y': HEIGHT//2 + 10, 'size': 44, 'color': (150, 255, 240), 'fade_in': 0.4},
            {'text': 'Build something real.', 'y': HEIGHT//2 + 90, 'size': 52, 'bold': True, 'color': (255, 255, 255), 'fade_in': 0.6},
        ]),
    ]
    
    # Build PIL frames for all scenes
    all_frame_paths = []
    start_frame = 0
    
    for i, (duration, texts) in enumerate(SCENE_CONFIG):
        print(f"   Building Act {i+1} slides ({duration}s)...")
        frames = generate_slide_sequence(scene_images[i], texts, duration, start_frame)
        all_frame_paths.extend(frames)
        start_frame += len(frames)
        print(f"   ✅ {len(frames)} frames")
    
    print(f"\n   Total frames: {len(all_frame_paths)} ({len(all_frame_paths)/FPS:.1f}s)")
    
    # ---- STEP 6: POLL KLING JOBS ----
    print("\n⏳ Waiting for Kling animation jobs...")
    kling_videos = {}
    
    for idx, job_id in kling_jobs.items():
        print(f"   Polling Kling scene {idx+1}...")
        vid_url = poll_kling(job_id, max_wait=300)
        if vid_url:
            vid_path = f"{TEMP_DIR}/kling_scene_{idx+1:02d}.mp4"
            response = requests.get(vid_url)
            if response.status_code == 200:
                with open(vid_path, 'wb') as f:
                    f.write(response.content)
                kling_videos[idx] = vid_path
                print(f"   ✅ Scene {idx+1} video: {len(response.content)//1024}KB")
            else:
                print(f"   ❌ Scene {idx+1} download failed")
        else:
            print(f"   ⚠️  Scene {idx+1} Kling timed out - using PIL fallback")
    
    # ---- STEP 7: REPLACE PIL FRAMES WITH KLING VIDEO WHERE AVAILABLE ----
    if kling_videos:
        print("\n🎬 Integrating Kling video sequences...")
        
        # Scene timings (cumulative frame starts)
        scene_starts = [0, 12*FPS, 22*FPS, 42*FPS, 52*FPS]
        scene_durations = [12, 10, 20, 10, 8]
        
        for scene_idx, vid_path in kling_videos.items():
            start = scene_starts[scene_idx]
            dur = scene_durations[scene_idx]
            
            print(f"   Replacing scene {scene_idx+1} frames with Kling video...")
            
            # Remove existing PIL frames for this scene
            for f_idx in range(start, start + dur * FPS):
                pil_frame = f"{TEMP_DIR}/frame_{f_idx:05d}.png"
                if os.path.exists(pil_frame):
                    os.remove(pil_frame)
            
            # Extract Kling frames and rename
            kling_frames = video_to_frames(vid_path, TEMP_DIR, start, dur)
            
            if kling_frames:
                # Add text overlays to Kling frames
                texts = SCENE_CONFIG[scene_idx][1]
                img_idx = scene_idx
                
                for frame_num, frame_path in enumerate(kling_frames):
                    if os.path.exists(frame_path):
                        progress = frame_num / len(kling_frames)
                        img = Image.open(frame_path).convert('RGB')
                        frame = create_animated_slide(
                            img, texts, frame_num, len(kling_frames), progress
                        )
                        frame.save(frame_path)
                
                print(f"   ✅ {len(kling_frames)} Kling frames integrated")
    
    # ---- STEP 8: ASSEMBLE VIDEO ----
    print("\n🎥 Assembling final video...")
    
    silent_path = f"{TEMP_DIR}/silent.mp4"
    
    # Use frame pattern approach
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-pattern_type", "glob",
        "-i", f"{TEMP_DIR}/frame_?????.png",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "slow", "-crf", "18",
        "-movflags", "+faststart",
        silent_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ffmpeg error: {result.stderr[-300:]}")
        return False
    
    print(f"   ✅ Silent video assembled")
    
    # ---- STEP 9: MIX AUDIO ----
    print("\n🎵 Mixing voiceover...")
    
    if vo_path and os.path.exists(vo_path):
        cmd = [
            "ffmpeg", "-y",
            "-i", silent_path,
            "-i", vo_path,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            FINAL_OUTPUT
        ]
    else:
        # No audio - just copy
        import shutil
        shutil.copy(silent_path, FINAL_OUTPUT)
        cmd = None
    
    if cmd:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   Audio mix error: {result.stderr[-300:]}")
            import shutil
            shutil.copy(silent_path, FINAL_OUTPUT)
        else:
            print("   ✅ Audio mixed")
    
    # ---- DONE ----
    if os.path.exists(FINAL_OUTPUT):
        size_mb = os.path.getsize(FINAL_OUTPUT) / (1024 * 1024)
        print(f"\n{'=' * 60}")
        print(f"✅ AINL 60s Inspirational Commercial COMPLETE!")
        print(f"📹 {FINAL_OUTPUT}")
        print(f"📦 Size: {size_mb:.1f} MB")
        print(f"{'=' * 60}")
        return True
    else:
        print("❌ Final output not found")
        return False

if __name__ == "__main__":
    main()
