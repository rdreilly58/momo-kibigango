#!/bin/bash
# Classify Coding Tasks for Model Selection
# Determines if task should use Haiku (cheap/fast) or Opus (capable)
# Usage: bash classify-coding-task.sh "Task description"

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Input
TASK_DESCRIPTION="${1:-}"

if [ -z "$TASK_DESCRIPTION" ]; then
  echo "Usage: bash classify-coding-task.sh \"Task description\""
  echo "Example: bash classify-coding-task.sh \"Fix missing semicolon in App.swift\""
  exit 1
fi

# Convert to lowercase for matching
TASK_LOWER=$(echo "$TASK_DESCRIPTION" | tr '[:upper:]' '[:lower:]')

# Initialize scores
HAIKU_SCORE=0
OPUS_SCORE=0
GPT4_SCORE=0

echo -e "${BLUE}🤖 CODING TASK CLASSIFIER${NC}"
echo "Task: $TASK_DESCRIPTION"
echo "================================"
echo ""

# ===================================
# TRIVIAL FIX PATTERNS (Haiku)
# ===================================

# Typo/spelling fixes
if echo "$TASK_LOWER" | grep -qE "typo|misspell|spelling|grammar"; then
  echo -e "${GREEN}✓ Typo pattern detected${NC} → Haiku"
  HAIKU_SCORE=$((HAIKU_SCORE + 3))
fi

# Format/lint fixes
if echo "$TASK_LOWER" | grep -qE "format|indent|whitespace|lint|style"; then
  echo -e "${GREEN}✓ Formatting pattern detected${NC} → Haiku"
  HAIKU_SCORE=$((HAIKU_SCORE + 3))
fi

# Add single import/line
if echo "$TASK_LOWER" | grep -qE "add.*import|add.*line|add.*semicolon|missing.*semicolon"; then
  echo -e "${GREEN}✓ Single-line addition detected${NC} → Haiku"
  HAIKU_SCORE=$((HAIKU_SCORE + 3))
fi

# Remove unused code
if echo "$TASK_LOWER" | grep -qE "remove.*unused|delete.*dead|remove.*comment"; then
  echo -e "${GREEN}✓ Code removal pattern detected${NC} → Haiku"
  HAIKU_SCORE=$((HAIKU_SCORE + 2))
fi

# Fix single error
if echo "$TASK_LOWER" | grep -qE "fix.*error|fix.*warning|fix.*bug" && \
   ! echo "$TASK_LOWER" | grep -qE "bugs|errors|issues"; then
  echo -e "${GREEN}✓ Single error fix detected${NC} → Haiku"
  HAIKU_SCORE=$((HAIKU_SCORE + 2))
fi

# ===================================
# MEDIUM COMPLEXITY PATTERNS (Opus)
# ===================================

# Add feature/function/layer/component
if echo "$TASK_LOWER" | grep -qE "add.*feature|implement.*feature|add.*function|implement.*function|add.*layer|add.*component|add.*system|caching|cache"; then
  echo -e "${YELLOW}✓ Feature addition detected${NC} → Opus"
  OPUS_SCORE=$((OPUS_SCORE + 3))
fi

# Refactor/improve (but not large refactors)
if echo "$TASK_LOWER" | grep -qE "refactor|improve|optimize|clean.*up" && \
   ! echo "$TASK_LOWER" | grep -qE "major.*refactor|large.*refactor"; then
  echo -e "${YELLOW}✓ Refactoring pattern detected${NC} → Opus"
  OPUS_SCORE=$((OPUS_SCORE + 3))
fi

# Build/create new (but not if distributed/complex)
if echo "$TASK_LOWER" | grep -qE "build|create|write|implement" && \
   ! echo "$TASK_LOWER" | grep -qE "add.*line|add.*import|fix|distributed|consistency"; then
  echo -e "${YELLOW}✓ Build pattern detected${NC} → Opus"
  OPUS_SCORE=$((OPUS_SCORE + 2))
fi

# Multiple files mentioned
if echo "$TASK_LOWER" | grep -qE "files|modules|components"; then
  echo -e "${YELLOW}✓ Multiple files pattern detected${NC} → Opus"
  OPUS_SCORE=$((OPUS_SCORE + 2))
fi

# ===================================
# COMPLEX PATTERNS (GPT-4)
# ===================================

# Architecture/design
if echo "$TASK_LOWER" | grep -qE "architecture|design.*pattern|design.*system|distributed|consistency|distributed.*system"; then
  echo -e "${RED}✓ Architecture pattern detected${NC} → GPT-4"
  GPT4_SCORE=$((GPT4_SCORE + 4))
fi

