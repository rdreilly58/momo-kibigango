#!/bin/bash
# run_total_recall_benchmarks.sh
# Executes the total_recall_search test and benchmarking suite.

# Activate the Python virtual environment for total_recall_search
# This assumes the venv is in ~/.openclaw/workspace/skills/total-recall-search/venv
# or that total-recall-search is otherwise in PATH

# Find the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

VENV_PATH="$SCRIPT_DIR/../skills/total-recall-search/venv"

# Ensure Python is available and venv is activated if it exists
if [ -d "$VENV_PATH" ]; then
  echo "Activating virtual environment: $VENV_PATH"
  source "$VENV_PATH/bin/activate"
else
  echo "WARNING: Virtual environment not found at $VENV_PATH. Ensure Python dependencies are globally installed or the venv is correctly set up."
fi

PYTHON_SCRIPT="$SCRIPT_DIR/test_total_recall_search.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
  echo "ERROR: Python test script not found at $PYTHON_SCRIPT"
  exit 1
fi

echo "Starting total_recall_search test and benchmarking suite..."
echo "---------------------------------------------------------"

python3 "$PYTHON_SCRIPT"

EXIT_CODE=$?

echo "---------------------------------------------------------"
echo "Benchmarking complete. Exit code: $EXIT_CODE"

exit $EXIT_CODE
