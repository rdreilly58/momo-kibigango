# Momotaro-iOS

A production-ready iOS application built with SwiftUI and MVVM architecture. Features real-time WebSocket communication, comprehensive error handling, unit tests, and clean separation of concerns.

## 🎯 Features

✅ **Clean MVVM Architecture** — Proper separation between Models, Views, and ViewModels
✅ **Centralized State Management** — Single source of truth with AppState
✅ **Real-time WebSocket** — URLSessionWebSocketTask with auto-reconnection
✅ **Network Layer** — Result type, comprehensive error handling
✅ **Local Storage** — UserDefaults and file system persistence
✅ **SwiftUI Views** — Modern, reactive UI components
✅ **Unit Tests** — Network tests with mock URLSession
✅ **Comprehensive Docs** — Architecture, integration, testing guides

## 📁 Project Structure

```
Momotaro-iOS/
├── Models/                    # Data structures (Peach, User, etc)
│   ├── Peach.swift
│   ├── User.swift
│   ├── GatewayMessage.swift
│   └── SortCriteria.swift
├── ViewModels/               # Business logic and state
│   ├── AppState.swift
│   ├── PeachViewModel.swift
│   └── UserViewModel.swift
├── Views/                    # SwiftUI components
│   ├── PeachListView.swift
│   ├── SettingsView.swift
│   └── ContentView.swift
├── Services/                 # External integrations
│   ├── NetworkService.swift
│   ├── WebSocketManager.swift
│   ├── StorageService.swift
│   └── GatewayService.swift
├── Utilities/
│   ├── Extensions/           # Swift extensions
│   │   ├── String+Extensions.swift
│   │   ├── URLSession+Extensions.swift
│   │   └── View+Extensions.swift
│   └── Helpers/              # Utilities
│       ├── Logger.swift
│       └── Constants.swift
├── Tests/                    # Unit tests
│   ├── NetworkServiceTests.swift
│   ├── PeachViewModelTests.swift
│   ├── AppStateTests.swift
│   └── UserViewModelTests.swift
├── Documentation/
│   ├── ARCHITECTURE.md       # Architecture overview
│   ├── INTEGRATION.md        # Step-by-step setup guide
│   ├── TESTING.md           # Testing guide
│   ├── WEBSOCKET.md         # WebSocket integration
│   └── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites
- Xcode 14.0+
- iOS 14.0+ deployment target
- Swift 5.7+

### 1. Clone or Copy Files
```bash
# Copy all files from MomotaroiOS-Implementation/ to your Xcode project
```

### 2. Create Project Structure
Follow the folder structure above in Xcode (File → New → Group)

### 3. Add Files to Project
Copy each Swift file into the corresponding group

### 4. Update App File
```swift
@main
struct MomotaroApp: App {
    @StateObject var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}
```

### 5. Build & Run
```bash
Cmd + B  # Build
Cmd + R  # Run on simulator
Cmd + U  # Run tests
```

## 🏗️ Architecture

### Data Flow
```
User Input (View) 
    ↓
ViewModel Method Called
    ↓
Service Layer (Network/Storage/Gateway)
    ↓
Models Updated
    ↓
ViewModel @Published Updated
    ↓
View Re-renders (Reactive)
```

### State Management
All app state flows through `AppState`:

```swift
@EnvironmentObject var appState: AppState

// Access in any view
Text("User: \(appState.currentUser?.username ?? "Guest")")
```

## 🌐 Network Layer

### Making API Calls
```swift
let networkService = NetworkService()
networkService.fetchPeaches { result in
    switch result {
    case .success(let peaches):
        print("Got \(peaches.count) peaches")
    case .failure(let error):
        print("Error: \(error.errorDescription ?? "")")
    }
}
```

### Error Handling
```swift
enum NetworkError: Error {
    case badURL
    case requestFailed(URLError)
    case decodingError(DecodingError)
    case serverError(statusCode: Int)
    case noData
}
```

## 🔌 WebSocket Integration

### Connect to Gateway
```swift
let wsManager = WebSocketManager(
    gatewayURL: URL(string: "wss://gateway.openclaw.local/ws")!
)
wsManager.connect()
```

### Send Messages
```swift
let message = try GatewayMessage(
    messageType: "command",
    content: "action_data"
)
wsManager.send(message)
```

### Receive Messages
```swift
@ObservedObject var wsManager: WebSocketManager

var body: some View {
    if let message = wsManager.lastMessage {
        Text("Message: \(message.content)")
    }
}
```

### Monitor Connection
```swift
switch wsManager.connectionState {
case .connected:
    Text("✅ Connected")
case .connecting:
    Text("⏳ Connecting...")
case .error(let desc):
    Text("❌ Error: \(desc)")
case .reconnecting(let attempt):
    Text("🔄 Reconnecting (\(attempt)/5)")
case .disconnected:
    Text("⭕ Disconnected")
}
```

## 💾 Local Storage

### Save Data
```swift
let storageService = StorageService()

// UserDefaults
try storageService.persist(user, forKey: "currentUser")

