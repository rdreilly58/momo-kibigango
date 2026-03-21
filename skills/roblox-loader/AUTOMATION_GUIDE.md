# Roblox Game Automation Guide

## Overview

This skill now provides **fully automated** game loading, launching, and testing without manual intervention.

Two key capabilities:

### 1. **GitHub → Loaded Game** (Programmatic Loading)
Load any Roblox game directly from a GitHub repository and launch it in Studio.

### 2. **Auto-Launch + 15s Startup + Output Capture** (Automated Testing)
Launch the game, wait 15 seconds, capture the Studio output window, and analyze for errors.

---

## Quick Start: Full Automation

The simplest way to automate everything:

```bash
bash ~/.openclaw/workspace/scripts/roblox-full-automation.sh \
  https://github.com/rdreilly58/momotaro-roblox-rpg
```

This runs the complete pipeline:
1. ✅ Clone/update from GitHub
2. ✅ Create blank .rbxl game file
3. ✅ Launch Roblox Studio
4. ✅ Load game
5. ✅ Wait 15 seconds for startup
6. ✅ Capture Studio output window
7. ✅ Parse for errors/warnings
8. ✅ Generate test report

---

## Step-by-Step: Manual Control

If you need more control, run each step separately:

### Step 1: Load from GitHub

```bash
bash ~/.openclaw/workspace/skills/roblox-loader/scripts/load-game-from-github.sh \
  https://github.com/rdreilly58/momotaro-roblox-rpg
```

**Output:**
```
📥 Cloning repository...
📁 GitHub repository loaded to ~/.games/momotaro-roblox-rpg
📋 Scripts found:
   📄 MainGameScript.lua
   📄 PlayerManager.lua
   📄 CombatSystem.lua
   ...
```

### Step 2: Auto-Launch & Capture Output

```bash
bash ~/.openclaw/workspace/scripts/roblox-game-startup-test.sh \
  ~/.games/momotaro-roblox-rpg
```

**What happens:**
- Roblox Studio launches with the game
- Waits 15 seconds for initialization
- Captures the output window
- Parses for errors
- Saves results to `.test_results.txt`

**Output:**
```
🎮 ROBLOX GAME STARTUP TEST & DEBUG

1️⃣  Creating game file template...
   ✅ Game file created
2️⃣  Creating script loader...
   ✅ Loader script ready
3️⃣  Generating test automation plugin...
   ✅ Plugin installed
4️⃣  Preparing environment...
   ✅ Environment cleared
5️⃣  Launching Roblox Studio...
   Studio PID: 12345
6️⃣  Waiting 15 seconds for game initialization...
   ⏳ 0 seconds remaining...
7️⃣  Capturing Studio output window...
   ✅ Output captured
8️⃣  Analyzing startup output for errors...

📊 Test Results Summary:
   Errors: 0
   Warnings: 3
   Status: ✅ PASS
```

---

## Output Files

After running the automation, check these files:

### `.test_results.txt`
Complete test results with summary and full output log.

```bash
cat ~/.games/momotaro-roblox-rpg/.test_results.txt
```

**Contains:**
- Test timestamp
- Error count / Warning count
- Status (PASS/FAIL)
- Last 50 lines of startup log
- Full output from Studio

### `.output_capture.txt`
Raw Studio output (all messages, errors, warnings).

```bash
cat ~/.games/momotaro-roblox-rpg/.output_capture.txt | grep -i error
```

### `.startup.log`
Complete launch sequence details.

---

## Error Analysis

The automation script automatically:
1. **Captures** Studio output
2. **Counts** errors and warnings
3. **Extracts** error messages
4. **Reports** status (PASS/FAIL)

Example output from results file:

```
SUMMARY:
--------
Errors Found: 2
Warnings Found: 5
Status: ❌ FAIL

⚠️  ERRORS DETECTED:
   [ERROR] Script "PlayerManager" failed to initialize
   [EXCEPTION] Attempt to index nil with 'Connect'
```

---

## Integration with Claude Code / Agents

You can use this automation in agent workflows:

```bash
# From Claude Code or any agent:
bash ~/.openclaw/workspace/scripts/roblox-full-automation.sh \
  $GITHUB_URL && \
cat ~/.games/$(basename $GITHUB_URL .git)/.test_results.txt
```

