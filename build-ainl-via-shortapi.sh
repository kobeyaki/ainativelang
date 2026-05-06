#!/bin/bash

# AINL 60s Inspirational Commercial - via ShortAPI → Kling-O1
# THIS IS THE RELIABLE PATH

SHORTAPI_KEY="ak-27f236fc371511f1bc0caaba74064af8"
CALLBACK_URL="https://clint-uncoquettish-jennifer.ngrok-free.dev/callback"
OUTPUT_DIR="/data/.openclaw/workspace/ainl-videos"
RESULTS_DIR="/data/.openclaw/workspace/ainl-video/webhook-results"

mkdir -p "$RESULTS_DIR"

echo "🎬 Building AINL 60s Inspirational via ShortAPI → Kling-O1"
echo "=========================================================="
echo ""

# Prompts for each act
prompts=(
  "Serene cosmic space with a bright star materializing, glowing with cyan neon light, slow elegant motion, cinematic"
  "Clean minimalist grid structure forming on dark background, data flowing smoothly, green and cyan colors, professional"
  "Large glowing numbers $29, 99.7%, 100+ flowing and morphing elegantly, golden and cyan neon, triumphant energy"
  "AINL logo materializing with radiating cyan energy lines, confident and bold, final triumphant moment"
  "Star glowing brightly with github.com/sbhooley/ainativelang text materializing below, call to action, hopeful energy"
)

echo "📹 Submitting 5 Kling-O1 video jobs..."
echo ""

job_ids=()

for i in {0..4}; do
  prompt="${prompts[$i]}"
  echo "$((i+1))/5: Submitting..."
  
  response=$(curl --request POST \
   --url https://api.shortapi.ai/api/v1/job/create \
   --header "Authorization: Bearer $SHORTAPI_KEY" \
   --header "Content-Type: application/json" \
   --data '{
   "model": "kwaivgi/kling-o1/text-to-video",
   "args": {
    "mode": "pro",
    "prompt": "'"$prompt"'",
    "duration": "10"
   },
   "callback_url": "'"$CALLBACK_URL"'"
  }')
  
  JOB_ID=$(echo "$response" | grep -o '"job_id":"[^"]*"' | sed 's/"job_id"://; s/"//g')
  
  if [ -n "$JOB_ID" ]; then
    echo "   ✅ Job: $JOB_ID"
    job_ids+=("$JOB_ID")
  else
    echo "   ❌ Failed"
    echo "   Response: $response"
  fi
  
  sleep 1
done

echo ""
echo "⏳ Waiting for video generation..."
echo "   (Typical: 5-10 min per video, 25-50 min total)"
echo ""
echo "Job IDs to monitor:"
printf '   %s\n' "${job_ids[@]}"
echo ""
echo "Results will appear in:"
echo "   $RESULTS_DIR"
echo ""
echo "Once all 5 videos are ready, we'll assemble them into:"
echo "   $OUTPUT_DIR/AINL-60s-Inspirational-KLING-FINAL.mp4"
