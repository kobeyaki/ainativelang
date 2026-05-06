#!/bin/bash

# AINL Commercial - Runway Generation + Audio Assembly
# Uses Runway API for motion graphics + OpenAI TTS for voiceover

set -e

RUNWAY_API_KEY="key_f8cc54a079666fb55af4f1764b16d235bc0272ed9051c106c3e9d93111888533385fcf8735393876cf509c25c861e000851a326a769db3ee4e6c653676fcf8af"
OUTPUT_DIR="/data/.openclaw/workspace/ainl-videos"
TEMP_DIR="/tmp/ainl-runway-commercial"

mkdir -p "$TEMP_DIR"
mkdir -p "$OUTPUT_DIR"

echo "🎬 AINL Commercial - Runway + Audio Build"
echo "=========================================="
echo ""

# ============================================================================
# PART 1: Generate Runway Sequences
# ============================================================================

echo "📹 Generating Runway sequences..."
echo ""

# Sequence 1: Problem ($1,183 chaos)
echo "1️⃣ Sequence 1: Chaos ($1,183)..."
curl -X POST "https://api.runwayml.com/v1/video_generation" \
  -H "Authorization: Bearer $RUNWAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Neon pink text $1,183 flashing and morphing on black background. Glitchy digital effects. Chromatic aberration. Cascading binary code. Intense, chaotic energy. Psychedelic color shifts between pink, cyan, purple. Fast-paced, hypnotic visual.",
    "duration": 15,
    "aspect_ratio": "16:9"
  }' > "$TEMP_DIR/seq1_response.json"

JOB_ID_1=$(jq -r '.id' "$TEMP_DIR/seq1_response.json")
echo "   Job ID: $JOB_ID_1"

# Sequence 2: Solution (Compilation grid)
echo "2️⃣ Sequence 2: Compilation..."
curl -X POST "https://api.runwayml.com/v1/video_generation" \
  -H "Authorization: Bearer $RUNWAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Neon grid materializing on screen. Text COMPILE morphing into view. Green checkmarks appearing. Code flowing smoothly. Grid expanding and contracting. Smooth transitions. Cyan and green neon. Ethereal, clean aesthetic. Calming energy building.",
    "duration": 25,
    "aspect_ratio": "16:9"
  }' > "$TEMP_DIR/seq2_response.json"

JOB_ID_2=$(jq -r '.id' "$TEMP_DIR/seq2_response.json")
echo "   Job ID: $JOB_ID_2"

# Sequence 3: Proof (Metrics flowing)
echo "3️⃣ Sequence 3: Proof..."
curl -X POST "https://api.runwayml.com/v1/video_generation" \
  -H "Authorization: Bearer $RUNWAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Numbers 17, $29, 99.7 flowing and morphing on screen. Green neon glow. Data streams cascading. Metrics pulsing. Multiple colors cycling (green, cyan, pink). Confident, powerful energy. Smooth animations. Cinematic depth.",
    "duration": 30,
    "aspect_ratio": "16:9"
  }' > "$TEMP_DIR/seq3_response.json"

JOB_ID_3=$(jq -r '.id' "$TEMP_DIR/seq3_response.json")
echo "   Job ID: $JOB_ID_3"

# Sequence 4: CTA (Radiating energy)
echo "4️⃣ Sequence 4: CTA..."
curl -X POST "https://api.runwayml.com/v1/video_generation" \
  -H "Authorization: Bearer $RUNWAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "AINL logo materializing with radiating lines. Text github.com/sbhooley/ainativelang flowing in. Neon cyan energy radiating outward. Smooth, confident finish. Pure energy. Triumphant but clean aesthetic. Final frame holds.",
    "duration": 20,
    "aspect_ratio": "16:9"
  }' > "$TEMP_DIR/seq4_response.json"

JOB_ID_4=$(jq -r '.id' "$TEMP_DIR/seq4_response.json")
echo "   Job ID: $JOB_ID_4"

echo ""
echo "⏳ Waiting for Runway to generate sequences..."
echo "This will take 5-10 minutes. Standing by..."
echo ""
echo "Job IDs:"
echo "  Seq 1 (Chaos): $JOB_ID_1"
echo "  Seq 2 (Compile): $JOB_ID_2"
echo "  Seq 3 (Proof): $JOB_ID_3"
echo "  Seq 4 (CTA): $JOB_ID_4"
echo ""
echo "Check status with:"
echo "  curl -H 'Authorization: Bearer $RUNWAY_API_KEY' https://api.runwayml.com/v1/video_generation/[JOB_ID]/status"
echo ""

# ============================================================================
# PART 2: Prepare Audio
# ============================================================================

echo "🎙️ Preparing audio..."
echo ""

# Voiceover already exists at /tmp/commercial-voiceover.mp3
if [ -f /tmp/commercial-voiceover.mp3 ]; then
    echo "✅ Voiceover ready"
    cp /tmp/commercial-voiceover.mp3 "$TEMP_DIR/voiceover.mp3"
else
    echo "⚠️  Voiceover not found. Will need to generate."
fi

# Sound design
echo "🔊 Adding sound design..."
cat > "$TEMP_DIR/sounddesign.txt" << 'EOF'
- 0-3s: Building tension tone (rising frequency)
- 3-8s: Glitch/digital effects (random beeps, whooshes)
- 8-15s: Intense bass (low frequency pulse)
- 15-25s: Transition chime (high, clear tone)
- 25-40s: Ascending synth (building)
- 40-50s: Triumphant synth chord
- 50-70s: Sustain + reverb
- 70-90s: Fade out with final pulse
EOF

echo "✅ Sound design plan created"

echo ""
echo "=========================================="
echo "Next steps:"
echo "1. Wait for Runway jobs to complete (~10 min)"
echo "2. Download video sequences"
echo "3. Assemble with ffmpeg"
echo "4. Add audio design + voiceover"
echo "5. Final commercial ready"
echo ""
