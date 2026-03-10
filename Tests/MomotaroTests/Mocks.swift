import Foundation

class MockWebSocketTask: URLSessionWebSocketTask {
    var connectCalled = false
    var disconnectCalled = false

    override func resume() {
        connectCalled = true
    }
    
    override func cancel(with closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        disconnectCalled = true
    }
    
    // Implement additional mock behaviors as needed
}
