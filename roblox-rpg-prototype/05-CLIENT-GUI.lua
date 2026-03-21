-- ============================================================================
-- CLIENT GUI & HUD SCRIPT
-- ============================================================================
-- Location: StarterPlayer > StarterCharacterScripts > ClientGUI (LocalScript)
-- Purpose: Display health/mana bars, stats, combat interface
-- ============================================================================

local UserInputService = game:GetService("UserInputService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local player = Players.LocalPlayer
local character = script.Parent
local humanoid = character:WaitForChild("Humanoid")
local humanoidRootPart = character:WaitForChild("HumanoidRootPart")

-- Create GUI
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "RPGGui"
screenGui.ResetOnSpawn = false
screenGui.Parent = player:WaitForChild("PlayerGui")

-- ============================================================================
-- HEALTH BAR
-- ============================================================================

local healthBarBg = Instance.new("Frame")
healthBarBg.Name = "HealthBar"
healthBarBg.Size = UDim2.new(0, 200, 0, 30)
healthBarBg.Position = UDim2.new(0.5, -100, 0, 20)
healthBarBg.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
healthBarBg.BorderSizePixel = 2
healthBarBg.BorderColor3 = Color3.fromRGB(200, 200, 200)
healthBarBg.Parent = screenGui

local healthBar = Instance.new("Frame")
healthBar.Name = "HealthFill"
healthBar.Size = UDim2.new(1, 0, 1, 0)
healthBar.BackgroundColor3 = Color3.fromRGB(100, 200, 100)
healthBar.BorderSizePixel = 0
healthBar.Parent = healthBarBg

local healthLabel = Instance.new("TextLabel")
healthLabel.Name = "HealthLabel"
healthLabel.Size = UDim2.new(1, 0, 1, 0)
healthLabel.BackgroundTransparency = 1
healthLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
healthLabel.TextScaled = true
healthLabel.Font = Enum.Font.GothamBold
healthLabel.Parent = healthBarBg

-- ============================================================================
-- MANA BAR
-- ============================================================================

local manaBarBg = Instance.new("Frame")
manaBarBg.Name = "ManaBar"
manaBarBg.Size = UDim2.new(0, 200, 0, 20)
manaBarBg.Position = UDim2.new(0.5, -100, 0, 55)
manaBarBg.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
manaBarBg.BorderSizePixel = 2
manaBarBg.BorderColor3 = Color3.fromRGB(100, 100, 200)
manaBarBg.Parent = screenGui

local manaBar = Instance.new("Frame")
manaBar.Name = "ManaFill"
manaBar.Size = UDim2.new(1, 0, 1, 0)
manaBar.BackgroundColor3 = Color3.fromRGB(100, 150, 255)
manaBar.BorderSizePixel = 0
manaBar.Parent = manaBarBg

-- ============================================================================
-- STATS DISPLAY
-- ============================================================================

local statsFrame = Instance.new("Frame")
statsFrame.Name = "StatsDisplay"
statsFrame.Size = UDim2.new(0, 250, 0, 150)
statsFrame.Position = UDim2.new(0, 20, 0, 20)
statsFrame.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
statsFrame.BorderSizePixel = 2
statsFrame.BorderColor3 = Color3.fromRGB(150, 150, 150)
statsFrame.Parent = screenGui

local statsLabel = Instance.new("TextLabel")
statsLabel.Name = "StatsText"
statsLabel.Size = UDim2.new(1, 0, 1, 0)
statsLabel.BackgroundTransparency = 1
statsLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
statsLabel.TextSize = 14
statsLabel.Font = Enum.Font.Gotham
statsLabel.TextXAlignment = Enum.TextXAlignment.Left
statsLabel.TextYAlignment = Enum.TextYAlignment.Top
statsLabel.Padding = UDim.new(0, 10)
statsLabel.Parent = statsFrame

-- ============================================================================
-- ABILITIES BAR
-- ============================================================================

local abilitiesFrame = Instance.new("Frame")
abilitiesFrame.Name = "Abilities"
abilitiesFrame.Size = UDim2.new(0, 400, 0, 60)
abilitiesFrame.Position = UDim2.new(0.5, -200, 1, -80)
abilitiesFrame.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
abilitiesFrame.BorderSizePixel = 2
abilitiesFrame.BorderColor3 = Color3.fromRGB(150, 100, 50)
abilitiesFrame.Parent = screenGui

local abilities = {
	{key = "Q", name = "Fireball", manaCost = 20},
	{key = "W", name = "Heal", manaCost = 25},
	{key = "E", name = "Power Strike", manaCost = 15},
	{key = "Space", name = "Dodge", manaCost = 0}
}

for i, ability in ipairs(abilities) do
	local abilityBtn = Instance.new("Frame")
	abilityBtn.Name = ability.key
	abilityBtn.Size = UDim2.new(0, 90, 0, 50)
	abilityBtn.Position = UDim2.new(0, 10 + (i-1) * 95, 0, 5)
	abilityBtn.BackgroundColor3 = Color3.fromRGB(80, 80, 80)
	abilityBtn.BorderSizePixel = 1
	abilityBtn.BorderColor3 = Color3.fromRGB(200, 200, 200)
	abilityBtn.Parent = abilitiesFrame
	
	local keyLabel = Instance.new("TextLabel")
	keyLabel.Text = ability.key
	keyLabel.Size = UDim2.new(1, 0, 0, 20)
	keyLabel.BackgroundTransparency = 1
	keyLabel.TextColor3 = Color3.fromRGB(255, 255, 100)
	keyLabel.TextSize = 12
	keyLabel.Font = Enum.Font.GothamBold
	keyLabel.Parent = abilityBtn
	
	local nameLabel = Instance.new("TextLabel")
	nameLabel.Text = ability.name
	nameLabel.Size = UDim2.new(1, 0, 0, 15)
	nameLabel.Position = UDim2.new(0, 0, 0, 15)
	nameLabel.BackgroundTransparency = 1
	nameLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
	nameLabel.TextSize = 11
	nameLabel.Font = Enum.Font.Gotham
	nameLabel.Parent = abilityBtn
	
	local costLabel = Instance.new("TextLabel")
	costLabel.Text = "(" .. ability.manaCost .. "mp)"
	costLabel.Size = UDim2.new(1, 0, 0, 12)
	costLabel.Position = UDim2.new(0, 0, 0, 32)
	costLabel.BackgroundTransparency = 1
	costLabel.TextColor3 = Color3.fromRGB(100, 150, 255)
	costLabel.TextSize = 9
	costLabel.Font = Enum.Font.Gotham
	costLabel.Parent = abilityBtn
end

-- ============================================================================
-- PLAYER DATA (LOCAL)
-- ============================================================================

local playerData = {
	health = 100,
	maxHealth = 100,
	mana = 50,
	maxMana = 50,
	level = 1,
	experience = 0,
	experienceToLevelUp = 100
}

-- ============================================================================
-- UPDATE GUI
-- ============================================================================

-- Sync with humanoid health
humanoid.HealthChanged:Connect(function(health)
	playerData.health = math.max(0, health)
	
	-- Update health bar
	healthBar.Size = UDim2.new(playerData.health / playerData.maxHealth, 0, 1, 0)
	healthLabel.Text = math.floor(playerData.health) .. " / " .. playerData.maxHealth .. " HP"
	
	-- Update color based on health percentage
	local healthPercent = playerData.health / playerData.maxHealth
	if healthPercent > 0.5 then
		healthBar.BackgroundColor3 = Color3.fromRGB(100, 200, 100)
	elseif healthPercent > 0.2 then
		healthBar.BackgroundColor3 = Color3.fromRGB(255, 200, 0)
	else
		healthBar.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
	end
end)

-- Update mana (local client update)
spawn(function()
	while character.Parent do
		if playerData.mana < playerData.maxMana then
			playerData.mana = math.min(playerData.mana + (1 * 0.1), playerData.maxMana)
		end
		
		local manaPercent = playerData.mana / playerData.maxMana
		manaBar.Size = UDim2.new(manaPercent, 0, 1, 0)
		
		wait(0.1)
	end
end)

-- Update stats display
spawn(function()
	while character.Parent do
		statsLabel.Text = string.format(
			"Level: %d\nExp: %d / %d\n\nStats:\nDamage: %d\nArmor: %d\n\nGold: %d",
			playerData.level,
			playerData.experience,
			playerData.experienceToLevelUp,
			15,
			5,
			0
		)
		wait(0.5)
	end
end)

-- ============================================================================
-- INPUT HANDLING
-- ============================================================================

local combatRemote = game.ReplicatedStorage:WaitForChild("GameRemotes"):WaitForChild("CombatAction")

-- Key bindings
UserInputService.InputBegan:Connect(function(input, gameProcessed)
	if gameProcessed then return end
	
	-- Left Click - Attack nearest enemy
	if input.UserInputType == Enum.UserInputType.MouseButton1 then
		-- Find nearest NPC in range
		local nearestNPC = nil
		local shortestDistance = math.huge
		
		for _, obj in pairs(workspace:GetChildren()) do
			if obj:FindFirstChild("IsNPC") then
				local npcRoot = obj:FindFirstChild("HumanoidRootPart")
				if npcRoot then
					local distance = (humanoidRootPart.Position - npcRoot.Position).Magnitude
					if distance < 50 and distance < shortestDistance then
						shortestDistance = distance
						nearestNPC = obj
					end
				end
			end
		end
		
		-- Attack
		if nearestNPC then
			combatRemote:InvokeServer("attack", nearestNPC.Name, "npc")
		end
	
	-- Q - Fireball
	elseif input.KeyCode == Enum.KeyCode.Q then
		combatRemote:InvokeServer("ability", 1, "npc")
	
	-- W - Heal
	elseif input.KeyCode == Enum.KeyCode.W then
		combatRemote:InvokeServer("ability", 2, "npc")
	
	-- E - Power Strike
	elseif input.KeyCode == Enum.KeyCode.E then
		combatRemote:InvokeServer("ability", 3, "npc")
	
	-- Space - Dodge
	elseif input.KeyCode == Enum.KeyCode.Space then
		combatRemote:InvokeServer("dodge", 0, "self")
	end
end)

print("[ClientGUI] HUD loaded successfully")
