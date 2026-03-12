# WebSocket Integration Guide

## Overview

Momotaro-iOS uses `URLSessionWebSocketTask` for real-time communication with the OpenClaw gateway. The `WebSocketManager` handles connection lifecycle, automatic reconnection, and message routing.

## WebSocketManager Features

### Connection States
```swift
enum ConnectionState: Equatable {
    case disconnected
    case connecting
    case connected
    case error(String)
    case reconnecting(attempt: Int)
}
```

### Auto-Reconnection
- Exponential backoff: 2s → 4s → 8s → 16s → 32s
- Maximum 5 reconnection attempts
- Thread-safe with DispatchQueue

## Basic Usage

### 1. Initialize Manager

```swift
class AppState: ObservableObject {
    @Published var wsManager: WebSocketManager?
    
    func setupWebSocket() {
        let url = URL(string: "wss://gateway.openclaw.local/ws")!
        wsManager = WebSocketManager(gatewayURL: url)
    }
}
```

### 2. Connect to Gateway

```swift
// In your app initialization
appState.wsManager?.connect()

// Monitor connection state
@Published var connectionState = ConnectionState.disconnected
```

### 3. Send Messages

```swift
let message = try GatewayMessage(
    messageType: "command",
    content: "action_name"
)
wsManager?.send(message)
```

### 4. Receive Messages

Messages are automatically received and stored in `lastMessage`:

```swift
@EnvironmentObject var wsManager: WebSocketManager

var body: some View {
    VStack {
        if let message = wsManager.lastMessage {
            Text("Received: \(message.content)")
        }
    }
}
```

## Connection Lifecycle

### Connect
```swift
wsManager.connect()
// State changes: disconnected → connecting → connected
```

### Disconnect
```swift
wsManager.disconnect()
// State changes: connected → disconnected
```

### Auto-Reconnection (on error)
```
connected → error → reconnecting(attempt: 1) 
→ connecting → connected
```

## Message Format

### Sending Messages
```swift
try GatewayMessage(
    id: UUID(),
    messageType: "command",
    content: """
    {
        "action": "peach_fetch",
        "params": {}
    }
    """,
    timestamp: Date()
)
```

### Receiving Messages
```swift
struct GatewayMessage: Codable {
    let id: UUID
    let messageType: String
    let content: String
    let timestamp: Date
}
```

## Implementation Examples

### Example 1: Monitor Connection Status

```swift
struct ConnectionStatusView: View {
    @ObservedObject var wsManager: WebSocketManager
    
    var body: some View {
        HStack {
            Circle()
                .fill(statusColor)
                .frame(width: 12, height: 12)
            
            Text(statusText)
                .font(.caption)
        }
    }
    
    var statusColor: Color {
        switch wsManager.connectionState {
        case .connected:
            return .green
        case .connecting, .reconnecting:
            return .yellow
        case .disconnected:
            return .gray
        case .error:
            return .red
        }
    }
    
    var statusText: String {
        switch wsManager.connectionState {
        case .connected:
            return "Connected"
        case .connecting:
            return "Connecting..."
        case .reconnecting(let attempt):
            return "Reconnecting (\(attempt)/5)"
        case .disconnected:
            return "Disconnected"
        case .error(let msg):
            return "Error: \(msg)"
        }
    }
}
```

### Example 2: Handle Messages

```swift
class GatewayMessageHandler {
    static func handle(_ message: GatewayMessage, appState: AppState) {
        let service = GatewayService()
        
        service.routeMessage(message) { messageType, payload in
            switch messageType {
            case .command:
                handleCommand(payload, appState: appState)
            case .notification:
                handleNotification(payload)
            case .response:
                handleResponse(payload, appState: appState)
            case .error:
                handleError(payload, appState: appState)
            }
        }
    }
    
    private static func handleCommand(_ payload: [String: Any], appState: AppState) {
        print("Command received: \(payload)")
    }
    
    private static func handleNotification(_ payload: [String: Any]) {
        print("Notification: \(payload)")
    }
    
    private static func handleResponse(_ payload: [String: Any], appState: AppState) {
        print("Response: \(payload)")
    }
    
    private static func handleError(_ payload: [String: Any], appState: AppState) {
        if let error = payload["error"] as? String {
            appState.setNetworkError(NetworkError.requestFailed(
                URLError(.badServerResponse)
            ))
        }
    }
}
```

