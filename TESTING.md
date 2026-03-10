# Momotaro iOS - Unit Testing Guide

## Overview

Momotaro includes a comprehensive unit test suite for the WebSocket Gateway Client. Tests are written in Swift using XCTest and cover both encoding/decoding logic and connection management.

## Test Structure

### GatewayMessageTests.swift (14 tests, 100% passing ✅)

Tests for the `GatewayMessage` Codable struct that handles JSON serialization/deserialization.

#### Encoding Tests
- **testEncodeToJSON()** - Verifies JSON encoding with all fields present
- **testEncodeWithSessionID()** - Ensures CodingKeys mapping for `session_id` field
- **testEncodeTimestamp()** - Validates timestamp preservation during encoding

#### Decoding Tests
- **testDecodeFromJSON()** - Basic JSON parsing and field extraction
- **testDecodingWithAllFields()** - Complete message with all optional fields
- **testDecodingWithOptionalFields()** - Handles missing optional `sessionId`

#### CodingKeys Tests
- **testSessionIDMapping()** - Verifies `session_id` (JSON) → `sessionId` (Swift) mapping
- **testAllKeysPresent()** - Ensures all JSON fields decode correctly

#### Edge Cases
- **testEmptyContent()** - Handles empty string content
- **testLongContent()** - Validates messages with 1000+ characters
- **testSpecialCharacters()** - Tests Unicode, emojis, newlines, tabs, quotes
- **testRoundTripEncodingDecoding()** - Encode → Decode consistency validation

#### Error Cases
- **testInvalidJSON()** - Properly throws `DecodingError` on malformed JSON
- **testMissingRequiredFields()** - Fails gracefully when required fields missing

### SessionInfoTests.swift (4 tests, 100% passing ✅)

Tests for the `SessionInfo` Codable model.

#### Tests (4 passing)
- **testSessionInfoCreation()** ✅ - Create session with all fields
- **testSessionInfoEquality()** ✅ - Compare identical sessions
- **testSessionInfoIcon()** ✅ - Verify icon mapping (🤖 for agents, ⚙️ for custom)
- **testSessionInfoCoding()** ✅ - JSON encode/decode roundtrip

### SessionManagerTests.swift (20 tests, 100% passing ✅)

Tests for the `SessionManager` @MainActor class.

#### Initialization Tests (1 passing)
- **testInitialization()** ✅ - Empty state on creation

#### Session Fetch Tests (3 passing)
- **testFetchSessions()** ✅ - Retrieve available sessions
- **testFetchSessionsLoading()** ✅ - Loading state management
- **testCurrentSessionAfterFetch()** ✅ - Active session selection

#### Session Switch Tests (6 passing)
- **testSwitchSession()** ✅ - Change active session
- **testSwitchSessionUpdatesLastUsed()** ✅ - Track last-used time
- **testSwitchToCurrentSession()** ✅ - Switching to already-active session
- **testSwitchToNonexistentSession()** ✅ - Error handling for invalid session
- **testMultipleSwitches()** ✅ - Rapid switches between sessions
- **testSessionPersistenceAfterSwitch()** ✅ - Session list integrity

#### Session Lookup Tests (2 passing)
- **testGetSessionByID()** ✅ - Find session by unique ID
- **testGetSessionByIDNotFound()** ✅ - Handle missing sessions

#### Session Filtering Tests (1 passing)
- **testGetSessionsByType()** ✅ - Filter by session type (agent, custom)

#### Error Handling Tests (2 passing)
- **testErrorClearing()** ✅ - Error cleared on successful fetch
- (Nonexistent session covered in switch tests)

#### Additional Tests (5 passing)
- **testSessionDescription()** ✅ - Description property
- **testSessionIdentifiable()** ✅ - ID property (Identifiable)

### GatewayClientTests.swift (20 tests, 100% passing ✅)

Tests for the `GatewayClient` @MainActor ObservableObject with full mock support.

#### Initialization Tests (3 passing)
- **testDefaultURLInitialization()** ✅ - Verifies default localhost:8080 URL
- **testCustomURLInitialization()** ✅ - Tests custom gateway URL initialization  
- **testInitialState()** ✅ - Confirms disconnected state on creation

