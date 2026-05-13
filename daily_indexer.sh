#!/bin/bash

# daily_indexer.sh
# Description: Automates the process of reading Markdown notes, extracting key properties (People, Projects, Dates),
# and summarizing these findings into a structured observation in MEMORY.md.
# This script must be run via cron or a scheduled job.

# --- Configuration ---
WORKSPACE_DIR="/Users/rreilly/.openclaw/workspace"
MEMORY_FILE="$WORKSPACE_DIR/MEMORY.md"

# --- Function to sanitize and format observation ---
# Usage: generate_observation "File path" "Extraction details"
generate_observation() {
    local file="$1"
    local details="$2"
    echo "### 🔍 Daily Indexing Observation: $file" >> "$MEMORY_FILE"
    echo "Source File: ${file}" >> "$MEMORY_FILE"
    echo "Observation: $details" >> "$MEMORY_FILE"
    echo "" >> "$MEMORY_FILE"
}

echo "--- Starting Daily Indexing Run ---"
echo "Targeting memory file: $MEMORY_FILE"

# 1. Find all Markdown files recursively in the workspace
# We exclude the MEMORY.md file itself to prevent infinite recursion/self-indexing
find "$WORKSPACE_DIR" -type f -name "*.md" ! -path "$MEMORY_FILE" | while read -r file; do
    echo "Processing file: $file"
    
    # 2. Run obsidian search to extract key properties
    # Assumption: The 'obsidian search' command is available in the PATH and accepts a file path.
    # We capture the output to process the structured data.
    
    OBSERVATION_OUTPUT=$(obsidian search "$file" 2>/dev/null)

    if [[ -z "$OBSERVATION_OUTPUT" ]]; then
        echo "   [WARN] No structured data found or obsidian search failed for $file."
        continue
    fi

    # 3. Extract and summarize findings
    # This part requires robust parsing of the 'obsidian search' output, 
    # but for the first pass, we'll use a generalized summary based on the output.
    
    # Example Placeholder Parsing Logic:
    # Replace this with actual robust parsing if the 'obsidian search' output format is known.
    
    # Simple check to see if the output contains the key elements
    if [[ "$OBSERVATION_OUTPUT" =~ [A-Za-z]+(People|Project|Dates) ]]; then
        
        SUMMARY="Discussions related to key entities were identified. The notes covered People, Projects, and Dates."
        
        # For a more detailed summary, we will use the raw output for the observation detail.
        DETAIL_LOG="Obsidian search output captured:\n---\n$OBSERVATION_OUTPUT\n---"
        
        # 4. Update MEMORY.md
        generate_observation "$file" "$DETAIL_LOG"
    else
        echo "   [INFO] File $file processed, but summary data was inconclusive."
    fi
done

echo "--- Daily Indexing Run Complete ---"

# Clean up the shebang line if it was manually added/modified later
# If the script fails, this provides a clear log.
