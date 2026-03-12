# Claude Code Build Process — Production Standard

## Overview
Structured process for spawning Claude Code subagents to ensure reliable builds, real-time monitoring, and verified GitHub deployment.

## Pre-Build Checklist

Before spawning Claude Code:
1. ✅ Have detailed task specification (40+ lines minimum)
2. ✅ Know expected file count and sizes
3. ✅ Know GitHub repo and target branch
4. ✅ Have success criteria defined
5. ✅ Notify Bob that build is starting

## Spawn Template

**Primary (Claude Code):**
```
sessions_spawn(
  runtime="subagent",
  task="[DETAILED 50+ LINE SPECIFICATION]",
  model="claude-opus-4-0"
)
```

**Fallback (if Claude Code fails):**
```
sessions_spawn(
  runtime="subagent",
  task="[DETAILED 50+ LINE SPECIFICATION]",
  model="gpt-4-turbo"
)
```

**For Large Tasks (16+ files): Use Incremental Batching**
```
Batch 1: sessions_spawn(..., task="BATCH 1: Backend - 3-4 files")
[Wait for completion, verify]
Batch 2: sessions_spawn(..., task="BATCH 2: macOS - 4 files")
[Wait for completion, verify]
Batch 3: sessions_spawn(..., task="BATCH 3: iPhone - 4 files")
[Wait for completion, verify]
Batch 4: sessions_spawn(..., task="BATCH 4: Tests + Docs - 3 files")
```

## Real-Time Monitoring Process

### Minute 1 (Check: Has Claude Code started working?)
- [ ] Monitor subagent for initial activity
- [ ] Check if files are being created in workspace
- [ ] Verify no immediate errors
- **Action:** Report to Bob: "✅ Claude Code started, building..."
- **If silent:** Kill subagent, investigate, respawn with more detail

### Minutes 2-3 (Backend progress)
- [ ] Check ~/onigashima/ for new backend files
- [ ] Verify file sizes are reasonable (not empty stubs)
- [ ] Look for websocket-handler.js, message-service.js
- **Action:** Report: "📝 Backend files appearing..."
- **If stalled:** Check last modified times, may need to kill and respawn

### Minutes 4-5 (Frontend progress)
- [ ] Check for macOS SwiftUI files (ChatView.swift, etc.)
- [ ] Check for iPhone SwiftUI files
- [ ] Verify file count growing
- **Action:** Report: "📱 Frontend files building..."

### Minutes 6-7 (Tests + Documentation)
- [ ] Check for test files (MessageServiceTests.swift, WebSocketTests.swift)
- [ ] Check for documentation (WEBSOCKET_GUIDE.md, WEEK_4_IMPLEMENTATION.md)
- **Action:** Report: "🧪 Tests and docs in progress..."

### Minute 8-10 (Build completion)
- [ ] Check total file count matches specification
- [ ] Verify all files have reasonable content (not stubs)
- [ ] Check for any error messages or incomplete files
- **Action:** Report: "✅ Build complete, preparing commit..."

## Post-Build GitHub Process

### Step 1: Verify Files (Bob's workspace)
```bash
ls -lh ~/.openclaw/workspace/onigashima/
# Check: All expected files present
# Check: File sizes reasonable (not 0 bytes)
# Check: Timestamps recent
```

### Step 2: Commit to Git
```bash
cd ~/.openclaw/workspace/onigashima/
git status  # Review what changed
git add .
git commit -m "[DETAILED MESSAGE]"
# Example: "Week 4: WebSocket real-time messaging - complete implementation"
```

### Step 3: Push to GitHub
```bash
git push origin main
# Watch for: 
# - "Creating..." messages (new files)
# - "Updating..." messages (existing files)
# - No errors or rejections
```

### Step 4: Verify Push on GitHub.com
1. Open https://github.com/rdreilly58/onigashima
2. Check main branch
3. Verify latest commit matches what we pushed
4. Check file list (compare to local)
5. Click on largest file, verify content is there (not stub)
6. **Action:** Report to Bob: "✅ GitHub push verified — X new files, Y commits behind origin"

