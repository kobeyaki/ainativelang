#!/bin/bash

# AINL YouTube Upload Script
# Uses YouTube API via curl (no Python dependencies needed)

set -e

VIDEO_FILE="/data/.openclaw/workspace/ainl-agent-template/demo-video-final.mp4"
CREDS_FILE="/data/.openclaw/workspace/.youtube-credentials.json"
TOKEN_FILE="/data/.openclaw/workspace/.youtube-token.json"

TITLE="AINL Agent Template - Demo Video"
DESCRIPTION="AINL Agent Template: Compile agents once. Run deterministically. Save 90% on tokens.

This 5-minute demo shows:
✓ Defining an agent graph in AINL
✓ Compiling to production binary
✓ Running deterministically (487 tokens per run)
✓ Cost comparison: \$1,183/year (traditional) vs \$130/year (AINL)
✓ Production metrics: 17 live agents, \$29/month, 99.7% uptime

Learn more:
→ GitHub: https://github.com/sbhooley/ainl-agent-template
→ Blog: \"Why Agent Orchestration Is Broken\"
→ Docs: https://ainativelang.com

17 agents. \$29/month. 99.7% uptime. Deterministic execution.

#AINL #Agents #AI #Infrastructure"

echo "📹 AINL YouTube Upload"
echo "======================="
echo ""

# Check if video file exists
if [ ! -f "$VIDEO_FILE" ]; then
    echo "❌ Video file not found: $VIDEO_FILE"
    exit 1
fi

FILE_SIZE=$(du -h "$VIDEO_FILE" | cut -f1)
echo "📁 Video: $(basename $VIDEO_FILE)"
echo "   Size: $FILE_SIZE"
echo ""

# Extract credentials
CLIENT_ID=$(jq -r '.web.client_id' "$CREDS_FILE")
CLIENT_SECRET=$(jq -r '.web.client_secret' "$CREDS_FILE")
REDIRECT_URI="http://localhost"

echo "🔐 Authenticating with YouTube..."
echo ""

# Step 1: Get authorization code
AUTH_URL="https://accounts.google.com/o/oauth2/auth?client_id=${CLIENT_ID}&scope=https://www.googleapis.com/auth/youtube.upload&redirect_uri=${REDIRECT_URI}&response_type=code"

echo "📱 Open this link in your browser:"
echo "   $AUTH_URL"
echo ""
echo "You will get a code like: 4/0Aa..."
echo ""
read -p "Paste the authorization code: " AUTH_CODE

if [ -z "$AUTH_CODE" ]; then
    echo "❌ No code provided"
    exit 1
fi

# Step 2: Exchange code for access token
echo "🔄 Exchanging code for access token..."

TOKEN_RESPONSE=$(curl -s -X POST "https://oauth2.googleapis.com/token" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}" \
  -d "code=${AUTH_CODE}" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=${REDIRECT_URI}")

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')
REFRESH_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.refresh_token')

if [ "$ACCESS_TOKEN" == "null" ] || [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Authentication failed"
    echo "$TOKEN_RESPONSE" | jq .
    exit 1
fi

# Save token for future use
echo "{\"access_token\": \"$ACCESS_TOKEN\", \"refresh_token\": \"$REFRESH_TOKEN\"}" > "$TOKEN_FILE"
chmod 600 "$TOKEN_FILE"

echo "✅ Authenticated!"
echo ""

# Step 3: Create video metadata
echo "📝 Preparing video metadata..."

METADATA=$(cat <<EOF
{
  "snippet": {
    "title": "$TITLE",
    "description": "$DESCRIPTION",
    "tags": ["AINL", "agents", "AI", "infrastructure"],
    "categoryId": "28"
  },
  "status": {
    "privacyStatus": "unlisted",
    "selfDeclaredMadeForKids": false
  }
}
EOF
)

# Step 4: Upload video
echo "🚀 Uploading to YouTube..."
echo ""

UPLOAD_URL="https://www.googleapis.com/upload/youtube/v3/videos?uploadType=multipart&part=snippet,status"

RESPONSE=$(curl -s -X POST "$UPLOAD_URL" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "snippet={$METADATA};type=application/json" \
  -F "status={\"privacyStatus\": \"unlisted\"};type=application/json" \
  -F "video=@$VIDEO_FILE;type=video/mp4")

VIDEO_ID=$(echo "$RESPONSE" | jq -r '.id // empty')

if [ -z "$VIDEO_ID" ] || [ "$VIDEO_ID" == "null" ]; then
    echo "❌ Upload failed"
    echo "$RESPONSE" | jq .
    exit 1
fi

YOUTUBE_URL="https://youtu.be/${VIDEO_ID}"

echo ""
echo "✅ Upload complete!"
echo ""
echo "=" * 60
echo "VIDEO DETAILS"
echo "=" * 60
echo "Video ID: $VIDEO_ID"
echo "URL: $YOUTUBE_URL"
echo "Visibility: Unlisted"
echo ""

# Save for reference
echo "$YOUTUBE_URL" > /tmp/youtube-url.txt

echo "Next steps:"
echo "1. Update GitHub README with URL: $YOUTUBE_URL"
echo "2. Send partnership emails"
echo "3. Post X thread"
echo "4. Submit to hackathon"
