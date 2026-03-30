import os
import sys
import time
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

BASE_PROMPT = "Cute cartoon starfish character with big expressive eyes, bold black outlines, vibrant orange color, fun degen crypto meme sticker style. Clean transparent background, white outline around character, no background elements. Telegram sticker style. The starfish is"

stickers = [
    ("higher", "doing an ecstatic fist pump in the air with the word HIGHER written above in bold chunky letters, confetti everywhere"),
    ("ath", "staring wide-eyed at a rocket shooting up off the top of the frame, stars in eyes, with text ATH in bold"),
    ("big_buy", "holding giant overflowing money bags in both arms with a huge grin, dollar signs floating around, text BIG BUY"),
    ("wagmi", "arms spread wide open in celebration with a massive smile, text WAGMI in bold colorful letters above"),
    ("ngmi", "slumped over dramatically crying a river of tears, red chart arrow going down, text NGMI"),
    ("lfg", "strapped to a rocket blasting off, helmet on, huge grin, fire trail below, text LFG"),
    ("gm", "holding an oversized coffee mug with sleepy half-open eyes and a cozy smile, text GM"),
    ("diamond_hands", "gripping huge sparkling diamonds tightly with a determined face, text DIAMOND HANDS"),
    ("wen_moon", "pointing dramatically at a crescent moon above, jaw dropped in awe, text WEN MOON"),
    ("rekt", "completely flat on the ground with X eyes and a wavy dizzy mouth, red chart crashing down, text REKT"),
]

out_dir = "/data/.openclaw/workspace/starfish-stickers/output"
os.makedirs(out_dir, exist_ok=True)

results = []
for name, action in stickers:
    print(f"Generating: {name}...")
    prompt = f"{BASE_PROMPT} {action}."
    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            quality="high",
            n=1,
            output_format="webp",
            background="transparent",
        )
        import base64
        img_data = base64.b64decode(response.data[0].b64_json)
        out_path = f"{out_dir}/{name}.webp"
        with open(out_path, "wb") as f:
            f.write(img_data)
        print(f"  ✓ Saved: {out_path}")
        results.append({"name": name, "file": out_path, "status": "ok"})
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        results.append({"name": name, "status": "error", "error": str(e)})
    time.sleep(1)

with open(f"{out_dir}/results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nDone! Results saved to results.json")
