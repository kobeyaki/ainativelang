# Arch Meme Generation Pipeline

## Quick Start

```bash
cd /data/.openclaw/workspace/ainl-video

# Submit a meme
./meme-gen.sh "glowing neon star character in chaos explosion"

# Check results (use the Job ID from meme-gen output)
./check-results.sh 69d547c3a2c98b57c2ca05f6
```

## What's Ready

**Locked Arch Character:**
- `/data/.openclaw/workspace/ainl-video/arch/arch-LOCKED-canonical.jpg` — NEVER CHANGE

**Scripts:**
- `meme-gen.sh` — Submit jobs with auto-fallback (MJ → nano-banana)
- `check-results.sh` — Poll for results and download images
- `submit-meme.sh` — Submission + webhook waiting (legacy, webhooks broken)

**Environment:**
- ShortAPI key: `ak-6ac5d1a132ab11f1a7bee29624258157`
- Webhook: `https://clint-uncoquettish-jennifer.ngrok-free.dev/callback` (not reliable)
- Use polling instead: `./check-results.sh JOB_ID`

## Known Issues

1. **Webhooks broken** — ShortAPI creates jobs but doesn't fire callbacks
2. **Polling works** — Use check-results.sh instead
3. **Only one model per job** — Never batch multiple jobs at once
4. **Results land in arch/ only** — No experiments, no temp files

## Workflow

1. Call `meme-gen.sh` with your prompt
2. Copy the Job ID from output
3. Wait 1-2 min, then call `check-results.sh JOB_ID`
4. Image downloads to `arch/` automatically
5. Send to X whenever ready

