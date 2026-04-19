#!/bin/bash
# Tier C Phase 2: Task Splitter
# Splits complex tasks into batches
# Usage: bash split-complex-task.sh "Task description" [file1 file2 ...]

set -e

TASK_DESCRIPTION="${1:-}"
shift
FILES=("$@")

if [ -z "$TASK_DESCRIPTION" ]; then
  echo "Usage: bash split-complex-task.sh \"Task\" [file1 file2 ...]"
  exit 1
fi

echo "✂️  TIER C TASK SPLITTER (Phase 2)"
echo "===================================="
echo "Task: $TASK_DESCRIPTION"
echo ""

if [ ${#FILES[@]} -eq 0 ]; then
  FILES=("example1.swift" "example2.swift" "tests/")
fi

TOTAL_FILES=${#FILES[@]}
echo "Files: $TOTAL_FILES"
echo ""

# Step 1: Classify files
echo "Step 1: Classifying files..."
echo ""

HAIKU_FILES=""
OPUS_FILES=""
GPT4_FILES=""
HAIKU_COUNT=0
OPUS_COUNT=0
GPT4_COUNT=0

for file in "${FILES[@]}"; do
  TIER="opus"
  
  if [[ "$file" =~ test|spec|Test ]]; then
    TIER="haiku"
  elif [[ "$file" =~ \.md|README ]]; then
    TIER="haiku"
  elif [[ "$TASK_DESCRIPTION" =~ fix|typo|format|lint ]]; then
    TIER="haiku"
  elif [[ "$TASK_DESCRIPTION" =~ redesign|architecture|rewrite ]]; then
    TIER="gpt4"
  fi
  
  case "$TIER" in
    haiku)
      HAIKU_FILES="$HAIKU_FILES $file"
      ((HAIKU_COUNT++))
      echo "  $file → HAIKU"
      ;;
    opus)
      OPUS_FILES="$OPUS_FILES $file"
      ((OPUS_COUNT++))
      echo "  $file → OPUS"
      ;;
    gpt4)
      GPT4_FILES="$GPT4_FILES $file"
      ((GPT4_COUNT++))
      echo "  $file → GPT-4"
      ;;
  esac
done

echo ""
echo "Step 2: Generating batches..."
echo ""

BATCH_NUM=1

# GPT-4 batch
if [ "$GPT4_COUNT" -gt 0 ]; then
  GPT4_COST=$(awk -v c="$GPT4_COUNT" 'BEGIN {printf "%.4f", c * 0.030}')
  echo "Batch $BATCH_NUM (GPT-4):"
  echo "  Files: $GPT4_FILES"
  echo "  Cost: $GPT4_COST (\$$GPT4_COST)"
  echo ""
  ((BATCH_NUM++))
fi

# Opus batch
if [ "$OPUS_COUNT" -gt 0 ]; then
  OPUS_COST=$(awk -v c="$OPUS_COUNT" 'BEGIN {printf "%.4f", c * 0.015}')
  echo "Batch $BATCH_NUM (Opus):"
  echo "  Files: $OPUS_FILES"
  echo "  Cost: $OPUS_COST (\$$OPUS_COST)"
  echo ""
  ((BATCH_NUM++))
fi

# Haiku batch
if [ "$HAIKU_COUNT" -gt 0 ]; then
  HAIKU_COST=$(awk -v c="$HAIKU_COUNT" 'BEGIN {printf "%.4f", c * 0.0001}')
  echo "Batch $BATCH_NUM (Haiku):"
  echo "  Files: $HAIKU_FILES"
  echo "  Cost: $HAIKU_COST (\$$HAIKU_COST)"
  echo ""
fi

# Cost analysis
echo "Step 3: Cost analysis"
echo ""

HAIKU_COST=$(awk -v c="$HAIKU_COUNT" 'BEGIN {printf "%.4f", c * 0.0001}')
OPUS_COST=$(awk -v c="$OPUS_COUNT" 'BEGIN {printf "%.4f", c * 0.015}')
GPT4_COST=$(awk -v c="$GPT4_COUNT" 'BEGIN {printf "%.4f", c * 0.030}')
TOTAL_COST=$(awk -v h="$HAIKU_COST" -v o="$OPUS_COST" -v g="$GPT4_COST" 'BEGIN {printf "%.4f", h + o + g}')

if [ "$GPT4_COUNT" -gt 0 ]; then
  WITHOUT=$(awk -v t="$TOTAL_FILES" 'BEGIN {printf "%.4f", t * 0.030}')
elif [ "$OPUS_COUNT" -gt 0 ]; then
  WITHOUT=$(awk -v t="$TOTAL_FILES" 'BEGIN {printf "%.4f", t * 0.015}')
else
  WITHOUT=$(awk -v t="$TOTAL_FILES" 'BEGIN {printf "%.4f", t * 0.0001}')
fi

SAVINGS=$(awk -v w="$WITHOUT" -v t="$TOTAL_COST" 'BEGIN {
  if (w == 0) print "0"
  else printf "%.0f", ((w - t) / w) * 100
}')

cat << SUMMARY

═══════════════════════════════════════════════════════════

COST SUMMARY (Tier C Batching)

With batching:
  • GPT-4 batch: \$$GPT4_COST
  • Opus batch: \$$OPUS_COST
  • Haiku batch: \$$HAIKU_COST
  ────────────────────────
  • Total: \$$TOTAL_COST

Without batching:
  • Cost: \$$WITHOUT

Savings: ${SAVINGS}% ✅

═══════════════════════════════════════════════════════════
SUMMARY

echo ""
echo "✅ Task split complete. Ready for execution (Phase 3)."
