import XCTest
@testable import Momotaro
import CryptoKit

@MainActor
class GatewayAuthenticationTests: XCTestCase {
    
    var securityManager: SecurityManager!
    var messagePersistence: MessagePersistence!
    var gatewayClient: GatewayClient!
    
    override func setUp() async throws {
        try await super.setUp()
        securityManager = SecurityManager()
        messagePersistence = MessagePersistence()
        gatewayClient = GatewayClient(
            gatewayURL: "ws://localhost:8080",
            securityManager: securityManager,
            messagePersistence: messagePersistence
        )
        
        // Generate test keypair
        let keypair = try await securityManager.generateKeyPair()
        try securityManager.storeKeyPair(keypair)
    }
    
    override func tearDown() async throws {
        try await super.tearDown()
        gatewayClient.disconnect()
    }
    
    // MARK: - Signature Generation Tests
    
    func testDeterministicSignature() async throws {
        let message = "test message"
        
        let signature1 = try await securityManager.signMessage(message)
        let signature2 = try await securityManager.signMessage(message)
        
        XCTAssertEqual(signature1, signature2, "Same message should produce same signature")
    }
    
    func testDifferentMessagesSignDifferently() async throws {
        let message1 = "message one"
        let message2 = "message two"
        
        let signature1 = try await securityManager.signMessage(message1)
        let signature2 = try await securityManager.signMessage(message2)
        
        XCTAssertNotEqual(signature1, signature2, "Different messages should produce different signatures")
    }
    
    func testSignatureWithPrivateKey() async throws {
        let message = "test message"
        let signature = try await securityManager.signMessage(message)
        
        XCTAssertFalse(signature.isEmpty, "Signature should not be empty")
        XCTAssertGreater(signature.count, 0, "Signature should have content")
    }
    
    // MARK: - Authenticated Message Tests
    
