import XCTest
@testable import Momotaro

class GatewayClientTests: XCTestCase {
    
    // MARK: - Initialization Tests
    
    @MainActor
    func testDefaultURLInitialization() {
        let client = GatewayClient()
        XCTAssertFalse(client.isConnected)
        XCTAssertEqual(client.connectionStatus, "Disconnected")
    }
    
    @MainActor
    func testCustomURLInitialization() {
        let customURL = "ws://custom.example.com:9000"
        let client = GatewayClient(gatewayURL: customURL)
        XCTAssertFalse(client.isConnected)
    }
    
    @MainActor
    func testInitialState() {
        let client = GatewayClient()
        XCTAssertFalse(client.isConnected)
        XCTAssertNil(client.error)
        XCTAssertEqual(client.connectionStatus, "Disconnected")
    }
    
    // MARK: - Message Creation Tests (No Network)
    
    @MainActor
    func testCreateMessage() {
        let message = GatewayMessage(
            type: "message",
            content: "Hello",
            sessionId: "session123",
            timestamp: "2026-03-10T13:48:00Z"
        )
        
        XCTAssertEqual(message.type, "message")
        XCTAssertEqual(message.content, "Hello")
        XCTAssertEqual(message.sessionId, "session123")
    }
    
    @MainActor
    func testMessageEncoding() throws {
        let message = GatewayMessage(
            type: "message",
            content: "Test encoding",
            sessionId: nil,
            timestamp: "2026-03-10T13:48:00Z"
        )
        
        let encoder = JSONEncoder()
        let jsonData = try encoder.encode(message)
        
        XCTAssertNotNil(jsonData)
        XCTAssertGreaterThan(jsonData.count, 0)
        
        // Verify it can be decoded back
        let decoder = JSONDecoder()
        let decoded = try decoder.decode(GatewayMessage.self, from: jsonData)
        XCTAssertEqual(decoded.content, "Test encoding")
    }
    
    @MainActor
    func testMessageDecoding() throws {
        let jsonString = """
        {
            "type": "message",
            "content": "Hello",
            "session_id": "session123",
            "timestamp": "2026-03-10T13:48:00Z"
        }
        """
        
        let decoder = JSONDecoder()
        let message = try decoder.decode(GatewayMessage.self, from: jsonString.data(using: .utf8)!)
        
        XCTAssertEqual(message.type, "message")
        XCTAssertEqual(message.content, "Hello")
        XCTAssertEqual(message.sessionId, "session123")
    }
    
    // MARK: - Callback Tests
    
    @MainActor
    func testCallbackAssignment() {
        let client = GatewayClient()
        
        var callbackCalled = false
        client.onMessageReceived = { _ in
            callbackCalled = true
        }
        
        XCTAssertNotNil(client.onMessageReceived)
        
        // Test callback can be invoked
        client.onMessageReceived?(GatewayMessage(
            type: "test",
            content: "test",
            sessionId: nil,
            timestamp: "2026-03-10T13:48:00Z"
        ))
        
        XCTAssertTrue(callbackCalled)
    }
    
    @MainActor
    func testConnectionStatusCallback() {
        let client = GatewayClient()
        
        var statusChanged = false
        client.onConnectionStatusChanged = { _ in
            statusChanged = true
        }
        
        XCTAssertNotNil(client.onConnectionStatusChanged)
    }
    
    // MARK: - Error Handling Tests
    
    @MainActor
    func testErrorMessageDisplay() {
        let client = GatewayClient()
        
        XCTAssertNil(client.error)
        
        client.error = "Test error"
        XCTAssertEqual(client.error, "Test error")
        
        client.error = nil
        XCTAssertNil(client.error)
    }
    
    // MARK: - State Management Tests
    
    @MainActor
    func testInitialStateProperties() {
        let client = GatewayClient()
        
        XCTAssertFalse(client.isConnected)
        XCTAssertEqual(client.connectionStatus, "Disconnected")
        XCTAssertNil(client.error)
        XCTAssertEqual(client.lastMessage, "")
    }
    
