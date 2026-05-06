# YouTube Upload Guide - AINL Agent Template Demo

**Video file:** `/data/.openclaw/workspace/ainl-agent-template/demo-video-final.mp4`  
**Size:** 983 KB  
**Duration:** ~63 seconds (5 minutes)  
**Format:** MP4 (H.264 + AAC) - YouTube-ready

---

## Step 1: Go to YouTube Studio

1. Go to https://youtube.com/studio
2. Sign in with your AINL YouTube channel account
3. Click **"Create"** (top left, red button) → **"Upload video"**

---

## Step 2: Select & Upload File

1. Click **"SELECT FILES"** or drag-and-drop
2. Choose: `/data/.openclaw/workspace/ainl-agent-template/demo-video-final.mp4`
3. Wait for upload (should be fast - 983 KB)

---

## Step 3: Fill in Details

### Title:
```
AINL Agent Template - Demo Video
```

### Description:
```
AINL Agent Template: Compile agents once. Run deterministically. Save 90% on tokens.

This 5-minute demo shows:
✓ Defining an agent graph in AINL
✓ Compiling to production binary
✓ Running deterministically (487 tokens per run)
✓ Cost comparison: $1,183/year (traditional) vs $130/year (AINL)
✓ Production metrics: 17 live agents, $29/month, 99.7% uptime

Learn more:
→ GitHub: https://github.com/sbhooley/ainativelang
→ Blog: "Why Agent Orchestration Is Broken"
→ Docs: https://ainativelang.com

17 agents. $29/month. 99.7% uptime. Deterministic execution.

#AINL #Agents #AI #Infrastructure #OpenSource
```

### Visibility:
- Select **"Unlisted"** (not Private, not Public - link-only access)
- ✓ This allows you to share the link with hackathon judges without it appearing in search/recommendations

### Other Settings (optional):
- **Comments:** Allow (probably good for feedback)
- **Premiere:** Off (just upload)
- **Age restriction:** None
- **License:** Standard YouTube license (or CC if you prefer)

---

## Step 4: Advanced Settings (Optional)

Go to **"More options"** if you want to:
- Add **Chapters/Timestamps**:
  ```
  0:00 - Intro
  0:03 - Code Example
  0:11 - Compilation
  0:19 - Runtime
  0:31 - Cost Analysis
  0:43 - Production Proof
  0:53 - CTA
  ```
- Add **Tags:** agent, AI, infrastructure, AINL, compiler
- Add **Custom Thumbnail:** (optional - YouTube will generate one)

---

## Step 5: Save & Upload

1. Click **"SAVE"** (bottom right)
2. YouTube processes the video (~2-3 minutes for this size)
3. Wait for **"Ready to play"** notification
4. You'll see a link like: `https://youtu.be/ABC123DEF456`

---

## Step 6: Copy the Video URL

Once processing is done:

1. Click the video title or thumbnail
2. Copy the URL from the address bar
   - Format: `https://youtu.be/ABC123` (short)
   - Or: `https://www.youtube.com/watch?v=ABC123` (long)
3. Use the **short format** (cleaner for sharing)

---

## Step 7: Update GitHub README

In your GitHub repo, update the README with the actual YouTube link:

**Before:**
```markdown
[Watch on YouTube (unlisted)](https://youtu.be/PLACEHOLDER)
```

**After:**
```markdown
[Watch on YouTube (unlisted)](https://youtu.be/ABC123)
```

Then push:
```bash
cd /data/.openclaw/workspace/ainl-agent-template
git add README.md
git commit -m "Add YouTube demo video link"
git push
```

---

## Step 8: Test the Link

1. Copy the short URL (e.g., https://youtu.be/ABC123)
2. Open in incognito/private window (fresh browser)
3. Verify:
   - ✓ Video plays
   - ✓ Audio works
   - ✓ Title visible
   - ✓ Description visible
   - ✓ Quality is 1080p (or available at 1080p)

---

## Copy-Paste Commands

Once you have the YouTube video ID (e.g., `ABC123DEF456`):

```bash
# Update README
cd /data/.openclaw/workspace/ainl-agent-template

# Replace PLACEHOLDER with actual ID
sed -i 's/PLACEHOLDER/ABC123DEF456/g' README.md

# Verify change
grep youtube README.md

# Push
git add README.md
git commit -m "Add YouTube demo video link"
git push
```

---

## Sharing the Link

Once live, share in:

1. **GitHub README** (already done above)
2. **Blog post** (add link to published blog)
3. **Partnership emails** (include link when sending)
4. **X thread** (quote-tweet with link)
5. **Hackathon submission** (add to application form)

---

## Expected Results

Once the video is up:

✅ **YouTube:**
- Unlisted video live
- Short URL working
- Embedded in GitHub README
- Play count starts accumulating

✅ **GitHub:**
- README updated with link
- Thumbnail preview loads
- Link drives traffic to YouTube

✅ **Outreach:**
- Partnership emails include video link
- X thread has video quote-tweet
- Hackathon application has video link

---

## Troubleshooting

**"Video still processing"**
- Wait 2-3 minutes, refresh
- Processing usually happens automatically

**"Unlisted option not available"**
- Make sure you're uploading to your own channel (not a brand account)
- Or switch to "Private" temporarily, then change to "Unlisted" after upload

**"Video won't play"**
- Check the file isn't corrupted: `file demo-video-final.mp4`
- Try uploading again if needed
- Check your internet connection

**"Audio not working"**
- The video has AAC audio track
- If YouTube shows "no audio," try re-uploading
- Or try downloading and re-encoding: `ffmpeg -i demo-video-final.mp4 -c:v copy -c:a aac output.mp4`

---

## Timeline

- **Upload:** 1 minute
- **Processing:** 2-3 minutes
- **Ready to share:** ~5 minutes total

**Then:** Update GitHub + send emails (another 30 min)

---

## You're all set. Go upload it.

Once live, reply with the YouTube link and I'll:
1. Update all references
2. Generate share cards for X
3. Help with any next steps

**Let's go.**
