#!/bin/bash

# Persistent webhook + ngrok setup
# Run once, survives restarts and session resets

WEBHOOK_HOME="/data/.openclaw/workspace/ainl-video"
NGROK_CONFIG="$WEBHOOK_HOME/.ngrok-config"
WEBHOOK_URL_FILE="$WEBHOOK_HOME/.webhook-url"
WEBHOOK_PID_FILE="/tmp/ainl-webhook.pid"
NGROK_PID_FILE="/tmp/ainl-ngrok.pid"

echo "=== Setting up persistent webhooks ==="

# 1. Install ngrok if missing
if ! command -v ngrok &> /dev/null; then
  echo "Installing ngrok..."
  mkdir -p ~/.local/bin
  curl -s -L https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip -o /tmp/ngrok.zip
  unzip -q /tmp/ngrok.zip -d ~/.local/bin/
  chmod +x ~/.local/bin/ngrok
fi

# 2. Start webhook server
start_webhook() {
  if [ -f "$WEBHOOK_PID_FILE" ]; then
    PID=$(cat "$WEBHOOK_PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
      echo "✓ Webhook already running (PID: $PID)"
      return 0
    fi
  fi

  cd "$WEBHOOK_HOME"
  node webhook-server.js >> webhook.log 2>&1 &
  PID=$!
  echo "$PID" > "$WEBHOOK_PID_FILE"
  echo "✓ Webhook server started (PID: $PID)"
}

# 3. Start ngrok tunnel
start_ngrok() {
  if [ -f "$NGROK_PID_FILE" ]; then
    PID=$(cat "$NGROK_PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
      if [ -f "$WEBHOOK_URL_FILE" ]; then
        URL=$(cat "$WEBHOOK_URL_FILE")
        echo "✓ Ngrok already running (PID: $PID)"
        echo "✓ Webhook URL: $URL"
        return 0
      fi
    fi
  fi

  ~/.local/bin/ngrok http 3333 --log=stdout >> /tmp/ngrok.log 2>&1 &
  PID=$!
  echo "$PID" > "$NGROK_PID_FILE"

  # Wait for URL to appear in log
  sleep 3
  URL=$(grep -oP 'https://[^/]*\.ngrok-free\.dev' /tmp/ngrok.log | head -1)
  
  if [ -n "$URL" ]; then
    echo "$URL/callback" > "$WEBHOOK_URL_FILE"
    echo "✓ Ngrok tunnel started (PID: $PID)"
    echo "✓ Webhook URL: $URL/callback"
  else
    echo "✗ Failed to get ngrok URL"
    return 1
  fi
}

# 4. Health check + restart loop
health_check() {
  while true; do
    sleep 30

    # Check webhook
    if ! ps -p "$(cat $WEBHOOK_PID_FILE 2>/dev/null)" > /dev/null 2>&1; then
      echo "Webhook died, restarting..."
      start_webhook
    fi

    # Check ngrok
    if ! ps -p "$(cat $NGROK_PID_FILE 2>/dev/null)" > /dev/null 2>&1; then
      echo "Ngrok died, restarting..."
      start_ngrok
    fi
  done
}

# Start both
start_webhook
start_ngrok

# Run health check in background
health_check &
HEALTH_PID=$!
echo $HEALTH_PID > /tmp/ainl-health-check.pid

echo "✓ Setup complete"
echo "Webhook URL saved to: $WEBHOOK_URL_FILE"
