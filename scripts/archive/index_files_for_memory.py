import os
import subprocess
import json
import glob

def extract_text(filepath):
    """Extracts text from various file types using macOS's textutil or plain read."""
    file_extension = os.path.splitext(filepath)[1].lower()

    if file_extension in ['.md', '.txt', '.py', '.js', '.sh', '.swift', '.json', '.xml', '.yml', '.yaml', '.log', '.h', '.m', '.c', '.cpp', '.hpp', '.html', '.css', '.rb', '.java', '.go', '.rs']:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading text file {filepath}: {e}"
    elif file_extension in ['.pdf', '.doc', '.docx', '.rtf', '.webarchive']:
        try:
            # Use textutil for macOS-specific document conversion
            result = subprocess.run(['textutil', '-convert', 'txt', '-stdout', filepath], capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error converting {filepath} with textutil: {e.stderr}"
        except Exception as e:
            return f"Error processing {filepath}: {e}"
    else:
        return None # Skip unsupported file types

def index_directory_for_memory(base_dir):
    """Indexes files within a directory and its subdirectories for OpenClaw's memory."""
    print(f"Indexing directory: {base_dir}", file=__import__('sys').stderr)
    for root, _, files in os.walk(base_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            if os.path.exists(filepath) and os.path.isfile(filepath):
                text_content = extract_text(filepath)
                if text_content:
                    # In a real OpenClaw integration, you would call a memory_add API here.
                    # For now, we'll print the path and a snippet of content.
                    print(json.dumps({"path": filepath, "content_snippet": text_content[:500]}))

if __name__ == "__main__":
    target_directories = [
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Projects"),
        os.path.expanduser("~/notes"),
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Library/Mobile Documents/com~apple~Notes/Accounts/All/"), # Apple Notes
        os.path.expanduser("~/.openclaw/workspace/"),
        os.path.expanduser("~/repos"),
        os.path.expanduser("~/sandbox"),
    ]

    for directory in target_directories:
        if os.path.isdir(directory):
            index_directory_for_memory(directory)
        else:
            print(f"Warning: Directory not found, skipping: {directory}")
