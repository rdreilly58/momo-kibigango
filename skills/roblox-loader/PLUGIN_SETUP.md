# Roblox Test Automation Plugin Setup

This plugin enables automated game testing, error capture, and reporting directly in Roblox Studio.

## Installation

### Step 1: Locate Plugin Directory

```bash
# Copy plugin to Roblox Studio plugins folder
mkdir -p ~/AppData/Local/Roblox/Plugins  # Windows
# OR
mkdir -p ~/Library/Application\ Support/Roblox/Plugins  # macOS
```

### Step 2: Copy Plugin File

```bash
# macOS
cp ~/.openclaw/workspace/skills/roblox-loader/plugins/TestAutomation.lua \
    ~/Library/Application\ Support/Roblox/Plugins/

# Linux
cp ~/.openclaw/workspace/skills/roblox-loader/plugins/TestAutomation.lua \
    ~/.local/share/Roblox/Plugins/
```

### Step 3: Restart Roblox Studio

Close and reopen Roblox Studio. You should see a "Game Testing" toolbar with a "Run Game Tests" button.

## Usage

### Automated Test Workflow

1. **Load game into Roblox Studio:**
   ```bash
   bash ~/.openclaw/workspace/skills/roblox-loader/scripts/load-github-game.sh \
     --repo https://github.com/rdreilly58/momotaro-roblox-rpg.git \
     --open-studio
   ```

2. **In Roblox Studio:**
   - Navigate to **Plugins** menu
   - Click **"Run Game Tests"** button
   - Plugin will:
     - Validate game structure
     - Execute all scripts
     - Capture output and errors
     - Generate test report

3. **View Results:**
   - Output printed in Studio console
   - Error summary with severity levels
   - Full test report with timestamp

### What the Plugin Tests

1. **Structure Validation**
   - Required scripts present (MainGameScript, NPCSpawner, CombatSystem, PlayerManager)
   - Correct folder organization
   - Asset availability

2. **Script Execution**
   - Each script loads without syntax errors
   - Initialization functions execute
   - No runtime crashes

3. **Gameplay Mechanics**
   - NPC spawning works
   - Combat system initializes
   - Player management functional

4. **Output Capture**
   - All print() statements captured
   - Error messages logged
   - Warnings recorded

### Test Configuration

Edit `TestAutomation.lua` to customize:

```lua
local TEST_CONFIG = {
    timeout = 120,              -- Test timeout in seconds
    captureOutput = true,       -- Capture print statements
    stopOnFirstError = false,   -- Stop on first error vs. continue
    autoFixErrors = true,       -- Attempt automatic fixes
}
```

## Troubleshooting

### Plugin doesn't appear in Studio

1. Check plugin file location:
   ```bash
   # macOS
   ls -la ~/Library/Application\ Support/Roblox/Plugins/TestAutomation.lua
   ```

2. Restart Studio (fully close and reopen)

3. Check Studio Output window for error messages

### Tests fail with "Game not loaded"

- Use the roblox-loader skill to load the game FIRST
- Ensure all scripts are imported into ServerScriptService
- Check that script names match expected names

### "Missing script" errors

The game may need manual script setup:
1. In Studio, drag scripts from `scripts/` folder to ServerScriptService
2. Or use the automated import tool (coming soon)

## Advanced Usage

### Run Tests Programmatically

```lua
-- In a script or command bar
local TestAutomation = require(game:GetService("ServerScriptService"):FindFirstChild("TestAutomation"))
local report = TestAutomation.runTests()
print("Tests completed:", report.testsPassed)
```

### Export Test Results

Plugin automatically logs to:
- **Studio Output Window** — Real-time test progress
- **Server Output** — Full test report
- **Console** — Error messages

Save output manually:
1. Select all text in Output window
2. Copy and paste to file
3. Save as `TEST_RESULTS.txt`

## Future Enhancements

- [ ] Automated script import into ServerScriptService
- [ ] Performance profiling during tests
- [ ] Memory usage tracking
- [ ] Screenshot capture on errors
- [ ] HTML report generation
- [ ] CI/CD integration hooks

## Questions?

Check:
- Plugin source: `~/.openclaw/workspace/skills/roblox-loader/plugins/TestAutomation.lua`
- Skill docs: `~/.openclaw/workspace/skills/roblox-loader/SKILL.md`
- Game repo: https://github.com/rdreilly58/momotaro-roblox-rpg
