import mlx.core as mx
from mlx_lm.models.llama import LlamaModel, generate_from_prompt
import os

# --- Configuration ---
# !!! CRITICAL: UPDATE THE MODEL ID AND PATH BELOW !!!
MODEL_ID = "microsoft/phi-3-mlx"
MODEL_PATH = f"./mlx_model_repo/microsoft/phi-3-mlx" 
# ---------------------

def run_inference(prompt: str, max_tokens: int = 150):
    print("-" * 50)
    print(f"Loading Model from: ")
    
    if not os.path.isdir(MODEL_PATH):
        print("="*70)
        print("!!! CRITICAL SETUP FAILURE !!!")
        print(f"The model directory was not found at: ")
        print("Please check the model repository structure and update the MODEL_PATH and MODEL_ID variables in this script.")
        print("="*70)
        return

    try:
        # Initialize the model (MLX handles the quantization loading internally)
        model = LlamaModel.load(MODEL_PATH)
    except Exception as e:
        print(f"FATAL ERROR: Could not load model. Check if the model is properly set up for MLX.")
        print(f"Underlying MLX error: {e}")
        return
    
    print("Model loaded successfully.")
    
    print(f"\n--- Running Inference for Prompt: \"{prompt}\" ---")
    
    # Generate the response using the MLX utility function
    response = generate_from_prompt(
        model, 
        prompt, 
        max_tokens=max_tokens
    )
    
    print("\nMLX Generated Response:")
    print(response)
    print("-" * 50)

if __name__ == "__main__":
    # Example usage: Change this prompt to test
    test_prompt = "Write a short, helpful poem about using advanced MLX tooling."
    run_inference(test_prompt)
