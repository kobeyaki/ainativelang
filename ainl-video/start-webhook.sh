#!/bin/bash

WEBHOOK_PID_FILE="/tmp/ainl-webhook.pid"
WEBHOOK_JS="/data/.openclaw/workspace/ainl-video/webhook-server.js"
WEBHOOK_LOG="/data/.openclaw/workspace/ainl-video/webhook.log"

# Check if process is already running
if [ -f "$WEBHOOK_PID_FILE" ]; then
  PID=$(cat "$WEBHOOK_PID_FILE")
  if ps -p "$PID" > /dev/null 2>&1; then
    echo "Webhook server already running (PID: $PID)"
    exit 0
  fi
fi

# Start the server
cd /data/.openclaw/workspace/ainl-video
node "$WEBHOOK_JS" >> "$WEBHOOK_LOG" 2>&1 &
PID=$!

# Save PID
echo "$PID" > "$WEBHOOK_PID_FILE"
echo "Webhook server started (PID: $PID)"
