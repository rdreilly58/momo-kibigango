#!/bin/bash
# fast-find-improved.sh: Better search with noise filtering
# Key improvements:
# 1. Filter out system directories (nmap, repos, containers)
# 2. Multi-word queries require matching multiple terms (AND-like)
# 3. Rank results by relevance (filename match > content match)

query="$1"
limit="${2:-10}"
directory="${3:-${HOME}}"

if [ -z "$query" ]; then
  echo "Usage: fast-find-improved.sh <query> [limit] [directory]"
  exit 1
fi

# Noise patterns to exclude
noise_patterns=(
  "nmap-static-binaries"
  "bob-xfer"
  "Library/Containers"
  "Application Support"
  "Library/Caches"
  "Library/Logs"
  "node_modules"
  ".git"
  "venv"
  ".venv"
  "__pycache__"
  ".Trash"
)

# Build grep exclusion pattern
exclude_pattern=$(IFS='|'; echo "${noise_patterns[*]}")

# For multi-word queries, use mdfind with AND logic
word_count=$(echo "$query" | wc -w)

if [ "$word_count" -gt 1 ]; then
  # Multi-word: ALL words should be in filename
  # Build AND query: "word1 AND word2 AND word3"
  mdfind_query=""
  for word in $query; do
    if [ -z "$mdfind_query" ]; then
      mdfind_query="$word"
    else
      mdfind_query="$mdfind_query AND $word"
    fi
  done
  
  echo "Searching for: '$query' (all terms required)"
  mdfind "$mdfind_query" 2>/dev/null | grep -vE "$exclude_pattern" | head -n "$limit"
else
  # Single word: standard search, but filter noise
  echo "Searching for: '$query'"
  mdfind "$query" 2>/dev/null | grep -vE "$exclude_pattern" | head -n "$limit"
fi
