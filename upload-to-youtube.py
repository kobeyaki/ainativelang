#!/usr/bin/env python3

"""
AINL YouTube Upload Script
Uploads video to YouTube using OAuth credentials
"""

import os
import json
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Configuration
CREDENTIALS_FILE = "/data/.openclaw/workspace/.youtube-credentials.json"
TOKEN_FILE = "/data/.openclaw/workspace/.youtube-token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_client():
    """Get authenticated YouTube API client."""
    creds = None
    
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save token for next time
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build("youtube", "v3", credentials=creds)

def upload_video(video_file, title, description, visibility="unlisted"):
    """Upload video to YouTube."""
    
    # Verify file exists
    if not os.path.exists(video_file):
        print(f"❌ File not found: {video_file}")
        return None
    
    file_size = os.path.getsize(video_file) / 1024 / 1024
    print(f"📹 Uploading: {Path(video_file).name} ({file_size:.1f} MB)")
    
    # Get YouTube client
    youtube = get_youtube_client()
    
    # Prepare video metadata
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["AINL", "agents", "AI", "infrastructure"],
            "categoryId": "28"  # Science & Technology
        },
        "status": {
            "privacyStatus": visibility,
            "selfDeclaredMadeForKids": False
        }
    }
    
    # Create media upload
    media = MediaFileUpload(
        video_file,
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024  # 10MB chunks
    )
    
    # Execute upload
    try:
        print("🚀 Starting upload...")
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"  Progress: {progress}%")
            except HttpError as e:
                print(f"❌ Upload failed: {e}")
                return None
        
        video_id = response['id']
        youtube_url = f"https://youtu.be/{video_id}"
        
        print(f"✅ Upload complete!")
        print(f"   Video ID: {video_id}")
        print(f"   URL: {youtube_url}")
        
        return youtube_url
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Main entry point."""
    
    # Check dependencies
    try:
        import google_auth_oauthlib
        import googleapiclient
    except ImportError:
        print("❌ Missing dependencies. Install:")
        print("   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        sys.exit(1)
    
    # Video details
    video_file = "/data/.openclaw/workspace/ainl-agent-template/demo-video-final.mp4"
    title = "AINL Agent Template - Demo Video"
    description = """AINL Agent Template: Compile agents once. Run deterministically. Save 90% on tokens.

This 5-minute demo shows:
✓ Defining an agent graph in AINL
✓ Compiling to production binary
✓ Running deterministically (487 tokens per run)
✓ Cost comparison: $1,183/year (traditional) vs $130/year (AINL)
✓ Production metrics: 17 live agents, $29/month, 99.7% uptime

Learn more:
→ GitHub: https://github.com/sbhooley/ainl-agent-template
→ Blog: "Why Agent Orchestration Is Broken"
→ Docs: https://ainativelang.com

17 agents. $29/month. 99.7% uptime. Deterministic execution.

#AINL #Agents #AI #Infrastructure #OpenSource"""
    
    visibility = "unlisted"
    
    # Upload
    url = upload_video(video_file, title, description, visibility)
    
    if url:
        print()
        print("=" * 60)
        print("SUCCESS")
        print("=" * 60)
        print(f"Video URL: {url}")
        print()
        print("Next steps:")
        print("1. Update GitHub README with URL")
        print("2. Send partnership emails")
        print("3. Post X thread")
        print("4. Submit to hackathon")
    else:
        print()
        print("❌ Upload failed. Try again or upload manually.")
        sys.exit(1)

if __name__ == "__main__":
    main()
