#!/bin/bash
# fast-find.sh: Fast keyword search using macOS mdfind

query="$1"
limit="${2:-10}" # Default to 10 results
directory="${3:-}" # Optional directory to search within

if [ -z "$query" ]; then
  echo "Usage: fast-find.sh <query> [limit] [directory]"
  exit 1
fi

echo "Searching for: '$query' (limit: $limit)"
if [ -n "$directory" ]; then
  # For directory-specific searches, use 'find' (more reliable than mdfind which relies on Spotlight indexing)
  find "$directory" -type f \( -name "*$query*" -o -exec grep -l "$query" {} \; 2>/dev/null \) | head -n "$limit"
else
  # For global searches, use mdfind (faster)
  mdfind "$query" | head -n "$limit"
fi
