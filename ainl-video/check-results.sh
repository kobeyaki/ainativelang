#!/bin/bash

# Poll ShortAPI directly for job results
# Usage: ./check-results.sh JOB_ID

SHORTAPI_KEY="ak-6ac5d1a132ab11f1a7bee29624258157"
JOB_ID="$1"

if [ -z "$JOB_ID" ]; then
  echo "Usage: $0 JOB_ID"
  exit 1
fi

echo "Polling job $JOB_ID..."

for i in {1..12}; do
  sleep 5
  
  response=$(curl -s --request GET \
    --url "https://api.shortapi.ai/api/v1/job/get?job_id=$JOB_ID" \
    --header "Authorization: Bearer $SHORTAPI_KEY")
  
  # Try multiple field paths for status
  status=$(echo "$response" | jq -r '.data.status // .result.status // .status // empty')
  
  if [ -n "$status" ] && [ "$status" != "1" ] && [ "$status" != "null" ]; then
    echo "Status: $status"
    
    # Extract image URL if available
    img_url=$(echo "$response" | jq -r '.data.result.images[0].url // .result.images[0].url // empty')
    
    if [ -n "$img_url" ]; then
      echo "✓ Image ready: $img_url"
      
      # Download
      filename=$(echo "$JOB_ID" | cut -c1-8)
      curl -s "$img_url" -o "/data/.openclaw/workspace/ainl-video/arch/$filename.jpg"
      echo "✓ Saved to arch/$filename.jpg"
      exit 0
    fi
  else
    echo "[$i/12] Status: $status (processing...)"
  fi
done

echo "✗ Timeout waiting for job result"
