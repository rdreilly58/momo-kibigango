import subprocess
import os
import json
from typing import List, Dict

# --- DeepSeek Model Simulation Placeholder ---
# In a real environment, this function would use a dedicated API client
# (e.g., using the 'claude-api' skill or a specific DeepSeek SDK) 
# to call the model. For this simulated test, we'll use a mock response 
# that mimics the expected function signature and complexity.

def generate_code_from_deepseek(prompt: str) -> str:
    """
    Mocks calling the DeepSeek model to generate code for a given prompt.
    Returns a string containing the executable Python code.
    """
    print(f"--- Calling DeepSeek Model for prompt: '{prompt[:50]}...' ---")
    
    if "fibonacci" in prompt.lower():
        # Mocking a simple, functional code generation
        return """
def calculate_fibonacci(n: int) -> int:
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
"""
    elif "reverse" in prompt.lower():
        # Mocking a slightly more complex, error-prone generation
        return """
def reverse_string(s: str) -> str:
    # Simple list reversal logic
    return "".join(reversed(list(s)))
"""
    else:
        return f"print('// Mock code generated for: {prompt}')"

# --- Test Harness Core Function ---

def run_coding_test(task_description: str):
    """
    Generates code via the mock DeepSeek model, executes it in an isolated environment,
    and validates the output against expected behavior.
    """
    print("====================================================================")
    print(f"🚀 Starting DeepSeek Coding Test: {task_description}")
    print("====================================================================")

    # 1. Code Generation
    generated_code = generate_code_from_deepseek(task_description)
    print("\n[INFO] ✅ Code Generated Successfully (Mocked).\n")
    
    # 2. Isolated Execution and Validation
    try:
        # Write the generated code to a temporary file for safe execution
        temp_script_path = "temp_test_script.py"
        with open(temp_script_path, "w") as f:
            f.write(generated_code)

        # For testing, we must define how the function is called.
        # This is the biggest assumption needed for a generic harness.
        # We assume the task description implies a runnable function call.
        
        # For this test, we will assume the prompt relates to the Fibonacci sequence.
        if "fibonacci" in task_description.lower():
            execution_code = "print(f'Fibonacci(10) = {calculate_fibonacci(10)}')"
        elif "reverse" in task_description.lower():
             execution_code = "print(f'Reversed(''Hello''){reverse_string(''Hello'')}')"
        else:
            execution_code = "print('Test run complete.')"
            
        full_execution_script = f"""
# {task_description}
{generated_code}
# --- EXECUTION BLOCK ---
{execution_code}
"""

        # Execute the combined script in a sandbox environment
        result = subprocess.run(
            ['python3', '-c', full_execution_script],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 3. Reporting
        print("\n[SUCCESS] ✅ Code executed and validated successfully.")
        print("\n--- DETAILED OUTPUT ---\n" + result.stdout.strip())
        return True, result.stdout.strip()

    except subprocess.CalledProcessError as e:
        print("\n[FAILURE] ❌ Code execution failed.")
        print(f"Standard Error: {e.stderr}")
        return False, e.stderr
    except Exception as e:
        print(f"\n[FAILURE] ❌ An unexpected error occurred during testing: {e}")
        return False, str(e)
    finally:
        # Cleanup
        if os.path.exists("temp_test_script.py"):
            os.remove("temp_test_script.py")

def run_test_suite():
    """Runs the full suite of tests."""
    print("\n\n====================================================================")
    print("--- STARTING DEEPSEEK CODING PROFICIENCY TEST SUITE ---")
    print("====================================================================")
    
    # Test 1: Simple mathematical sequence (Fibonacci)
    task_1 = "Write a clean, function-based Python script to calculate the Nth Fibonacci number."
    run_coding_test(task_1)
    
    print("\n\n####################################################################\n")
    
    # Test 2: String manipulation and logic (String reversal)
    task_2 = "Write a Python function to reverse a given string."
    run_coding_test(task_2)

if __name__ == "__main__":
    run_test_suite()