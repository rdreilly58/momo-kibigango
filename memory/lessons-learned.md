# Lessons Learned

A running record of non-trivial problems encountered and solved in the OpenClaw system.
Format: one entry per problem, structured for fast recall and prevention.

> **Convention**: `fix:` commits should reference the relevant entry with
> `(see lessons-learned.md#anchor)` in the commit body when applicable.

---

## 2026-04-26

### Archive sweep removed an active script (generate-status.sh)
- **Commit**: `fbb105f` — fix: restore generate-status.sh removed by archive sweep
- **Symptom**: `observer-agent.sh` failed to refresh STATUS.md after an archive cleanup pass moved scripts to `_archive/`
- **Root cause**: Archive sweep was too broad — grabbed `generate-status.sh` which is still called by the observer agent at runtime
- **Fix**: Restored script to active location; copy kept in `_archive/` for reference
- **Prevention**: Before archiving any script, grep for active references in cron jobs, shell scripts, and agent configs. Never archive without checking callers first
- **Check**: `grep -r "generate-status" ~/.openclaw/workspace/scripts/ ~/.openclaw/cron/`

---

## 2026-04-24

### Grafana: log2 scale + `min:0` breaks panel rendering
- **Symptom**: Barchart panel for Memory by Tier showed no data after switching to log scale
- **Root cause**: Log₂(0) is undefined — Grafana silently drops the panel when `min: 0` is set with a log scale
- **Fix**: Remove `min` from fieldConfig when using log scale
- **Prevention**: Never set `min: 0` on log-scale panels. Use `min: 1` if a floor is needed, or omit entirely
- **Test**: `TestGrafanaBarchartMemoryTier.test_no_min_zero_on_log_scale`

### Grafana: stacked bars + log scale are incompatible
- **Symptom**: Proposed stacked barchart with log2 Y-axis — visually broken
- **Root cause**: Stacking sums values before applying scale, producing meaningless log-of-sum readings
- **Fix**: Use grouped bars (no stacking) when log scale is required
- **Prevention**: Log scale → always grouped bars. Stacked bars → always linear scale
- **Test**: `TestGrafanaBarchartMemoryTier.test_no_stacking`

### Grafana: TSDB warm-up gap causes blank timeseries panels
- **Symptom**: CPU/RAM timeseries panels showed no data after adding `openclaw-tsdb` datasource
- **Root cause**: Real Prometheus (TSDB) only started scraping at 13:54; panels used `now-2h` window, leaving a 47-min gap with no data
- **Fix**: Switch instant/stat panels to ring-buffer exporter (immediate data); extend default time range to `now-24h` for timeseries panels
- **Prevention**: After adding a new Prometheus datasource, set the dashboard default range to `now-24h` minimum. New scrapers need warm-up time before short windows are useful
- **Test**: `TestGrafanaPanelRouting` (asserts correct datasource per panel type)

### Gateway detection: lsof shows nothing but process is running
- **Symptom**: `lsof -i :18789` returned empty — led to false belief gateway was down
- **Root cause**: OpenClaw gateway uses internal IPC, not a raw TCP socket visible to lsof
- **Fix**: Detect via `psutil` process name scan (`openclaw_gateway_running` metric already correct)
- **Prevention**: Never use `lsof` alone to confirm gateway status. Always cross-check with `ps`/psutil or the `/health` endpoint
- **Test**: `TestGatewayProcessDetection`

### Symlinks in skills/ blocked by gateway security policy
- **Symptom**: 18 skills silently unavailable; gateway logged security errors
- **Root cause**: `~/.openclaw/skills/` contained symlinks pointing outside the allowed directory (`~/.agents/skills/`). Gateway security policy blocks symlink escapes
- **Fix**: Replace all 18 symlinks with real file copies
- **Prevention**: Never use symlinks for skill files. Copy files directly into `~/.openclaw/skills/`. When adding skills, verify with `file <path>` that the result is a regular file not a symlink
- **Test**: `TestSkillsStubFile.test_not_a_symlink`

