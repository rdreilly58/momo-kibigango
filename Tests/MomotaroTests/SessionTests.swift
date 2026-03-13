import XCTest
@testable import Momotaro

// MARK: - SessionInfo Tests

final class SessionInfoTests: XCTestCase {
    
    func testSessionInfoCreation() {
        let session = SessionInfo(
            id: "test_1",
            name: "Test Session",
            description: "A test session",
            type: "agent",
            isActive: true,
            createdAt: Date(),
            lastUsedAt: nil
        )
        
        XCTAssertEqual(session.id, "test_1")
        XCTAssertEqual(session.name, "Test Session")
        XCTAssertTrue(session.isActive)
    }
    
    func testSessionInfoEquality() {
        let date = Date()
        let session1 = SessionInfo(
            id: "test_1",
            name: "Test",
            description: "Test",
            type: "agent",
            isActive: true,
            createdAt: date,
            lastUsedAt: nil
        )
        let session2 = SessionInfo(
            id: "test_1",
            name: "Test",
            description: "Test",
            type: "agent",
            isActive: true,
            createdAt: date,
            lastUsedAt: nil
        )
        
        XCTAssertEqual(session1, session2)
    }
    
    func testSessionInfoIcon() {
        let agentSession = SessionInfo(
            id: "1",
            name: "Agent",
            description: "Agent",
            type: "agent",
            isActive: true,
            createdAt: Date(),
            lastUsedAt: nil
        )
        XCTAssertEqual(agentSession.icon, "🤖")
        
        let customSession = SessionInfo(
            id: "2",
            name: "Custom",
            description: "Custom",
            type: "custom",
            isActive: false,
            createdAt: Date(),
            lastUsedAt: nil
        )
        XCTAssertEqual(customSession.icon, "⚙️")
    }
    
    func testSessionInfoCoding() throws {
        let session = SessionInfo(
            id: "test_1",
            name: "Test Session",
            description: "A test session",
            type: "agent",
            isActive: true,
            createdAt: Date(),
            lastUsedAt: Date()
        )
        
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        let data = try encoder.encode(session)
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let decoded = try decoder.decode(SessionInfo.self, from: data)
        
        XCTAssertEqual(session.id, decoded.id)
        XCTAssertEqual(session.name, decoded.name)
    }
}

// MARK: - SessionManager Tests

@MainActor
final class SessionManagerTests: XCTestCase {
    
    var gateway: GatewayClient!
    var manager: SessionManager!
    
    override func setUp() {
        super.setUp()
        gateway = GatewayClient()
        manager = SessionManager(gateway: gateway)
    }
    
    override func tearDown() {
        manager = nil
        gateway = nil
        super.tearDown()
    }
    
    func testInitialization() {
        XCTAssertNotNil(manager)
        XCTAssertTrue(manager.availableSessions.isEmpty)
        XCTAssertNil(manager.currentSession)
        XCTAssertFalse(manager.isLoading)
        XCTAssertNil(manager.error)
    }
    
    func testFetchSessions() async {
        await manager.fetchSessions()
        
        XCTAssertFalse(manager.availableSessions.isEmpty)
        XCTAssertEqual(manager.availableSessions.count, 3)
        XCTAssertNotNil(manager.currentSession)
    }
    
    func testFetchSessionsLoading() async {
        let fetchTask = Task {
            await manager.fetchSessions()
        }
        
        try? await Task.sleep(nanoseconds: 10_000_000)
        
        await fetchTask.value
        XCTAssertFalse(manager.isLoading)
    }
    
    func testCurrentSessionAfterFetch() async {
        await manager.fetchSessions()
        
        XCTAssertNotNil(manager.currentSession)
        XCTAssertTrue(manager.currentSession?.isActive ?? false)
        XCTAssertEqual(manager.currentSession?.id, "session_claude")
    }
    
    func testSwitchSession() async {
        await manager.fetchSessions()
        
        guard let targetSession = manager.availableSessions.first(where: { $0.id == "session_gpt4" }) else {
            XCTFail("Target session not found")
            return
        }
        
        await manager.switchSession(to: targetSession)
        
        XCTAssertEqual(manager.currentSession?.id, "session_gpt4")
        XCTAssertTrue(manager.currentSession?.isActive ?? false)
    }
    
