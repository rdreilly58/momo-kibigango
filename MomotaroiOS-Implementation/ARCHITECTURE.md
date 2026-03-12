# Momotaro-iOS Architecture

## Overview

Momotaro-iOS follows a clean MVVM (Model-View-ViewModel) architecture with centralized state management, proper separation of concerns, and comprehensive error handling.

## Architecture Layers

### 1. Models (Data Layer)
Located in: `Models/`

**Purpose:** Define data structures and domain entities

- **Peach.swift** — Core data model with Codable support
- **User.swift** — User authentication model
- **GatewayMessage.swift** — OpenClaw gateway messages with validation
- **SortCriteria.swift** — Sorting enumeration

**Key Features:**
- Codable conformance for JSON serialization
- Identifiable protocol for SwiftUI integration
- Input validation in initializers
- Custom error types

### 2. Services (Business Logic Layer)
Located in: `Services/`

**Purpose:** Handle networking, storage, and external integrations

- **NetworkService.swift** — REST API communication with Result type
- **WebSocketManager.swift** — Real-time WebSocket connections
- **StorageService.swift** — Local data persistence
- **GatewayService.swift** — Gateway message parsing and routing

**Key Features:**
- Centralized network requests
- Proper error handling
- Mock-friendly design for testing
- Thread-safe operations

### 3. ViewModels (Presentation Logic)
Located in: `ViewModels/`

**Purpose:** Bridge between Views and Services

- **AppState.swift** — Centralized application state (@ObservableObject)
- **PeachViewModel.swift** — Peach list management, filtering, sorting
- **UserViewModel.swift** — User authentication and management

**Key Features:**
- @Published properties for reactive updates
- Async operations with DispatchQueue
- Error handling and user feedback
- State caching and persistence

### 4. Views (Presentation Layer)
Located in: `Views/`

**Purpose:** SwiftUI components and screens

- **PeachListView.swift** — Main peach list with search and sorting
- **SettingsView.swift** — User settings (uses @EnvironmentObject AppState)
- **ContentView.swift** — App navigation structure

**Key Features:**
- SwiftUI declarative syntax
- Proper state binding (@ObservedObject, @EnvironmentObject)
- Reusable components
- Pull-to-refresh, error states, loading states

### 5. Extensions & Utilities
Located in: `Utilities/`

**Extensions:**
- **String+Extensions.swift** — Email validation, numeric checks, trimming
- **URLSession+Extensions.swift** — Network utilities
- **View+Extensions.swift** — Custom SwiftUI modifiers

**Helpers:**
- **Logger.swift** — Centralized logging
- **Constants.swift** — API endpoints and configuration

## Data Flow

```
User Interaction (View)
    ↓
ViewModel Methods
    ↓
Services (Network, Storage, Gateway)
    ↓
Models (Data structures)
    ↓
ViewModels update @Published properties
    ↓
Views re-render automatically (reactive)
```

## State Management

### AppState (Single Source of Truth)

```swift
class AppState: ObservableObject {
    @Published var isLoggedIn: Bool
    @Published var currentUser: User?
    @Published var networkError: NetworkError?
    @Published var peaches: [Peach]
    @Published var connectionState: ConnectionState
}
```

**Usage in Views:**
```swift
@EnvironmentObject var appState: AppState

// Automatic updates when appState properties change
```

## Error Handling

### Network Errors
```swift
enum NetworkError: Error {
    case badURL
    case requestFailed(URLError)
    case decodingError(DecodingError)
    case serverError(statusCode: Int)
    case noData
}
```

### Gateway Message Errors
```swift
enum ValidationError: Error {
    case emptyContent
    case invalidMessageType
}
```

### Best Practices
- Use Result type for async operations
- Provide user-friendly error messages
- Log errors for debugging
- Implement error recovery UI

## Async Operations

### Network Requests
```swift
networkService.fetchPeaches { [weak self] result in
    switch result {
    case .success(let peaches):
        self?.peaches = peaches
    case .failure(let error):
        self?.errorMessage = error.errorDescription
    }
}
```

### Using DispatchQueue
```swift
DispatchQueue.main.async { [weak self] in
    self?.updateUI()
}
```

## WebSocket Integration

### Connection Management
```swift
let wsManager = WebSocketManager()
wsManager.connect()
wsManager.send(message)
wsManager.disconnect()
```

### Connection States
- `.disconnected` — Not connected
- `.connecting` — In process
- `.connected` — Active connection
- `.error(String)` — Error occurred
- `.reconnecting(attempt: Int)` — Retrying connection

### Auto-Reconnection
- Exponential backoff: 2s, 4s, 8s, 16s, 32s
- Max 5 reconnection attempts
- Thread-safe with DispatchQueue

## Testing

### Unit Tests
- NetworkServiceTests (mock URLSession)
- PeachViewModelTests (mock data)
- UserViewModelTests (authentication flow)
- AppStateTests (state updates)

### Test Patterns
```swift
// Arrange
let testData = MockFactory.createPeaches()

// Act
viewModel.filterPeaches(with: "Golden")

// Assert
XCTAssertEqual(viewModel.filteredPeaches.count, 1)
```

### Mock Objects
- MockURLSession
- MockNetworkService
- MockStorageService

## Performance Considerations

1. **Memory Management**
   - Use `[weak self]` in closures to prevent cycles
   - Clean up timers and subscriptions

2. **Threading**
   - Fetch on background thread
   - Update UI on main thread
   - Use DispatchQueue for thread safety

3. **Caching**
   - Cache network responses locally
   - Use StorageService for persistence
   - Implement cache invalidation

4. **Image Loading**
   - Use deferred loading
   - Implement placeholder images
   - Cache images in memory

## Future Improvements

1. **Reactive Streams**
   - Implement Combine publishers
   - Use async/await (iOS 13+)

2. **Architecture Evolution**
   - Consider Redux-style state management
   - Implement dependency injection

3. **Performance**
   - Implement pagination
   - Add lazy loading
   - Optimize image rendering

4. **Testing**
   - Add UI tests with XCUITest
   - Implement snapshot testing
   - Add integration tests

## References

- [Apple's MVVM Guide](https://developer.apple.com/tutorials/swiftui)
- [Result Type Documentation](https://developer.apple.com/documentation/swift/result)
- [URLSession Documentation](https://developer.apple.com/documentation/foundation/urlsession)
- [WebSocket Support](https://developer.apple.com/documentation/foundation/urlsessionwebsockettask)
