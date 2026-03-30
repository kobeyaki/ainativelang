#!/bin/bash
# AINL Session Summarizer - Using OpenAI API
# Simple manual compression of unsummarized memory files

WORKSPACE="/data/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
CACHE_FILE="$WORKSPACE/.summarizer_cache.json"

API_KEY="${OPENAI_API_KEY:-}"
API_ENDPOINT="https://api.openai.com/v1/chat/completions"

# Initialize cache
[ ! -f "$CACHE_FILE" ] && echo "{}" > "$CACHE_FILE"

TODAY=$(date +%Y-%m-%d)
echo "[$(date -Is)] AINL Session Summarizer starting..."
echo "Using OpenAI gpt-4o-mini for compression"

# Find unsummarized files
CANDIDATES=()
for file in "$MEMORY_DIR"/*.md; do
  [ ! -f "$file" ] && continue
  fname=$(basename "$file")
  datestr="${fname:0:10}"
  
  [ "$datestr" = "$TODAY" ] && continue
  
  cache_key="summarized.$datestr"
  cache_val=$(jq -r ".\"$cache_key\" // empty" "$CACHE_FILE" 2>/dev/null)
  [ "$cache_val" = "done" ] && continue
  
  CANDIDATES+=("$fname")
done

echo "Found ${#CANDIDATES[@]} unsummarized files: ${CANDIDATES[@]}"

[ ${#CANDIDATES[@]} -eq 0 ] && {
  echo "No files to summarize."
  exit 0
}

MAX_PER_RUN=3
[ ${#CANDIDATES[@]} -lt 3 ] && MAX_PER_RUN=${#CANDIDATES[@]}

echo "Processing up to $MAX_PER_RUN files..."

SUMMARIES_CREATED=0

for ((i=0; i<MAX_PER_RUN; i++)); do
  candidate="${CANDIDATES[$i]}"
  datestr="${candidate:0:10}"
  
  echo ""
  echo "[$((i+1))/$MAX_PER_RUN] $candidate"
  
  content=$(cat "$MEMORY_DIR/$candidate" 2>/dev/null)
  content_len=${#content}
  
  [ $content_len -lt 100 ] && {
    echo "  → Too short ($content_len chars)"
    jq ".\"summarized.$datestr\" = \"done\"" "$CACHE_FILE" > "$CACHE_FILE.tmp" && mv "$CACHE_FILE.tmp" "$CACHE_FILE"
    continue
  }
  
  echo "  → Size: $content_len chars"
  
  # Truncate to 5000 chars
  if [ $content_len -gt 5000 ]; then
    content="${content: -5000}"
  fi
  
  # Escape content for JSON
  content_json=$(echo "$content" | jq -R -s .)
  
  # Call OpenAI
  response=$(curl -s -X POST "$API_ENDPOINT" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d @- <<EOF
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "system",
      "content": "You are a memory compression engine. Summarize ONLY into terse D:/P:/T:/L:/S: bullets. Max 15 bullets, 20 words each. D=decision, P=preference, T=todo, L=lesson, S=setting. Output ONLY bullets."
    },
    {
      "role": "user",
      "content": "Compress this session: $content_json"
    }
  ],
  "temperature": 0.3,
  "max_tokens": 800
}
EOF
)
  
  summary=$(echo "$response" | jq -r '.choices[0].message.content // empty' 2>/dev/null)
  
  if [ -z "$summary" ] || [ ${#summary} -lt 20 ]; then
    echo "  → No summary (LLM returned: $(echo "$response" | jq -c '.error // .choices[0].message.content[0:50]' 2>/dev/null))"
  else
    echo "  → Summary: ${#summary} chars"
    {
      echo ""
      echo ""
      echo "### Session Summary — $datestr"
      echo "$summary"
      echo ""
    } >> "$MEMORY_FILE"
    SUMMARIES_CREATED=$((SUMMARIES_CREATED + 1))
    echo "  ✓ Appended"
  fi
  
  # Mark done
  jq ".\"summarized.$datestr\" = \"done\"" "$CACHE_FILE" > "$CACHE_FILE.tmp" && mv "$CACHE_FILE.tmp" "$CACHE_FILE"
done

echo ""
echo "============================================================"
echo "SUMMARY:"
echo "  Files found: ${#CANDIDATES[@]}"
echo "  Files processed: $MAX_PER_RUN"
echo "  Summaries created: $SUMMARIES_CREATED"
echo "  Model: gpt-4o-mini (OpenAI)"
echo "  Timestamp: $(date -Is)"
echo "  Token budget: Check /status for current session usage"
echo "============================================================"