### Step 5: Report Success
```
✅ WEEK 4 BUILD COMPLETE

📊 Summary:
- 16 files created (backend + frontend + tests + docs)
- Backend: websocket-handler.js, message-service.js, routes/messages.js
- macOS: ChatView.swift, ChatViewModel.swift, WebSocketManager.swift, Message.swift
- iPhone: MessagesView.swift, MessagesViewModel.swift, WebSocketClient.swift, Message+CoreData.swift
- Tests: MessageServiceTests.swift, WebSocketTests.swift
- Docs: WEBSOCKET_GUIDE.md, WEEK_4_IMPLEMENTATION.md

🔗 GitHub: https://github.com/rdreilly58/onigashima/commits/main
✅ Latest commit: "Week 4: WebSocket real-time messaging - complete implementation"
```

## Failure Detection & Recovery

### If build stalls (no file activity after 2 minutes):
1. Kill subagent: `subagents(action="kill", target="<session-key>")`
2. Diagnose: What went wrong? (bad spec? missing context?)
3. Respawn with improved specification + more detail

### If files are empty stubs:
1. Kill subagent
2. Check Claude Code's output/error messages
3. Add more specific implementation details to spec
4. Respawn with corrected task

### If GitHub push fails:
1. Check git status locally
2. Verify credentials/auth
3. Try pushing again with: `git push origin main --verbose`
4. If still failing, report to Bob for manual investigation

## Spec Template (For All Future Builds)

Start every Claude Code task with:

```
ONIGASHIMA WEEK [X]: [FEATURE NAME]

GOAL: [Clear 1-sentence objective]

DELIVERABLES (Production-Ready Code):

## Backend (Node.js/Express)
[List each file with ~line count and bullet points of what it does]

## macOS (SwiftUI)
[List each file with ~line count and bullet points]

## iPhone (SwiftUI)
[List each file with ~line count and bullet points]

## Tests
[List test files with coverage goals]

## Documentation
[List documentation files]

REQUIREMENTS:
- Production-ready (not pseudocode)
- [Specific technical requirements]
- [Error handling expectations]
- [Performance targets]
- [Testing coverage]

TIMELINE:
- Start: Immediate
- Target: [X hours]
- Deliver: All code files, tests, documentation
- Ready for: [Integration/Deployment/Testing]

GITHUB:
- Repo: https://github.com/rdreilly58/onigashima
- Branch: main
- Commit message: "Week [X]: [Feature] - complete implementation"

VERIFICATION CHECKLIST (after build):
- [ ] All [N] files created
- [ ] No empty stub files
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Code committed to git
- [ ] GitHub push successful
- [ ] File count matches specification

GO!
```

## Monitoring Commands (Quick Reference)

```bash
# Check file creation in real-time
ls -lht ~/.openclaw/workspace/onigashima/ | head -20

# Count files by type
find ~/.openclaw/workspace/onigashima -name "*.js" | wc -l
find ~/.openclaw/workspace/onigashima -name "*.swift" | wc -l
find ~/.openclaw/workspace/onigashima -name "*.md" | wc -l

# Check git status
cd ~/.openclaw/workspace/onigashima && git status

# View latest commit
cd ~/.openclaw/workspace/onigashima && git log -1 --oneline

# Push and verify
git push origin main -v
```

## Expected Timelines

| Task Size | Approach | Time | Success Rate |
|-----------|----------|------|--------------|
| 1-3 files (small) | Single spawn | 10-15 min | 85%+ |
| 4-8 files (medium) | Single spawn | 20-35 min | 75%+ |
| 16+ files (large) | Incremental batches | 60-80 min total | 95%+ |

**Incremental Batch Timeline Example (Week 4):**
- Batch 1 (Backend): 15 min
- Batch 2 (macOS): 20 min
- Batch 3 (iPhone): 25 min
- Batch 4 (Tests + Docs): 15 min
- Total: 75 minutes ✅ (vs. 45-60 min single spawn = higher reliability)

## When to Intervene

- **After 2 minutes with no file activity:** Check status, report to Bob
- **After 5 minutes with minimal progress:** Consider kill + respawn with smaller batch
- **After 10 minutes with incomplete/stub files:** Kill, diagnose, improve spec, respawn
- **Files exist but are empty stubs:** Immediate retry or switch to GPT-4 fallback

## Critical Lesson: File Creation Requirement

