#!/bin/bash

# Persistent webhook + ngrok health check loop
# Run in background: nohup ./keep-alive.sh > /tmp/webhook-keepalive.log 2>&1 &

WEBHOOK_HOME="/data/.openclaw/workspace/ainl-video"
WEBHOOK_PID_FILE="/tmp/webhook.pid"
NGROK_PID_FILE="/tmp/ngrok.pid"

while true; do
  # Check webhook
  if [ ! -f "$WEBHOOK_PID_FILE" ] || ! ps -p $(cat "$WEBHOOK_PID_FILE" 2>/dev/null) > /dev/null 2>&1; then
    echo "[$(date)] Webhook down, restarting..."
    cd "$WEBHOOK_HOME"
    node webhook-server.js > webhook.log 2>&1 &
    echo $! > "$WEBHOOK_PID_FILE"
  fi

  # Check ngrok
  if [ ! -f "$NGROK_PID_FILE" ] || ! ps -p $(cat "$NGROK_PID_FILE" 2>/dev/null) > /dev/null 2>&1; then
    echo "[$(date)] Ngrok down, restarting..."
    ~/.local/bin/ngrok http 3333 --log=stdout > /tmp/ngrok.log 2>&1 &
    echo $! > "$NGROK_PID_FILE"
    sleep 3
    NGROK_URL=$(grep -oP 'https://[^/]*\.ngrok-free\.dev' /tmp/ngrok.log | head -1)
    if [ -n "$NGROK_URL" ]; then
      echo "$NGROK_URL/callback" > .webhook-url
      echo "[$(date)] Ngrok URL: $NGROK_URL/callback"
    fi
  fi

  sleep 30
done
