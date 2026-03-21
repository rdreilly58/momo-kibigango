-- ============================================================================
-- NPC SPAWNER & AI MODULE
-- ============================================================================
-- Location: ServerScriptService > NPCSpawner (ModuleScript)
-- Purpose: Spawn NPCs, manage NPC AI behavior, handle NPC combat
-- ============================================================================

local NPCSpawner = {}
local RunService = game:GetService("RunService")

-- NPC templates
local NPC_TEMPLATES = {
	goblin = {
		displayName = "Goblin",
		health = 30,
		damage = 8,
		armor = 1,
		speed = 16,
		level = 1,
		expReward = 50,
		color = Color3.fromRGB(0, 150, 0)
	},
	orc = {
		displayName = "Orc",
		health = 60,
		damage = 15,
		armor = 3,
		speed = 14,
		level = 2,
		expReward = 100,
		color = Color3.fromRGB(100, 100, 100)
	},
	skeleton = {
		displayName = "Skeleton",
		health = 45,
		damage = 12,
		armor = 2,
		speed = 15,
		level = 2,
		expReward = 75,
		color = Color3.fromRGB(200, 200, 200)
	},
	troll = {
		displayName = "Troll",
		health = 100,
		damage = 20,
		armor = 5,
		speed = 12,
		level = 3,
		expReward = 200,
		color = Color3.fromRGB(50, 100, 50)
	}
}

-- ============================================================================
-- Spawn Enemies
-- ============================================================================

