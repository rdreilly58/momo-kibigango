# Cron Jobs Audit — 2026-05-08

**Method:** Cross-referenced `~/.openclaw/config.json` cron.jobs[] against `openclaw cron list` gateway output.

---

## Summary

**config.json has 7 cron jobs. None appear in the gateway cron list by name.**

The config.json `cron.jobs[]` array appears to be a separate scheduling system from the gateway-managed cron. They likely run through different execution paths:
- **config.json jobs** → executed directly by the OpenClaw config scheduler
- **Gateway cron** → registered via `openclaw cron add` / `openclaw cron edit`

---

## config.json Cron Jobs vs Gateway Equivalents

| # | config.json Name | Schedule | Model | Gateway Equivalent | Status |
|---|-----------------|----------|-------|-------------------|--------|
| 1 | `daily-briefing` | `0 7 * * 1-5` (Mon–Fri 7am) | sonnet-4-6 | "Morning Briefing" (gateway, daily 6:15am) | ⚠️ **Possible duplicate** — different time & days, same concept |
| 2 | `dreams-consolidation` | `30 23 * * *` (daily 11:30pm) | haiku-4-6 | None | ✅ **Live** — no gateway equivalent |
| 3 | `memory-decay` | `0 2 * * 0` (Sunday 2am) | haiku-4-6 | "Weekly Memory Pruning" (Sunday 3am) | ⚠️ **Possible overlap** — different scripts, 1 hour apart |
| 4 | `weekly-memory-smart-prune` | `0 9 * * 3` (Wednesday 9am) | haiku-4-6 | None | ✅ **Live** — no gateway equivalent |
| 5 | `memory-lint` | `0 6 * * 1` (Monday 6am) | haiku-4-6 | None (Bootstrap Size Check is Monday 9am, different task) | ✅ **Live** — no gateway equivalent |
| 6 | `memory-auto-promote` | `45 23 * * *` (daily 11:45pm) | haiku-4-6 | None | ✅ **Live** — no gateway equivalent |
| 7 | `memory-compress-daily` | `0 3 * * 6` (Saturday 3am) | haiku-4-6 | None | ✅ **Live** — no gateway equivalent |

---

## Gateway Cron Jobs (Reference)

| ID | Name | Schedule | Target | Model |
|----|------|----------|--------|-------|
| c73e4009 | Session Watchdog | `7 * * * *` | main | — |
| 892c4cff | Generate STATUS.md | `*/30 * * * *` | main | — |
| ad2625b7 | Memory Incremental Sync | `*/30 * * * *` | main | — |
| 838c7ec2 | Total Recall Observer | `13 */2 * * *` | isolated | claude-sonnet |
| 9b5b78c9 | Morning Briefing | `15 6 * * *` | main | — |
| c614daf1 | Daily Anthropic Spend Check | `0 8 * * *` | main | — |
| ceb2cd04 | Anthropic Billing Monitor | `0 */4 * * *` | main | — |
| 10e52215 | API Quota Monitor (Morning) | `0 9 * * *` | isolated | claude-sonnet |
| 35ba6ee2 | Evening Briefing | `0 17 * * *` | main | — |
| 856f36a1 | API Quota Monitor (Evening) | `0 22 * * *` | isolated | claude-sonnet |
| ed61e164 | Daily Session Reset | `0 1 * * *` | isolated | claude-sonnet |
| 3039a145 | Auto-Update System | `0 2 * * *` | main | — |
| 9db987c3 | daily-backup | `30 2 * * *` | main | — |
| 6f1247ea | ReillyDesignStudio Deploy | `30 5 * * 6` | main | — |
| cbc07acf | Weekly Memory Consolidation | `0 1 * * 0` | isolated | claude-sonnet |
| 59e40727 | Weekly Memory Pruning | `0 3 * * 0` | isolated | claude-sonnet |
| 1dd98948 | Weekly Backup Verification | `0 10 * * 0` | isolated | claude-sonnet |
| 197d1cfc | Bootstrap Size Check | `0 9 * * 1` | isolated | claude-sonnet |

---

## Detailed Analysis of Potential Overlaps

### 1. `daily-briefing` vs `Morning Briefing`
- config.json: Mon–Fri at 7:00am, uses Sonnet, task = "Give me my daily briefing using the ai-daily-briefing skill format"
- Gateway: Daily at 6:15am, target = main, no dedicated model
- **Verdict:** Different schedules (weekdays vs daily) and different times (7am vs 6:15am). Possibly the gateway "Morning Briefing" replaced this, or they run independently. **Investigate before removing.**

### 2. `memory-decay` vs `Weekly Memory Pruning`
- config.json: Sunday 2am, runs `scripts/memory-decay.py --apply`
- Gateway: Sunday 3am, task details not shown in `cron list` output
- **Verdict:** Both are Sunday memory operations but 1 hour apart. May be complementary (different scripts) or one may be redundant. **Investigate what the gateway "Weekly Memory Pruning" actually runs.**

---

## Recommendations

| config.json Job | Recommendation |
|----------------|----------------|
| `daily-briefing` | **Investigate** — may duplicate gateway "Morning Briefing". If Morning Briefing is comprehensive, this is redundant. |
| `dreams-consolidation` | **Keep** — no gateway equivalent; unique nightly task |
| `memory-decay` | **Keep for now** — gateway "Weekly Memory Pruning" may overlap but runs a different script |
| `weekly-memory-smart-prune` | **Keep** — no gateway equivalent; runs Wednesday (different day than Sunday pruning) |
| `memory-lint` | **Keep** — no gateway equivalent |
| `memory-auto-promote` | **Keep** — no gateway equivalent; runs after dreams-consolidation |
| `memory-compress-daily` | **Keep** — no gateway equivalent |

---

## Action Items

- [ ] **Clarify `daily-briefing`**: Compare the config.json daily-briefing task prompt vs what gateway "Morning Briefing" does. If equivalent, remove from config.json.
- [ ] **Clarify `memory-decay` overlap**: Run `openclaw cron show 59e40727` (Weekly Memory Pruning) to see full task spec, then decide if config.json `memory-decay` is redundant.
- [ ] **No removals made**: No config.json jobs removed in this audit. Too much ambiguity to remove safely without investigation.

---

*Audit performed by Momotaro subagent, 2026-05-08*