Then parse the results file to determine next steps:
- If errors → Spawn debugging session
- If pass → Deploy or continue testing
- If warnings → Log for review

---

## Workflow: Development Loop

### Typical developer workflow:

```bash
# 1. Make changes to game code
vi ~/.games/momotaro-roblox-rpg/scripts/MainGameScript.lua

# 2. Commit changes
cd ~/.games/momotaro-roblox-rpg
git add .
git commit -m "Fix: player respawn logic"
git push origin main

# 3. Test the updated game automatically
bash ~/.openclaw/workspace/scripts/roblox-full-automation.sh \
  https://github.com/rdreilly58/momotaro-roblox-rpg

# 4. Review results
cat ~/.games/momotaro-roblox-rpg/.test_results.txt

# 5. If errors, debug and repeat
```

---

## Automation Features Checklist

- ✅ **GitHub Integration**
  - Clone repository
  - Pull latest changes
  - Extract game structure

- ✅ **Programmatic Game Loading**
  - Create blank .rbxl file
  - Inject scripts automatically
  - Launch Studio with game loaded

- ✅ **15-Second Startup Wait**
  - Launch Studio
  - Monitor initialization
  - Auto-capture at 15s mark

- ✅ **Output Capture**
  - Capture Studio output window
  - Save to text file
  - Parse for errors

- ✅ **Error Analysis**
  - Count errors and warnings
  - Extract error messages
  - Generate PASS/FAIL status

- ✅ **Results Reporting**
  - Save detailed test report
  - Include all output
  - Provide actionable feedback

---

## Advanced: Custom Plugins

The automation system supports custom test plugins.

Create a file: `~/.games/momotaro-roblox-rpg/.test_plugin.lua`

This plugin will be injected and run automatically.

Example:

```lua
-- Custom test plugin
local function runCustomTests()
    print("[CUSTOM TEST] Starting custom verification")
    
    -- Your tests here
    local workspace = game:GetService("Workspace")
    
    if workspace:FindFirstChild("Spawner") then
        print("[CUSTOM TEST] ✅ Spawner found")
    else
        print("[CUSTOM TEST] ❌ Spawner not found")
    end
    
    print("[CUSTOM TEST] Complete")
end

runCustomTests()
```

The plugin will be loaded and executed during Studio startup.

---

## Troubleshooting

### Problem: "Studio won't load game file"

Check that Roblox Studio is installed:
```bash
ls -la /Applications/RobloxStudio.app/Contents/MacOS/RobloxStudio
```

### Problem: "Scripts not found in repo"

Verify the game structure:
```bash
ls -la ~/.games/momotaro-roblox-rpg/scripts/
```

Expected:
```
scripts/
├── PlayerManager.lua
├── MainGameScript.lua
├── AnimationController.lua
├── CombatSystem.lua
├── NPCSpawner.lua
└── ClientGUI.lua
```

### Problem: "Cannot read output file"

Check that output capture was successful:
```bash
cat ~/.games/momotaro-roblox-rpg/.output_capture.txt | head -20
```

If empty, check Studio logs directly:
```bash
tail -50 ~/Library/Logs/Roblox/*last.log
```

### Problem: "All errors, no details"

Increase the detail level. The output file contains everything:
```bash
# See ALL output (including debug messages)
cat ~/.games/momotaro-roblox-rpg/.test_results.txt | tail -200
```

---

## What's Automated vs What Requires Manual Intervention

### ✅ Fully Automated
- Clone from GitHub
- Create game files
- Launch Studio
- Load game
- Wait for startup
- Capture output
- Parse errors
- Generate reports

### ⚠️ Semi-Automated (Can be extended)
- Script injection (currently uses Lua loader)
- Game testing (currently captures output only)
- Performance profiling
- Custom test cases

### 🔧 Future Enhancements
- Programmatically inject scripts into .rbxl (binary)
- Run actual test scenarios
- Performance profiling
- Memory usage tracking
- Network simulation

---

## See Also

- `SKILL.md` — Skill overview
- `PLUGIN_SETUP.md` — Plugin installation guide
- `scripts/` — Individual automation scripts
