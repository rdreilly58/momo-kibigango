#!/bin/bash
set -e

echo "🚀 Starting local vLLM-MLX inference server..."
echo ""

source ~/mlx-vllm-env/bin/activate

MODEL_PATH=~/models/qwen35b-4bit

if [ ! -d "$MODEL_PATH" ]; then
  echo "❌ Model not found at $MODEL_PATH"
  exit 1
fi

echo "📂 Model: Qwen2-7B-4bit"
echo "🔌 Starting server on http://localhost:8000"
echo ""

# Use mlx-lm directly for inference
python3 << 'PYTHON_SERVER'
import mlx.core as mx
from mlx_lm import load, generate
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import asyncio

app = FastAPI()

# Load model
model, tokenizer = load("~/models/qwen35b-4bit".replace("~", os.path.expanduser("~")))

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7
    top_p: float = 0.95

@app.post("/generate")
async def generate_endpoint(request: GenerateRequest):
    try:
        result = generate(
            model,
            tokenizer,
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p
        )
        return {
            "prompt": request.prompt,
            "response": result,
            "tokens": len(result.split())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ready", "model": "Qwen2-7B-4bit"}

if __name__ == "__main__":
    print("✓ Model loaded!")
    print("🔗 Starting server on http://localhost:8000")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=8000)
PYTHON_SERVER