### Example 3: Automatic Message Listening

```swift
class MessageListener {
    private var wsManager: WebSocketManager
    private var appState: AppState
    private var timer: Timer?
    
    init(wsManager: WebSocketManager, appState: AppState) {
        self.wsManager = wsManager
        self.appState = appState
        setupListener()
    }
    
    private func setupListener() {
        // Check for new messages every 100ms
        timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            guard let self = self, let message = self.wsManager.lastMessage else {
                return
            }
            
            GatewayMessageHandler.handle(message, appState: self.appState)
        }
    }
    
    deinit {
        timer?.invalidate()
    }
}
```

## Error Handling

### Connection Errors

```swift
switch wsManager.connectionState {
case .error(let description):
    // Show error to user
    appState.setNetworkError(
        NetworkError.requestFailed(
            URLError(.unknown)
        )
    )
case .reconnecting(let attempt):
    // Show retry UI
    if attempt >= 3 {
        showWarning("Reconnecting... \(attempt)/5")
    }
default:
    break
}
```

### Message Validation

```swift
func validateMessage(_ message: GatewayMessage) -> Bool {
    // Check message type is valid
    guard ["command", "notification", "response", "error"].contains(message.messageType) else {
        return false
    }
    
    // Check content is not empty
    guard !message.content.isEmpty else {
        return false
    }
    
    // Check timestamp is reasonable
    let timeDiff = Date().timeIntervalSince(message.timestamp)
    guard abs(timeDiff) < 3600 else { // Within 1 hour
        return false
    }
    
    return true
}
```

## Advanced Configuration

### Custom Reconnection Strategy

```swift
class CustomWebSocketManager: WebSocketManager {
    override func attemptReconnection() {
        // Implement custom logic
        // e.g., exponential backoff with jitter
    }
}
```

### Message Queue

```swift
class MessageQueue {
    private var queue: [GatewayMessage] = []
    private let lock = NSLock()
    
    func enqueue(_ message: GatewayMessage) {
        lock.lock()
        defer { lock.unlock() }
        queue.append(message)
    }
    
    func dequeue() -> GatewayMessage? {
        lock.lock()
        defer { lock.unlock() }
        return queue.isEmpty ? nil : queue.removeFirst()
    }
}
```

## Testing WebSocket

### Mock WebSocket Manager

```swift
class MockWebSocketManager: ObservableObject {
    @Published var connectionState: ConnectionState = .connected
    @Published var lastMessage: GatewayMessage?
    
    func connect() { }
    func disconnect() { }
    func send(_ message: GatewayMessage) { }
    
    func simulateMessage(_ message: GatewayMessage) {
        lastMessage = message
    }
}
```

### Test Example

```swift
func testWebSocketMessage() {
    let mockWS = MockWebSocketManager()
    let message = try? GatewayMessage(
        messageType: "test",
        content: "Hello"
    )
    
    mockWS.simulateMessage(message!)
    
    XCTAssertNotNil(mockWS.lastMessage)
    XCTAssertEqual(mockWS.lastMessage?.content, "Hello")
}
```

## Performance Tips

1. **Batch Messages** — Group multiple operations in single message
2. **Debounce** — Avoid sending duplicate messages
3. **Cleanup** — Disconnect when app goes to background
4. **Memory** — Use weak self in WebSocket callbacks

## Monitoring & Debugging

### Enable WebSocket Logging

```swift
func enableWebSocketLogging() {
    Logger.log("WebSocket manager initialized")
    Logger.log("Connection state: \(wsManager.connectionState)")
}
```

### Network Debugging

Use Charles Proxy or Xcode Network Link Conditioner to simulate:
- Poor connections
- Packet loss
- High latency
- Disconnections

## Common Issues

### Connection Drops After 5 Minutes
- **Cause:** Keep-alive not implemented
- **Solution:** Send heartbeat messages every 30 seconds

### Memory Leak from WebSocket
- **Cause:** Forgotten `[weak self]` in closures
- **Solution:** Always use weak self in completion handlers

### Messages Not Received
- **Cause:** Message receiving loop not running
- **Solution:** Ensure `receive()` is called after connect

## References

- [Apple's WebSocket Documentation](https://developer.apple.com/documentation/foundation/urlsessionwebsockettask)
- [RFC 6455 - WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- [Debugging WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