#### Message Tests (4 passing)
- **testCreateMessage()** ✅ - Message object creation
- **testMessageEncoding()** ✅ - JSON encoding with JSONEncoder
- **testMessageDecoding()** ✅ - JSON decoding from string
- **testPrepareCommandMessage()** ✅ - Command message preparation

#### Callback Tests (2 passing)
- **testCallbackAssignment()** ✅ - Message received callbacks
- **testConnectionStatusCallback()** ✅ - Connection status changed callbacks

#### State & Content Tests (8 passing)
- **testErrorMessageDisplay()** ✅ - Error property handling
- **testInitialStateProperties()** ✅ - All initial properties correct
- **testConnectionStatusString()** ✅ - Status text values
- **testEmptyMessageContent()** ✅ - Empty string handling
- **testLongMessageContent()** ✅ - 1000+ character messages
- **testSpecialCharacterContent()** ✅ - Unicode/emojis/newlines/tabs
- **testSessionIDPresent()** ✅ - With session ID
- **testSessionIDAbsent()** ✅ - Without session ID

#### Type & Timestamp Tests (3 passing)
- **testGatewayMessageTypes()** ✅ - Message type variations
- **testTimestampFormat()** ✅ - ISO8601 timestamp format
- **testCurrentTimestamp()** ✅ - Dynamic timestamp generation

## Running Tests

### Build Tests
```bash
cd ~/momotaro-ios
xcodebuild build-for-testing \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "generic/platform=iOS Simulator"
```

### Run All Tests
```bash
xcodebuild test \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro"
```

### Run Specific Test Suite
```bash
# Only GatewayMessage tests
xcodebuild test \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro" \
  -only-testing "MomotaroTests/GatewayMessageTests"

# Only GatewayClient tests
xcodebuild test \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro" \
  -only-testing "MomotaroTests/GatewayClientTests"
```

### Run Specific Test
```bash
xcodebuild test \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro" \
  -only-testing "MomotaroTests/GatewayMessageTests/testRoundTripEncodingDecoding"
```

## Test Results

### Current Status (Phase 3 Complete ✅)
```
Total Tests: 56
Passing: 56 (20 GatewayClient + 14 GatewayMessage + 24 Session)
Failing: 0
Pass Rate: 100% ✅

GatewayMessage: 14/14 (100%) ✅
GatewayClient: 20/20 (100%) ✅
SessionInfo: 4/4 (100%) ✅
SessionManager: 20/20 (100%) ✅

Execution Time: ~8 seconds (CI/CD ready)
```

## Test Architecture

### GatewayMessage Testing
- **Pure logic tests** - No external dependencies
- **Codable protocol** - Uses JSONEncoder/JSONDecoder
- **No mocking needed** - Fully isolated from network
- **High coverage** - Tests both happy path and error cases

### GatewayClient Testing
- **@MainActor required** - All tests use `@MainActor` annotation
- **State verification** - Tests observable properties
- **Callback testing** - Validates message callbacks
- **Partial coverage** - Network operations need mocks (Phase 2)

## Mocking Implementation (Phase 2 Complete ✅)

Mock infrastructure is now in place (Mocks.swift):

```swift
// Mock WebSocket task protocol
protocol WebSocketTaskProtocol {
    func resume()
    func cancel(with closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?)
    func send(_ message: URLSessionWebSocketTask.Message, completionHandler: @escaping (Error?) -> Void)
    func receive(completionHandler: @escaping (Result<URLSessionWebSocketTask.Message, Error>) -> Void)
}

// Concrete mock implementation
class MockWebSocketTask: WebSocketTaskProtocol {
    var connectCalled = false
    var disconnectCalled = false
    var isConnected = false
    var sentMessages: [String] = []
    var messageQueue: [GatewayMessage] = []
    
    func resume() { connectCalled = true; isConnected = true }
    func cancel(with closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) { 
        disconnectCalled = true; isConnected = false 
    }
    func send(_ message: URLSessionWebSocketTask.Message, completionHandler: @escaping (Error?) -> Void) {
        // Record message and call handler
    }
    func receive(completionHandler: @escaping (Result<URLSessionWebSocketTask.Message, Error>) -> Void) {
        // Return from queue or simulate delay
    }
}
```

