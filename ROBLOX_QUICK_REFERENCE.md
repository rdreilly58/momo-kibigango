# 🍑 Roblox Game Automation — Quick Reference

## One Command: Full Automation

```bash
bash ~/.openclaw/workspace/scripts/roblox-full-automation.sh \
  https://github.com/rdreilly58/momotaro-roblox-rpg
```

**What it does in 45 seconds:**
1. Clone/update from GitHub
2. Create blank game file
3. Launch Roblox Studio
4. Load game
5. Wait 15 seconds for startup
6. Capture Studio output
7. Analyze for errors
8. Generate test report

---

## View Results

```bash
# Full test report
cat ~/.games/momotaro-roblox-rpg/.test_results.txt

# Just errors/warnings
grep -i error ~/.games/momotaro-roblox-rpg/.test_results.txt

# Raw output (if needed)
cat ~/.games/momotaro-roblox-rpg/.output_capture.txt
```

---

## Step-by-Step Manual Control

### 1. Clone from GitHub
```bash
bash ~/.openclaw/workspace/skills/roblox-loader/scripts/load-game-from-github.sh \
  https://github.com/rdreilly58/momotaro-roblox-rpg
```

### 2. Launch & Capture (15s wait)
```bash
bash ~/.openclaw/workspace/scripts/roblox-game-startup-test.sh \
  ~/.games/momotaro-roblox-rpg
```

---

## Output Files

| File | Purpose |
|------|---------|
| `.test_results.txt` | **Primary** — Test summary with errors/warnings |
| `.output_capture.txt` | Raw Studio console output |
| `.startup.log` | Studio launch sequence details |

---

## Integration Examples

### GitHub Actions (Auto-test on commit)
```yaml
- name: Test Roblox Game
  run: |
    bash ~/.openclaw/workspace/scripts/roblox-full-automation.sh \
      ${{ github.repository }}
```

### Claude Code Agent
```bash
# Load game, test, analyze, report
REPO="https://github.com/rdreilly58/momotaro-roblox-rpg"
bash ~/.openclaw/workspace/scripts/roblox-full-automation.sh "$REPO"
cat ~/.games/$(basename $REPO .git)/.test_results.txt
```

### Development Loop
```bash
# 1. Make changes
vi ~/.games/momotaro-roblox-rpg/scripts/MainGameScript.lua

# 2. Commit
cd ~/.games/momotaro-roblox-rpg && git commit -am "Fix: bug" && git push

# 3. Test automatically
bash ~/.openclaw/workspace/scripts/roblox-full-automation.sh \
  https://github.com/rdreilly58/momotaro-roblox-rpg

# 4. Check results
cat ~/.games/momotaro-roblox-rpg/.test_results.txt
```

---

## Capabilities

✅ **Programmatic Loading**  
Load any game from GitHub without manual navigation

✅ **Auto-Launch**  
Studio opens with game loaded automatically

✅ **15-Second Capture**  
Wait for startup, then capture output window

✅ **Error Analysis**  
Count errors, extract details, determine PASS/FAIL

✅ **Zero Manual Steps**  
Fully automated — no UI interaction needed

---

## Troubleshooting

### Studio won't launch?
```bash
# Check installation
ls /Applications/RobloxStudio.app/Contents/MacOS/RobloxStudio

# Try manually
/Applications/RobloxStudio.app/Contents/MacOS/RobloxStudio
```

### No output captured?
```bash
# Check logs directly
tail -100 ~/Library/Logs/Roblox/*last.log
```

### Need more details?
```bash
# View full test report (tail shows last 200 lines)
cat ~/.games/momotaro-roblox-rpg/.test_results.txt
```

---

## Files Involved

| Script | Purpose |
|--------|---------|
| `roblox-full-automation.sh` | Orchestrates everything (GitHub → Studio → Test) |
| `roblox-game-startup-test.sh` | Launch, wait 15s, capture, analyze |
| `load-game-from-github.sh` | Clone/update from GitHub |

---

## Documentation

- **Full Guide:** `~/.openclaw/workspace/skills/roblox-loader/AUTOMATION_GUIDE.md`
- **Integration:** `~/.openclaw/workspace/docs/ROBLOX_AUTOMATION_INTEGRATION.md`
- **Skill Ref:** `~/.openclaw/workspace/skills/roblox-loader/SKILL.md`

---

## Example Output

```
═══════════════════════════════════════════════════════════════
🎮 ROBLOX GAME STARTUP TEST & DEBUG
═══════════════════════════════════════════════════════════════

1️⃣  Creating game file template...
2️⃣  Creating script loader...
3️⃣  Generating test automation plugin...
4️⃣  Preparing environment...
5️⃣  Launching Roblox Studio...
6️⃣  Waiting 15 seconds for game initialization...
   ⏳ 0 seconds remaining...
7️⃣  Capturing Studio output window...
8️⃣  Analyzing startup output for errors...

📊 Test Results Summary:
   Errors: 0
   Warnings: 3
   Status: ✅ PASS

═══════════════════════════════════════════════════════════════
Full results saved to: ~/.games/momotaro-roblox-rpg/.test_results.txt
```

---

**Ready to automate? Run the one-command version above!** 🍑
