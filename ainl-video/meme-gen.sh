#!/bin/bash

# Bulletproof meme generation with multiple model fallbacks
# Usage: ./meme-gen.sh "prompt"

SHORTAPI_KEY="ak-0e4129b1343911f1bc0caaba74064af8"
CALLBACK_URL="https://clint-uncoquettish-jennifer.ngrok-free.dev/callback"
PROMPT="${1:-glowing neon star character}"

echo "=== Meme Gen: $PROMPT ==="

# Try MJ v7 text-to-image first
echo "Trying MJ v7 text-to-image..."
response=$(curl -s --request POST \
  --url https://api.shortapi.ai/api/v1/job/create \
  --header "Authorization: Bearer $SHORTAPI_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "model": "midjourney/midjourney-v7/text-to-image",
    "args": {
      "mode": "fast",
      "prompt": "'"$PROMPT"'",
      "aspect_ratio": "1:1",
      "omni_weight": 85
    },
    "callback_url": "'"$CALLBACK_URL"'"
  }')

JOB_ID=$(echo "$response" | jq -r '.data.job_id // empty')

if [ -z "$JOB_ID" ]; then
  # Fallback to nano-banana
  echo "MJ failed, trying nano-banana..."
  response=$(curl -s --request POST \
    --url https://api.shortapi.ai/api/v1/job/create \
    --header "Authorization: Bearer $SHORTAPI_KEY" \
    --header "Content-Type: application/json" \
    --data '{
      "model": "google/nano-banana-pro/text-to-image",
      "args": {
        "prompt": "'"$PROMPT"'",
        "aspect_ratio": "1:1"
      },
      "callback_url": "'"$CALLBACK_URL"'"
    }')
  
  JOB_ID=$(echo "$response" | jq -r '.data.job_id // empty')
fi

if [ -z "$JOB_ID" ]; then
  echo "✗ Both models failed"
  echo "$response" | jq .
  exit 1
fi

echo "✓ Job: $JOB_ID"
echo "Submitted to ShortAPI. Results will appear in /data/.openclaw/workspace/ainl-video/webhook-results/"
echo "Job ID: $JOB_ID"
