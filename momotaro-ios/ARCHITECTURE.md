# Momotaro-iOS Architecture

## System Overview

```mermaid
graph LR
    App["📱 Momotaro App<br/>SwiftUI"]
    Client["🔌 GatewayClient<br/>WebSocket"]
    Network["🌐 Network Layer<br/>URLSession"]
    Gateway["☁️ OpenClaw Gateway<br/>WebSocket Server"]
    Storage["💾 Local Storage<br/>UserDefaults"]
    
    App -->|Messages| Client
    Client -->|Connect/Send| Network
    Network -->|TCP/WebSocket| Gateway
    Gateway -->|Events| Network
    Network -->|Receive| Client
    Client -->|State Updates| App
    App -->|Persist| Storage
```

## Connection State Machine

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    
    Disconnected --> Connecting: connect()
    Connecting --> Connected: TCP Established
    Connecting --> Disconnected: Connection Failed
    
    Connected --> Connected: Send/Receive Messages
    Connected --> Reconnecting: Connection Lost<br/>Network Error
    
    Reconnecting --> Connecting: Backoff Expired<br/>Exponential: 1s, 4s, 9s, 16s, 25s
    Reconnecting --> MaxRetries: 5 Attempts Failed
    
    MaxRetries --> [*]: Give Up
    
    Connected --> Disconnected: disconnect()<br/>User Initiated
```

## Message Flow

```mermaid
sequenceDiagram
    participant UI as SwiftUI View
    participant Client as GatewayClient
    participant URLSession as URLSession<br/>WebSocket
    participant Server as OpenClaw<br/>Gateway
    
    UI->>Client: send(message: "Hello")
    activate Client
    
    Client->>URLSession: Create URLSessionWebSocketTask
    activate URLSession
    
    URLSession->>Server: Establish WebSocket
    activate Server
    
    Server-->>URLSession: ✓ Connected
    deactivate Server
    
    URLSession-->>Client: Connection Ready
    deactivate URLSession
    
    Client->>URLSession: Send String Message
    URLSession->>Server: Message Arrives
    
    Server-->>URLSession: Echo Response
    URLSession->>Client: Message Received
    
    Client->>UI: Update @Published property
    deactivate Client
    
    UI->>UI: Re-render with new message
```

## Error Handling Flow

```mermaid
graph TD
    A["Error Occurs"]
    
    B["Log Error Context:<br/>- Type<br/>- Message<br/>- Timestamp"]
    
    C["Determine Error Type"]
    
    D1["Network Error"]
    D2["Parse Error"]
    D3["Unknown Error"]
    
    E1["Trigger Reconnect<br/>with Exponential Backoff"]
    E2["Log & Ignore"]
    E3["Log to Firebase"]
    
    F["Update UI:<br/>isConnected = false<br/>errorMessage = String"]
    
    G["User Sees:<br/>Reconnecting..."]
    
    A --> B
    B --> C
    C --> D1
    C --> D2
    C --> D3
    D1 --> E1
    D2 --> E2
    D3 --> E3
    E1 --> F
    E2 --> F
    E3 --> F
    F --> G
```

## Class Structure

```mermaid
classDiagram
    class MomotaroApp {
        +init()
        +body: Scene
    }
    
    class ContentView {
        -viewModel: ContentViewModel
        +body: View
    }
    
    class ContentViewModel {
        -gateway: GatewayClient
        +isConnected: Bool
        +messageCount: Int
        +sendMessage(String)
    }
    
    class GatewayClient {
        -url: URL
        -webSocketTask: URLSessionWebSocketTask
        -backoffAttempts: Int
        -maxBackoffAttempts: Int
        +isConnected: Bool
        +errorMessage: String?
        +connect()
        +disconnect()
        +send(message: String)
        -listenForMessages()
        -attemptReconnect()
        -handleData(Data)
    }
    
    class GatewayMessage {
        -id: String
        -type: String
        -payload: Data
        -timestamp: Date
        +init(from: Decoder)
        +encode(to: Encoder)
    }
    
    class Logger {
        +shared: AppLogger
        +log(level: LogLevel, message: String)
        +debug(String)
        +info(String)
        +warning(String)
        +error(String, Error?)
    }
    
    class FirebaseConfig {
        +configure()
    }
    
    MomotaroApp --|> ContentView
    ContentView --|> ContentViewModel
    ContentViewModel --|> GatewayClient
    GatewayClient --|> GatewayMessage
    GatewayClient --|> Logger
    MomotaroApp --|> FirebaseConfig
```

## Logging & Monitoring

```mermaid
graph LR
    App["Momotaro App"]
    
    Log1["🔍 Console Logs<br/>Development"]
    Log2["🔥 Firebase Crashlytics<br/>Crashes & Errors"]
    Log3["📊 Firebase Analytics<br/>User Events"]
    
    App -->|Info/Debug| Log1
    App -->|Exceptions| Log2
    App -->|Track Events| Log3
    
    Log1 -->|Display| Xcode["Xcode Console<br/>During Development"]
    Log2 -->|Dashboard| Firebase["Firebase Console<br/>Crash Reports"]
    Log3 -->|Dashboard| Analytics["Firebase Analytics<br/>User Engagement"]
    
    Firebase -->|Alert| Dev["📱 Developer<br/>Notified of Crashes"]
    Analytics -->|Insights| Dev
