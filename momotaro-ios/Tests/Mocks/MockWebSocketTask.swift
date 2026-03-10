// Mock for URLSessionWebSocketTask

import Foundation

class MockWebSocketTask: URLSessionWebSocketTask {
    private var isConnected = false

    override func resume() {
        isConnected = true
    }

    override func cancel(with closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        isConnected = false
    }

    // Add more mock functionality as needed
}