# Large refactor
if echo "$TASK_LOWER" | grep -qE "large.*refactor|major.*rewrite|major.*refactor|complete.*redesign|rewrite.*CQRS"; then
  echo -e "${RED}✓ Large refactor pattern detected${NC} → GPT-4"
  GPT4_SCORE=$((GPT4_SCORE + 5))
fi

# Multiple features
if echo "$TASK_LOWER" | grep -qE "build.*multiple|add.*several|implement.*multiple"; then
  echo -e "${RED}✓ Multiple features pattern detected${NC} → GPT-4"
  GPT4_SCORE=$((GPT4_SCORE + 3))
fi

# ===================================
# SCORE CALCULATION
# ===================================

echo ""
echo "Score Calculation:"
echo "  Haiku score:  $HAIKU_SCORE"
echo "  Opus score:   $OPUS_SCORE"
echo "  GPT-4 score:  $GPT4_SCORE"
echo ""

# Determine winner
MAX_SCORE=$HAIKU_SCORE
RECOMMENDED_MODEL="haiku"

if [ $OPUS_SCORE -gt $MAX_SCORE ]; then
  MAX_SCORE=$OPUS_SCORE
  RECOMMENDED_MODEL="opus"
fi

if [ $GPT4_SCORE -gt $MAX_SCORE ]; then
  MAX_SCORE=$GPT4_SCORE
  RECOMMENDED_MODEL="gpt-4"
fi

# ===================================
# SPECIAL CASE ADJUSTMENTS
# ===================================

# If task is very short and simple, prefer Haiku
TASK_LENGTH=${#TASK_DESCRIPTION}
if [ $TASK_LENGTH -lt 30 ] && [ "$RECOMMENDED_MODEL" = "opus" ]; then
  echo -e "${BLUE}ℹ️  Task is very short (${TASK_LENGTH} chars)${NC} → Downgrade to Haiku"
  RECOMMENDED_MODEL="haiku"
fi

# If task mentions multiple areas, prefer Opus minimum
if echo "$TASK_LOWER" | grep -qE "and.*and|multiple|several|various"; then
  if [ "$RECOMMENDED_MODEL" = "haiku" ]; then
    echo -e "${BLUE}ℹ️  Multiple areas mentioned${NC} → Upgrade to Opus minimum"
    RECOMMENDED_MODEL="opus"
  fi
fi

# ===================================
# OUTPUT
# ===================================

echo ""
echo "═════════════════════════════════════════"
echo -e "${BLUE}CLASSIFICATION RESULT${NC}"
echo "═════════════════════════════════════════"
echo ""

case "$RECOMMENDED_MODEL" in
  haiku)
    echo -e "${GREEN}✅ HAIKU${NC} (Fast & Cheap)"
    echo ""
    echo "   Cost:     \$0.0001 per 1K tokens"
    echo "   Speed:    0.1-0.3 seconds"
    echo "   Best for: Trivial fixes, single-line changes"
    echo ""
    echo "   Savings vs Opus: 150x cheaper!"
    MODEL_ALIAS="anthropic/claude-haiku-4-5"
    ;;
  opus)
    echo -e "${YELLOW}⭐ OPUS${NC} (Balanced)"
    echo ""
    echo "   Cost:     \$0.015 per 1K tokens"
    echo "   Speed:    0.5-2 seconds"
    echo "   Best for: Features, refactoring, medium builds"
    echo ""
    echo "   Use for most coding tasks"
    MODEL_ALIAS="anthropic/claude-opus-4-0"
    ;;
  gpt-4)
    echo -e "${RED}🚀 GPT-4${NC} (Premium)"
    echo ""
    echo "   Cost:     \$0.03 per 1K tokens"
    echo "   Speed:    1-3 seconds"
    echo "   Best for: Complex architecture, large refactors"
    echo ""
    echo "   Use for most challenging tasks"
    MODEL_ALIAS="openai/gpt-4-turbo"
    ;;
esac

echo ""
echo "═════════════════════════════════════════"
echo ""
echo "JSON Output (for scripting):"
echo "{"
echo "  \"model\": \"$RECOMMENDED_MODEL\","
echo "  \"model_alias\": \"$MODEL_ALIAS\","
echo "  \"haiku_score\": $HAIKU_SCORE,"
echo "  \"opus_score\": $OPUS_SCORE,"
echo "  \"gpt4_score\": $GPT4_SCORE,"
echo "  \"confidence\": \"high\""
echo "}"
echo ""

# Exit with model in variable (for sourcing)
# Normalize model name (gpt-4 → gpt4 for consistency)
NORMALIZED_MODEL=$(echo "$RECOMMENDED_MODEL" | sed 's/-//g')
echo "CLASSIFIED_MODEL=$NORMALIZED_MODEL"
echo "CLASSIFIED_MODEL_ALIAS=$MODEL_ALIAS"