```

## Data Flow: Message Lifecycle

```mermaid
graph LR
    A["User Types<br/>Message"]
    B["Tap Send Button"]
    C["GatewayClient<br/>validates message"]
    D{Connected?}
    E["Queue Message"]
    F["Send via<br/>WebSocket"]
    G["Server<br/>Receives"]
    H["Echo/Process"]
    I["Response<br/>Received"]
    J["Update UI:<br/>Show Message"]
    K["Complete"]
    
    A --> B
    B --> C
    C --> D
    D -->|Yes| F
    D -->|No| E
    E -.->|When Connected| F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    
    style E fill:#ffcccc
    style K fill:#ccffcc
```

## Network Architecture

```mermaid
graph TD
    A["iOS Device"]
    B["URLSession<br/>WebSocket API"]
    C["Network Stack<br/>TCP/IP"]
    D["WiFi or<br/>Cellular"]
    E["Internet"]
    F["OpenClaw<br/>Gateway Server"]
    
    A -->|SwiftUI| A
    A -->|URLSessionWebSocketTask| B
    B -->|Establish Connection| C
    C -->|Physical Layer| D
    D -->|IP Packets| E
    E -->|DNS/TLS| F
    
    F -.->|Response| E
    E -.->|Receive| D
    D -.->|Decode| C
    C -.->|WebSocket Data| B
    B -.->|Message Callback| A
```

## Reconnection Strategy

```mermaid
graph LR
    Disconnect["Connection Lost"]
    
    R1["Attempt 1<br/>Wait 1s"]
    R2["Attempt 2<br/>Wait 4s"]
    R3["Attempt 3<br/>Wait 9s"]
    R4["Attempt 4<br/>Wait 16s"]
    R5["Attempt 5<br/>Wait 25s"]
    
    Success["✅ Connected!<br/>Reset counter"]
    MaxRetries["❌ Max Retries<br/>Give Up"]
    UserAction["👤 User<br/>Reconnects"]
    
    Disconnect --> R1
    R1 -->|Fail| R2
    R2 -->|Fail| R3
    R3 -->|Fail| R4
    R4 -->|Fail| R5
    R5 -->|Fail| MaxRetries
    
    R1 -->|Success| Success
    R2 -->|Success| Success
    R3 -->|Success| Success
    R4 -->|Success| Success
    R5 -->|Success| Success
    
    MaxRetries --> UserAction
    UserAction --> R1
    
    Success --> Connected["Connected State"]
```

## Performance & Memory Management

```mermaid
graph LR
    A["GatewayClient Instance"]
    B["[weak self] in Closures"]
    C["Cancel WebSocketTask<br/>on Disconnect"]
    D["Release Resources"]
    E["Memory Freed"]
    
    A -->|Prevent Retain<br/>Cycles| B
    B -->|Explicit<br/>Cleanup| C
    C -->|On deallocate| D
    D -->|Automatic<br/>ARC| E
```

## Deployment & Testing

```mermaid
graph TD
    Dev["👨‍💻 Developer<br/>Local Xcode"]
    Test["🧪 Unit Tests<br/>XCTest"]
    Sim["📱 Simulator<br/>Testing"]
    TestFlight["🔄 TestFlight<br/>Beta Testing"]
    Monitor["📊 Firebase<br/>Monitoring"]
    AppStore["🎯 App Store<br/>Production"]
    
    Dev -->|Code Change| Test
    Test -->|Pass| Sim
    Sim -->|Manual Test| Dev
    Sim -->|Pass| TestFlight
    TestFlight -->|User Testing| Monitor
    Monitor -->|No Crashes| AppStore
    Monitor -->|Crash Found| Dev
```

## Technology Stack

**Language & Framework:**
- Swift (iOS 17+)
- SwiftUI (UI Framework)
- Combine (Reactive Programming)

**Networking:**
- URLSession (WebSocket support)
- TCP/IP (Underlying protocol)
- TLS/SSL (Encryption)

**Data:**
- Codable (JSON serialization)
- UserDefaults (Local persistence)

**Logging & Monitoring:**
- os.Logger (Apple unified logging)
- Firebase Crashlytics (Crash reporting)
- Firebase Analytics (Event tracking)

**Development Tools:**
- Xcode 15+
- Swift Package Manager
- XCTest (Unit testing)

---

## Key Decisions

### Why URLSession WebSocket?
- Native iOS API (no external dependencies)
- Full WebSocket support
- Automatic TLS handling
- Battery efficient

### Why SwiftUI + Combine?
- Modern, reactive UI
- Automatic state management
- Less boilerplate than UIKit
- Future-proof

### Why Firebase Crashlytics?
- Automatic crash capture
- Real-time alerts
- No setup needed (just plist)
- Free tier is generous

### Why Exponential Backoff for Reconnection?
- Prevents server overload
- Efficient battery usage
- Standard practice
- Configurable multiplier

---

## Related Documents
- [DEBUGGING_TIER1_DEPLOYED.md](../DEBUGGING_TIER1_DEPLOYED.md) - Monitoring setup
- [DIAGRAMMING_TOOLS_ANALYSIS.md](../DIAGRAMMING_TOOLS_ANALYSIS.md) - More architecture patterns
- [GatewayClient Tests](./Tests/GatewayClientTests.swift) - Unit tests
