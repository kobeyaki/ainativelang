---
summary: "Workspace template for HEARTBEAT.md"
read_when:
  - Bootstrapping a workspace manually
---

# HEARTBEAT.md

# HEARTBEAT TASKS

## Content Quality Check (every session)
- Read the last 5 posts from /data/.openclaw/workspace/ainl-x/post-index.json
- Flag any that contain: "top 10", "top 5", "SEO", "traffic", "flashy", "don't chase", "lobster" used weakly/repetitively, vague sea metaphors, or the "X does Y but lobsters do Z" pattern
- If ANY are off-brand: alert Kobe immediately with the tweet text and IDs
- Do NOT wait to be asked

## Cron Health (every session)
- Check for any jobs with consecutiveErrors > 0
- Alert if found