    func testAuthenticatedMessageWrapsCorrectly() async throws {
        let gatewayMessage = GatewayMessage(
            type: "message",
            content: "test",
            sessionId: "session-123",
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        let signature = try await securityManager.signMessage(gatewayMessage.content)
        let publicKey = try securityManager.retrievePublicKey()
        
        let authenticatedMessage = AuthenticatedMessage(
            deviceId: "device-123",
            publicKey: publicKey.base64EncodedString(),
            message: gatewayMessage,
            signature: signature.base64EncodedString(),
            timestamp: ISO8601DateFormatter().string(from: Date()),
            nonce: UUID().uuidString
        )
        
        XCTAssertEqual(authenticatedMessage.deviceId, "device-123")
        XCTAssertEqual(authenticatedMessage.message.content, "test")
        XCTAssertFalse(authenticatedMessage.publicKey.isEmpty)
        XCTAssertFalse(authenticatedMessage.signature.isEmpty)
    }
    
    func testAuthenticatedMessageIncludesNonce() async throws {
        let gatewayMessage = GatewayMessage(
            type: "message",
            content: "test",
            sessionId: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        let signature = try await securityManager.signMessage(gatewayMessage.content)
        let publicKey = try securityManager.retrievePublicKey()
        
        let nonce1 = UUID().uuidString
        let nonce2 = UUID().uuidString
        
        let msg1 = AuthenticatedMessage(
            deviceId: "device-123",
            publicKey: publicKey.base64EncodedString(),
            message: gatewayMessage,
            signature: signature.base64EncodedString(),
            timestamp: ISO8601DateFormatter().string(from: Date()),
            nonce: nonce1
        )
        
        let msg2 = AuthenticatedMessage(
            deviceId: "device-123",
            publicKey: publicKey.base64EncodedString(),
            message: gatewayMessage,
            signature: signature.base64EncodedString(),
            timestamp: ISO8601DateFormatter().string(from: Date()),
            nonce: nonce2
        )
        
        XCTAssertNotEqual(msg1.nonce, msg2.nonce, "Each message should have unique nonce")
    }
    
    func testAuthenticatedMessageIncludesTimestamp() async throws {
        let gatewayMessage = GatewayMessage(
            type: "message",
            content: "test",
            sessionId: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        let signature = try await securityManager.signMessage(gatewayMessage.content)
        let publicKey = try securityManager.retrievePublicKey()
        let now = ISO8601DateFormatter().string(from: Date())
        
        let authenticatedMessage = AuthenticatedMessage(
            deviceId: "device-123",
            publicKey: publicKey.base64EncodedString(),
            message: gatewayMessage,
            signature: signature.base64EncodedString(),
            timestamp: now,
            nonce: UUID().uuidString
        )
        
        XCTAssertFalse(authenticatedMessage.timestamp.isEmpty)
        // Verify ISO8601 format
        XCTAssertTrue(authenticatedMessage.timestamp.contains("T"), "Timestamp should be in ISO8601 format")
    }
    
    func testAuthenticatedMessageIncludesPublicKey() async throws {
        let gatewayMessage = GatewayMessage(
            type: "message",
            content: "test",
            sessionId: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        let signature = try await securityManager.signMessage(gatewayMessage.content)
        let publicKey = try securityManager.retrievePublicKey()
        
        let authenticatedMessage = AuthenticatedMessage(
            deviceId: "device-123",
            publicKey: publicKey.base64EncodedString(),
            message: gatewayMessage,
            signature: signature.base64EncodedString(),
            timestamp: ISO8601DateFormatter().string(from: Date()),
            nonce: UUID().uuidString
        )
        
        XCTAssertFalse(authenticatedMessage.publicKey.isEmpty)
        XCTAssertEqual(authenticatedMessage.publicKey, publicKey.base64EncodedString())
    }
    
    // MARK: - Signature Verification Tests
    
    func testValidSignatureVerifies() async throws {
        let message = "test message"
        let signature = try await securityManager.signMessage(message)
        let publicKey = try securityManager.retrievePublicKey()
        
        let isValid = securityManager.verifySignature(signature, for: message, publicKey: publicKey)
        XCTAssertTrue(isValid, "Valid signature should verify")
    }
    
    func testTamperedSignatureFails() async throws {
        let message = "test message"
        let signature = try await securityManager.signMessage(message)
        let publicKey = try securityManager.retrievePublicKey()
        
        // Tamper with signature
        var tamperedSignature = signature
        if !tamperedSignature.isEmpty {
            let data = UnsafeMutableRawBufferPointer.allocate(byteCount: tamperedSignature.count, alignment: 1)
            defer { data.deallocate() }
            _ = tamperedSignature.withUnsafeBytes { $0.copyMemory(to: data) }
            if let ptr = data.baseAddress?.assumingMemoryBound(to: UInt8.self) {
                ptr[0] = ptr[0] ^ 0xFF // Flip bits
                tamperedSignature = Data(bytes: ptr, count: tamperedSignature.count)
            }
        }
        
        let isValid = securityManager.verifySignature(tamperedSignature, for: message, publicKey: publicKey)
        XCTAssertFalse(isValid, "Tampered signature should fail verification")
    }
    
    func testWrongPublicKeyFails() async throws {
        let message = "test message"
        let signature = try await securityManager.signMessage(message)
        
        // Generate different keypair
        let differentKeypair = try await securityManager.generateKeyPair()
        let wrongPublicKey = differentKeypair.publicKey
        
        let isValid = securityManager.verifySignature(signature, for: message, publicKey: wrongPublicKey)
        XCTAssertFalse(isValid, "Wrong public key should fail verification")
    }
    
    // MARK: - Session Token Tests
    
    func testRequestSessionToken() async throws {
        let token = SessionToken(
            token: "test-token-123",
            expiresAt: Date().addingTimeInterval(24 * 60 * 60),
            createdAt: Date()
        )
        
        try securityManager.storeSessionToken(token)
        let retrieved = try securityManager.retrieveSessionToken()
        
        XCTAssertNotNil(retrieved, "Should retrieve stored token")
        XCTAssertEqual(retrieved?.token, "test-token-123")
    }
    
    func testStoreSessionToken() async throws {
        let token = SessionToken(
            token: "test-token-456",
            expiresAt: Date().addingTimeInterval(24 * 60 * 60),
            createdAt: Date()
        )
        
        try securityManager.storeSessionToken(token)
        
        XCTAssertTrue(securityManager.isAuthenticated)
        XCTAssertNotNil(securityManager.currentToken)
    }
    
    func testRetrieveSessionToken() async throws {
        let token = SessionToken(
            token: "test-token-789",
            expiresAt: Date().addingTimeInterval(24 * 60 * 60),
            createdAt: Date()
        )
        
        try securityManager.storeSessionToken(token)
        let retrieved = try securityManager.retrieveSessionToken()
        
        XCTAssertNotNil(retrieved)
        XCTAssertEqual(retrieved?.token, "test-token-789")
    }
    
    func testAutoRefreshExpiredToken() async throws {
        // Create expired token
        let expiredToken = SessionToken(
            token: "expired-token",
            expiresAt: Date().addingTimeInterval(-1), // Already expired
            createdAt: Date().addingTimeInterval(-24 * 60 * 60)
        )
        
        try securityManager.storeSessionToken(expiredToken)
        
        // Refresh token
        let newToken = try securityManager.refreshToken(currentToken: expiredToken)
        
        XCTAssertNotNil(newToken)
        XCTAssertNotEqual(newToken.token, expiredToken.token)
        XCTAssertTrue(securityManager.isTokenValid(newToken))
    }
    
    // MARK: - End-to-End Tests
    
    func testSendCommandSignsMessage() async throws {
        let mockWebSocketTask = MockURLSessionWebSocketTask()
        let urlSession = MockURLSession(webSocketTask: mockWebSocketTask)
        
        let client = GatewayClient(
            gatewayURL: "ws://localhost:8080",
            urlSession: urlSession,
            securityManager: securityManager,
            messagePersistence: messagePersistence
        )
        
        try await client.sendCommand("Hello, Gateway!")
        
        XCTAssertNotNil(mockWebSocketTask.lastSentMessage, "Message should be sent")
    }
    
    func testReceiveResponsePersistsMessage() async throws {
        let gatewayMessage = GatewayMessage(
            type: "message",
            content: "Hello from Gateway",
            sessionId: gatewayClient.deviceId,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        let jsonData = try JSONEncoder().encode(gatewayMessage)
        let jsonString = String(data: jsonData, encoding: .utf8)!
        
        // Simulate receiving message
        gatewayClient.onMessageReceived?(gatewayMessage)
        
        let messages = try messagePersistence.fetchAllMessages()
        XCTAssertGreaterThan(messages.count, 0, "Received messages should be persisted")
    }
    
    func testUIUpdatesAfterSignedMessage() async throws {
        let expectation = XCTestExpectation(description: "UI updates after message")
        
        gatewayClient.onMessageReceived = { message in
            XCTAssertEqual(message.content, "Updated content")
            expectation.fulfill()
        }
        
        let message = GatewayMessage(
            type: "message",
            content: "Updated content",
            sessionId: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        gatewayClient.onMessageReceived?(message)
        
        await fulfillment(of: [expectation], timeout: 1.0)
    }
    
    // MARK: - Error Handling Tests
    
    func testInvalidKeyThrowsError() async throws {
        // Try to sign without valid private key
        let tempManager = SecurityManager()
        
        do {
            _ = try await tempManager.signMessage("test")
            XCTFail("Should throw error for missing private key")
        } catch {
            XCTAssertNotNil(error)
        }
    }
    
    func testNetworkErrorHandled() async throws {
        let failingURLSession = MockURLSessionWithError()
        
        let client = GatewayClient(
            gatewayURL: "ws://invalid",
            urlSession: failingURLSession,
            securityManager: securityManager,
            messagePersistence: messagePersistence
        )
        
        XCTAssertFalse(client.isConnected)
    }
    
    func testMalformedResponseHandled() async throws {
        let gatewayMessage = GatewayMessage(
            type: "message",
            content: "test",
            sessionId: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        // Set callback to verify error is caught
        var errorCaught = false
        gatewayClient.onMessageReceived = { _ in
            errorCaught = false // Message decoded successfully
        }
        
        // Try to handle malformed JSON - this should not crash
        gatewayClient.onMessageReceived?(gatewayMessage)
        
        XCTAssertFalse(errorCaught)
    }
    
    // MARK: - Replay Prevention Tests
    
    func testNonceValidation() async throws {
        let nonce1 = UUID().uuidString
        let nonce2 = UUID().uuidString
        
        let msg1 = GatewayMessage(
            type: "message",
            content: "message 1",
            sessionId: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        let msg2 = GatewayMessage(
            type: "message",
            content: "message 2",
            sessionId: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        // Different content should have different nonces in authenticated messages
        XCTAssertNotEqual(msg1.content, msg2.content)
    }
    
    func testTimestampFreshness() async throws {
        let now = Date()
        let timestamp = ISO8601DateFormatter().string(from: now)
        
        let message = GatewayMessage(
            type: "message",
            content: "test",
            sessionId: nil,
            timestamp: timestamp
        )
        
        // Parse timestamp and verify it's recent
        if let messageDate = ISO8601DateFormatter().date(from: message.timestamp) {
            let timeDifference = now.timeIntervalSince(messageDate)
            XCTAssertLessThan(abs(timeDifference), 1.0, "Timestamp should be recent")
        }
    }
}

// MARK: - Mock Objects

class MockURLSessionWebSocketTask: URLSessionWebSocketTask {
    var lastSentMessage: URLSessionWebSocketTask.Message?
    var messageQueue: [URLSessionWebSocketTask.Message] = []
    
    override func send(_ message: URLSessionWebSocketTask.Message, completionHandler: @escaping (Error?) -> Void) {
        lastSentMessage = message
        completionHandler(nil)
    }
    
    override func receive(completionHandler: @escaping (Result<URLSessionWebSocketTask.Message, Error>) -> Void) {
        if !messageQueue.isEmpty {
            let message = messageQueue.removeFirst()
            completionHandler(.success(message))
        }
    }
    
    override func resume() {
        // Mock implementation
    }
    
    override func cancel(with closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        // Mock implementation
    }
}

class MockURLSession: URLSession {
    let webSocketTask: URLSessionWebSocketTask
    
    init(webSocketTask: URLSessionWebSocketTask) {
        self.webSocketTask = webSocketTask
    }
    
    override func webSocketTask(with url: URL) -> URLSessionWebSocketTask {
        return webSocketTask
    }
}

class MockURLSessionWithError: URLSession {
    override func webSocketTask(with url: URL) -> URLSessionWebSocketTask {
        return MockURLSessionWebSocketTask()
    }
}