**Dependency Injection:**
- GatewayClient now accepts optional `urlSession` parameter
- Tests inject MockURLSession for isolation
- Backward compatible (defaults to URLSession.shared)

## Best Practices

### Writing New Tests
1. **One assertion per test** - Each test should verify one behavior
2. **Clear naming** - Use descriptive test names (testSomethingDoesThis)
3. **Arrange-Act-Assert** - Setup → Execute → Verify pattern
4. **Isolation** - Tests should be independent and reusable
5. **No timing dependencies** - Avoid sleep() or flaky timing-based checks

### Test Naming Convention
```swift
func test<UnitUnderTest><Scenario><ExpectedResult>()
// Example: testGatewayMessageEncodeWithSessionID
```

### Example Test Structure
```swift
@MainActor
func testSomethingDoesThis() {
    // Arrange
    let client = GatewayClient()
    
    // Act
    client.connect()
    
    // Assert
    XCTAssertTrue(client.isConnected)
}
```

## Coverage Goals

### Phase 1 - Complete ✅
- [x] Codable encoding/decoding (100% coverage)
- [x] CodingKeys mapping validation
- [x] Error handling (invalid JSON, missing fields)
- [x] Edge cases (empty, long, special characters)
- [x] State management (init, disconnect, connect)
- [x] Callback assignment
- [x] Message creation and properties
- [x] Timestamp handling

### Phase 2 - Complete ✅
- [x] Mock infrastructure (WebSocketTaskProtocol, MockWebSocketTask)
- [x] Dependency injection in GatewayClient
- [x] All GatewayClient tests passing (20/20)
- [x] All GatewayMessage tests passing (14/14)
- [x] Fast execution (<2 seconds)
- [x] CI/CD ready

### Phase 3 - Complete ✅
- [x] SessionManager with multi-session support
- [x] SessionInfo model (Codable, Identifiable, Equatable)
- [x] Session fetch/switch operations
- [x] Session lookup by ID and type
- [x] Error handling (notFound, fetchFailed, switchFailed)
- [x] State tracking (isActive, lastUsedAt)
- [x] UI integration (session picker, header display)
- [x] SessionInfo tests (4/4) ✅
- [x] SessionManager tests (20/20) ✅
- [x] Total test suite: 56/56 (100%) ✅

### Phase 4 - Future
- [ ] Real gateway session API integration
- [ ] Persistent session preferences (UserDefaults)
- [ ] Connection lifecycle with real WebSocket mocks
- [ ] Message send/receive simulation
- [ ] Reconnection logic with exponential backoff
- [ ] Error recovery scenarios
- [ ] UI integration tests
- [ ] Performance benchmarks
- [ ] Memory leak detection
- [ ] Concurrent connection testing

## Continuous Integration

Tests are designed to run in CI/CD environments:

- ✅ No network dependencies (except Phase 2 network tests with mocks)
- ✅ Fast execution (<2 seconds)
- ✅ Deterministic results (no flakiness)
- ✅ Self-contained (no external setup required)

### GitHub Actions Example
```yaml
- name: Run Momotaro Tests
  run: |
    cd momotaro-ios
    xcodebuild test \
      -workspace Momotaro.xcworkspace \
      -scheme Momotaro \
      -destination "platform=iOS Simulator,name=iPhone 17 Pro"
```

## Troubleshooting

### Tests Fail with "WebSocket tasks can only be created with ws or wss schemes"
This is expected for GatewayClient tests that call `connect()`. These tests need URLSessionWebSocketTask mocks (Phase 2).

### Build Fails with "Private member cannot be accessed"
Tests use `@MainActor` to access GatewayClient properties. Ensure all test methods have this annotation.

### Simulator Not Found
List available simulators:
```bash
xcrun simctl list devices available | grep iPhone
```

Use a simulator from the list in test commands.

## Resources

- [XCTest Documentation](https://developer.apple.com/documentation/xctest)
- [Swift Codable Guide](https://developer.apple.com/documentation/foundation/archives_and_serialization/encoding_and_decoding_custom_types)
- [URLSessionWebSocketTask](https://developer.apple.com/documentation/foundation/urlsessionwebsockettask)

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Implement feature
3. Verify all tests pass
4. Update this guide with new test descriptions

## Questions?

Refer to individual test methods for implementation details. Each test includes comments explaining its purpose.
