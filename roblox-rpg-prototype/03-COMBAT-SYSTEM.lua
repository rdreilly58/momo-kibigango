-- ============================================================================
-- COMBAT SYSTEM MODULE
-- ============================================================================
-- Location: ServerScriptService > CombatSystem (ModuleScript)
-- Purpose: Handle combat mechanics, damage, abilities, dodge
-- ============================================================================

local CombatSystem = {}

-- Combat constants
local ATTACK_COOLDOWN = 1.0
local DODGE_COOLDOWN = 2.0
local DODGE_DURATION = 0.5
local BASE_CRIT_CHANCE = 0.1 -- 10%

-- ============================================================================
-- Damage System
-- ============================================================================

function CombatSystem:calculateDamage(attacker, defender, baseDamage)
	-- Base damage with attack stat scaling
	local damage = baseDamage * (attacker.attackDamage / 15) -- 15 is base damage
	
	-- Critical hit calculation
	if math.random() < BASE_CRIT_CHANCE then
		damage = damage * 1.5
		print("[Combat] CRITICAL HIT! Damage: " .. tostring(math.floor(damage)))
		return damage, true -- true = critical
	end
	
	-- Armor reduction
	local armorReduction = defender.armor * 2
	damage = damage * (1 - (armorReduction / 100))
	
	-- Minimum damage
	damage = math.max(1, damage)
	
	return damage, false
end

function CombatSystem:damageTarget(player, attackerData, targetNPC, baseDamage)
	-- Check attack cooldown
	local currentTime = tick()
	if currentTime - attackerData.lastAttackTime < ATTACK_COOLDOWN then
		return false
	end
	
	attackerData.lastAttackTime = currentTime
	
	-- Calculate damage
	local damage, isCrit = self:calculateDamage(attackerData, {armor = 0}, baseDamage)
	
	-- Apply damage to NPC
	local humanoid = targetNPC:FindFirstChild("Humanoid")
	if humanoid then
		humanoid:TakeDamage(damage)
		
		-- Grant experience to player on kill
		if humanoid.Health <= 0 then
			self:grantExperienceForKill(attackerData, targetNPC)
		end
	end
	
	print("[Combat] " .. attackerData.name .. " attacked " .. targetNPC.Name .. " for " .. tostring(math.floor(damage)) .. " damage")
	
	return true
end

function CombatSystem:castAbility(playerData, targetId, targetType)
	-- Get available abilities
	local abilities = {
		{id = 1, name = "Fireball", manaCost = 20, damage = 30},
		{id = 2, name = "Heal", manaCost = 25, heal = 40},
		{id = 3, name = "Power Strike", manaCost = 15, damage = 40},
	}
	
	-- Find the ability
	local ability = nil
	for _, ab in ipairs(abilities) do
		if ab.id == targetId then
			ability = ab
			break
		end
	end
	
	if not ability then return false end
	
	-- Check mana
	if playerData.mana < ability.manaCost then
		print("[Combat] Not enough mana for " .. ability.name)
		return false
	end
	
	-- Consume mana
	playerData.mana = playerData.mana - ability.manaCost
	
	-- Execute ability
	if ability.heal then
		playerData.health = math.min(playerData.health + ability.heal, playerData.maxHealth)
		print("[Combat] " .. playerData.name .. " cast Heal for " .. ability.heal .. " HP")
	elseif ability.damage then
		-- Would target an NPC or player here
		print("[Combat] " .. playerData.name .. " cast " .. ability.name .. " for " .. ability.damage .. " damage")
	end
	
	return true
end

function CombatSystem:performDodge(playerData)
	-- Check dodge cooldown
	local currentTime = tick()
	if currentTime - playerData.lastDodgeTime < DODGE_COOLDOWN then
		return false
	end
	
	playerData.lastDodgeTime = currentTime
	playerData.isDodging = true
	
	print("[Combat] " .. playerData.name .. " dodged!")
	
	-- Cancel dodge after duration
	wait(DODGE_DURATION)
	playerData.isDodging = false
	
	return true
end

-- ============================================================================
-- Experience & Rewards
-- ============================================================================

function CombatSystem:grantExperienceForKill(playerData, npcTarget)
	-- Base experience from NPC level/difficulty
	local baseExp = 50
	
	-- Find NPC level if available
	local npcLevel = 1
	local levelTag = npcTarget:FindFirstChild("Level")
	if levelTag then
		npcLevel = levelTag.Value
	end
	
	-- Scale experience based on level difference
	local expGain = baseExp * npcLevel
	
	-- Bonus for overkill
	if playerData.level > npcLevel then
		expGain = expGain * 0.5 -- Reduced bonus for higher level players
	elseif playerData.level < npcLevel then
		expGain = expGain * 1.5 -- Bonus for defeating higher level enemies
	end
	
	playerData.experience = playerData.experience + expGain
	
	-- Gold reward
	local goldReward = baseExp / 2
	playerData.gold = playerData.gold + goldReward
	
	print("[Combat] " .. playerData.name .. " gained " .. tostring(math.floor(expGain)) .. " XP and " .. tostring(math.floor(goldReward)) .. " gold")
	
	return expGain
end

-- ============================================================================
-- Combat Utilities
-- ============================================================================

function CombatSystem:isInCombat(playerData, targetDistance)
	-- Check if player is within combat range of enemies
	targetDistance = targetDistance or 50
	
	if not playerData.character then return false end
	
	local humanoidRootPart = playerData.character:FindFirstChild("HumanoidRootPart")
	if not humanoidRootPart then return false end
	
	-- This would check for nearby enemies in real implementation
	return false
end

function CombatSystem:applyStatusEffect(target, effectType, duration)
	-- Status effects: "poison", "stun", "burn", "slow"
	
	local effect = {
		type = effectType,
		duration = duration,
		startTime = tick()
	}
	
	if not target.statusEffects then
		target.statusEffects = {}
	end
	
	table.insert(target.statusEffects, effect)
	print("[Combat] Applied " .. effectType .. " to target for " .. duration .. " seconds")
	
	return effect
end

function CombatSystem:updateStatusEffects(playerData, deltaTime)
	if not playerData.statusEffects then
		playerData.statusEffects = {}
		return
	end
	
	-- Remove expired effects
	for i = #playerData.statusEffects, 1, -1 do
		local effect = playerData.statusEffects[i]
		if tick() - effect.startTime > effect.duration then
			table.remove(playerData.statusEffects, i)
		end
	end
	
	-- Apply effect damage/penalties
	for _, effect in ipairs(playerData.statusEffects) do
		if effect.type == "poison" then
			-- Damage over time
			if tick() % 1 < deltaTime then
				playerData.health = math.max(0, playerData.health - 2)
			end
		elseif effect.type == "burn" then
			-- More damage
			if tick() % 0.5 < deltaTime then
				playerData.health = math.max(0, playerData.health - 3)
			end
		end
	end
end

return CombatSystem
