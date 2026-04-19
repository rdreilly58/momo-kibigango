# Speculative Decoding Explained: Theory & Examples

## What is Speculative Decoding?

Speculative decoding is an optimization technique that **speeds up LLM inference by generating multiple tokens per step instead of one**. It uses a smaller, faster "draft" model to predict the next few tokens, then a larger "verifier" model validates them all at once.

### The Problem It Solves

Standard LLM inference generates one token at a time:

```
Step 1: Generate "Hello"
Step 2: Generate "world"
Step 3: Generate "!"

Total: 3 steps (slow)
```

**Bottleneck:** Even though the model *could* process multiple tokens in parallel, we're limited by sequential generation.

### The Solution: Speculative Decoding

Instead, use two models:

```
Draft model (fast, small):   Predicts next 5 tokens quickly
Verifier model (large, accurate): Validates all 5 tokens in one pass

If correct: Accept all 5, move forward
If wrong: Accept partial, restart from where draft diverged

Result: 5 tokens in ~1.5x the time of 1 token
Speed gain: 3-5x acceleration
```

---

## How It Works: Technical Details

### Step-by-Step Process

**Setup:**
- **Draft model:** Small & fast (e.g., 1B-3B parameters)
- **Verifier model:** Large & accurate (e.g., 7B-13B parameters)
- **Context:** Current tokens generated so far

### Execution Loop

```python
# Simplified pseudocode
def speculative_decode(prompt, draft_model, verifier_model, max_tokens=100):
    generated = [prompt_tokens]
    
    while len(generated) < max_tokens:
        # Step 1: Draft model predicts MULTIPLE tokens (faster)
        draft_predictions = draft_model.predict_next_n_tokens(
            context=generated,
            n=5  # Predict 5 tokens ahead
        )
        # Result: [token_1, token_2, token_3, token_4, token_5]
        
        # Step 2: Verifier model validates ALL 5 at once (batched)
        verified = verifier_model.verify_tokens(
            context=generated,
            candidates=draft_predictions
        )
        # Result: Which tokens match verifier's top choices?
        
        # Step 3: Accept valid tokens, continue from there
        if verified[0] == draft_predictions[0]:  # First token correct?
            if verified[1] == draft_predictions[1]:  # Second?
                # ... etc
                accepted = 3  # Accept first 3 tokens
                generated.extend(draft_predictions[:3])
        else:
            # Draft diverged immediately, accept verifier's token
            generated.append(verifier_model.generate_one_token(generated))
    
    return generated
```

### Key Insight

The magic is that the **verifier processes all draft tokens in one forward pass**. Modern GPUs/accelerators can batch process multiple tokens simultaneously, so verifying 5 tokens costs almost the same as verifying 1.

---

## Performance Improvement Analysis

### Standard Inference (No Speculative Decoding)

```
Generate 100 tokens:
- 100 forward passes (one per token)
- Latency: ~100 × 50ms = 5000ms (5 seconds)
```

### With Speculative Decoding

```
Generate 100 tokens with draft + verify:
- Draft model: Predicts 5 at a time (fast)
  Time: 5ms per prediction × 20 rounds = 100ms
  
- Verifier model: Validates 5 tokens in one pass (batched)
  Time: 40ms per verification × 20 rounds = 800ms
  
Total: 900ms (vs 5000ms without)
Speedup: 5.5x acceleration
```

**Real-world results:**
- Simple queries: 2-3x faster (more draft accuracy)
- Complex queries: 1.5-2x faster (more draft divergence)

---

## Example 1: Simple Query (High Accuracy Case)

**Prompt:** `"What is 2+2?"`

### Without Speculative Decoding

```
Input: "What is 2+2?"

Step 1: Generate " The"     (verifier predicts " The")
Step 2: Generate " answer"  (verifier predicts " answer")
Step 3: Generate " is"      (verifier predicts " is")
Step 4: Generate " 4"       (verifier predicts " 4")
Step 5: Generate "."        (verifier predicts ".")

Total: 5 steps
Time: 5 × 50ms = 250ms
```

### With Speculative Decoding

```
Input: "What is 2+2?"

Step 1 - DRAFT PREDICTS 5 TOKENS:
  Draft: [" The", " answer", " is", " 4", "."]
  (takes 5ms - draft is tiny)

Step 2 - VERIFIER VALIDATES ALL 5:
  Verifier processes context + [" The", " answer", " is", " 4", "."]
  in one batch → checks: "Do these match my top predictions?"
  
  Check:
    Token 1 (" The") → ✓ Matches verifier's #1 choice
    Token 2 (" answer") → ✓ Matches verifier's #1 choice
    Token 3 (" is") → ✓ Matches verifier's #1 choice
    Token 4 (" 4") → ✓ Matches verifier's #1 choice
    Token 5 (".") → ✓ Matches verifier's #1 choice
  
  Result: ALL 5 ACCEPTED
  (takes 40ms - batched verification)

Total: 1 big step (45ms)
Time: 45ms
Speedup: 250ms → 45ms = 5.5x faster
```

