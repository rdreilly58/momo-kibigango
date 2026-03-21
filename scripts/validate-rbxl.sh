#!/bin/bash

# validate-rbxl.sh
# Validates a Roblox place file (.rbxl)
# Usage: ./validate-rbxl.sh <rbxl_file>

set -euo pipefail

# Check if file argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <rbxl_file>"
    exit 1
fi

RBXL_FILE="$1"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== RBXL File Validator ===${NC}"
echo "File: $RBXL_FILE"
echo ""

# Check if file exists
if [ ! -f "$RBXL_FILE" ]; then
    echo -e "${RED}❌ ERROR: File does not exist${NC}"
    exit 1
fi

# Check file size
FILE_SIZE=$(wc -c < "$RBXL_FILE")
echo "File size: $FILE_SIZE bytes"

# Basic structure checks
echo -e "\n${YELLOW}Checking RBXL structure...${NC}"

# Check for roblox root element with version 4
if grep -q '<roblox.*version="4"' "$RBXL_FILE"; then
    echo -e "${GREEN}✅ Valid roblox root element with version 4${NC}"
else
    echo -e "${RED}❌ Missing or invalid roblox root element${NC}"
fi

# Check for required services
REQUIRED_SERVICES=("Workspace" "Lighting" "SoundService" "ReplicatedStorage" "StarterPlayer")
for service in "${REQUIRED_SERVICES[@]}"; do
    if grep -q "class=\"$service\"" "$RBXL_FILE"; then
        echo -e "${GREEN}✅ Found $service${NC}"
    else
        echo -e "${RED}❌ Missing $service${NC}"
    fi
done

# Check for SpawnLocation
if grep -q "class=\"SpawnLocation\"" "$RBXL_FILE"; then
    echo -e "${GREEN}✅ Found SpawnLocation${NC}"
else
    echo -e "${YELLOW}⚠️  No SpawnLocation found (optional but recommended)${NC}"
fi

# XML validation if xmllint is available
if command -v xmllint >/dev/null 2>&1; then
    echo -e "\n${YELLOW}Running XML validation...${NC}"
    if xmllint --noout "$RBXL_FILE" 2>/dev/null; then
        echo -e "${GREEN}✅ XML structure is valid${NC}"
    else
        echo -e "${RED}❌ XML validation failed${NC}"
        xmllint --noout "$RBXL_FILE" 2>&1 | head -5
    fi
else
    echo -e "\n${YELLOW}⚠️  xmllint not found, skipping XML validation${NC}"
fi

echo -e "\n${GREEN}=== Validation Complete ===${NC}"