// File system
try storageService.writeToFile(peaches, filename: "peaches.json")
```

### Retrieve Data
```swift
// From UserDefaults
let user: User? = try storageService.retrieve(forKey: "currentUser")

// From file system
let peaches: [Peach]? = try storageService.readFromFile(filename: "peaches.json")
```

## 🧪 Testing

### Run Tests
```bash
Cmd + U  # Run all tests
```

### Test Structure
```swift
class NetworkServiceTests: XCTestCase {
    var sut: NetworkService!
    var mockSession: MockURLSession!
    
    func testFetchPeachesSuccess() {
        // Arrange
        // Act
        // Assert
    }
}
```

### Mock Objects Available
- `MockURLSession` — Mock network responses
- `MockNetworkService` — Mock API calls
- `MockStorageService` — Mock persistence

## 📱 Views

### PeachListView
Main view for displaying peach list with search, sort, and filter

**Features:**
- Search functionality
- Sort by name/ripeness/color
- Filter by criteria
- Error states
- Loading indicator

### SettingsView
Settings screen with @EnvironmentObject access to AppState

### ContentView
Navigation root view

## 🛠️ ViewModels

### AppState
Centralized application state
- `isLoggedIn` — Authentication status
- `currentUser` — Current user
- `peaches` — Peach list data
- `networkError` — Error tracking
- `connectionState` — WebSocket connection state

### PeachViewModel
Manage peach operations
- `loadPeaches()` — Fetch from network
- `sortPeaches(by:)` — Sort list
- `filterPeaches()` — Filter by criteria

### UserViewModel
User authentication
- `authenticate()` — Login user
- `logout()` — Clear user
- `changePassword()` — Update password

## 📚 Documentation

Read the comprehensive guides:

1. **ARCHITECTURE.md** — System design and data flow
2. **INTEGRATION.md** — Step-by-step setup instructions
3. **TESTING.md** — Testing strategies and examples
4. **WEBSOCKET.md** — WebSocket connection guide

## ⚙️ Configuration

### Update API Endpoints
In `Services/NetworkService.swift`:
```swift
private let baseURL: String = "https://your-api.com"
```

### Update WebSocket URL
In `Services/WebSocketManager.swift`:
```swift
gatewayURL: URL(string: "wss://your-gateway.com/ws")!
```

### Logging
Enable debug logging in `Utilities/Helpers/Logger.swift`

## 🔐 Security Best Practices

1. **Token Management**
   - Store tokens securely (don't use UserDefaults)
   - Implement token refresh logic
   - Handle expired tokens gracefully

2. **Network Security**
   - Use HTTPS/WSS only
   - Implement certificate pinning
   - Validate SSL certificates

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Use keychain for credentials
   - Clear sensitive data on logout

## 🐛 Debugging

### Enable Verbose Logging
```swift
Logger.log("Debug message")
```

### Monitor Network Calls
- Use Charles Proxy
- Check Xcode Network Link Conditioner
- Enable URLSession logging

### Debug State Changes
- Use Xcode breakpoints
- Print AppState changes
- Monitor @Published updates

## ⚡ Performance Optimization

1. **Memory Management**
   - Use `[weak self]` in closures
   - Clean up timers and subscriptions
   - Implement image caching

2. **Network Optimization**
   - Cache responses locally
   - Implement request batching
   - Use pagination for large lists

3. **UI Performance**
   - Lazy load images
   - Use `.onAppear` for initial data
   - Optimize list rendering

## 🚀 Deployment

### Before Release
- [ ] Run all tests (`Cmd + U`)
- [ ] Check code coverage
- [ ] Profile with Instruments
- [ ] Test on real devices
- [ ] Update API endpoints
- [ ] Verify certificate pinning
- [ ] Review error handling
- [ ] Update privacy policy

### App Store Submission
```bash
# Archive for upload
Product → Archive
```

## 📈 Future Enhancements

- [ ] Implement Combine reactive streams
- [ ] Add async/await support
- [ ] Implement Redux-style state management
- [ ] Add UI tests with XCUITest
- [ ] Implement snapshot testing
- [ ] Add analytics tracking
- [ ] Support offline mode with sync

## 🤝 Contributing

1. Follow MVVM architecture
2. Add unit tests for new code
3. Update documentation
4. Run full test suite before PR

## 📖 Learning Resources

- [Apple SwiftUI Documentation](https://developer.apple.com/tutorials/swiftui)
- [MVVM Pattern Guide](https://www.raywenderlich.com/4001-mvvm-in-swift-5)
- [Combine Framework](https://developer.apple.com/documentation/combine)
- [URLSession Guide](https://developer.apple.com/documentation/foundation/urlsession)

## 📄 License

This code is provided as-is for the Momotaro-iOS project.

## 🆘 Support

For issues or questions:
1. Check documentation files
2. Review test cases for examples
3. Check error messages and logs
4. Consult Apple documentation

## 🎉 Summary

Momotaro-iOS provides a solid foundation with:
- ✅ Clean, maintainable architecture
- ✅ Real-time WebSocket support
- ✅ Comprehensive error handling
- ✅ Full unit test coverage
- ✅ Production-ready code
- ✅ Complete documentation

Happy coding! 🍑