function NPCSpawner:spawnEnemies(gameState, count)
	local spawnZones = {
		Vector3.new(30, 5, 30),
		Vector3.new(-30, 5, 30),
		Vector3.new(30, 5, -30),
		Vector3.new(-30, 5, -30),
		Vector3.new(0, 5, 50),
	}
	
	for i = 1, count do
		-- Pick random template and spawn zone
		local templateNames = {"goblin", "goblin", "orc", "skeleton"} -- Weighted towards goblins
		local templateName = templateNames[math.random(#templateNames)]
		local template = NPC_TEMPLATES[templateName]
		local spawnZone = spawnZones[math.random(#spawnZones)]
		
		-- Randomize spawn position
		local randomOffset = Vector3.new(
			math.random(-15, 15),
			0,
			math.random(-15, 15)
		)
		local spawnPos = spawnZone + randomOffset
		
		-- Create NPC
		local npc = self:createNPC(template, templateName, spawnPos)
		
		-- Start AI behavior
		if npc and npc.Parent then
			self:startNPCAI(gameState, npc, template)
			table.insert(gameState.npcs, npc)
			print("[NPCSpawner] Spawned " .. template.displayName .. " at " .. tostring(spawnPos))
		end
	end
end

function NPCSpawner:createNPC(template, templateName, spawnPos)
	-- Create NPC model (humanoid character)
	local npc = Instance.new("Model")
	npc.Name = template.displayName
	
	-- Create humanoid
	local humanoid = Instance.new("Humanoid")
	humanoid.MaxHealth = template.health
	humanoid.Health = template.health
	humanoid.Parent = npc
	
	-- Create root part (HumanoidRootPart)
	local rootPart = Instance.new("Part")
	rootPart.Name = "HumanoidRootPart"
	rootPart.Shape = Enum.PartType.Ball
	rootPart.Size = Vector3.new(2, 2, 2)
	rootPart.CanCollide = false
	rootPart.CFrame = CFrame.new(spawnPos)
	rootPart.Parent = npc
	
	-- Create head
	local head = Instance.new("Part")
	head.Name = "Head"
	head.Shape = Enum.PartType.Ball
	head.Size = Vector3.new(1.6, 1.6, 1.6)
	head.TopSurface = Enum.SurfaceType.Smooth
	head.BottomSurface = Enum.SurfaceType.Smooth
	head.BrickColor = BrickColor.new(template.color)
	head.CanCollide = false
	head.Parent = npc
	
	-- Weld head to root
	local weld = Instance.new("Weld")
	weld.Part0 = rootPart
	weld.Part1 = head
	weld.C0 = CFrame.new(0, 1.5, 0)
	weld.Parent = rootPart
	
	-- Create humanoid root part position joint
	local rootJoint = Instance.new("Motor6D")
	rootJoint.Name = "RootJoint"
	rootJoint.Part0 = rootPart
	rootJoint.Part1 = rootPart
	rootJoint.Parent = rootPart
	
	-- Add stats as values
	local stats = Instance.new("Folder")
	stats.Name = "Stats"
	stats.Parent = npc
	
	local healthValue = Instance.new("IntValue")
	healthValue.Name = "Health"
	healthValue.Value = template.health
	healthValue.Parent = stats
	
	local damageValue = Instance.new("IntValue")
	damageValue.Name = "Damage"
	damageValue.Value = template.damage
	damageValue.Parent = stats
	
	local levelValue = Instance.new("IntValue")
	levelValue.Name = "Level"
	levelValue.Value = template.level
	levelValue.Parent = stats
	
	-- Add NPC tag
	local npcTag = Instance.new("BoolValue")
	npcTag.Name = "IsNPC"
	npcTag.Parent = npc
	
	-- Add to workspace
	npc.Parent = workspace
	
	return npc
end

-- ============================================================================
-- NPC AI Behavior
-- ============================================================================

function NPCSpawner:startNPCAI(gameState, npc, template)
	local rootPart = npc:FindFirstChild("HumanoidRootPart")
	if not rootPart then return end
	
	local targetPlayer = nil
	local lastAttackTime = 0
	local attackCooldown = 1.5
	
	-- AI loop
	spawn(function()
		while npc.Parent and npc:FindFirstChild("Humanoid").Health > 0 do
			-- Find nearest player
			local shortestDistance = math.huge
			targetPlayer = nil
			
			for userId, playerData in pairs(gameState.players) do
				if playerData and playerData.character and playerData.character.Parent then
					local playerRoot = playerData.character:FindFirstChild("HumanoidRootPart")
					if playerRoot then
						local distance = (rootPart.Position - playerRoot.Position).Magnitude
						if distance < shortestDistance and distance < 100 then -- 100 stud range
							shortestDistance = distance
							targetPlayer = playerData
						end
					end
				end
			end
			
			-- Move toward target or wander
			if targetPlayer and targetPlayer.character and targetPlayer.character.Parent then
				local playerRoot = targetPlayer.character:FindFirstChild("HumanoidRootPart")
				if playerRoot then
					-- Chase player
					local direction = (playerRoot.Position - rootPart.Position).Unit
					rootPart.Velocity = direction * template.speed
					
					-- Attack if close
					if shortestDistance < 10 and tick() - lastAttackTime > attackCooldown then
						self:npcAttackPlayer(gameState, npc, targetPlayer, template)
						lastAttackTime = tick()
					end
				end
			else
				-- Wander behavior
				if math.random() < 0.05 then
					local randomDirection = Vector3.new(
						math.random(-1, 1),
						0,
						math.random(-1, 1)
					).Unit
					rootPart.Velocity = randomDirection * template.speed
				end
			end
			
			wait(0.1) -- Update every 100ms
		end
	end)
end

function NPCSpawner:npcAttackPlayer(gameState, npc, playerData, template)
	if not playerData or not playerData.character then return end
	
	-- Apply damage
	local humanoid = playerData.character:FindFirstChild("Humanoid")
	if humanoid then
		-- Calculate damage with variance
		local damage = template.damage * (0.8 + math.random() * 0.4)
		humanoid:TakeDamage(damage)
		print("[NPC] " .. npc.Name .. " attacked " .. playerData.name .. " for " .. math.floor(damage) .. " damage")
	end
end

-- ============================================================================
-- NPC Utilities
-- ============================================================================

function NPCSpawner:despawnNPC(npc)
	if npc and npc.Parent then
		npc:Destroy()
	end
end

function NPCSpawner:getNPCStats(npc)
	local stats = npc:FindFirstChild("Stats")
	if not stats then return nil end
	
	return {
		health = stats:FindFirstChild("Health") and stats.Health.Value or 0,
		damage = stats:FindFirstChild("Damage") and stats.Damage.Value or 0,
		level = stats:FindFirstChild("Level") and stats.Level.Value or 1
	}
end

return NPCSpawner
