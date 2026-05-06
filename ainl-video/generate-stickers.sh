#!/bin/bash

# Generate 3-second Arch sticker animations via Runway
# Output: transparent MP4 stickers for X @stickers pack

RUNWAY_KEY=$(grep RUNWAY_API_KEY /data/.openclaw/workspace/ainl-x/.env | cut -d= -f2)

if [ -z "$RUNWAY_KEY" ]; then
  echo "✗ No Runway API key"
  exit 1
fi

cd /data/.openclaw/workspace/ainl-video/stickers

echo "=== Generating Arch Sticker Animations ==="

# 1. Arch celebrating/bouncing (hype energy)
echo "Sticker 1: Celebrating Arch..."
curl -s -X POST https://api.runwayml.com/v1/videos \
  -H "Authorization: Bearer $RUNWAY_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gen3",
    "promptImage": "https://files.catbox.moe/nokadh.jpg",
    "prompt": "glowing neon star character Arch bouncing excitedly with celebration energy, jumping up and down, fireworks around it, 3 seconds, loop ready, transparent background",
    "duration": 3,
    "seed": 42
  }' | jq -r '.id'

# 2. Arch spinning/rotating (cool pose)
echo "Sticker 2: Spinning Arch..."
curl -s -X POST https://api.runwayml.com/v1/videos \
  -H "Authorization: Bearer $RUNWAY_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gen3",
    "promptImage": "https://files.catbox.moe/nokadh.jpg",
    "prompt": "glowing neon star character Arch spinning gracefully in place, smooth rotation, cyberpunk glow intensifying, 3 seconds, loop ready, transparent background",
    "duration": 3,
    "seed": 43
  }' | jq -r '.id'

# 3. Arch blinking/winking (personality)
echo "Sticker 3: Winking Arch..."
curl -s -X POST https://api.runwayml.com/v1/videos \
  -H "Authorization: Bearer $RUNWAY_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gen3",
    "promptImage": "https://files.catbox.moe/nokadh.jpg",
    "prompt": "glowing neon star character Arch blinking and winking at camera, cute expression, subtle glow pulse, 3 seconds, loop ready, transparent background",
    "duration": 3,
    "seed": 44
  }' | jq -r '.id'

echo -e "\n✓ Sticker animations submitted to Runway"
echo "Check /data/.openclaw/workspace/ainl-video/stickers/results.txt for status"
