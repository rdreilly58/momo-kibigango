# Implementation Notes - Phase 2

## System Environment
- Python 3.14.3 
- macOS (Apple Silicon assumed based on context)
- 16GB total RAM, ~6.6GB available
- No PyTorch/Transformers installed yet

## Framework Decision: vLLM vs Custom Implementation

### Option A: vLLM (Recommended in requirements)
**Pros:**
- Built-in speculative decoding support
- Production-ready, well-tested
- Optimized inference engine
- Good documentation

**Cons:**
- Less flexibility for custom acceptance logic
- Heavier dependency
- May not support all our specific models

### Option B: Custom Implementation (Current approach)
**Pros:**
- Full control over acceptance logic
- Easier to debug and understand
- Can optimize specifically for our models
- Lighter weight initial setup

**Cons:**
- More development work
- Need to implement optimizations ourselves
- Less battle-tested

**Decision:** Start with custom implementation for Phase 2 to understand the mechanics, then consider vLLM for Phase 3/4 production deployment.

## Model Availability Check

### Target Model
- Qwen2-7B-4bit already cached at: `~/.cache/huggingface/hub/models--mlx-community--Qwen2-7B-4bit`
- This is good - no need to download

### Draft Model
- Phi-2 (2.7B) will need to be downloaded on first run
- Alternative: Could use a smaller model like TinyLlama (1.1B) to save memory

## Memory Considerations

With 16GB total RAM and ~6.6GB available:
- Qwen2-7B-4bit: ~4GB
- Phi-2: ~2.7GB (or ~1.4GB if quantized)
- Overhead: ~2-3GB
- **Total:** ~9-10GB needed

This is tight but should work. May need to:
1. Close other applications during testing
2. Consider using a smaller draft model
3. Enable aggressive quantization

## Next Steps for Testing

1. **Minimal Setup First:**
   ```bash
   pip install torch transformers psutil tqdm
   ```

2. **Test Model Loading:**
   - Create a simple script to just load the models
   - Monitor memory usage
   - Verify we stay under limits

3. **Then Full Setup:**
   ```bash
   ./scripts/setup_phase2.sh
   ```

4. **Alternative: Docker Container**
   - Could create a Docker image with all dependencies
   - Better isolation and reproducibility
   - But adds overhead

## Testing Strategy

Given the memory constraints, suggest:

1. **Start Small:**
   - Test with very short prompts first
   - Limit max_tokens to 50-100 initially
   - Monitor memory closely

2. **Gradual Scale-Up:**
   - Increase prompt length
   - Increase max_tokens
   - Add more complex benchmarks

3. **Fallback Plan:**
   - If Phi-2 is too large, try TinyLlama (1.1B)
   - If still too large, try even smaller models
   - Consider cloud GPU for final benchmarks

## Alternative Approach: Use Existing Qwen 35B Model

We noticed `~/models/qwen35b-4bit` exists. This is likely:
- Qwen 3.5 35B quantized to 4-bit
- Much larger than our target 7B model
- Would require different approach

For now, stick with the plan to use Qwen2-7B for Phase 2.