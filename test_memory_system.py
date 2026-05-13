#!/usr/bin/env python3
import subprocess
import time
import os
from datetime import datetime

# --- Configuration ---
WORKSPACE = os.environ.get("WORK_DIR", "/Users/rreilly/.openclaw/workspace")
TEST_LOG = "memory_test_results.log"
print(f"--- Starting Memory System Test Suite ---\nLogging output to {TEST_LOG}")

def run_test(test_name, command):
    """Helper function to execute a command and log results."""
    print(f"==================================================")
    print(f"TEST: {test_name}")
    print(f"==================================================")
    try:
        start_time = time.time()
        # Use subprocess.run to capture stdout/stderr reliably
        result = subprocess.run(
            command,
            shell=True,
            check=True, # Raise an error on non-zero exit code
            capture_output=True,
            text=True
        )
        end_time = time.time()
        print(f"STATUS: SUCCESS (Time: {end_time - start_time:.2f}s)")
        with open(TEST_LOG, "a") as f:
            f.write(f"--- {test_name} ---\n")
            f.write(f"Status: SUCCESS\n")
            f.write(f"Output:\n{result.stdout}\n")
            f.write(f"Stderr:\n{result.stderr}\n\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"STATUS: FAILURE")
        print(f"ERROR MESSAGE: Command failed with return code {e.returncode}")
        print(f"STDOUT:\n{e.stdout}")
        print(f"STDERR:\n{e.stderr}")
        with open(TEST_LOG, "a") as f:
            f.write(f"--- {test_name} ---\n")
            f.write(f"Status: FAILURE (Code {e.returncode})\n")
            f.write(f"Error Output (Stdout):\n{e.stdout}\n")
            f.write(f"Error Output (Stderr):\n{e.stderr}\n\n")
        return False
    except Exception as e:
        print(f"STATUS: CRITICAL FAILURE")
        print(f"UNEXPECTED ERROR: {e}")
        with open(TEST_LOG, "a") as f:
            f.write(f"--- {test_name} ---\n")
            f.write(f"Status: CRITICAL FAILURE\n")
            f.write(f"Error: {str(e)}\n\n")
        return False

def main():
    print("--- Memory System Test Suite Initialized ---")

    # 1. Test Search (total-recall-search.py)
    # Simulates a complex, targeted search query.
    search_cmd = "python3 scripts/total-recall-search.py \"Memory system architecture update\" --rerank"
    run_test("Search/Recall Test", search_cmd)

    # 2. Test Consolidation (scripts/dreams-consolidation.py)
    # Simulates the nightly process of consolidating ephemeral data.
    consolidation_cmd = "python3 scripts/dreams-consolidation.py"
    run_test("Consolidation/Dreaming Test", consolidation_cmd)

    # 3. Test Tier Management & Promotion (scripts/memory_tier_manager.py & scripts/memory-auto-promote.py)
    # Tests the movement of memories between hot, warm, and cold tiers.
    tier_cmd = "python3 scripts/memory_tier_manager.py --test-promote"
    run_test("Tier Management/Promotion Test", tier_cmd)

    # 4. Test Decay (scripts/memory-decay.py)
    # Simulates the removal/archiving of old, unused memories.
    decay_cmd = "python3 scripts/memory-decay.py --dry-run"
    run_test("Decay/TTL Test (Dry Run)", decay_cmd)

    # 5. Test Subagent Context/Writeback (scripts/memory-writeback.py)
    # Simulates a subagent completing a task and saving structured knowledge back to memory.
    writeback_cmd = "python3 scripts/memory-writeback.py --test-writeback 'The memory test suite executed successfully.'"
    run_test("Writeback/Context Test", writeback_cmd)

    print("\n==================================================")
    print("--- Memory System Test Suite Execution Finished ---")
    print(f"Detailed results saved to {TEST_LOG}")

if __name__ == "__main__":
    main()