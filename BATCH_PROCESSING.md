# Batch Processing Strategy

**Purpose:** Combine similar tasks into single requests to reduce API calls and improve throughput.

---

## When to Use Batch Processing

**Perfect for:**
- ✅ Password generation (5-10 passwords in one request)
- ✅ Repetitive lookups (multiple email searches, calendar queries)
- ✅ Configuration updates (multiple file edits)
- ✅ Data transformations (batch conversions, reformatting)

**Not ideal for:**
- ❌ Single items (overhead > benefit)
- ❌ Diverse tasks (hard to structure)
- ❌ Real-time interactions (user expects immediate response)
- ❌ Error-critical work (better to fail small)

---

## Implementation Pattern

**Structure:**
```
Request all 5 items at once with structured output

1. Generate password for Gmail
2. Generate password for AWS
3. Generate password for Cloudflare
4. Generate password for GitHub
5. Generate password for Mercury

Output format: JSON array with [service, username, password]
```

**Benefit:**
- Reduces API calls from 5 to 1
- Faster overall throughput
- Easier to track and validate
- Better context continuity

---

## Password Generation Batch Example

**Old way (5 separate calls):**
```
Call 1: Generate Gmail password
Call 2: Generate AWS password
Call 3: Generate Cloudflare password
Call 4: Generate GitHub password
Call 5: Generate Mercury password
Total time: ~5-10 seconds
```

**New way (1 batch call):**
```
Call 1: Generate all 5 passwords in structured format
Total time: ~1-2 seconds
Savings: 4-8 seconds per batch
```

---

## Batch Processing Rules

1. **Max batch size:** 5-10 items per request (diminishing returns after)
2. **Error handling:** If 1 fails, return partial results + error details
3. **Validation:** Always validate output structure before using
4. **Fallback:** Single-item requests if batch fails
5. **User notification:** Show batch progress (e.g., "Processing 5 passwords...")

---

## Current Batch-Friendly Tasks

| Task | Items | Frequency | Savings |
|------|-------|-----------|---------|
| Password generation | 3-5 | High | 2-4s per batch |
| Calendar lookups | 5-7 | Medium | 1-2s per batch |
| Config updates | 2-5 | Low | 1-3s per batch |
| File operations | 3-8 | Medium | 1-2s per batch |

---

## Future Optimization

**Speculative Decoding (TBD - Q3/Q4 2026):**
- Requires API provider support
- Expected 2-3x speedup without quality loss
- Will activate automatically when available
- No user code changes needed

---

## Testing & Monitoring

- Test batch requests with real data
- Monitor success/failure rates
- Track time savings
- Adjust batch sizes based on results
- Document edge cases
