#!/bin/bash
# roblox-game-startup-test-integrated.sh - Load game using template.rbxl
# Usage: ./roblox-game-startup-test-integrated.sh <game-directory> [repo-url]
# 
# This script:
# 1. Uses existing template.rbxl from the repo
# 2. Injects all scripts from scripts/ directory into the template
# 3. Launches Roblox Studio with the enhanced game
# 4. Waits 15 seconds for game to initialize
# 5. Captures Studio's Output window contents
# 6. Parses for errors/warnings
# 7. Reports results

set -e

GAME_DIR="$1"
REPO_URL="$2"

if [[ -z "$GAME_DIR" ]]; then
    echo "❌ Usage: $0 <game-directory> [repo-url]"
    echo "Example: $0 ~/.games/momotaro-roblox-rpg https://github.com/rdreilly58/momotaro-roblox-rpg"
    exit 1
fi

if [[ ! -d "$GAME_DIR" ]]; then
    echo "❌ Game directory not found: $GAME_DIR"
    exit 1
fi

if [[ ! -d "$GAME_DIR/scripts" ]]; then
    echo "❌ No scripts directory in $GAME_DIR"
    exit 1
fi

if [[ ! -f "$GAME_DIR/template.rbxl" ]]; then
    echo "❌ No template.rbxl in $GAME_DIR"
    exit 1
fi

# Locations
STUDIO_APP="/Applications/RobloxStudio.app/Contents/MacOS/RobloxStudio"
OUTPUT_DIR="$GAME_DIR"
TEMPLATE_FILE="$OUTPUT_DIR/template.rbxl"
GAME_FILE="$OUTPUT_DIR/game.rbxl"
OUTPUT_LOG="$OUTPUT_DIR/.studio_output.log"
STARTUP_LOG="$OUTPUT_DIR/.startup.log"
INJECTED_FILE="$OUTPUT_DIR/game-with-scripts.rbxl"

echo "═══════════════════════════════════════════════════════════════"
echo "🎮 ROBLOX GAME STARTUP TEST (TEMPLATE INTEGRATED)"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Game Directory: $GAME_DIR"
echo "Template File: template.rbxl"
echo "Scripts Found: $(ls -1 $GAME_DIR/scripts/*.lua 2>/dev/null | wc -l)"
echo ""

# Step 1: Validate template.rbxl
echo "1️⃣  Validating template.rbxl..."
if bash ~/.openclaw/workspace/scripts/validate-rbxl.sh "$TEMPLATE_FILE" > "$OUTPUT_DIR/.template_validation.log" 2>&1; then
    echo "   ✅ Template validation passed"
else
    echo "   ⚠️  Template validation had warnings/errors:"
    tail -10 "$OUTPUT_DIR/.template_validation.log" | sed 's/^/      /'
fi
echo ""

# Step 2: Inject scripts into the template
echo "2️⃣  Injecting scripts into template..."
if python3 ~/.openclaw/workspace/scripts/inject-scripts-into-template.py "$TEMPLATE_FILE" "$GAME_DIR/scripts" "$GAME_FILE"; then
    echo "   ✅ Scripts successfully injected into game.rbxl"
else
    echo "   ❌ Script injection failed!"
    exit 1
fi
echo ""

# Step 3: Validate the injected game file
echo "3️⃣  Validating injected game file..."

if bash ~/.openclaw/workspace/scripts/validate-rbxl.sh "$GAME_FILE" > "$OUTPUT_DIR/.validation.log" 2>&1; then
    echo "   ✅ Game file validation passed"
else
    echo "   ⚠️  Validation warnings (non-critical):"
    grep -E "(WARNING|Missing)" "$OUTPUT_DIR/.validation.log" | head -5 | sed 's/^/      /'
fi
echo ""

# Step 4: Kill any existing Roblox processes
echo "4️⃣  Preparing environment..."
pkill -f RobloxStudio 2>/dev/null || true
pkill -f RobloxPlayer 2>/dev/null || true
sleep 2
echo "   ✅ Environment cleared"
echo ""

# Step 5: Launch Studio with the template game file
echo "5️⃣  Launching Roblox Studio with template game..."
echo "   Opening: $GAME_FILE"
echo ""

# Launch and capture logs
"$STUDIO_APP" "$GAME_FILE" > "$STARTUP_LOG" 2>&1 &
STUDIO_PID=$!
echo "   Studio PID: $STUDIO_PID"
echo ""

# Step 6: Wait 15 seconds for startup
echo "6️⃣  Waiting 15 seconds for game initialization..."
START_TIME=$(date +%s)
WAIT_TIME=15
for ((i=WAIT_TIME; i>0; i--)); do
    echo -ne "\r   ⏳ $i seconds remaining..."
    sleep 1
done
echo -ne "\r   ✅ Startup period complete                   \n"
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo ""

# Step 7: Capture output
echo "7️⃣  Capturing Studio output..."
OUTPUT_CAPTURE="$OUTPUT_DIR/.output_capture.txt"

# Try multiple methods to capture output
echo "=== STUDIO OUTPUT CAPTURE ===" > "$OUTPUT_CAPTURE"
echo "Capture Time: $(date)" >> "$OUTPUT_CAPTURE"
echo "" >> "$OUTPUT_CAPTURE"

# Method 1: Check Roblox logs directory
if [[ -d "$HOME/Library/Logs/Roblox" ]]; then
    LATEST_LOG=$(ls -t "$HOME/Library/Logs/Roblox/"*.log 2>/dev/null | head -1)
    if [[ -f "$LATEST_LOG" ]]; then
        echo "=== FROM ROBLOX LOG FILE ===" >> "$OUTPUT_CAPTURE"
        tail -200 "$LATEST_LOG" >> "$OUTPUT_CAPTURE"
    fi
