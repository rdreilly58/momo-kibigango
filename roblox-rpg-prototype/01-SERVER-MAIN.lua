-- ============================================================================
-- ROBLOX MULTIPLAYER RPG PROTOTYPE - MAIN SERVER SCRIPT
-- ============================================================================
-- Location: ServerScriptService > MainGameScript
-- Purpose: Initialize game, handle player joins/leaves, manage global state
-- ============================================================================

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService") -- Client only, removed from server

-- Import modules (create these scripts in ServerScriptService)
local PlayerManager = require(script:WaitForChild("PlayerManager"))
local CombatSystem = require(script:WaitForChild("CombatSystem"))
local NPCSpawner = require(script:WaitForChild("NPCSpawner"))

-- Game Configuration
local SPAWN_LOCATION = Vector3.new(0, 5, 0) -- Adjust to your map
local MAX_PLAYERS = 10

-- Game State
local gameState = {
	players = {},
	npcs = {},
	isRunning = true
}

-- ============================================================================
-- INITIALIZATION
-- ============================================================================

print("[RPG] Game Server initialized")
print("[RPG] Max players: " .. MAX_PLAYERS)

-- Spawn starting NPCs
NPCSpawner:spawnEnemies(gameState, 5) -- Spawn 5 enemies at start

-- ============================================================================
-- PLAYER LIFECYCLE
-- ============================================================================

-- Handle new player joining
Players.PlayerAdded:Connect(function(player)
	print("[RPG] Player joined: " .. player.Name)
	
	-- Initialize player data
	local playerData = PlayerManager:createPlayerData(player)
	gameState.players[player.UserId] = playerData
	
	-- Wait for character to load
	local character = player.Character or player.CharacterAdded:Wait()
	print("[RPG] Character loaded for " .. player.Name)
	
	-- Setup character
	PlayerManager:setupCharacter(character, playerData, SPAWN_LOCATION)
	
	-- Handle respawning
	character:FindFirstChild("Humanoid").Died:Connect(function()
		print("[RPG] Player died: " .. player.Name)
		
		-- Reset stats but keep level/exp
		playerData.health = playerData.maxHealth
		playerData.mana = playerData.maxMana
		
		-- Respawn after 3 seconds
		wait(3)
		if player.Parent then
			player:LoadCharacter()
		end
	end)
	
	-- Handle character respawn
	player.CharacterAdded:Connect(function(newCharacter)
		print("[RPG] Character respawned: " .. player.Name)
		playerData.health = playerData.maxHealth
		playerData.mana = playerData.maxMana
		PlayerManager:setupCharacter(newCharacter, playerData, SPAWN_LOCATION)
	end)
end)

-- Handle player leaving
Players.PlayerRemoving:Connect(function(player)
	print("[RPG] Player left: " .. player.Name)
	gameState.players[player.UserId] = nil
end)

-- ============================================================================
-- GAME LOOP (Server Update)
-- ============================================================================

RunService.Heartbeat:Connect(function(deltaTime)
	if not gameState.isRunning then return end
	
	-- Update all active players
	for userId, playerData in pairs(gameState.players) do
		if playerData and playerData.character and playerData.character.Parent then
			-- Mana regeneration
			if playerData.mana < playerData.maxMana then
				playerData.mana = math.min(playerData.mana + (1 * deltaTime), playerData.maxMana)
			end
			
			-- Sync player position for other clients
			local humanoidRootPart = playerData.character:FindFirstChild("HumanoidRootPart")
			if humanoidRootPart then
				playerData.position = humanoidRootPart.Position
			end
		end
	end
	
	-- Remove dead NPCs and respawn new ones
	local aliveNPCs = 0
	for i = #gameState.npcs, 1, -1 do
		local npc = gameState.npcs[i]
		if not npc or not npc.Parent or npc:FindFirstChild("Humanoid").Health <= 0 then
			if npc and npc.Parent then
				npc:Destroy()
			end
			table.remove(gameState.npcs, i)
		else
			aliveNPCs = aliveNPCs + 1
		end
	end
	
	-- Maintain NPC population (spawn 1 at a time)
	if aliveNPCs < 5 then
		NPCSpawner:spawnEnemies(gameState, 1)
	end
end)

-- ============================================================================
-- REMOTE FUNCTIONS & EVENTS (Client-Server Communication)
-- ============================================================================

-- Create RemoteFolder for communication
local remoteFolder = Instance.new("Folder")
remoteFolder.Name = "GameRemotes"
remoteFolder.Parent = game.ReplicatedStorage

-- Combat action remote
local combatRemote = Instance.new("RemoteFunction")
combatRemote.Name = "CombatAction"
combatRemote.Parent = remoteFolder

function combatRemote.OnServerInvoke(player, actionType, targetId, targetType)
	local playerData = gameState.players[player.UserId]
	if not playerData then return false end
	
	-- Handle different combat actions
	if actionType == "attack" then
		local target = gameState.npcs[targetId]
		if target then
			return CombatSystem:damageTarget(player, playerData, target, 10)
		end
	elseif actionType == "dodge" then
		return CombatSystem:performDodge(playerData)
	elseif actionType == "ability" then
		return CombatSystem:castAbility(playerData, targetId, targetType)
	end
	
	return false
end

-- Player state sync remote
local syncRemote = Instance.new("RemoteEvent")
syncRemote.Name = "SyncPlayerState"
syncRemote.Parent = remoteFolder

syncRemote.OnServerEvent:Connect(function(player, playerStatsTable)
	local playerData = gameState.players[player.UserId]
	if playerData then
		-- Server validates and updates stats
		if playerStatsTable.health then
			playerData.health = math.max(0, math.min(playerStatsTable.health, playerData.maxHealth))
		end
	end
end)

-- Broadcast game state to all clients
local broadcastRemote = Instance.new("RemoteEvent")
broadcastRemote.Name = "BroadcastGameState"
broadcastRemote.Parent = remoteFolder

spawn(function()
	while gameState.isRunning do
		wait(0.1) -- Sync every 100ms
		
		-- Build state packet
		local statePacket = {
			players = {},
			npcs = {}
		}
		
		-- Add player positions/stats
		for userId, playerData in pairs(gameState.players) do
			if playerData and playerData.character and playerData.character.Parent then
				statePacket.players[userId] = {
					name = playerData.name,
					position = playerData.position,
					health = playerData.health,
					maxHealth = playerData.maxHealth,
					mana = playerData.mana,
					maxMana = playerData.maxMana,
					level = playerData.level,
					experience = playerData.experience
				}
			end
		end
		
		-- Add NPC positions/stats
		for i, npc in pairs(gameState.npcs) do
			if npc and npc.Parent then
				local humanoid = npc:FindFirstChild("Humanoid")
				if humanoid and humanoid.Health > 0 then
					local humanoidRootPart = npc:FindFirstChild("HumanoidRootPart")
					if humanoidRootPart then
						statePacket.npcs[i] = {
							position = humanoidRootPart.Position,
							health = humanoid.Health,
							maxHealth = humanoid.MaxHealth
						}
					end
				end
			end
		end
		
		-- Broadcast to all players
		broadcastRemote:FireAllClients(statePacket)
	end
end)

print("[RPG] Server initialization complete - waiting for players...")
