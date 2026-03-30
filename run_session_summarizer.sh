#!/bin/bash
# AINL Session Summarizer - Bash Edition
# Scans memory/*.md files for unsummarized days, calls OpenRouter LLM for compression

set -e

WORKSPACE="/data/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
CACHE_FILE="$WORKSPACE/.summarizer_cache.json"

# LLM Configuration
LLM_MODEL="${AINL_SUMMARIZER_MODEL:-arcee-ai/trinity-large-preview:free}"
API_KEY="${OPENROUTER_API_KEY:-}"
API_ENDPOINT="https://openrouter.ai/api/v1/chat/completions"

# Initialize cache if missing
if [ ! -f "$CACHE_FILE" ]; then
  echo "{}" > "$CACHE_FILE"
fi

# Get today's date
TODAY=$(date +%Y-%m-%d)
echo "[$(date -Is)] AINL Session Summarizer starting..."

# Find candidates
CANDIDATES=()
if [ -d "$MEMORY_DIR" ]; then
  for file in "$MEMORY_DIR"/*.md; do
    fname=$(basename "$file")
    datestr="${fname:0:10}"
    
    # Skip today
    if [ "$datestr" = "$TODAY" ]; then
      continue
    fi
    
    # Skip if already summarized
    cache_key="summarized.$datestr"
    cache_val=$(jq -r ".\"$cache_key\" // empty" "$CACHE_FILE" 2>/dev/null || echo "")
    if [ "$cache_val" = "done" ]; then
      continue
    fi
    
    CANDIDATES+=("$fname")
  done
fi

echo "Found ${#CANDIDATES[@]} unsummarized files"

if [ ${#CANDIDATES[@]} -eq 0 ]; then
  echo "No files to summarize."
  exit 0
fi

# Process up to 3 files
MAX_PER_RUN=3
if [ ${#CANDIDATES[@]} -lt 3 ]; then
  MAX_PER_RUN=${#CANDIDATES[@]}
fi

echo "Processing up to $MAX_PER_RUN files..."
echo "LLM Model: $LLM_MODEL"

SUMMARIES_CREATED=0

for ((i=0; i<MAX_PER_RUN; i++)); do
  candidate="${CANDIDATES[$i]}"
  datestr="${candidate:0:10}"
  
  echo ""
  echo "[$((i+1))/$MAX_PER_RUN] Processing $candidate..."
  
  # Read file content
  content=$(cat "$MEMORY_DIR/$candidate" 2>/dev/null || echo "")
  content_len=${#content}
  
  if [ $content_len -lt 100 ]; then
    echo "  → Content too short ($content_len chars), skipping"
    # Mark as done anyway
    jq ".\"summarized.$datestr\" = \"done\"" "$CACHE_FILE" > "$CACHE_FILE.tmp"
    mv "$CACHE_FILE.tmp" "$CACHE_FILE"
    continue
  fi
  
  echo "  → Content length: $content_len chars"
  
  # Truncate if needed
  if [ $content_len -gt 6000 ]; then
    content="${content: -6000}"
    echo "  → Truncated to 6000 chars"
  fi
  
  # Build LLM request
  system_msg="You are a memory compression engine. Summarize conversation logs into ONLY terse bullet points using these exact prefixes: D: decision made, P: preference expressed, T: todo/action item, L: lesson learned, S: setting/config change. Rules: Max 15 bullets. No timestamps. No greetings. No filler. Each bullet max 20 words. Output ONLY the bullets, one per line."
  
  user_msg="Summarize this day's activity:\\n\\n$content"
  
  # Create JSON payload
  payload=$(cat <<EOF
{
  "model": "$LLM_MODEL",
  "messages": [
    {"role": "system", "content": "$system_msg"},
    {"role": "user", "content": "Summarize this day's activity"}
  ],
  "temperature": 0.2,
  "max_tokens": 4096
}
EOF
)
  
  # Call LLM (simplified - using curl with JSON)
  if [ -z "$API_KEY" ]; then
    echo "  ERROR: OPENROUTER_API_KEY not set"
    continue
  fi
  
  echo "  → Calling LLM..."
  response=$(curl -s -X POST "$API_ENDPOINT" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -H "HTTP-Referer: https://openclaw.ai" \
    -H "X-Title: AINL Session Summarizer" \
    -d "$payload" \
    --max-time 120)
  
  # Extract summary from response
  summary=$(echo "$response" | jq -r '.choices[0].message.content // .choices[0].message.reasoning // empty' 2>/dev/null || echo "")
  
  if [ -z "$summary" ] || [ ${#summary} -lt 10 ]; then
    echo "  → No summary returned"
  else
    echo "  → Summary length: ${#summary} chars"
    echo "  → Appending to MEMORY.md..."
    
    # Append to MEMORY.md
    {
      echo ""
      echo ""
      echo "### Session Summary — $datestr"
      echo "$summary"
      echo ""
    } >> "$MEMORY_FILE"
    
    SUMMARIES_CREATED=$((SUMMARIES_CREATED + 1))
    echo "  ✓ Appended to MEMORY.md"
  fi
  
  # Mark as done in cache
  jq ".\"summarized.$datestr\" = \"done\"" "$CACHE_FILE" > "$CACHE_FILE.tmp"
  mv "$CACHE_FILE.tmp" "$CACHE_FILE"
done

echo ""
echo "============================================================"
echo "SUMMARY:"
echo "  Files found: ${#CANDIDATES[@]}"
echo "  Files processed: $MAX_PER_RUN"
echo "  Summaries created: $SUMMARIES_CREATED"
echo "  Model: $LLM_MODEL"
echo "  Timestamp: $(date -Is)"
echo "============================================================"