    @MainActor
    func testConnectionStatusString() {
        let client = GatewayClient()
        
        XCTAssertEqual(client.connectionStatus, "Disconnected")
    }
    
    // MARK: - Command Preparation Tests
    
    @MainActor
    func testPrepareCommandMessage() {
        let client = GatewayClient()
        
        // Simulate what sendCommand does
        let timestamp = ISO8601DateFormatter().string(from: Date())
        let message = GatewayMessage(
            type: "message",
            content: "Hello",
            sessionId: nil,
            timestamp: timestamp
        )
        
        XCTAssertEqual(message.type, "message")
        XCTAssertEqual(message.content, "Hello")
    }
    
    // MARK: - GatewayMessage Type Tests
    
    @MainActor
    func testGatewayMessageTypes() {
        let commandMessage = GatewayMessage(
            type: "command",
            content: "execute",
            sessionId: "s1",
            timestamp: "2026-03-10T13:48:00Z"
        )
        
        let eventMessage = GatewayMessage(
            type: "event",
            content: "trigger",
            sessionId: "s1",
            timestamp: "2026-03-10T13:48:00Z"
        )
        
        let responseMessage = GatewayMessage(
            type: "response",
            content: "ok",
            sessionId: "s1",
            timestamp: "2026-03-10T13:48:00Z"
        )
        
        XCTAssertEqual(commandMessage.type, "command")
        XCTAssertEqual(eventMessage.type, "event")
        XCTAssertEqual(responseMessage.type, "response")
    }
    
    // MARK: - Message Content Tests
    
    @MainActor
    func testEmptyMessageContent() {
        let message = GatewayMessage(
            type: "message",
            content: "",
            sessionId: nil,
            timestamp: "2026-03-10T13:48:00Z"
        )
        
        XCTAssertEqual(message.content, "")
    }
    
    @MainActor
    func testLongMessageContent() {
        let longContent = String(repeating: "a", count: 1000)
        let message = GatewayMessage(
            type: "message",
            content: longContent,
            sessionId: nil,
            timestamp: "2026-03-10T13:48:00Z"
        )
        
        XCTAssertEqual(message.content.count, 1000)
    }
    
    @MainActor
    func testSpecialCharacterContent() {
        let specialContent = "Hello 👋 World! \n New line \t Tab"
        let message = GatewayMessage(
            type: "message",
            content: specialContent,
            sessionId: nil,
            timestamp: "2026-03-10T13:48:00Z"
        )
        
        XCTAssertEqual(message.content, specialContent)
    }
    
    // MARK: - Session ID Tests
    
    @MainActor
    func testSessionIDPresent() {
        let message = GatewayMessage(
            type: "message",
            content: "Test",
            sessionId: "session123",
            timestamp: "2026-03-10T13:48:00Z"
        )
        
        XCTAssertEqual(message.sessionId, "session123")
    }
    
    @MainActor
    func testSessionIDAbsent() {
        let message = GatewayMessage(
            type: "message",
            content: "Test",
            sessionId: nil,
            timestamp: "2026-03-10T13:48:00Z"
        )
        
        XCTAssertNil(message.sessionId)
    }
    
    // MARK: - Timestamp Tests
    
    @MainActor
    func testTimestampFormat() {
        let timestamp = "2026-03-10T13:48:00Z"
        let message = GatewayMessage(
            type: "message",
            content: "Test",
            sessionId: nil,
            timestamp: timestamp
        )
        
        XCTAssertEqual(message.timestamp, timestamp)
    }
    
    @MainActor
    func testCurrentTimestamp() {
        let timestamp = ISO8601DateFormatter().string(from: Date())
        let message = GatewayMessage(
            type: "message",
            content: "Test",
            sessionId: nil,
            timestamp: timestamp
        )
        
        XCTAssertNotNil(message.timestamp)
    }
}
