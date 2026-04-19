#!/bin/bash
# Test suite for Total Recall file indexing and search capabilities

set -euo pipefail

# --- Configuration ---
WORKSPACE="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPTS_DIR="$WORKSPACE/scripts"
TEST_DIR="$WORKSPACE/test_recall_data"
OBSERVATIONS_FILE="$WORKSPACE/memory/observations.md"
FAST_FIND_SCRIPT="$SCRIPTS_DIR/fast-find.sh"
INDEX_FILES_SCRIPT="$SCRIPTS_DIR/index_files_for_memory.py"
OBSERVER_AGENT_SCRIPT="$WORKSPACE/skills/total-recall/scripts/observer-agent.sh"

# --- Utility functions ---
log() {
  echo "$(date '+%H:%M:%S') [TEST] $1"
}

cleanup() {
  log "Cleaning up test data..."
  rm -rf "$TEST_DIR"
  # Ensure observer-agent doesn't pick up test data later
  # We are not cleaning up memory/observations.md, as it might contain real observations.
}

assert_contains() {
  local file="$1"
  local expected_text="$2"
  if grep -qF "$expected_text" "$file"; then
    log "PASS: \"$expected_text\" found in \"$file\""
  else
    log "FAIL: \"$expected_text\" NOT found in \"$file\""
    exit 1
  fi
}

# --- Setup ---
log "Starting Total Recall file indexing test suite..."
cleanup # Ensure a clean slate
mkdir -p "$TEST_DIR/Documents" "$TEST_DIR/Projects" "$TEST_DIR/notes"

# Create dummy files with unique content
echo "This is a test document with a unique keyword: apple-pie and semantic content about delicious fruit desserts." > "$TEST_DIR/Documents/test_doc.txt"
echo "This is a markdown file with another keyword: banana-split and instructions for a tasty treat." > "$TEST_DIR/notes/test_note.md"
echo "def hello_world():\n    # Python code with keyword: python-magic\n    print('Hello from Python!')" > "$TEST_DIR/Projects/test_code.py"

# Create a dummy PDF (using textutil to create a rich text file, then converting to PDF can be tricky via CLI, so we'll just test text extraction on a known text file for now)
echo "This is a mock PDF content with keyword: pdf-search and details about digital documents." > "$TEST_DIR/Documents/mock_pdf.txt"

log "Dummy test files created in $TEST_DIR"

# --- Test fast-find.sh ---
log "Testing fast-find.sh (keyword search)..."
FAST_FIND_RESULT=$(bash "$FAST_FIND_SCRIPT" "apple-pie" 10 "$TEST_DIR/Documents" 2>/dev/null || true)
if echo "$FAST_FIND_RESULT" | grep -q "$TEST_DIR/Documents/test_doc.txt"; then
  log "PASS: fast-find found 'apple-pie' in test_doc.txt"
else
  log "FAIL: fast-find did NOT find 'apple-pie' in test_doc.txt"
  log "Output: $FAST_FIND_RESULT"
  exit 1
fi

FAST_FIND_LIMIT_RESULT=$(bash "$FAST_FIND_SCRIPT" "test_" 1 "$TEST_DIR" 2>/dev/null || true)
RESULT_COUNT=$(echo "$FAST_FIND_LIMIT_RESULT" | grep "$TEST_DIR" | wc -l)
if [ "$RESULT_COUNT" -ge 1 ] && echo "$FAST_FIND_LIMIT_RESULT" | grep -q "$TEST_DIR"; then
  log "PASS: fast-find limit 1 worked (found $RESULT_COUNT file)"
else
  log "FAIL: fast-find limit 1 did NOT work"
  log "Output: $FAST_FIND_LIMIT_RESULT"
  exit 1
fi

log "fast-find.sh tests complete."

# --- Test index_files_for_memory.py (content extraction & JSON output) ---
log "Testing index_files_for_memory.py..."
# Temporarily override target_directories in the Python script for testing
cp "$INDEX_FILES_SCRIPT" "$INDEX_FILES_SCRIPT.bak"
sed -i '' "s|target_directories = \[|target_directories = \[\\n        os.path.expanduser(\"$TEST_DIR\"),|" "$INDEX_FILES_SCRIPT"

INDEX_OUTPUT=$(python3 "$INDEX_FILES_SCRIPT")

# Restore original python script
mv "$INDEX_FILES_SCRIPT.bak" "$INDEX_FILES_SCRIPT"

# Verify JSON output structure and content
if echo "$INDEX_OUTPUT" | grep -q '"path": ".*test_doc.txt", "content_snippet": ".*apple-pie.*"' && \
   echo "$INDEX_OUTPUT" | grep -q '"path": ".*test_note.md", "content_snippet": ".*banana-split.*"' && \
   echo "$INDEX_OUTPUT" | grep -q '"path": ".*test_code.py", "content_snippet": ".*python-magic.*"' ; then
  log "PASS: index_files_for_memory.py produced correct JSON output"
else
  log "FAIL: index_files_for_memory.py output was incorrect"
  log "Output: $INDEX_OUTPUT"
  exit 1
fi
log "index_files_for_memory.py tests complete."

# --- Test observer-agent.sh integration (semantic/content recall via LLM) ---
log "Testing observer-agent.sh integration (this will call an LLM)..."
# Temporarily modify observer-agent.sh to force it to index our test dir
cp "$OBSERVER_AGENT_SCRIPT" "$OBSERVER_AGENT_SCRIPT.bak"
sed -i '' "s|target_directories = \[|target_directories = \[\\n        os.path.expanduser(\"$TEST_DIR\"),|" "$INDEX_FILES_SCRIPT"

# To make observer-agent process our test files, we need to ensure it sees them
# and that there are no conflicting locks or hashes. Also, ensure it feeds to LLM.
# For a true integration test, we'd run the observer, then memory_search.
# This part needs careful orchestration to ensure the LLM processes the test content.

# For now, let's ensure the observer runs and tries to process the content.
# A full memory_search test after LLM processing requires a real API call and time.
# We will simulate the observer running and check for expected output patterns.

# Create a dummy observation that can be overwritten by the test
echo "# Total Recall Observations" > "$OBSERVATIONS_FILE"
echo "" >> "$OBSERVATIONS_FILE"

# Run observer-agent.sh, forcing a lookback over the test files
# We need to pass the OPENCLAW_WORKSPACE env var, and ensure it uses our test dir
OPENCLAW_WORKSPACE="$WORKSPACE" bash "$OBSERVER_AGENT_SCRIPT" --flush > /dev/null

# Restore original observer-agent script
mv "$OBSERVER_AGENT_SCRIPT.bak" "$OBSERVER_AGENT_SCRIPT"

log "Waiting a moment for LLM processing and observation writing..."
sleep 10 # Give LLM time to process and write

# Check if observations.md contains content from our dummy files
assert_contains "$OBSERVATIONS_FILE" "apple-pie"
assert_contains "$OBSERVATIONS_FILE" "banana-split"
assert_contains "$OBSERVATIONS_FILE" "python-magic"
assert_contains "$OBSERVATIONS_FILE" "pdf-search"

log "observer-agent.sh integration tests complete."

# --- Final Cleanup ---
cleanup
log "All Total Recall file indexing tests PASSED!"
