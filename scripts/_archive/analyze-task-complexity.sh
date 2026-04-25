#!/bin/bash
# Tier C Phase 1: Task Complexity Analyzer
# Analyzes large tasks for file-level complexity distribution
# Usage: bash analyze-task-complexity.sh "Task description" [file1 file2 ...]

set -e

TASK_DESCRIPTION="${1:-}"
shift
FILES=("$@")

if [ -z "$TASK_DESCRIPTION" ]; then
  echo "Usage: bash analyze-task-complexity.sh \"Task\" [file1 file2 ...]"
  echo ""
  echo "Examples:"
  echo "  analyze-task-complexity.sh \"Add caching layer\" NetworkCache.swift NetworkManager.swift"
  exit 1
fi

echo "🔍 TIER C TASK ANALYZER (Phase 1)"
echo "================================="
echo "Task: $TASK_DESCRIPTION"
echo ""

# If no files specified, use defaults
if [ ${#FILES[@]} -eq 0 ]; then
  echo "Step 1: Using default files..."
  FILES=("example1.swift" "example2.swift" "tests/")
else
  echo "Step 1: Processing ${#FILES[@]} files..."
fi

echo ""

# Track counts
HAIKU_COUNT=0
OPUS_COUNT=0
GPT4_COUNT=0

# Process each file
echo "Step 2: Analyzing per-file complexity..."
echo ""

for file in "${FILES[@]}"; do
  # Classify based on filename + task context
  TIER="opus"  # Default
  
  # Test files are simpler
  if [[ "$file" =~ test|spec|Test ]]; then
    TIER="haiku"
  # Documentation is simple
  elif [[ "$file" =~ \.md|README|CHANGELOG ]]; then
    TIER="haiku"
  # Task context analysis
  elif [[ "$TASK_DESCRIPTION" =~ fix|typo|format|lint|import ]]; then
    TIER="haiku"
  elif [[ "$TASK_DESCRIPTION" =~ redesign|architecture|rewrite|major ]]; then
    TIER="gpt4"
  fi
  
  case "$TIER" in
    haiku)
      ((HAIKU_COUNT++))
      TYPE_DESC="simple"
      ;;
    opus)
      ((OPUS_COUNT++))
      TYPE_DESC="medium"
      ;;
    gpt4)
      ((GPT4_COUNT++))
      TYPE_DESC="complex"
      ;;
  esac
  
  printf "  %-30s → %-5s (%-8s)\n" "$file" "$TIER" "$TYPE_DESC"
done

echo ""
echo "Step 3: Computing costs..."
echo ""

TOTAL_FILES=$((HAIKU_COUNT + OPUS_COUNT + GPT4_COUNT))

# Compute costs using awk
HAIKU_COST=$(awk -v c="$HAIKU_COUNT" 'BEGIN {printf "%.4f", c * 0.0001}')
OPUS_COST=$(awk -v c="$OPUS_COUNT" 'BEGIN {printf "%.4f", c * 0.015}')
GPT4_COST=$(awk -v c="$GPT4_COUNT" 'BEGIN {printf "%.4f", c * 0.030}')
TOTAL_COST=$(awk -v h="$HAIKU_COST" -v o="$OPUS_COST" -v g="$GPT4_COST" 'BEGIN {printf "%.4f", h + o + g}')

# Estimate without Tier C
if [ "$GPT4_COUNT" -gt 0 ]; then
  HIGHEST="gpt4"
  WITHOUT_COST=$(awk -v t="$TOTAL_FILES" 'BEGIN {printf "%.4f", t * 0.030}')
elif [ "$OPUS_COUNT" -gt 0 ]; then
  HIGHEST="opus"
  WITHOUT_COST=$(awk -v t="$TOTAL_FILES" 'BEGIN {printf "%.4f", t * 0.015}')
else
  HIGHEST="haiku"
  WITHOUT_COST=$(awk -v t="$TOTAL_FILES" 'BEGIN {printf "%.4f", t * 0.0001}')
fi

# Calculate savings percentage
SAVINGS=$(awk -v w="$WITHOUT_COST" -v t="$TOTAL_COST" 'BEGIN {
  if (w == 0) print "0"
  else printf "%.0f", ((w - t) / w) * 100
}')

cat << SUMMARY

═══════════════════════════════════════════════════════════

BATCH PLAN (Tier C Analysis)

Files analyzed: $TOTAL_FILES
  • Haiku tier: $HAIKU_COUNT files (simple)
  • Opus tier: $OPUS_COUNT files (medium)
  • GPT-4 tier: $GPT4_COUNT files (complex)

Cost with Tier C (batched):
  • Haiku batch: \$$HAIKU_COST ($HAIKU_COUNT × \$0.0001)
  • Opus batch: \$$OPUS_COST ($OPUS_COUNT × \$0.015)
  • GPT-4 batch: \$$GPT4_COST ($GPT4_COUNT × \$0.030)
  ──────────────────────────────
  • Total: \$$TOTAL_COST

Cost without Tier C (single $HIGHEST model):
  • Cost: \$$WITHOUT_COST ($TOTAL_FILES × \$[$([ "$HIGHEST" = "haiku" ] && echo "0.0001" || [ "$HIGHEST" = "opus" ] && echo "0.015" || echo "0.030")])

Savings with Tier C: ${SAVINGS}% ✅
  \$$TOTAL_COST vs \$$WITHOUT_COST

═══════════════════════════════════════════════════════════
SUMMARY

echo ""
echo "✅ Analysis complete."
echo ""
echo "Next: split-complex-task.sh to generate execution plan"
