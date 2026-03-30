#!/usr/bin/env python3
"""AINL Session Summarizer - OpenAI Edition (no external deps)."""

import json
import urllib.request
import urllib.error
import os
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_FILE = WORKSPACE / "MEMORY.md"
CACHE_FILE = WORKSPACE / ".summarizer_cache.json"

API_KEY = os.environ.get("OPENAI_API_KEY", "")
API_ENDPOINT = "https://api.openai.com/v1/chat/completions"

def load_cache():
    """Load cache."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE) as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    """Save cache."""
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_today():
    """Get today's date."""
    return datetime.now().isoformat()[:10]

def find_candidates():
    """Find unsummarized files."""
    today = get_today()
    cache = load_cache()
    candidates = []
    
    if not MEMORY_DIR.exists():
        return candidates
    
    for path in sorted(MEMORY_DIR.glob("*.md")):
        fname = path.name
        datestr = fname[:10]
        
        if datestr == today:
            continue
        
        if cache.get(f"summarized.{datestr}") == "done":
            continue
        
        candidates.append(fname)
    
    return candidates

def call_llm(content):
    """Call OpenAI API."""
    if not API_KEY:
        print("ERROR: OPENAI_API_KEY not set")
        return None
    
    # Truncate
    if len(content) > 5000:
        content = content[-5000:]
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a memory compression engine. Summarize session activity into ONLY terse D:/P:/T:/L:/S: bullets (max 15). D=decision made, P=preference expressed, T=todo/action, L=lesson learned, S=setting/config change. Each bullet max 20 words. Output ONLY the bullets, one per line, no intro."
            },
            {
                "role": "user",
                "content": f"Compress this session:\n\n{content}"
            }
        ],
        "temperature": 0.3,
        "max_tokens": 800
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            API_ENDPOINT,
            data=data,
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=120) as response:
            resp_data = json.loads(response.read().decode('utf-8'))
            choices = resp_data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"API Error: {e.code}")
        try:
            error_json = json.loads(error_body)
            print(f"  Message: {error_json.get('error', {}).get('message', error_body)}")
        except:
            print(f"  {error_body[:200]}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    return None

def main():
    print(f"[{datetime.now().isoformat()}] AINL Session Summarizer starting...")
    print("Using OpenAI gpt-4o-mini for compression")
    
    candidates = find_candidates()
    print(f"Found {len(candidates)} unsummarized files: {candidates}")
    
    if not candidates:
        print("No files to summarize.")
        return
    
    cache = load_cache()
    summaries_created = 0
    max_per_run = min(len(candidates), 3)
    
    print(f"Processing up to {max_per_run} files...\n")
    
    for idx, candidate in enumerate(candidates[:max_per_run]):
        datestr = candidate[:10]
        print(f"[{idx+1}/{max_per_run}] {candidate}")
        
        # Read content
        filepath = MEMORY_DIR / candidate
        try:
            with open(filepath) as f:
                content = f.read()
        except:
            print(f"  → ERROR reading file")
            cache[f"summarized.{datestr}"] = "done"
            continue
        
        content_len = len(content)
        
        if content_len < 100:
            print(f"  → Too short ({content_len} chars)")
            cache[f"summarized.{datestr}"] = "done"
            continue
        
        print(f"  → Size: {content_len} chars")
        
        # Call LLM
        summary = call_llm(content)
        
        if summary and len(summary) > 20:
            print(f"  → Summary: {len(summary)} chars")
            
            # Append
            with open(MEMORY_FILE, "a") as f:
                f.write(f"\n\n### Session Summary — {datestr}\n")
                f.write(summary)
                f.write("\n")
            
            summaries_created += 1
            print(f"  ✓ Appended to MEMORY.md")
        else:
            print(f"  → No summary returned")
        
        # Mark done
        cache[f"summarized.{datestr}"] = "done"
    
    save_cache(cache)
    
    print("\n" + "="*60)
    print("SUMMARY:")
    print(f"  Files found: {len(candidates)}")
    print(f"  Files processed: {max_per_run}")
    print(f"  Summaries created: {summaries_created}")
    print(f"  Model: gpt-4o-mini (OpenAI)")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print(f"  Token budget: Check /status for session usage")
    print("="*60)

if __name__ == "__main__":
    main()
