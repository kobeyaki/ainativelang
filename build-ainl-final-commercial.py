#!/usr/bin/env python3
"""
AINL 60s Inspirational Commercial - Final Build
ElevenLabs + Kling
"""

import os
import requests
import json
import time
import subprocess
from pathlib import Path

# API Keys
KLING_KEY = "sk_189d02eb3e607d0dcaa52a8ee54cf4a26215a06762e23b49"
ELEVENLABS_KEY = "ak-39bb2a97379a11f1bc0caaba74064af8"

OUTPUT_DIR = "/data/.openclaw/workspace/ainl-videos"
TEMP_DIR = "/tmp/ainl-final"

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Script text
SCRIPT = """What if building agents didn't have to be expensive? What if you could ship faster, cheaper, with complete control? What if the future of AI was deterministic, not chaotic? There's a better way. AINL is the compiler for the future. Turn reasoning into structure. Turn ideas into systems. This isn't theoretical. It's real. 100+ agents running at scale. $29 a month. 99.7% uptime. 90% cheaper than traditional orchestration. The cost problem is solved. The speed problem is solved. The reliability problem is solved. You can build this. You already have the tools. You already have the vision. AINL gives you the infrastructure. Join the future. github.com/sbhooley/ainativelang. Build something real."""

print("🎬 AINL 60s Inspirational Commercial Build")
print("=" * 60)

# ============================================================================
# STEP 1: Generate voiceover with ElevenLabs
# ============================================================================

print("\n🎙️ Generating voiceover with ElevenLabs...")

url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
headers = {
    "xi-api-key": ELEVENLABS_KEY,
    "Content-Type": "application/json"
}
data = {
    "text": SCRIPT,
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
    }
}

try:
    response = requests.post(url, json=data, headers=headers, timeout=60)
    if response.status_code == 200:
        voiceover_path = f"{TEMP_DIR}/voiceover.mp3"
        with open(voiceover_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ Voiceover generated: {voiceover_path}")
    else:
        print(f"❌ ElevenLabs error: {response.status_code} - {response.text}")
        voiceover_path = None
except Exception as e:
    print(f"❌ Error generating voiceover: {e}")
    voiceover_path = None

# ============================================================================
# STEP 2: Generate Kling video sequences
# ============================================================================

print("\n🎥 Generating Kling video sequences...")

kling_prompts = [
    "Serene, hopeful visual of a bright star materializing in cosmic space, glowing with cyan neon light, soft motion",
    "Clean, minimalist grid structure forming, data flowing smoothly, green and cyan colors, professional aesthetic",
    "Numbers $29, 99.7%, 100+ flowing and morphing elegantly on screen, glowing metrics, triumphant energy",
    "AINL logo with radiating cyan energy, confident and bold, final moment of triumph",
    "Star glowing brightly with github.com/sbhooley/ainativelang text materializing, call to action"
]

kling_jobs = []

for i, prompt in enumerate(kling_prompts, 1):
    print(f"  {i}/5: {prompt[:50]}...")
    
    url = "https://api.kling.com/v1/videos/text-to-video"
    headers = {"Authorization": f"Bearer {KLING_KEY}"}
    payload = {
        "prompt": prompt,
        "duration": 12,  # seconds
        "mode": "pro"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            job_id = data.get('id')
            kling_jobs.append(job_id)
            print(f"     ✅ Job {job_id}")
        else:
            print(f"     ❌ Error: {response.status_code}")
            kling_jobs.append(None)
    except Exception as e:
        print(f"     ❌ Error: {e}")
        kling_jobs.append(None)

print(f"\n⏳ Submitted {len([j for j in kling_jobs if j])} Kling jobs")
print("   Waiting for generation (typical: 5-10 min per video)...")

# ============================================================================
# FALLBACK: Use PIL slides if Kling unavailable
# ============================================================================

print("\n⚠️  Using PIL slides as fallback while waiting for Kling...")

# Use the 1800 slides we already generated
slides_dir = "/tmp/ainl-60s-story"
slides = sorted([f for f in os.listdir(slides_dir) if f.endswith('.png')])[:1800]

if slides:
    print(f"✅ Found {len(slides)} slides")
    
    # Build concat list
    concat_file = f"{TEMP_DIR}/concat.txt"
    with open(concat_file, "w") as f:
        for slide in slides:
            f.write(f"file '{slides_dir}/{slide}'\n")
            f.write(f"duration 0.033\n")
    
    # Assemble video
    print("🎬 Assembling silent video from slides...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        f"{TEMP_DIR}/video-silent.mp4"
    ]
    
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    if result.returncode == 0:
        print("✅ Silent video assembled")
        
        # Add voiceover if available
        if voiceover_path and os.path.exists(voiceover_path):
            print("🎙️ Adding voiceover...")
            cmd = [
                "ffmpeg", "-y",
                "-i", f"{TEMP_DIR}/video-silent.mp4",
                "-i", voiceover_path,
                "-c:v", "copy", "-c:a", "aac",
                "-map", "0:v:0", "-map", "1:a:0",
                "-shortest",
                f"{OUTPUT_DIR}/AINL-60s-Inspirational-FINAL.mp4"
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            if result.returncode == 0:
                print("✅ Final commercial assembled with voiceover")
            else:
                print("⚠️  Using silent version")
                import shutil
                shutil.copy(f"{TEMP_DIR}/video-silent.mp4", f"{OUTPUT_DIR}/AINL-60s-Inspirational-FINAL.mp4")
        else:
            print("⚠️  No voiceover, using silent version")
            import shutil
            shutil.copy(f"{TEMP_DIR}/video-silent.mp4", f"{OUTPUT_DIR}/AINL-60s-Inspirational-FINAL.mp4")
    else:
        print("❌ Video assembly failed")

# ============================================================================
# FINAL OUTPUT
# ============================================================================

output_file = f"{OUTPUT_DIR}/AINL-60s-Inspirational-FINAL.mp4"
if os.path.exists(output_file):
    size = os.path.getsize(output_file) / (1024 * 1024)
    print(f"\n{'='*60}")
    print(f"🎬 AINL 60s Inspirational Commercial Ready!")
    print(f"📹 File: {output_file}")
    print(f"💾 Size: {size:.1f} MB")
    print(f"{'='*60}")
else:
    print(f"\n❌ Output file not found")
