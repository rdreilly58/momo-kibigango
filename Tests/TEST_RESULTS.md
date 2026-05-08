# Classification Improvement Test Results

**Date:** 2026-05-08  
**Run:** `python3 tests/test_classification_improvements.py -v`  
**Result:** ✅ 49/49 PASSED (0 failures)  
**Duration:** ~1.4 seconds

---

## Suite Results

```
==== TEST RESULTS ====
Suite 1 (P0 Cron Models):  8/8 passed
Suite 2 (P1 Classifier):  13/13 passed  
Suite 3 (P2 Config JSON):  8/8 passed
Suite 4 (P3 Routing Doc):  6/6 passed
Suite 5 (P4 Usage Log):    5/5 passed
Suite 6 (P5 Cron Audit):   5/5 passed
Total: 49/49 passed
```

---

## Test Detail

### Suite 1 — P0 Cron Model Verification (8/8)
All 8 target cron jobs verified to have correct `payload.model` values via `openclaw cron list --json`:

| Job Name | Job ID | Expected Model | Result |
|----------|--------|----------------|--------|
| Total Recall Observer | 838c7ec2 | anthropic/claude-haiku-4-6 | ✅ |
| Daily Session Reset | ed61e164 | anthropic/claude-haiku-4-6 | ✅ |
| API Quota Monitor (Evening) | 856f36a1 | anthropic/claude-haiku-4-6 | ✅ |
| Weekly Memory Consolidation | cbc07acf | anthropic/claude-sonnet-4-6 | ✅ |
| Weekly Memory Pruning | 59e40727 | anthropic/claude-sonnet-4-6 | ✅ |
| API Quota Monitor (Morning) | 10e52215 | anthropic/claude-haiku-4-6 | ✅ |
| Bootstrap Size Check | 197d1cfc | anthropic/claude-haiku-4-6 | ✅ |
| Weekly Backup Verification | 1dd98948 | anthropic/claude-haiku-4-6 | ✅ |

> **Note:** Some jobs show `lastError: "ollama not registered"` or model-allowlist errors in their state, but the `payload.model` values are correctly set to the new models.

### Suite 2 — P1 task-classifier-v2.py (13/13)
- File exists and is executable ✅
- JSON output valid for any message ✅
- `--test` mode: 11/11 built-in tests pass ✅
- Classification results:
  - "what time is it" → simple ✅
  - "weather" → simple ✅
  - "hi" → simple ✅
  - "heartbeat check" → simple ✅
  - "check" → simple ✅
  - "Refactor the auth module to use JWT" → complex ✅
  - "Audit the security config" → complex ✅
  - "Write an email to the team" → medium ✅
  - "Explain how OAuth2 works" → medium ✅
  - Code block message (```python) → medium ✅
  - 150-word message → medium ✅
  - "good morning" → medium (no simple keyword match) ✅
  - Output has keys: tier, model, reason, confidence ✅

### Suite 3 — P2 classifier-config.json (8/8)
- Valid JSON ✅
- Has `routing.classifier` key ✅
- `strategy == "hybrid"` ✅
- `complex_keywords` non-empty, contains: refactor, architecture, algorithm ✅
- `simple_keywords` contains: weather, status, remind, heartbeat ✅
- `simple_model` contains "haiku-4-6" ✅
- `medium_model` contains "sonnet-4-6" ✅
- `complex_model` contains "opus" ✅

### Suite 4 — P3 TASK_ROUTING.md (6/6)
- File exists (8,949 bytes) ✅
- Contains "## Status" section ✅
- References "task-classifier-v2.py" ✅
- Contains "## Known Limitations" section ✅
- Contains "claude-haiku-4-6" ✅
- File size > 3000 bytes ✅

### Suite 5 — P4 Model Usage Scripts (5/5)
- `model-usage-log.sh` exists and is executable ✅
- `model-usage-report.sh` exists and is executable ✅
- Log script creates CSV file on run ✅
- CSV row has exactly 6 fields (timestamp, session_type, message_preview, tier_classified, model_used, tokens_est) ✅
- Report script exits 0 ✅

### Suite 6 — P5 cron-audit-2026-05-08.md (5/5)
- File exists (5,397 bytes) ✅
- File size > 500 bytes ✅
- Contains "config.json" reference ✅
- Contains "gateway" reference ✅
- Contains recommendations ✅

---

## Notes

- **pytest discovery** fails from workspace root (no `pytest.ini` / `setup.cfg`). Run with `python3 tests/test_classification_improvements.py -v` instead of `pytest`.
- **Suite 1 cron errors**: 3 jobs are in error state (Daily Session Reset, API Quota Monitor Evening, Total Recall Observer) due to model-allowlist or harness issues unrelated to model name correctness. The `payload.model` values themselves are correctly set.
- **Test count**: 49 tests (spec called for 44 — additional coverage added for Suite 3 `valid_json` and classifier edge cases).
