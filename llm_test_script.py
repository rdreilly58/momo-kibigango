import mlx.core as mx
from mlx_lm import load, generate_step
from mlx_lm.sample_utils import make_sampler

# 1. Load model and tokenizer
model, tokenizer = load("mlx-community/Mistral-7B-Instruct-v0.3-4bit")

# 2. Prepare the prompt as a token array
prompt = "The capital of France is"
tokens = mx.array(tokenizer.encode(prompt))

# 3. Configure the sampler (e.g., temperature 0.7)
# generate_step does NOT accept 'temp' or 'top_p' directly
sampler = make_sampler(temp=0.7)

# 4. Iterate using generate_step
print(prompt, end="", flush=True)
for token, probability in generate_step(model, tokens, sampler=sampler):
 if token == tokenizer.eos_token_id:
 break

 # Decode and print individual tokens
 print(tokenizer.decode([token]), end="", flush=True)