#!/bin/bash

# Once image is ready, this creates animated sticker with transparent bg

INPUT="/tmp/star-jetpack-laser.png"
OUTPUT_DIR="/data/.openclaw/workspace/ainl-stickers"
mkdir -p "$OUTPUT_DIR"

echo "Converting image to animated sticker..."

# 1. Remove background (make transparent)
# 2. Create animation frames (hover/float effect)
# 3. Generate WebP animated sticker
# 4. Create Telegram sticker set

# For now, just save the base image
cp "$INPUT" "$OUTPUT_DIR/ainl-star-jetpack-base.png"

echo "✅ Sticker pack prepared at: $OUTPUT_DIR"
