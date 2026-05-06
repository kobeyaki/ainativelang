#!/bin/bash

# Simple wrapper to always use the right webhook URL
# Usage: ./job-submit.sh "prompt" "aspect_ratio" "model" [omni_weight]

SHORTAPI_KEY="ak-406b5e5f326211f19ef2c6e98b914f8d"
WEBHOOK_URL_FILE="/data/.openclaw/workspace/ainl-video/.webhook-url"

# Ensure webhook is running
/data/.openclaw/workspace/ainl-video/setup-webhooks-persistent.sh 2>/dev/null

# Get the webhook URL
CALLBACK_URL=$(cat "$WEBHOOK_URL_FILE" 2>/dev/null)

if [ -z "$CALLBACK_URL" ]; then
  echo "✗ No webhook URL found. Run setup-webhooks-persistent.sh first"
  exit 1
fi

PROMPT="$1"
ASPECT_RATIO="${2:-1:1}"
MODEL="${3:-midjourney/midjourney-v7/text-to-image}"
OMNI_WEIGHT="${4:-80}"
IMAGE_URL="${5:-}"

echo "Submitting job to $MODEL..."
echo "Webhook: $CALLBACK_URL"

if [ -n "$IMAGE_URL" ]; then
  # Image-to-image request
  curl --silent --request POST \
    --url https://api.shortapi.ai/api/v1/job/create \
    --header "Authorization: Bearer $SHORTAPI_KEY" \
    --header "Content-Type: application/json" \
    --data "{
      \"model\": \"$MODEL\",
      \"args\": {
        \"mode\": \"fast\",
        \"image_url\": \"$IMAGE_URL\",
        \"prompt\": \"$PROMPT\",
        \"aspect_ratio\": \"$ASPECT_RATIO\",
        \"omni_weight\": $OMNI_WEIGHT
      },
      \"callback_url\": \"$CALLBACK_URL\"
    }" | jq .
else
  # Text-to-image request
  curl --silent --request POST \
    --url https://api.shortapi.ai/api/v1/job/create \
    --header "Authorization: Bearer $SHORTAPI_KEY" \
    --header "Content-Type: application/json" \
    --data "{
      \"model\": \"$MODEL\",
      \"args\": {
        \"prompt\": \"$PROMPT\",
        \"aspect_ratio\": \"$ASPECT_RATIO\"
      },
      \"callback_url\": \"$CALLBACK_URL\"
    }" | jq .
fi
