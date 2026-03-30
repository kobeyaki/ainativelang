#!/bin/bash
# AINL Mascot Animation Generator - ShortAPI (Kling 3.0)

source "$(dirname "$0")/.env"

IMAGE_PATH="${1:-}"
PROMPT="${2:-}"
DURATION="${3:-5}"
MODE="${4:-pro}"

if [ -z "$IMAGE_PATH" ] || [ -z "$PROMPT" ]; then
  echo "Usage: $0 <image_path_or_url> <prompt> [duration] [mode]"
  exit 1
fi

# If local file, base64 encode it
if [ -f "$IMAGE_PATH" ]; then
  IMAGE_B64=$(base64 -w 0 "$IMAGE_PATH")
  IMAGE_DATA="data:image/jpeg;base64,$IMAGE_B64"
else
  IMAGE_DATA="$IMAGE_PATH"
fi

echo "🚀 Submitting image-to-video job..."
RESPONSE=$(curl -s --request POST \
  --url https://api.shortapi.ai/api/v1/job/create \
  --header "Authorization: Bearer $KLING_API_KEY" \
  --header "Content-Type: application/json" \
  --data "{
    \"model\": \"kwaivgi/kling-3.0/image-to-video\",
    \"args\": {
      \"mode\": \"$MODE\",
      \"duration\": \"$DURATION\",
      \"prompt\": \"$PROMPT\",
      \"image\": \"$IMAGE_DATA\"
    }
  }")

echo "Response: $RESPONSE"
JOB_ID=$(echo "$RESPONSE" | grep -o '"job_id": *"[^"]*"' | sed 's/"job_id": *//; s/"//g')

if [ -z "$JOB_ID" ]; then
  echo "❌ Failed to get job ID"
  exit 1
fi

echo "✅ Job ID: $JOB_ID"
echo "⏳ Polling for result..."

for i in {1..60}; do
  sleep 5
  RESULT=$(curl -s --request GET \
    --url "https://api.shortapi.ai/api/v1/job/$JOB_ID" \
    --header "Authorization: Bearer $KLING_API_KEY")
  
  STATUS=$(echo "$RESULT" | grep -o '"status": *"[^"]*"' | head -1 | sed 's/"status": *//; s/"//g')
  echo "[$i] Status: $STATUS"
  
  if [ "$STATUS" = "completed" ]; then
    VIDEO_URL=$(echo "$RESULT" | grep -o '"url": *"[^"]*"' | head -1 | sed 's/"url": *//; s/"//g')
    echo "🎬 Done! Video URL: $VIDEO_URL"
    
    # Download it
    OUTPUT="ainl-animation-$(date +%s).mp4"
    curl -s -o "/data/.openclaw/workspace/ainl-video/$OUTPUT" "$VIDEO_URL"
    echo "💾 Saved to: /data/.openclaw/workspace/ainl-video/$OUTPUT"
    exit 0
  fi
  
  if [ "$STATUS" = "failed" ]; then
    echo "❌ Job failed: $RESULT"
    exit 1
  fi
done

echo "⏰ Timed out waiting for job $JOB_ID"
