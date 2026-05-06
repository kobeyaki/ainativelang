#!/bin/bash

# Simple, reliable meme submission + polling
# Usage: ./submit-meme.sh "prompt" "model" [aspect_ratio]

SHORTAPI_KEY="ak-6ac5d1a132ab11f1a7bee29624258157"
CALLBACK_URL="https://clint-uncoquettish-jennifer.ngrok-free.dev/callback"

PROMPT="${1:-glowing neon star character}"
MODEL="${2:-midjourney/midjourney-v7/text-to-image}"
ASPECT="${3:-1:1}"

echo "=== Submitting meme ==="
echo "Prompt: $PROMPT"
echo "Model: $MODEL"

# Submit job
response=$(curl -s --request POST \
  --url https://api.shortapi.ai/api/v1/job/create \
  --header "Authorization: Bearer $SHORTAPI_KEY" \
  --header "Content-Type: application/json" \
  --data "{
    \"model\": \"$MODEL\",
    \"args\": {
      \"mode\": \"fast\",
      \"prompt\": \"$PROMPT\",
      \"aspect_ratio\": \"$ASPECT\",
      \"omni_weight\": 85
    },
    \"callback_url\": \"$CALLBACK_URL\"
  }")

JOB_ID=$(echo "$response" | jq -r '.data.job_id // empty')

if [ -z "$JOB_ID" ]; then
  echo "✗ Job creation failed"
  echo "$response" | jq .
  exit 1
fi

echo "✓ Job: $JOB_ID"
echo "Waiting for webhook result..."

# Poll webhook results for up to 2 minutes
for i in {1..24}; do
  sleep 5
  
  # Check if new result file appeared with this job
  result=$(find /data/.openclaw/workspace/ainl-video/webhook-results -name "*.json" -newer /tmp/.submit-meme-marker 2>/dev/null | xargs grep -l "$JOB_ID" 2>/dev/null | head -1)
  
  if [ -n "$result" ]; then
    echo "✓ Result received!"
    
    # Extract best image
    img_url=$(jq -r '.payload.result.images[1].url' "$result" 2>/dev/null)
    if [ -z "$img_url" ] || [ "$img_url" = "null" ]; then
      img_url=$(jq -r '.payload.result.images[0].url' "$result" 2>/dev/null)
    fi
    
    if [ -n "$img_url" ] && [ "$img_url" != "null" ]; then
      echo "Image URL: $img_url"
      echo "$img_url"
      exit 0
    fi
  fi
done

echo "✗ No webhook result after 2 minutes"
echo "Job might still be processing. Job ID: $JOB_ID"
