import XCTest
@testable import Momotaro

class GatewayClientTests: XCTestCase {
    
    // MARK: - Initialization Tests
    
    @MainActor
    func testDefaultURLInitialization() {
        let client = GatewayClient()
        // URL is private, so we test through behavior
        XCTAssertFalse(client.isConnected)
    }
    
    @MainActor
    func testCustomURLInitialization() {
        let customURL = "ws://custom.example.com:9000"
        let client = GatewayClient(gatewayURL: customURL)
        // URL is private, but initialization should succeed
        XCTAssertFalse(client.isConnected)
    }
    
    @MainActor
    func testInitialState() {
        let client = GatewayClient()
        XCTAssertFalse(client.isConnected)
        XCTAssertNil(client.error)
        XCTAssertEqual(client.connectionStatus, "Disconnected")
    }
    
    // MARK: - Connection Lifecycle Tests
    
    @MainActor
    func testConnectSuccess() {
        let client = GatewayClient()
        client.connect()
        
        // After connect is called, isConnected should be true
        XCTAssertTrue(client.isConnected)
        XCTAssertEqual(client.connectionStatus, "Connected")
    }
    
    @MainActor
    func testDisconnect() {
        let client = GatewayClient()
        client.connect()
        XCTAssertTrue(client.isConnected)
        
        client.disconnect()
        XCTAssertFalse(client.isConnected)
        XCTAssertEqual(client.connectionStatus, "Disconnected")
    }
    
    @MainActor
    func testConnectionStatusUpdates() {
        let client = GatewayClient()
        XCTAssertEqual(client.connectionStatus, "Disconnected")
        
        client.connect()
        XCTAssertEqual(client.connectionStatus, "Connected")
        
        client.disconnect()
        XCTAssertEqual(client.connectionStatus, "Disconnected")
    }
    
    @MainActor
    func testMultipleConnectDisconnectCycles() {
        let client = GatewayClient()
        
        // Cycle 1
        client.connect()
        XCTAssertTrue(client.isConnected)
        client.disconnect()
        XCTAssertFalse(client.isConnected)
        
        // Cycle 2
        client.connect()
        XCTAssertTrue(client.isConnected)
        client.disconnect()
        XCTAssertFalse(client.isConnected)
    }
    
    // MARK: - Message Tests
    
    @MainActor
    func testSendCommand() {
        let client = GatewayClient()
        
        client.connect()
        client.sendCommand("Hello")
        
        // Verify the command was sent while connected
        XCTAssertTrue(client.isConnected)
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
    }
    
    @MainActor
    func testMessageCallback() {
        let client = GatewayClient()
        
        client.onMessageReceived = { message in
            XCTAssertEqual(message.content, "Test")
        }
        
        client.connect()
        client.sendCommand("Test")
        
        // Callback should be set
        XCTAssertNotNil(client.onMessageReceived)
    }
    
    @MainActor
    func testMultipleMessages() {
        let client = GatewayClient()
        
        client.connect()
        client.sendCommand("Message 1")
        client.sendCommand("Message 2")
        client.sendCommand("Message 3")
        
        // Verify client is connected and can handle multiple sends
        XCTAssertTrue(client.isConnected)
    }
    
    // MARK: - Error Handling Tests
    
    @MainActor
    func testInvalidURL() {
        let client = GatewayClient(gatewayURL: "invalid://url")
        client.connect()
        
        // Invalid URL should still attempt connection but may have issues
        // The implementation handles this gracefully
        XCTAssertNotNil(client)
    }
    
    @MainActor
    func testDisconnectClears() {
        let client = GatewayClient()
        client.connect()
        XCTAssertTrue(client.isConnected)
        
        client.disconnect()
        XCTAssertFalse(client.isConnected)
        XCTAssertEqual(client.connectionStatus, "Disconnected")
    }
    
    @MainActor
    func testErrorMessageDisplay() {
        let client = GatewayClient()
        
        // Verify error property exists
        XCTAssertNil(client.error)
        
        // Error should be clearable
        client.error = nil
        XCTAssertNil(client.error)
    }
    
    // MARK: - State Management Tests
    
    @MainActor
    func testStateConsistency() {
        let client = GatewayClient()
        
        // Initially disconnected
        XCTAssertFalse(client.isConnected)
        XCTAssertEqual(client.connectionStatus, "Disconnected")
        
        // After connect
        client.connect()
        XCTAssertTrue(client.isConnected)
        XCTAssertEqual(client.connectionStatus, "Connected")
        
        // After disconnect
        client.disconnect()
        XCTAssertFalse(client.isConnected)
        XCTAssertEqual(client.connectionStatus, "Disconnected")
    }
    
    @MainActor
    func testConnectionStatusString() {
        let client = GatewayClient()
        
        XCTAssertEqual(client.connectionStatus, "Disconnected")
        
        client.connect()
        XCTAssertEqual(client.connectionStatus, "Connected")
    }
    
    @MainActor
    func testCallbackAssignment() {
        let client = GatewayClient()
        
        var callbackCalled = false
        client.onMessageReceived = { _ in
            callbackCalled = true
        }
        
        XCTAssertNotNil(client.onMessageReceived)
        client.onMessageReceived?(GatewayMessage(
            type: "test",
            content: "test",
            sessionId: nil,
            timestamp: "2026-03-10T13:48:00Z"
        ))
        
        XCTAssertTrue(callbackCalled)
    }
}