    func testSwitchSessionUpdatesLastUsed() async {
        await manager.fetchSessions()
        
        let targetSession = manager.availableSessions[1]
        let beforeSwitch = targetSession.lastUsedAt
        
        await manager.switchSession(to: targetSession)
        
        let afterSwitch = manager.availableSessions.first(where: { $0.id == targetSession.id })?.lastUsedAt
        XCTAssertNotNil(afterSwitch)
        XCTAssertNotEqual(beforeSwitch, afterSwitch)
    }
    
    func testGetSessionByID() async {
        await manager.fetchSessions()
        
        let session = manager.getSession(id: "session_claude")
        XCTAssertNotNil(session)
        XCTAssertEqual(session?.name, "Claude AI")
    }
    
    func testGetSessionByIDNotFound() async {
        await manager.fetchSessions()
        
        let session = manager.getSession(id: "nonexistent")
        XCTAssertNil(session)
    }
    
    func testGetSessionsByType() async {
        await manager.fetchSessions()
        
        let agents = manager.getSessionsByType("agent")
        XCTAssertEqual(agents.count, 2)
        
        let custom = manager.getSessionsByType("custom")
        XCTAssertEqual(custom.count, 1)
    }
    
    func testSwitchToNonexistentSession() async {
        await manager.fetchSessions()
        
        let fakeSession = SessionInfo(
            id: "fake",
            name: "Fake",
            description: "Fake",
            type: "agent",
            isActive: false,
            createdAt: Date(),
            lastUsedAt: nil
        )
        
        await manager.switchSession(to: fakeSession)
        
        XCTAssertEqual(manager.error as? SessionError, SessionError.notFound)
    }
    
    func testSwitchToCurrentSession() async {
        await manager.fetchSessions()
        
        guard let current = manager.currentSession else {
            XCTFail("No current session")
            return
        }
        
        await manager.switchSession(to: current)
        
        XCTAssertEqual(manager.currentSession?.id, current.id)
        XCTAssertTrue(manager.currentSession?.isActive ?? false)
    }
    
    func testMultipleSwitches() async {
        await manager.fetchSessions()
        
        // Start with session 1 (claude)
        XCTAssertEqual(manager.currentSession?.id, "session_claude")
        
        // Switch to session 2 (gpt4)
        let session2 = manager.getSession(id: "session_gpt4")!
        await manager.switchSession(to: session2)
        XCTAssertEqual(manager.currentSession?.id, "session_gpt4")
        
        // Switch to session 3 (local)
        let session3 = manager.getSession(id: "session_local")!
        await manager.switchSession(to: session3)
        XCTAssertEqual(manager.currentSession?.id, "session_local")
        
        // Switch back to session 1 (claude)
        let session1 = manager.getSession(id: "session_claude")!
        await manager.switchSession(to: session1)
        XCTAssertEqual(manager.currentSession?.id, "session_claude")
    }
    
    func testSessionPersistenceAfterSwitch() async {
        await manager.fetchSessions()
        
        let originalCount = manager.availableSessions.count
        
        guard let target = manager.availableSessions.first(where: { $0.id == "session_gpt4" }) else {
            XCTFail("Target not found")
            return
        }
        
        await manager.switchSession(to: target)
        
        XCTAssertEqual(manager.availableSessions.count, originalCount)
    }
    
    func testErrorClearing() async {
        manager.error = SessionError.fetchFailed("test")
        
        await manager.fetchSessions()
        
        XCTAssertNil(manager.error)
    }
    
    func testSessionDescription() {
        let session = SessionInfo(
            id: "test",
            name: "Test",
            description: "Test description",
            type: "agent",
            isActive: false,
            createdAt: Date(),
            lastUsedAt: nil
        )
        
        XCTAssertEqual(session.description, "Test description")
    }
    
    func testSessionIdentifiable() {
        let session = SessionInfo(
            id: "unique_id",
            name: "Test",
            description: "Test",
            type: "agent",
            isActive: false,
            createdAt: Date(),
            lastUsedAt: nil
        )
        
        XCTAssertEqual(session.id, "unique_id")
    }
}
