# Quick Start Guide - 5 Minute Setup

## TL;DR

1. Open Roblox Studio → New Place (Baseplate)
2. Create 3 ModuleScripts in ServerScriptService
3. Paste 5 scripts from files 01-05
4. Add LocalScript in StarterCharacterScripts
5. Press F5 → Play
6. Click enemies to attack, press Q/W/E/Space for abilities

---

## Step 1: Create Modules (2 min)

In **Explorer** → **ServerScriptService**:

```
Right-click → Insert Object → ModuleScript
```

Create these 3 modules:
- `PlayerManager`
- `CombatSystem`
- `NPCSpawner`

---

## Step 2: Paste Scripts (3 min)

### File 01-SERVER-MAIN.lua
1. **Right-click ServerScriptService** → Insert Object → Script
2. **Name it: MainGameScript**
3. **Paste entire code** from `01-SERVER-MAIN.lua`
4. **Save**

### File 02-PLAYER-MANAGER.lua
1. **Click on PlayerManager** (ModuleScript)
2. **Delete default code**
3. **Paste entire code** from `02-PLAYER-MANAGER.lua`
4. **Save**

### File 03-COMBAT-SYSTEM.lua
1. **Click on CombatSystem** (ModuleScript)
2. **Delete default code**
3. **Paste entire code** from `03-COMBAT-SYSTEM.lua`
4. **Save**

### File 04-NPC-SPAWNER.lua
1. **Click on NPCSpawner** (ModuleScript)
2. **Delete default code**
3. **Paste entire code** from `04-NPC-SPAWNER.lua`
4. **Save**

### File 05-CLIENT-GUI.lua
1. **In Explorer** → **StarterPlayer** → **StarterCharacterScripts**
2. **Right-click** → Insert Object → LocalScript
3. **Name it: ClientGUI**
4. **Paste entire code** from `05-CLIENT-GUI.lua`
5. **Save**

---

## Step 3: Adjust Spawn Location (optional)

1. **In Workspace**, find **SpawnLocation**
2. **In Properties**, set Position:
   - X: 0
   - Y: 5
   - Z: 0

---

## Step 4: Test! (30-45 min)

**Press F5** to start testing.

### What Should Happen:

✅ You spawn in center of map  
✅ HUD appears top-left (stats) and top-center (health/mana)  
✅ Enemies (Goblins, Orcs) spawn around you  
✅ Click enemies to attack  
✅ Enemies attack you back  

### Controls:

| Input | Action | Cost |
|-------|--------|------|
| **Mouse Click** | Attack nearest NPC | – |
| **Q** | Fireball ability | 20 mana |
| **W** | Heal ability | 25 mana |
| **E** | Power Strike | 15 mana |
| **Space** | Dodge (i-frames) | – |

### Expected Output Messages:

```
[RPG] Game Server initialized
[RPG] Max players: 10
[NPCSpawner] Spawned Goblin at Vector3(30, 5, 30)
[RPG] Player joined: YourName
[RPG] Character loaded for YourName
[PlayerManager] Character setup complete for YourName
[Combat] YourName attacked Goblin for 12 damage
[Combat] YourName gained 50 XP and 25 gold
[Combat] YourName leveled up to 2
```

---

## If Something Breaks:

### Scripts show RED ERROR in Output

**Check:**
1. All 3 ModuleScripts named exactly: `PlayerManager`, `CombatSystem`, `NPCSpawner`
2. Code pasted completely (no lines cut off)
3. LocalScript is in `StarterCharacterScripts`, not `StarterPlayer`

### Character doesn't spawn

**Check:**
1. MainGameScript runs (check for errors in Output)
2. SpawnLocation exists and CanCollide is unchecked
3. Look for error: `Spawn location not found`

### GUI doesn't appear

**Check:**
1. LocalScript named `ClientGUI` is in StarterCharacterScripts
2. Output shows: `[ClientGUI] HUD loaded successfully`

### Enemies don't spawn

**Check:**
1. Output shows: `[NPCSpawner] Spawned Goblin...`
2. You see Goblin/Orc models moving around
3. Check for errors in NPCSpawner code

---

## Customization (2 minutes)

### Make enemies harder:

Edit **04-NPC-SPAWNER.lua**, change `goblin` stats:

```lua
goblin = {
	health = 30,      -- ← increase to 60
	damage = 8,       -- ← increase to 15
	armor = 1,
	...
}
```

### More mana, more health:

Edit **02-PLAYER-MANAGER.lua**:

```lua
health = 100,      -- ← change to 200
maxHealth = 100,
mana = 50,         -- ← change to 100
maxMana = 50,
```

### Stronger abilities:

Edit **03-COMBAT-SYSTEM.lua**:

```lua
{id = 1, name = "Fireball", manaCost = 20, damage = 30},  -- ← change damage to 50
{id = 2, name = "Heal", manaCost = 25, heal = 40},        -- ← change heal to 60
```

---

## Files You Need

| File | Purpose | Paste Into |
|------|---------|-----------|
| **01-SERVER-MAIN.lua** | Main game loop | ServerScriptService (new Script) |
| **02-PLAYER-MANAGER.lua** | Player stats/leveling | PlayerManager ModuleScript |
| **03-COMBAT-SYSTEM.lua** | Combat mechanics | CombatSystem ModuleScript |
| **04-NPC-SPAWNER.lua** | NPC creation/AI | NPCSpawner ModuleScript |
| **05-CLIENT-GUI.lua** | HUD & input | StarterCharacterScripts LocalScript |

---

## Directory Structure (Final)

```
ServerScriptService/
├── MainGameScript (Script) ← from 01-SERVER-MAIN.lua
├── PlayerManager (ModuleScript) ← from 02-PLAYER-MANAGER.lua
├── CombatSystem (ModuleScript) ← from 03-COMBAT-SYSTEM.lua
└── NPCSpawner (ModuleScript) ← from 04-NPC-SPAWNER.lua

StarterPlayer/
└── StarterCharacterScripts/
    └── ClientGUI (LocalScript) ← from 05-CLIENT-GUI.lua

Workspace/
├── SpawnLocation (Position: 0, 5, 0)
├── Baseplate (or custom arena)
└── [NPCs spawn here at runtime]
```

---

## Success = ✅

When you see this in Output:

```
[RPG] Game Server initialized
[RPG] Max players: 10
[NPCSpawner] Spawned Goblin at ...
[RPG] Player joined: YourName
[PlayerManager] Character setup complete for YourName
[ClientGUI] HUD loaded successfully
```

**You're done! The prototype is running.** 🎉

---

## Next Steps

After 30-45 minutes of testing:

1. **Explore the map** - Find spawn zones, test pathfinding
2. **Kill 5 enemies** - Verify leveling system works
3. **Use all abilities** - Check mana costs and cooldowns
4. **Invite a friend** - Test multiplayer (edit SOUL.md with friend's user, run separate client)
5. **Read ARCHITECTURE.md** - Understand systems for customization

---

**Good luck, Bob!** 🍑🎮

Start with Step 1 and follow through. You'll have a playable RPG in ~60 minutes.
