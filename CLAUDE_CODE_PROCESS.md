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

```
sessions_spawn(
  runtime="subagent",
  task="[DETAILED 50+ LINE SPECIFICATION]",
  model="claude-opus-4-0"  # or gpt-5 for fallback
)
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

- **4-6 files (small feature):** 15-20 minutes
- **8-12 files (medium feature):** 25-40 minutes
- **16+ files (large feature like Week 4):** 45-90 minutes

## When to Intervene

- **After 2 minutes with no file activity:** Check status
- **After 5 minutes with no progress:** Consider kill + respawn
- **After 10 minutes with incomplete files:** Kill, diagnose, improve spec, respawn

---

## Locked-In Process for All Future Claude Code Builds

1. **Detailed Spec** (50+ lines)
2. **Spawn Subagent** with monitoring enabled
3. **Minute 1 Check:** Has it started?
4. **Minute 2-3:** Backend progress?
5. **Minute 4-5:** Frontend progress?
6. **Minute 6-7:** Tests + docs?
7. **Minute 8-10:** Done?
8. **GitHub Commit:** All files
9. **GitHub Push:** Verify on github.com
10. **Report to Bob:** Success summary

---

**This is now the standard process for all Claude Code builds.** 🍑
