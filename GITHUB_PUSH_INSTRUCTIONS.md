# GitHub Push Instructions - ainl-agent-template

**Status:** Local git repo initialized, ready to push ✓

---

## Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Fill in details:
   - **Repository name:** `ainl-agent-template`
   - **Description:** "AINL Agent Template: Production-grade starter for deterministic, compiled multi-agent systems. 90% cheaper than traditional orchestration."
   - **Visibility:** Public
   - **Initialize this repository with:**
     - ☐ README (we have one)
     - ☐ .gitignore (optional)
     - ☐ License (we'll add MIT)
3. Click **Create repository**

---

## Step 2: Push from Local

Copy and paste these commands:

```bash
cd /data/.openclaw/workspace/ainl-agent-template

git remote add origin https://github.com/sbhooley/ainl-agent-template.git

git branch -M main

git push -u origin main
```

---

## Step 3: Verify

1. Go to https://github.com/sbhooley/ainl-agent-template
2. You should see:
   - ✓ README.md (with demo video link placeholder)
   - ✓ Makefile
   - ✓ examples/ folder (market_monitor, research_agent)
   - ✓ docs/ folder (COST_CALCULATOR.md)
   - ✓ .github/ folder (HACKATHON.md)
   - ✓ demo-video-final.mp4 (983 KB)

---

## Step 4: Add License

If you didn't select MIT license during creation:

1. Go to repo settings → Add file → Create new file
2. Name: `LICENSE`
3. Paste MIT license text (GitHub will auto-detect and fill)
4. Commit

---

## After Push: Update README

Once video is on YouTube, update the README with actual video ID:

1. Go to YouTube, find your video
2. Extract video ID from URL (e.g., `https://youtu.be/ABC123` → `ABC123`)
3. Update README.md:

```markdown
[![AINL Agent Template Demo Video](https://img.youtube.com/vi/ABC123/maxresdefault.jpg)](https://youtu.be/ABC123)

[Watch on YouTube (unlisted)](https://youtu.be/ABC123)
```

Push this change:
```bash
git add README.md
git commit -m "Add YouTube demo video link"
git push
```

---

## Status Checklist

- [ ] GitHub repo created
- [ ] Local code pushed
- [ ] README verified
- [ ] Demo video on YouTube
- [ ] YouTube link added to README
- [ ] Blog post published
- [ ] Partnership emails sent
- [ ] X thread posted
- [ ] Hackathon application submitted

---

## Need Help?

If push fails:

```bash
# Check remote
git remote -v

# Check branch
git branch -a

# Check commits
git log --oneline

# Test connection
ssh -T git@github.com
```

Common issues:
- **Authentication:** Make sure you have GitHub SSH key set up (or use HTTPS with token)
- **Branch mismatch:** `git branch -M main` renames master → main
- **Remote already exists:** `git remote rm origin` then add again

---

**Once pushed:** Repo is live. Share link for hackathon submission.
