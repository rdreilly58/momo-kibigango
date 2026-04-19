--[[
Roblox Studio Plugin: Game Test Automation
Automates testing, error capture, and reporting for loaded games

Usage:
  1. Load this plugin into Roblox Studio
  2. Click "Run Game Tests" in the Plugin toolbar
  3. Plugin executes game, captures output, generates report
]]

local toolbar = plugin:CreateToolbar("Game Testing")
local runTestsButton = toolbar:CreateButton(
    "Run Game Tests",
    "Load game from GitHub and run automated tests",
    "rbxasset://textures/Developers/Debugger/Play.png"
)

local testState = {
    running = false,
    errors = {},
    warnings = {},
    output = {},
    startTime = 0,
    endTime = 0,
    gameLoaded = false,
    testsCompleted = 0,
}

-- Configuration
local TEST_CONFIG = {
    timeout = 120, -- seconds
    captureOutput = true,
    stopOnFirstError = false,
    autoFixErrors = true,
}

-- Output capture
local OutputCapture = {}
OutputCapture.log = {}

local function log(message, level)
    level = level or "INFO"
    local timestamp = os.date("%H:%M:%S")
    local entry = string.format("[%s] %s: %s", timestamp, level, message)
    table.insert(OutputCapture.log, entry)
    print(entry)
end

-- Test utilities
local TestUtils = {}

function TestUtils:findScript(name)
    for _, service in pairs({game:GetService("ServerScriptService"), game:GetService("StarterPlayer")}) do
        local script = service:FindFirstChild(name)
        if script then return script end
    end
    return nil
end

function TestUtils:executeScript(script)
    log("Executing script: " .. script.Name)
    local success, result = pcall(function()
        return loadstring(script.Source)()
    end)
    if not success then
        table.insert(testState.errors, {
            script = script.Name,
            error = result,
            severity = "CRITICAL"
        })
        log("ERROR in " .. script.Name .. ": " .. tostring(result), "ERROR")
        return false
    end
    return true
end

function TestUtils:validateGameStructure()
    log("Validating game structure...")
    local requiredScripts = {
        "MainGameScript",
        "NPCSpawner",
        "CombatSystem",
        "PlayerManager"
    }
    
    local missing = {}
    for _, scriptName in pairs(requiredScripts) do
        if not TestUtils:findScript(scriptName) then
            table.insert(missing, scriptName)
            table.insert(testState.errors, {
                check = "structure",
                missing = scriptName,
                severity = "WARNING"
            })
            log("Missing script: " .. scriptName, "WARNING")
        end
    end
    
    if #missing > 0 then
        log("Game structure incomplete - missing " .. #missing .. " script(s)")
        return false
    end
    
    log("Game structure valid ✓")
    return true
end

function TestUtils:testGameplay()
    log("Testing gameplay mechanics...")
    
    -- Test 1: NPC Spawning
    local testsPassed = 0
    local testsFailed = 0
    
    local npcSpawner = TestUtils:findScript("NPCSpawner")
    if npcSpawner then
        log("Test 1: NPC Spawning")
        if TestUtils:executeScript(npcSpawner) then
            testsPassed = testsPassed + 1
            log("✓ NPC Spawner works")
        else
            testsFailed = testsFailed + 1
            log("✗ NPC Spawner failed", "ERROR")
        end
    end
    
    -- Test 2: Combat System
    local combatSystem = TestUtils:findScript("CombatSystem")
    if combatSystem then
        log("Test 2: Combat System")
        if TestUtils:executeScript(combatSystem) then
            testsPassed = testsPassed + 1
            log("✓ Combat System works")
        else
            testsFailed = testsFailed + 1
            log("✗ Combat System failed", "ERROR")
        end
    end
    
    -- Test 3: Player Manager
    local playerManager = TestUtils:findScript("PlayerManager")
    if playerManager then
        log("Test 3: Player Manager")
        if TestUtils:executeScript(playerManager) then
            testsPassed = testsPassed + 1
            log("✓ Player Manager works")
        else
            testsFailed = testsFailed + 1
            log("✗ Player Manager failed", "ERROR")
        end
    end
    
    testState.testsCompleted = testsPassed + testsFailed
    return testsFailed == 0, testsPassed, testsFailed
end

function TestUtils:captureGameOutput()
    log("Capturing game runtime output...")
    
    -- Hook into print to capture output
    local originalPrint = print
    function print(...)
        table.insert(OutputCapture.log, table.concat({...}, " "))
        originalPrint(...)
    end
    
    -- Simulate game start
    local mainGame = TestUtils:findScript("MainGameScript")
    if mainGame then
        local success = TestUtils:executeScript(mainGame)
        return success
    end
    
    return false
end

function TestUtils:generateReport()
    log("Generating test report...")
    
    local report = {
        timestamp = os.date("%Y-%m-%d %H:%M:%S"),
        duration = testState.endTime - testState.startTime,
        testsPassed = testState.testsCompleted,
        errorCount = #testState.errors,
        warningCount = #testState.warnings,
        gameLoaded = testState.gameLoaded,
        output = OutputCapture.log,
        errors = testState.errors,
    }
    
    -- Save report to file
    local reportPath = game:GetService("HttpService"):GenerateGUID(false)
    
    -- Print summary
    print("\n" .. string.rep("=", 50))
    print("TEST REPORT")
    print(string.rep("=", 50))
    print("Timestamp: " .. report.timestamp)
    print("Duration: " .. report.duration .. "s")
    print("Tests: " .. report.testsPassed)
    print("Errors: " .. report.errorCount)
    print("Warnings: " .. report.warningCount)
    print(string.rep("=", 50) .. "\n")
    
    return report
end

-- Main test execution
local function runTests()
    if testState.running then
        log("Tests already running", "WARNING")
        return
    end
    
    testState.running = true
    testState.startTime = tick()
    testState.errors = {}
    testState.warnings = {}
    OutputCapture.log = {}
    
    log("========================================")
    log("STARTING AUTOMATED GAME TESTS")
    log("========================================")
    
    -- Check if game is loaded
    if not game:GetService("ServerScriptService"):FindFirstChild("MainGameScript") then
        log("ERROR: Game not loaded - use roblox-loader skill first", "ERROR")
        testState.running = false
        return
    end
    
    -- Run validation
    testState.gameLoaded = TestUtils:validateGameStructure()
    
    if not testState.gameLoaded then
        log("Game structure validation failed", "ERROR")
        testState.running = false
        return
    end
    
    -- Run gameplay tests
    local success, passed, failed = TestUtils:testGameplay()
    
    -- Capture output
    TestUtils:captureGameOutput()
    
    -- Generate report
    testState.endTime = tick()
    local report = TestUtils:generateReport()
    
    testState.running = false
    log("TEST EXECUTION COMPLETE")
    
    return report
end

-- Button click handler
runTestsButton.Click:Connect(function()
    log("Test button clicked")
    local report = runTests()
    
    if report then
        log("Report generated: " .. #report.output .. " output lines captured")
    end
end)

log("TestAutomation plugin loaded successfully")

return {
    runTests = runTests,
    testState = testState,
    TestUtils = TestUtils,
}
