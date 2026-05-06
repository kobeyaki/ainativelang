#!/bin/bash

# Persistent webhook server keep-alive
# Runs forever, auto-restarts if process dies

SCRIPT_DIR="/data/.openclaw/workspace/ainl-video"
LOG_FILE="/tmp/webhook-keepalive.log"
PID_FILE="/tmp/webhook-server.pid"

echo "[$(date)] Starting webhook keepalive..." >> $LOG_FILE

while true; do
  # Check if process is running
  if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    if ps -p $PID > /dev/null 2>&1; then
      # Process is alive
      sleep 30
      continue
    else
      # Process died, restart
      echo "[$(date)] Process $PID died, restarting..." >> $LOG_FILE
    fi
  fi

  # Start webhook server
  cd "$SCRIPT_DIR"
  node webhook-server.js > /tmp/webhook-server.log 2>&1 &
  NEW_PID=$!
  echo $NEW_PID > "$PID_FILE"
  
  echo "[$(date)] Started webhook server (PID: $NEW_PID)" >> $LOG_FILE
  
  # Wait before checking again
  sleep 30
done
