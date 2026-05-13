
# never-forget/commit_handler.py
# Commit Handler for the Never-Forget Memory System

import json
import os
from datetime import datetime

CORE_MEMORY_FILE = "Project_Never_Forget_Core.md"

def load_existing_core_memory():
    """Loads the current content of the core memory file."""
    if not os.path.exists(CORE_MEMORY_FILE):
        return "## Core Memory Bank\n\n---\n\n*No memories committed yet.*"
    
    with open(CORE_MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def commit_new_memory(structured_json_string: str):
    """
    Writes the structured memory to the Project_Never_Forget_Core.md file.

    :param structured_json_string: JSON string output from the Extraction Engine.
    :return: Status message.
    """
    print(f"Attempting to commit memory to {CORE_MEMORY_FILE}...")
    
    try:
        # 1. Parse and Validate
        new_data = json.loads(structured_json_string)
        
        if 'memory_entries' not in new_data or not new_data['memory_entries']:
            return "⚠️ Warning: Attempted commit, but no memory entries were found in the structured data. Commit aborted."
        
        # 2. Load existing content
        existing_content = load_existing_core_memory()
        
        # 3. Format the new entries for Markdown inclusion
        memory_markdown = ""
        for entry in new_data['memory_entries']:
            type_map = {"fact": "Fact", "decision": "Decision", "learning": "Learning", "task": "Actionable Task"}
            entry_type = type_map.get(entry['type'], "Memory Snippet")
            
            markdown = f"### {entry_type}: {entry['summary']}\n"
            markdown += f"**Type:** {entry['type'].upper()}\n"
            markdown += f"**Source:** {new_data['metadata']['source_chat_id']} ({new_data['metadata']['source_timestamp']})\n"
            markdown += f"**Details:** {entry['details']}\n"
            markdown += f"**References:** {', '.join(entry['source_references'])}\n"
            markdown += "---\n"
            memory_markdown += markdown

        # 4. Construct the full update block
        commit_block = f"""
\n\n***\n## 💾 Newly Committed Memory Block: {new_data['metadata']['summary_key']}\n\n"""
        commit_block += memory_markdown
        commit_block += "\n\n***\n\n"

        # 5. Write/Append (Using a safe write operation)
        final_content = existing_content + commit_block
        
        # For safety, we'll write to a temporary file first and then replace the core file
        # (This simulates a robust commit process)
        temp_file = CORE_MEMORY_FILE + ".tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
            
        # Overwrite the original file
        with open(CORE_MEMORY_FILE, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"✅ Success: Memory committed and core file updated to {CORE_MEMORY_FILE}.")
        return f"Successfully committed {len(new_data['memory_entries'])} memory entries to {CORE_MEMORY_FILE}."

    except json.JSONDecodeError as e:
        return f"❌ Error: Failed to parse the structured JSON output. The commit process was aborted. Error: {e}"
    except Exception as e:
        return f"❌ Fatal Error during commit: {e}"

if __name__ == "__main__":
    # --- DEMO MODE ---
    print("--- Running Commit Handler Demo ---")
    
    # Mock structured JSON output from the Extraction Engine
    mock_structured_json = json.dumps({
      "metadata": {
        "source_chat_id": "telegram:8755120444",
        "source_timestamp": "Wed 2026-05-13 18:01 EDT",
        "summary_key": "System Status Check Follow-up"
      },
      "memory_entries": [
        {
          "type": "fact",
          "summary": "The cron system successfully ran both a status check and a memory sync job.",
          "details": "The system logs show that both generate-status.sh and memory-incremental-sync.sh were executed, indicating core background health checks are operational.",
          "source_references": ["Cron Job Log 1", "Cron Job Log 2"]
        },
        {
          "type": "learning",
          "summary": "The memory sync process is initiated by external system signals.",
          "details": "The presence of the `memory-incremental-sync.sh` log suggests that manual or automated syncs must be regularly monitored for data integrity.",
          "source_references": ["System Log"]
        }
      ]
    }, indent=2)

    # Cleanup previous dummy file for a clean demo run
    if os.path.exists(CORE_MEMORY_FILE):
        os.remove(CORE_MEMORY_FILE)
        print(f"Cleaned up previous {CORE_MEMORY_FILE}.")

    # Run the commit process
    result = commit_new_memory(mock_structured_json)
    print("\n--- RESULT ---\n")
    print(result)

    # Verify file content (Optional)
    print("\n--- VERIFYING CORE FILE CONTENTS (Snippet) ---")
    print(load_existing_core_memory()[-1000:]) # Show the end of the file