**Why so fast?** For simple math, both models agree strongly. Draft predictions are almost always correct.

---

## Example 2: Complex Query (Lower Accuracy Case)

**Prompt:** `"Explain the philosophical implications of quantum entanglement in the context of..."`

### Without Speculative Decoding

```
Step 1: Generate "Quantum"
Step 2: Generate " entanglement"
Step 3: Generate " is"
Step 4: Generate " a"
Step 5: Generate " phenomenon"
... (many more steps)

Total: 50+ steps
Time: 50 × 50ms = 2500ms (2.5 seconds)
```

### With Speculative Decoding

```
Step 1 - DRAFT PREDICTS 5:
  Draft: ["Quantum", " entanglement", " suggests", " that", " particles"]
  
Step 2 - VERIFIER VALIDATES:
  Token 1 ("Quantum") → ✓ Matches verifier
  Token 2 (" entanglement") → ✓ Matches verifier
  Token 3 (" suggests") → ✗ DIVERGE! Verifier wanted " demonstrates"
  
  Result: ACCEPT 2, REJECT 3
  (Continue from position 2)

Step 3 - VERIFIER GENERATES 1 TOKEN:
  " demonstrates" (verifier's correct choice)

Step 4 - DRAFT PREDICTS 5 AGAIN:
  Draft: [" how", " quantum", " mechanics", " works", " differently"]
  
Step 5 - VERIFIER VALIDATES:
  Token 1 (" how") → ✗ Diverge (verifier wants " the")
  
  Result: ACCEPT 0, REJECT ALL
  
Step 6 - VERIFIER GENERATES 1:
  " the" (verifier's choice)

... (continue pattern)

Total: ~25 big steps (instead of 50 single steps)
Time: 25 × 50ms = 1250ms
Speedup: 2500ms → 1250ms = 2x faster
```

**Why less gain?** For complex topics, the draft model is less confident. It makes mistakes, so verifier has to reject and restart more often. Still get 2x speedup, but not the 5.5x we got with math.

---

## Current Setup: Local Qwen2 (Not Using Speculative Decoding Yet)

### What We Have Now

```
Local inference:
├─ Model: Qwen2-7B-4bit (single model)
├─ Framework: MLX-LM
├─ Throughput: 12.5 tokens/sec
└─ Latency: 5.1 seconds average
```

**No speculative decoding because:**
- Would need TWO models loaded simultaneously
- Draft model (1-3B) + Verifier (7B) = 11GB+ total
- M4 Max has ~24GB, so it fits theoretically
- But complexity/latency tradeoff not yet justified for our usage

### Why We Don't Use It Yet

Speculative decoding is best for:
- **High-throughput servers** (1000s of requests/sec)
- **Latency-critical APIs** (need <100ms response)
- **Long-form generation** (1000+ tokens)

We use it for:
- Interactive development (one user, 5-10 min between queries)
- Short-to-medium responses (100-200 tokens typical)
- Cost-optimization (local GPU, already free)

**ROI calculation:**
- Setup cost: 15-30 min (implementing dual-model)
- Performance gain: 2-3x speedup on long queries
- Usage pattern: 5 sessions/day, 30 min total active
- Actual gain: 5-10 minutes/day (negligible)
- **Not worth it right now**

---

## When We WOULD Use Speculative Decoding

✅ **Reasons to add it:**
1. If throughput becomes bottleneck (e.g., 50+ concurrent users)
2. If we need <2 second latency guarantee
3. If we switch to cloud inference (g4dn.2xlarge) and want ROI
4. If we generate long documents regularly (1000+ tokens)

📋 **Implementation roadmap:**
- Phase 1: Stay with single-model local (current)
- Phase 2: Monitor AWS deployment (if deployed)
- Phase 3: Add speculative decoding if needed (Q3/Q4 2026)

---

## Summary: Speculative Decoding in Plain English

**The idea:** Use a small "guess" model to predict multiple tokens fast, then have a large "checker" model validate them all at once.

**The result:** 2-5x faster inference without quality loss.

**Simple example:** Draft guesses "Hello world" (2ms), verifier checks both words at once (40ms) = 42ms total instead of 100ms.

**Complex example:** Draft guesses 5 words, gets 2 right. Verifier accepts those 2, generates the correct 3rd word, draft tries again = ~2x speedup.

**For your current setup:** Not needed yet. Single-model is simpler and adequate for 5-10 daily sessions. Worth revisiting Q3 2026 if usage scales.

---

**Status:** Documented for future reference. Can implement when ROI justifies complexity.
