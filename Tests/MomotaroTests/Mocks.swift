import Foundation
@testable import Momotaro

// MARK: - Mock WebSocket Task Protocol

/// Protocol for WebSocket tasks to support mocking
protocol WebSocketTaskProtocol {
    func resume()
    func cancel(with closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?)
    func send(_ message: URLSessionWebSocketTask.Message, completionHandler: @escaping (Error?) -> Void)
    func receive(completionHandler: @escaping (Result<URLSessionWebSocketTask.Message, Error>) -> Void)
}

// MARK: - Mock WebSocket Task

/// Mock implementation of WebSocket for testing without real network calls
class MockWebSocketTask: WebSocketTaskProtocol {
    
    // MARK: - Properties
    private(set) var connectCalled = false
    private(set) var disconnectCalled = false
    private(set) var isConnected = false
    private(set) var sentMessages: [String] = []
    
    var messageQueue: [GatewayMessage] = []
    var shouldThrowError: Error? = nil
    var receiveDelay: TimeInterval = 0
    
    // MARK: - Initialization
    init() {}
    
    // MARK: - WebSocketTaskProtocol Methods
    
    func resume() {
        connectCalled = true
        isConnected = true
    }
    
    func cancel(with closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        disconnectCalled = true
        isConnected = false
    }
    
    func send(_ message: URLSessionWebSocketTask.Message, completionHandler: @escaping (Error?) -> Void) {
        // Record sent message
        switch message {
        case .string(let text):
            sentMessages.append(text)
        case .data(let data):
            if let text = String(data: data, encoding: .utf8) {
                sentMessages.append(text)
            }
        @unknown default:
            break
        }
        
        // Call completion handler
        completionHandler(shouldThrowError)
    }
    
    func receive(completionHandler: @escaping (Result<URLSessionWebSocketTask.Message, Error>) -> Void) {
        if let error = shouldThrowError {
            completionHandler(.failure(error))
            return
        }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + receiveDelay) { [weak self] in
            guard let self = self, !self.messageQueue.isEmpty else {
                completionHandler(.failure(NSError(domain: "MockWebSocket", code: -1, userInfo: nil)))
                return
            }
            
            let message = self.messageQueue.removeFirst()
            if let jsonData = try? JSONEncoder().encode(message),
               let jsonString = String(data: jsonData, encoding: .utf8) {
                completionHandler(.success(.string(jsonString)))
            } else {
                completionHandler(.failure(NSError(domain: "MockWebSocket", code: -2, userInfo: nil)))
            }
        }
    }
    
    // MARK: - Helper Methods
    
    /// Simulate receiving a message
    func simulateReceive(_ message: GatewayMessage) {
        messageQueue.append(message)
    }
    
    /// Reset mock state for new test
    func reset() {
        connectCalled = false
        disconnectCalled = false
        isConnected = false
        sentMessages = []
        messageQueue = []
        shouldThrowError = nil
        receiveDelay = 0
    }
}

// MARK: - Test Helpers

/// Helper for setting up common mock scenarios
class MockGatewaySetup {
    
    static func createMockTask() -> MockWebSocketTask {
        return MockWebSocketTask()
    }
    
    static func createTestMessage(
        type: String = "message",
        content: String = "Test",
        sessionId: String? = nil,
        timestamp: String? = nil
    ) -> GatewayMessage {
        let ts = timestamp ?? ISO8601DateFormatter().string(from: Date())
        return GatewayMessage(
            type: type,
            content: content,
            sessionId: sessionId,
            timestamp: ts
        )
    }
}
