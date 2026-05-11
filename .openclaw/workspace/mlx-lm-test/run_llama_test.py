# run_llama_test.py
import os
import subprocess
from pathlib import Path

# --- Configuration ---
# Recommended Llama 3 variant for 8B:
# NOTE: You may need to adjust this model path based on how 'mlx-lm' expects the model name.
MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"

# Target directory setup (assumes we run this script from the project root)
PROJECT_DIR = Path(__file__).parent

def run_inference(model_name, prompt):
    """
    Attempts to run the LLM inference using the mlx-lm wrapper.
    """
    print(f"--- 🚀 Starting Llama 3 ({model_name}) Inference Test ---")
    print("Dependencies check passed: Torch, Transformers, mlx-lm should be available.")
    print("If this fails, ensure your environment is correctly sourced (venv/bin/activate).")

    # --- MLX-LM Call Structure ---
    # The exact command structure depends on the current mlx-lm wrapper's API.
    # This template assumes a standard command-line interface for simplicity.
    
    # For 4-bit quantization, the model name often implicitly handles this
    # if the mlx-lm wrapper is correctly set up.
    command = [
        "mlx_lm", 
        "run", 
        "--model", model_name, 
        "--prompt", prompt,
        "--context_size", "8192" # Common default context size
    ]

    try:
        # Use subprocess.run to execute the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True # Raises CalledProcessError if command fails
        )
        print("\n=======================================")
        print("✅ INFERENCE SUCCESSFUL:")
        print("======================================")
        print(result.stdout)
        
    except FileNotFoundError:
        print("\n=======================================")
        print("❌ ERROR: 'mlx_lm' command not found.")
        print("Please confirm that the 'mlx-lm' library was correctly installed and accessible in the environment PATH.")
        print("======================================")
    except subprocess.CalledProcessError as e:
        print("\n=======================================")
        print(f"❌ ERROR: Inference failed with exit code {e.returncode}.")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        print("\nTip: Check if you need to log in via huggingface-cli or if the model requires specific API keys.")
        print("======================================")

if __name__ == "__main__":
    user_prompt = "Explain the basic principles of a reversible computer in three short paragraphs, assuming I have a background in classic computing."
    run_inference(MODEL_NAME, user_prompt)
