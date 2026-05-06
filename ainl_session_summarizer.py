#!/usr/bin/env python3
"""
AINL Session Summarizer — Python implementation of proactive_session_summarizer.lang

Reads unsummarized memory/*.md files, calls LLM (OpenRouter API), and appends
terse D:/P:/T:/L:/S: format summaries to MEMORY.md.
"""

import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")
CACHE_FILE = WORKSPACE / ".ainl_summarizer_cache.json"
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_FILE = WORKSPACE / "MEMORY.md"

# Configuration
DEFAULT_MODEL = "arcee-ai/trinity-large-preview:free"
MAX_SUMMARIES_PER_RUN = 3
MAX_CHARS_PER_FILE = 6000
MAX_SUMMARY_BULLETS = 15
MAX_SUMMARY_TOKENS = 300

def load_cache():
    """Load summarization cache."""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save summarization cache."""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def get_candidates():
    """Find unsummarized memory/*.md files (excluding today)."""
    today = datetime.now().strftime("%Y-%m-%d")
    cache = load_cache()
    candidates = []
    
    if not MEMORY_DIR.exists():
        return candidates
    
    for md_file in sorted(MEMORY_DIR.glob("*.md")):
        fname = md_file.name
        if not fname.endswith(".md"):
            continue
        
        date_str = fname[:10]  # YYYY-MM-DD
        
        # Skip today
        if date_str == today:
            continue
        
        # Check if already summarized
        cache_key = f"summarized.{date_str}"
        if cache.get(cache_key) == "done":
            continue
        
        candidates.append(fname)
    
    return sorted(candidates)

def build_llm_prompt(content, date_str):
    """Build system and user messages for LLM summarization."""
    system_msg = {
        "role": "system",
        "content": (
            "You are a memory compression engine. Summarize conversation logs into ONLY "
            "terse bullet points using these exact prefixes: "
            "D: decision made, P: preference expressed, T: todo/action item, L: lesson learned, "
            "S: setting/config change. Rules: Max 15 bullets. No timestamps. No greetings. No filler. "
            "Each bullet max 20 words. Output ONLY the bullets, one per line."
        )
    }
    
    user_msg = {
        "role": "user",
        "content": f"Summarize this day's activity ({date_str}):\n\n{content}"
    }
    
    return [system_msg, user_msg]

def summarize_file(file_path, llm_model, api_key):
    """Call OpenAI API to summarize a file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR reading {file_path}: {e}", file=sys.stderr)
        return None
    
    # Skip if too short
    if len(content) < 100:
        print(f"  → Skipped {file_path.name} (too short)")
        return None
    
    # Truncate if needed
    if len(content) > MAX_CHARS_PER_FILE:
        content = content[-MAX_CHARS_PER_FILE:]
    
    date_str = file_path.name[:10]
    messages = build_llm_prompt(content, date_str)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": llm_model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": MAX_SUMMARY_TOKENS
    }
    
    try:
        print(f"  → POST to OpenAI ({llm_model})...", file=sys.stderr)
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=120
        )
        response.raise_for_status()
        
        data = response.json()
        if "choices" not in data or len(data["choices"]) == 0:
            print(f"  ✗ No choices in response for {file_path.name}", file=sys.stderr)
            return None
        
        message = data["choices"][0].get("message", {})
        summary = message.get("content")
        
        if not summary or len(summary) < 10:
            print(f"  ✗ Invalid or empty summary for {file_path.name}", file=sys.stderr)
            return None
        
        print(f"  ✓ Generated {len(summary.splitlines())} bullet(s) for {file_path.name}", file=sys.stderr)
        return summary
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ API error for {file_path.name}: {e}", file=sys.stderr)
        return None

def append_summary_to_memory(date_str, summary):
    """Append summary to MEMORY.md."""
    try:
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE, 'r') as f:
                current = f.read()
        else:
            current = "# Long-Term Memory\n\n"
        
        section_header = f"\n\n### Session Summary — {date_str}\n"
        new_content = current + section_header + summary + "\n"
        
        with open(MEMORY_FILE, 'w') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"ERROR writing MEMORY.md: {e}", file=sys.stderr)
        return False

def main():
    """Main execution."""
    now = datetime.now()
    now_iso = now.isoformat()
    today = now.strftime("%Y-%m-%d")
    
    print(f"\n[{now_iso}] AINL Session Summarizer", file=sys.stderr)
    print(f"  Current time: {today} {now.strftime('%H:%M:%S')} (America/New_York)", file=sys.stderr)
    
    # Get API key from OpenAI
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        return {"status": "error", "message": "Missing OPENAI_API_KEY"}
    
    # Use GPT-4 for summaries (was using arcee-ai/trinity, but OpenAI is available)
    llm_model = "gpt-4o-mini"
    
    # Get candidates
    candidates = get_candidates()
    print(f"  Found {len(candidates)} unsummarized day(s)", file=sys.stderr)
    
    if not candidates:
        print("  → No files to summarize", file=sys.stderr)
        return {"status": "ok", "summaries_created": 0, "files_processed": 0}
    
    # Process up to MAX_SUMMARIES_PER_RUN
    cache = load_cache()
    summaries_created = 0
    files_processed = 0
    
    for fname in candidates[:MAX_SUMMARIES_PER_RUN]:
        date_str = fname[:10]
        file_path = MEMORY_DIR / fname
        
        print(f"\n  Processing: {fname}", file=sys.stderr)
        files_processed += 1
        
        summary = summarize_file(file_path, llm_model, api_key)
        
        if summary:
            if append_summary_to_memory(date_str, summary):
                cache[f"summarized.{date_str}"] = "done"
                summaries_created += 1
                print(f"  ✓ Summary appended to MEMORY.md", file=sys.stderr)
        else:
            # Mark as done even if failed (avoid re-processing)
            cache[f"summarized.{date_str}"] = "done"
            print(f"  → Marked as done (skip on retry)", file=sys.stderr)
    
    save_cache(cache)
    
    result = {
        "status": "ok",
        "timestamp": now_iso,
        "summaries_created": summaries_created,
        "files_processed": files_processed,
        "model": llm_model,
        "max_per_run": MAX_SUMMARIES_PER_RUN,
        "candidates_remaining": max(0, len(candidates) - MAX_SUMMARIES_PER_RUN)
    }
    
    print(f"\n[{now_iso}] Summary Report:", file=sys.stderr)
    print(f"  Files processed: {files_processed}", file=sys.stderr)
    print(f"  Summaries created: {summaries_created}", file=sys.stderr)
    print(f"  Candidates remaining: {result['candidates_remaining']}", file=sys.stderr)
    print(f"  Model used: {llm_model}", file=sys.stderr)
    
    return result

if __name__ == "__main__":
    try:
        result = main()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("status") == "ok" else 1)
    except Exception as e:
        print(f"FATAL: {e}", file=sys.stderr)
        sys.exit(1)