**IMPORTANT:** Claude Code subagents may:
1. Claim "completion" without actually creating files (Week 4 Attempt #1)
2. Create stub files with just pseudocode comments (Week 4 Attempt #2)

This happened in Week 4:
- **Attempt #1:** Reported "completed the implementation" → ❌ 0 files created
- **Attempt #2:** Created 15 stubs (17 lines each) → ❌ No production code
- **Solution:** Direct code generation successfully created all 16 files

### Prevention Strategies (MANDATORY)

1. **Use explicit file paths** in the spec:
   - ✅ DO: "Create `/Users/rreilly/.openclaw/workspace/onigashima/websocket-handler.js` (264 lines)"
   - ❌ DON'T: "Create websocket-handler.js" (may not find right directory)

2. **Require verification shell commands** in the task (NON-NEGOTIABLE):
   - "After each file creation, run: `wc -l /path/to/file`"
   - "After all files, run: `ls -lh /Users/rreilly/.openclaw/workspace/onigashima/ | grep -E '(websocket|message|Chat|Messages)'`"
   - "After commit, run: `git log --oneline -1` (must show actual commit hash and message)"
   - "After push, run: `git push origin main --verbose` (must show 'Updating XXX...XXX')"

3. **Don't accept summary-only responses (RED FLAG):**
   - ❌ Summary: "I've built ChatView.swift, WebSocketManager.swift, Message.swift..."
   - ✅ Actual proof: File listing with line counts + git commit output
   - **Exception:** Only accept if followed by actual shell output showing files created

4. **Always check git status after claimed completion:**
   - `cd ~/.openclaw/workspace/onigashima && git status`
   - ✅ Should show: "nothing to commit, working tree clean" (files committed)
   - ✅ Should show: "Changes to be committed" (if using git add but not commit)
   - ❌ Should NOT show: "On branch main" with no changes (means nothing happened)

5. **Verify file content (minimum 50 lines per file):**
   - `wc -l /path/to/file` must show > 50 lines
   - `head -20 /path/to/file` should show actual code, not comments
   - Check for stub patterns: "// TODO", "// placeholder", "// not implemented"

---

## Locked-In Process for All Future Claude Code Builds

### For Small/Medium Builds (1-8 files)

1. **Detailed Spec** (50+ lines, explicit file paths, verification commands)
2. **Spawn Subagent** with `model="claude-opus-4-0"` (Claude Code default)
3. **Minute 1 Check:** Has it started? Any file activity?
4. **Minute 2-5:** Monitor file creation + line counts
5. **Minute 5-8:** Check git status + commit message
6. **Minute 8-10:** Verify GitHub push successful
7. **Report to Bob:** Success summary with file list + line counts
8. **Fallback:** If failed, retry with `model="gpt-4-turbo"`

### For Large Builds (16+ files)

**Use Incremental Batch Approach:**

1. **Batch 1:** Spawn Claude Code with first 4 files
   - Monitor, verify, commit
   - Report progress to Bob
   
2. **Batch 2:** Spawn Claude Code with next 4 files
   - Same monitoring/verify/commit process
   
3. **Batch 3 & 4:** Continue batch pattern
   - Total time: 60-80 min (vs. 45-60 min risky single spawn)
   - Success rate: 95%+ (vs. 50% for single large spawn)

### Post-Build Verification Checklist

- [ ] All expected files created (ls -lh)
- [ ] No empty or stub files (wc -l > 50 for each)
- [ ] Git status shows changes committed
- [ ] git log -1 shows actual commit
- [ ] git push origin main succeeds
- [ ] GitHub.com reflects new commit
- [ ] Spot-check 2-3 large files for real code (not stubs)

### Model Selection Strategy

| Scenario | Primary | Fallback | Notes |
|----------|---------|----------|-------|
| First attempt | claude-opus-4-0 | gpt-4-turbo | Claude Code is default |
| Claude Code failed once | Try again with better spec | gpt-4-turbo | Sometimes clearer spec helps |
| Claude Code failed twice | gpt-4-turbo | Direct generation | Switch to GPT-4 |
| GPT-4 failed | Direct generation | Manual (Bob reviews) | Last resort |

---

## Summary: Standards Locked In

✅ **Claude Code is the default for all coding tasks**
✅ **GPT-4 is the fallback if Claude Code struggles**
✅ **Large tasks use incremental batching (4 files per spawn)**
✅ **Verification is mandatory (shell output required, not summaries)**
✅ **No empty stub files accepted (minimum 50 lines per file)**

**This is now the standard process for all Claude Code builds.** 🍑
