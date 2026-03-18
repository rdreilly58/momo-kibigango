#!/bin/bash
# Git pre-commit hook for MBSE model validation
# Place in: .git/hooks/pre-commit
# Make executable: chmod +x .git/hooks/pre-commit

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 MBSE Model Validation..."

# Find model.yaml files in the commit
MODEL_FILES=$(git diff --cached --name-only | grep -E "model\.yaml|system-model\.yaml")

if [ -z "$MODEL_FILES" ]; then
    echo -e "${GREEN}✓${NC} No model files to validate"
    exit 0
fi

VALIDATION_FAILED=0

for MODEL_FILE in $MODEL_FILES; do
    if [ ! -f "$MODEL_FILE" ]; then
        continue
    fi
    
    echo "Validating: $MODEL_FILE"
    
    # Get the path to mbse-validate tool
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    MBSE_TOOL="$SCRIPT_DIR/../../skills/mbse/mbse-validate"
    
    # If not in expected location, search for it
    if [ ! -f "$MBSE_TOOL" ]; then
        MBSE_TOOL=$(find . -name "mbse-validate" -type f 2>/dev/null | head -1)
    fi
    
    if [ -z "$MBSE_TOOL" ] || [ ! -f "$MBSE_TOOL" ]; then
        echo -e "${YELLOW}⚠${NC} MBSE validation tool not found, skipping"
        continue
    fi
    
    # Run validation
    python3 "$MBSE_TOOL" "$MODEL_FILE"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗${NC} Validation failed for $MODEL_FILE"
        VALIDATION_FAILED=1
    else
        echo -e "${GREEN}✓${NC} $MODEL_FILE is valid"
    fi
done

if [ $VALIDATION_FAILED -eq 1 ]; then
    echo ""
    echo -e "${RED}❌ MBSE validation failed${NC}"
    echo "Fix errors before committing"
    exit 1
fi

echo -e "${GREEN}✓ All MBSE models validated${NC}"
exit 0
