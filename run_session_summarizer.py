#!/usr/bin/env python3
"""
AINL Session Summarizer - Direct Execution
Scans memory/*.md files for unsummarized days, calls LLM for compression.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
WORKSPACE = Path("/data/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_FILE = WORKSPACE / "MEMORY.md"
CACHE_FILE = WORKSPACE / ".summarizer_cache.json"

# LLM Configuration
LLM_MODEL = os.getenv("AINL_SUMMARIZER_MODEL", "arcee-ai/trinity-large-preview:free")
API_KEY = os.getenv("OPENROUTER_API_KEY", "")
API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

def load_cache():
    """Load summarization cache."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE) as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    """Save summarization cache."""
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_today_str():
    """Get today's date as YYYY-MM-DD."""
    return datetime.now().isoformat()[:10]

def find_candidates():
    """Find memory/*.md files not yet summarized."""
    today = get_today_str()
    cache = load_cache()
    candidates = []
    
    if not MEMORY_DIR.exists():
        return candidates
    
    for file_path in sorted(MEMORY_DIR.glob("*.md")):
        fname = file_path.name
        date_str = fname[:10]  # YYYY-MM-DD
        
        # Skip today
        if date_str == today:
            continue
        
        # Skip already summarized
        cache_key = f"summarized.{date_str}"
        if cache.get(cache_key) == "done":
            continue
        
        candidates.append(fname)
    
    return candidates

def read_file_content(fname):
    """Read memory file content."""
    path = MEMORY_DIR / fname
    try:
        with open(path) as f:
            return f.read()
    except:
        return ""

def call_llm(content):
    """Call OpenRouter LLM for summarization."""
    if not API_KEY:
        print("ERROR: OPENROUTER_API_KEY not set")
        return None
    
    # Truncate if too long
    if len(content) > 6000:
        content = content[-6000:]
    
    system_prompt = """You are a memory compression engine. Summarize conversation logs into ONLY terse bullet points using these exact prefixes:
D: decision made
P: preference expressed
T: todo/action item
L: lesson learned
S: setting/config change

Rules: Max 15 bullets. No timestamps. No greetings. No filler. Each bullet max 20 words. Output ONLY the bullets, one per line."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Summarize this day's activity:\n\n{content}"}
    ]
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openclaw.ai",
        "X-Title": "AINL Session Summarizer"
    }
    
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 4096
    }
    
    try:
        resp = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            choices = data.get("choices", [])
            if choices:
                msg = choices[0].get("message", {})
                # Try content first, then reasoning
                summary = msg.get("content") or msg.get("reasoning")
                return summary
    except Exception as e:
        print(f"ERROR calling LLM: {e}")
    
    return None

def append_to_memory(date_str, summary):
    """Append summary to MEMORY.md."""
    if not summary or len(summary) < 10:
        return False
    
    section_header = f"\n\n### Session Summary — {date_str}\n"
    with open(MEMORY_FILE, "a") as f:
        f.write(section_header)
        f.write(summary)
        f.write("\n")
    
    return True

def main():
    """Main execution."""
    print(f"[{datetime.now().isoformat()}] AINL Session Summarizer starting...")
    
    candidates = find_candidates()
    print(f"Found {len(candidates)} unsummarized files: {candidates}")
    
    if not candidates:
        print("No files to summarize. Exiting.")
        return {"status": "no_candidates", "files_summarized": 0}
    
    cache = load_cache()
    summaries_created = 0
    max_per_run = min(len(candidates), 3)
    
    print(f"Processing up to {max_per_run} files...")
    print(f"LLM Model: {LLM_MODEL}")
    
    for idx, candidate in enumerate(candidates[:max_per_run]):
        date_str = candidate[:10]
        print(f"\n[{idx+1}/{max_per_run}] Processing {candidate}...")
        
        content = read_file_content(candidate)
        if len(content) < 100:
            print(f"  → Content too short, skipping")
            cache[f"summarized.{date_str}"] = "done"
            continue
        
        print(f"  → Content length: {len(content)} chars")
        summary = call_llm(content)
        
        if summary and len(summary) > 10:
            print(f"  → Summary length: {len(summary)} chars")
            if append_to_memory(date_str, summary):
                cache[f"summarized.{date_str}"] = "done"
                summaries_created += 1
                print(f"  ✓ Appended to MEMORY.md")
        else:
            cache[f"summarized.{date_str}"] = "done"
            print(f"  → No summary returned, marking as done")
    
    save_cache(cache)
    
    result = {
        "status": "complete",
        "files_found": len(candidates),
        "files_processed": max_per_run,
        "summaries_created": summaries_created,
        "model_used": LLM_MODEL,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"  Files found: {result['files_found']}")
    print(f"  Files processed: {result['files_processed']}")
    print(f"  Summaries created: {result['summaries_created']}")
    print(f"  Model: {result['model_used']}")
    print(f"  Timestamp: {result['timestamp']}")
    print(f"{'='*60}")
    
    return result

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