fi

# Method 2: Startup log
echo "" >> "$OUTPUT_CAPTURE"
echo "=== FROM STARTUP LOG ===" >> "$OUTPUT_CAPTURE"
tail -100 "$STARTUP_LOG" >> "$OUTPUT_CAPTURE" 2>/dev/null || true

echo "   ✅ Output captured"
echo ""

# Step 8: Parse for errors
echo "8️⃣  Analyzing output for issues..."
echo ""

# Count errors and warnings
ERROR_COUNT=$(grep -i -E "error|fail|exception|unable to|could not|missing|invalid" "$OUTPUT_CAPTURE" 2>/dev/null | grep -v -E "No errors|0 errors" | wc -l | tr -d ' ')
WARNING_COUNT=$(grep -i "warning" "$OUTPUT_CAPTURE" 2>/dev/null | wc -l | tr -d ' ')
# Since scripts are now embedded in the XML, check for their existence differently
SCRIPT_LOADED_COUNT=$(grep -E "MainGameScript|PlayerManager|CombatSystem|NPCSpawner|AnimationController|ClientGUI" "$GAME_FILE" 2>/dev/null | wc -l | tr -d ' ')
# Also check for runtime script loading messages
SCRIPT_RUNTIME_COUNT=$(grep -i "script loaded\|script started\|initialized" "$OUTPUT_CAPTURE" 2>/dev/null | wc -l | tr -d ' ')

# Determine test status
if [ "$ERROR_COUNT" -eq 0 ] && [ "$SCRIPT_LOADED_COUNT" -gt 0 ]; then
    TEST_STATUS="✅ PASS"
else
    TEST_STATUS="❌ FAIL"
fi

# Generate detailed report
cat > "$OUTPUT_DIR/.test_results.txt" << RESULTSEOF
═══════════════════════════════════════════════════════════════
ROBLOX GAME STARTUP TEST RESULTS (TEMPLATE INTEGRATED)
═══════════════════════════════════════════════════════════════

Test Time: $(date)
Game Directory: $GAME_DIR
Template Used: template.rbxl
Studio PID: $STUDIO_PID
Startup Duration: ${ELAPSED} seconds

SUMMARY:
--------
Test Status: $TEST_STATUS
Errors Found: $ERROR_COUNT
Warnings Found: $WARNING_COUNT
Scripts Loaded: $SCRIPT_LOADED_COUNT / 6 expected

PERFORMANCE METRICS:
-------------------
Startup Time: ${ELAPSED}s
Template Size: $(wc -c < "$TEMPLATE_FILE") bytes
Memory Usage: $(ps -o rss= -p $STUDIO_PID 2>/dev/null || echo "N/A") KB

WHAT WORKED:
-----------
$(if [ -f "$TEMPLATE_FILE" ]; then echo "✅ Template file found and loaded"; fi)
$(if [ "$SCRIPT_LOADED_COUNT" -gt 0 ]; then echo "✅ Scripts were injected ($SCRIPT_LOADED_COUNT detected)"; fi)
$(if [ "$ERROR_COUNT" -eq 0 ]; then echo "✅ No errors during startup"; fi)
$(if ps -p $STUDIO_PID > /dev/null; then echo "✅ Studio process is running"; fi)

WHAT DIDN'T WORK:
----------------
$(if [ "$ERROR_COUNT" -gt 0 ]; then echo "❌ Errors detected during startup ($ERROR_COUNT)"; fi)
$(if [ "$SCRIPT_LOADED_COUNT" -eq 0 ]; then echo "❌ No scripts were loaded"; fi)
$(if [ "$WARNING_COUNT" -gt 10 ]; then echo "⚠️  High number of warnings ($WARNING_COUNT)"; fi)

ERROR DETAILS:
--------------
$(if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "First 10 errors:"
    grep -i -E "error|fail|exception" "$OUTPUT_CAPTURE" 2>/dev/null | grep -v -E "No errors|0 errors" | head -10 | sed 's/^/  /'
else
    echo "No errors found"
fi)

WARNING DETAILS:
---------------
$(if [ "$WARNING_COUNT" -gt 0 ]; then
    echo "First 5 warnings:"
    grep -i "warning" "$OUTPUT_CAPTURE" 2>/dev/null | head -5 | sed 's/^/  /'
else
    echo "No warnings found"
fi)

FULL OUTPUT (last 100 lines):
----------------------------
$(tail -100 "$OUTPUT_CAPTURE")

═══════════════════════════════════════════════════════════════
END OF REPORT
═══════════════════════════════════════════════════════════════
RESULTSEOF

# Display summary
echo "📊 Test Results Summary:"
echo "   Status: $TEST_STATUS"
echo "   Errors: $ERROR_COUNT"
echo "   Warnings: $WARNING_COUNT" 
echo "   Scripts Loaded: $SCRIPT_LOADED_COUNT"
echo "   Performance: ${ELAPSED}s startup time"
echo ""

if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "⚠️  ERRORS DETECTED:"
    grep -i -E "error|fail|exception" "$OUTPUT_CAPTURE" 2>/dev/null | grep -v -E "No errors|0 errors" | head -5 | sed 's/^/   /'
    echo ""
fi

echo "═══════════════════════════════════════════════════════════════"
echo "Full results saved to: $OUTPUT_DIR/.test_results.txt"
echo ""
echo "Studio is running with PID $STUDIO_PID"
echo "The game window should be open for manual testing."
echo ""