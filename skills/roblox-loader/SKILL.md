---
name: roblox-loader
description: Load and test Roblox games from GitHub repositories programmatically. Clone, validate, open in Studio, run tests, and debug errors automatically.
---

# Roblox Game Loader

Programmatically load Roblox games from GitHub, validate them, run them in Studio, and debug errors.

## Features

- **GitHub Integration**: Clone repos and extract game structure
- **Lua Validation**: Syntax check all scripts before loading
- **Studio Automation**: Open game in Roblox Studio
- **Automated Testing**: Run game and capture output
- **Error Detection**: Identify and log errors from Studio console
- **Fix Suggestions**: Provide debugging hints for common issues

## Installation

```bash
# One-time setup
bash {baseDir}/install.sh
```

## Quick Start

### Full Automation (GitHub → Studio → Test → Capture Output)

```bash
# Load game from GitHub, launch Studio, wait 15s, capture output
bash ~/.openclaw/workspace/scripts/roblox-full-automation.sh \
  https://github.com/rdreilly58/momotaro-roblox-rpg
```

This will:
1. Clone/update from GitHub
2. Create blank .rbxl game file
3. Launch Roblox Studio with game loaded
4. Wait 15 seconds for startup
5. Capture Studio output window
6. Parse for errors/warnings
7. Report test results

### Manual Load & Test

```bash
# Load and test a game from GitHub (step by step)
bash {baseDir}/scripts/load-github-game.sh \
  --repo https://github.com/rdreilly58/momotaro-roblox-rpg.git \
  --game-name "Momotaro RPG" \
  --open-studio
```

## Usage

### Full Automation Pipeline (Recommended)

```bash
bash ~/.openclaw/workspace/scripts/roblox-full-automation.sh <github-url> [auto-start]
```

**Example:**
```bash
bash ~/.openclaw/workspace/scripts/roblox-full-automation.sh \
  https://github.com/rdreilly58/momotaro-roblox-rpg true
```

**What it does:**
1. Clones/updates game from GitHub
2. Creates proper .rbxl game file
3. Launches Studio with game loaded
4. Waits 15 seconds for initialization
5. Captures Studio output window
6. Parses for errors and warnings
7. Generates test report

**Output files created:**
- `.test_results.txt` — Summary of startup test with errors/warnings
- `.output_capture.txt` — Raw Studio output log
- `.startup.log` — Launch sequence log

### Load from GitHub

```bash
bash {baseDir}/scripts/load-github-game.sh \
  --repo <github-url> \
  --branch main \
  --game-name "Game Name" \
  --output-dir ~/.games/my-game \
  --validate-only \
  --open-studio
```

**Options:**
- `--repo` (required) — GitHub repository URL
- `--branch` (optional) — Git branch, default: main
- `--game-name` (optional) — Display name for the game
- `--output-dir` (optional) — Where to clone, default: ~/.games/repo-name
- `--validate-only` — Check syntax without opening Studio
- `--open-studio` — Automatically open game in Roblox Studio

### Validate Lua Scripts

```bash
bash {baseDir}/scripts/validate-lua.sh /path/to/scripts/
```

Checks for:
- Syntax errors
- Missing dependencies
- Common Roblox mistakes

### Open in Studio

```bash
bash {baseDir}/scripts/open-studio.sh /path/to/game/
```

### Run Tests & Capture Output (Automated)

```bash
bash ~/.openclaw/workspace/scripts/roblox-game-startup-test.sh /path/to/game/
```

**What it does:**
1. Creates blank game file (.rbxl)
2. Injects all scripts from scripts/ directory
3. Launches Studio
4. Waits 15 seconds for initialization
5. Captures output window
6. Parses for errors/warnings
7. Generates results file

**Captured data:**
- Console output from Studio
- Error/exception messages
- Warning messages
- Startup sequence logs

**Output:**
- `~/.studio_output.log` — Raw output from Studio
- `.test_results.txt` — Parsed results with error count
- Returns exit code 0 (success) or 1 (errors found)

## Example Workflow

```bash
# 1. Load game
bash roblox-loader/scripts/load-github-game.sh \
  --repo https://github.com/rdreilly58/momotaro-roblox-rpg.git \
  --game-name "Momotaro RPG" \
  --output-dir ~/.games/momotaro-rpg

# 2. Validate scripts
bash roblox-loader/scripts/validate-lua.sh ~/.games/momotaro-rpg/scripts/

# 3. Open in Studio
bash roblox-loader/scripts/open-studio.sh ~/.games/momotaro-rpg/

# 4. Run tests and capture errors
bash roblox-loader/scripts/run-tests.sh ~/.games/momotaro-rpg/
```

## Supported Game Structures

This skill works with Roblox games stored in GitHub with:
- **scripts/** directory with Lua files
- **models/** or **assets/** directories (optional)
- Clear entry points (MainGameScript, or similar)

## Error Handling

Common errors and fixes:

### "Script not found"
- Check if repo has scripts/ directory
- Verify file extensions (.lua)

### "Syntax error in script X"
- Run validate-lua.sh to identify line
- Check Lua 5.1 compatibility

### "Studio won't open game"
- Ensure Roblox Studio is installed
- Check file permissions
- Verify game structure

## Troubleshooting

```bash
# Check if Studio is installed
which RobloxStudio

# View detailed logs
cat ~/.openclaw/logs/roblox-loader.log

# Validate game structure
bash {baseDir}/scripts/check-structure.sh /path/to/game/
```

## Requirements

- Roblox Studio (installed)
- Git CLI
- Bash 4+
- `luac` (Lua compiler, for syntax checking)

## References

- **Roblox API:** https://developer.roblox.com/
- **Game Repository:** https://github.com/rdreilly58/momotaro-roblox-rpg