### Skills: missing SKILL.md generates log noise every cron cycle
- **Symptom**: Every cron invocation logged an error for `speculative-decoding/SKILL.md` missing
- **Root cause**: Gateway enumerates all skill directories and expects a `SKILL.md` in each; archived/removed skills leave orphan directories
- **Fix**: Add a stub `SKILL.md` explaining the skill is archived
- **Prevention**: When archiving a skill, always leave a stub `SKILL.md` rather than deleting the directory
- **Test**: `TestSkillsStubFile.test_stub_file_exists`

### Session metrics: sawtooth chart misread as many short sessions
- **Symptom**: Session duration chart showed repeated resets, appearing as dozens of short sessions per day
- **Root cause**: Metric was sourced from `agent:main:telegram:direct:*.updatedAt` which resets on every Telegram message — not a session boundary
- **Fix**: Split into two metrics: `openclaw_session_duration_seconds` (anchored to daily `session-start.json`, monotonically rising) and `openclaw_session_last_activity_seconds` (the sawtooth, correctly labelled "Since Last Message")
- **Prevention**: Distinguish between *session age* (anchored to start) and *activity age* (anchored to last event) when designing metrics. Label charts explicitly
- **Test**: `TestSessionMetricsSplit`

### CI: case-sensitive path failure on Linux
- **Symptom**: CI pytest step would fail on Linux runners with "no such file" even though it worked on macOS
- **Root cause**: macOS filesystem is case-insensitive (`tests/` == `Tests/`); Linux is case-sensitive. The workflow used lowercase `tests/`
- **Fix**: Changed workflow path to `Tests/` (matching the actual directory name)
- **Prevention**: Always match directory names exactly in CI config. When creating test directories, use `ls` to confirm the exact case before referencing in workflows
- **Test**: `TestCIPipeline.test_pytest_uses_correct_tests_path`

### Gitignore: already-tracked files are not suppressed by new rules
- **Symptom**: `memory/2026-04-24.md` still appeared in `git status` after adding `memory/2026-*.md` to `.gitignore`
- **Root cause**: `.gitignore` only affects untracked files. Files already committed to the index are not suppressed by new gitignore rules
- **Fix**: `git rm --cached <file>` to untrack, then commit the removal. Gitignore then takes effect going forward
- **Prevention**: When adding gitignore rules for files that may already be tracked, always run `git ls-files <pattern>` first and untrack as needed
- **Test**: `TestGitignoreRuntimeFiles`

### f-string syntax error with nested quotes
- **Symptom**: Python syntax error in `agent_coordinator.py` SQL query using f-string with `','.join(...)`
- **Root cause**: Nested quotes inside an f-string break the parser: `f'...({','.join(...)})...'`
- **Fix**: Extract the join expression to a variable before the f-string
- **Prevention**: Never nest quotes of the same type inside an f-string. Use a pre-built variable or triple-quote the outer string
- **Test**: `TestAgentCoordinatorPurge` (would catch a syntax error at import time)

## 2026-04-25

### Gmail OAuth expired, briefing broke silently
- **Symptom**: `send-briefing-v2.sh` failed to send; no error logs (using reillyrd58, Gmail-only OAuth)
- **Root cause**: Script used hardcoded `reillyrd58@gmail.com` with expired/limited OAuth scope; reillyrd58 only has Gmail scope, not full account access needed for briefing
- **Fix**: Changed script to use `rdreilly2010@gmail.com` via `email-utils.sh` wrapper, which has full OAuth; wrapper handles email account selection
- **Prevention**: Never hardcode email addresses in briefing/notification scripts. Use a helper that wraps account selection (e.g., `email-utils.sh`, preferring the primary account). Document which OAuth scopes each account has, and test briefing with the fallback account before deploying
- **Context**: Three Gmail accounts exist: rdreilly2010 (full OAuth ✅), reillyrd58 (Gmail-only ⚠️), reillydesignstudio (not added ❌)
