#!/bin/bash
# fast-find-v2.sh: Intelligent file search with better relevance ranking
# Improvements:
# - Smarter query parsing (multi-word gets AND-like behavior)
# - Relevance ranking (exact matches first, then partial)
# - Excludes system/binary directories (no noise)
# - Optimized for accuracy

set -euo pipefail

query="$1"
limit="${2:-10}"
directory="${3:-}"

if [ -z "$query" ]; then
  echo "Usage: fast-find-v2.sh <query> [limit] [directory]"
  exit 1
fi

# Directories to exclude (noise & clutter)
EXCLUDE_DIRS=(
  "node_modules"
  ".git"
  "venv"
  "__pycache__"
  ".venv"
  "build"
  "dist"
  ".cargo"
  "target"
  "DerivedData"
  "xcuserdata"
  "nmap-static-binaries"
  "bob-xfer"
  ".Trash"
  "Library/Caches"
  "Library/Logs"
  "Library/Containers"
  "Application Support"
)

# Default to home directory if not specified
if [ -z "$directory" ]; then
  directory="$HOME"
fi

# Build exclusion pattern for find
build_exclude_args() {
  local result=""
  for dir in "${EXCLUDE_DIRS[@]}"; do
    result="$result -path */$dir -prune -o"
  done
  echo "$result"
}

exclude_args=$(build_exclude_args)

# Smart query parsing
word_count=$(echo "$query" | wc -w)

# Search function: rank results by relevance
search_and_rank() {
  local q="$1"
  local d="$2"
  
  # Find files matching query in filename
  # eval needed because $exclude_args has multiple arguments
  eval "find \"$d\" -type f $exclude_args -type f \( -iname \"*$q*\" \) 2>/dev/null" | while read -r filepath; do
    filename=$(basename "$filepath")
    
    # Ranking logic:
    # 200: Exact match or starts with query
    # 100: Contains query
    # 50: Any match (fallback)
    
    if [[ "$filename" =~ ^${q}$ ]]; then
      # Exact match
      echo "300|$filepath"
    elif [[ "$filename" =~ ^${q} ]]; then
      # Starts with query
      echo "250|$filepath"
    else
      # Contains query somewhere
      echo "100|$filepath"
    fi
  done | sort -rn -t'|' -k1 | cut -d'|' -f2
}

# Multi-word search: find files matching ALL terms
search_multiword() {
  local words=($1)
  local d="$2"
  
  # For multi-word queries, find files where filename contains as many terms as possible
  eval "find \"$d\" -type f $exclude_args -type f -print0 2>/dev/null" | while IFS= read -r -d '' filepath; do
    filename=$(basename "$filepath" | tr '[:upper:]' '[:lower:]')
    
    # Count how many search terms are in the filename
    match_count=0
    for word in "${words[@]}"; do
      if [[ "$filename" =~ ${word,,} ]]; then
        ((match_count++))
      fi
    done
    
    # Only return if at least 2 terms match (helps filter out noise)
    if [ "$match_count" -ge 2 ]; then
      # Higher score for more matches
      score=$((100 * match_count))
      echo "$score|$filepath"
    fi
  done | sort -rn -t'|' -k1 | cut -d'|' -f2
}

# Execute search
if [ "$word_count" -gt 2 ]; then
  # Multi-word (3+): Strict AND matching
  search_multiword "$query" "$directory" | head -n "$limit"
elif [ "$word_count" -eq 2 ]; then
  # Two words: Balance AND with relevance
  # First try strict match, then fall back to any term match
  results=$(search_multiword "$query" "$directory" | head -n "$limit")
  if [ -z "$results" ]; then
    # No strict matches, broaden search
    search_and_rank "$(echo "$query" | cut -d' ' -f1)" "$directory" | head -n "$limit"
  else
    echo "$results"
  fi
else
  # Single word: ranked search
  search_and_rank "$query" "$directory" | head -n "$limit"
fi
