-- ============================================================================
-- PLAYER MANAGER MODULE
-- ============================================================================
-- Location: ServerScriptService > PlayerManager (ModuleScript)
-- Purpose: Handle player data, character setup, stats management
-- ============================================================================

local PlayerManager = {}

-- Player data template
local function createPlayerDataTemplate(player)
	return {
		userId = player.UserId,
		name = player.Name,
		character = nil,
		position = Vector3.new(0, 0, 0),
		
		-- Stats
		health = 100,
		maxHealth = 100,
		mana = 50,
		maxMana = 50,
		
		-- Progression
		level = 1,
		experience = 0,
		experienceToLevelUp = 100,
		
		-- Combat
		armor = 5,
		magicResist = 5,
		attackDamage = 15,
		attackSpeed = 1.0,
		
		-- Inventory
		inventory = {},
		gold = 0,
		
		-- Flags
		isAlive = true,
		isDodging = false,
		lastAttackTime = 0,
		lastDodgeTime = 0
	}
end

-- ============================================================================
-- Create Player Data
-- ============================================================================

function PlayerManager:createPlayerData(player)
	return createPlayerDataTemplate(player)
end

-- ============================================================================
-- Setup Character (Humanoid, Animations, etc)
-- ============================================================================

function PlayerManager:setupCharacter(character, playerData, spawnLocation)
	playerData.character = character
	playerData.isAlive = true
	playerData.health = playerData.maxHealth
	playerData.mana = playerData.maxMana
	
	-- Move to spawn location
	local humanoidRootPart = character:FindFirstChild("HumanoidRootPart")
	if humanoidRootPart then
		humanoidRootPart.CFrame = CFrame.new(spawnLocation + Vector3.new(math.random(-10, 10), 0, math.random(-10, 10)))
	end
	
	-- Setup humanoid
	local humanoid = character:FindFirstChild("Humanoid")
	if humanoid then
		humanoid.MaxHealth = playerData.maxHealth
		humanoid.Health = playerData.health
		
		-- Sync health
		humanoid.HealthChanged:Connect(function(health)
			playerData.health = math.max(0, health)
			if health <= 0 then
				playerData.isAlive = false
			end
		end)
	end
	
	-- Add player tag for NPC targeting
	local playerTag = Instance.new("StringValue")
	playerTag.Name = "PlayerTag"
	playerTag.Value = playerData.name
	playerTag.Parent = character
	
	-- Add team color for visual distinction
	local colorTag = Instance.new("Color3Value")
	colorTag.Name = "TeamColor"
	colorTag.Value = Color3.fromRGB(math.random(100, 255), math.random(100, 255), math.random(100, 255))
	colorTag.Parent = character
	
	print("[PlayerManager] Character setup complete for " .. playerData.name)
end

-- ============================================================================
-- Stat Management
-- ============================================================================

function PlayerManager:gainExperience(playerData, amount)
	playerData.experience = playerData.experience + amount
	
	-- Check for level up
	while playerData.experience >= playerData.experienceToLevelUp do
		self:levelUp(playerData)
	end
end

function PlayerManager:levelUp(playerData)
	playerData.level = playerData.level + 1
	playerData.experience = playerData.experience - playerData.experienceToLevelUp
	playerData.experienceToLevelUp = playerData.experienceToLevelUp + 50 -- Scaling
	
	-- Stat increases on level up
	playerData.maxHealth = playerData.maxHealth + 20
	playerData.maxMana = playerData.maxMana + 10
	playerData.health = playerData.maxHealth
	playerData.mana = playerData.maxMana
	playerData.attackDamage = playerData.attackDamage + 5
	playerData.armor = playerData.armor + 1
	
	print("[PlayerManager] " .. playerData.name .. " leveled up to " .. playerData.level)
	
	return true
end

function PlayerManager:takeDamage(playerData, damageAmount, damageType)
	-- damageType: "physical", "magic"
	local resistance = 0
	
	if damageType == "physical" then
		resistance = playerData.armor * 2 -- 2% reduction per armor point
	elseif damageType == "magic" then
		resistance = playerData.magicResist * 2
	end
	
	local finalDamage = damageAmount * (1 - (resistance / 100))
	finalDamage = math.max(1, finalDamage) -- Minimum 1 damage
	
	playerData.health = math.max(0, playerData.health - finalDamage)
	
	-- Update humanoid
	if playerData.character then
		local humanoid = playerData.character:FindFirstChild("Humanoid")
		if humanoid then
			humanoid.Health = playerData.health
		end
	end
	
	return finalDamage
end

function PlayerManager:restoreMana(playerData, amount)
	playerData.mana = math.min(playerData.mana + amount, playerData.maxMana)
	return playerData.mana
end

function PlayerManager:addInventoryItem(playerData, itemName, quantity)
	if playerData.inventory[itemName] then
		playerData.inventory[itemName] = playerData.inventory[itemName] + quantity
	else
		playerData.inventory[itemName] = quantity
	end
end

function PlayerManager:removeInventoryItem(playerData, itemName, quantity)
	if playerData.inventory[itemName] and playerData.inventory[itemName] >= quantity then
		playerData.inventory[itemName] = playerData.inventory[itemName] - quantity
		return true
	end
	return false
end

function PlayerManager:addGold(playerData, amount)
	playerData.gold = playerData.gold + amount
end

-- ============================================================================
-- Ability Management
-- ============================================================================

function PlayerManager:getAbilities(playerData)
	-- Return available abilities based on level
	local abilities = {
		{id = 1, name = "Fireball", manaCost = 20, cooldown = 2, damage = 30},
		{id = 2, name = "Heal", manaCost = 25, cooldown = 3, heal = 40},
		{id = 3, name = "Power Strike", manaCost = 15, cooldown = 1.5, damage = 40}
	}
	
	-- Filter by level requirement
	if playerData.level >= 2 then
		table.insert(abilities, {id = 4, name = "Meteor Storm", manaCost = 50, cooldown = 5, damage = 60})
	end
	
	return abilities
end

return PlayerManager
