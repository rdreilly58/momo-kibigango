# Momotaro-iOS Unit Tests Documentation

## Overview

This document describes the comprehensive unit test suite for the Momotaro-iOS WebSocket Gateway Client implementation.

## Test Structure

### Files

```
Tests/
├── GatewayClientTests.swift     - WebSocket client lifecycle and connection tests
├── GatewayMessageTests.swift    - Message encoding/decoding and Codable tests
└── Mocks/
    └── MockWebSocketTask.swift  - Mock URLSessionWebSocketTask for isolation
```

### Test Statistics

- **Total test cases**: 25+
- **Lines of test code**: 583
- **Framework**: XCTest with async/await support
- **Target**: iOS 17.0+

## Test Coverage

### 1. GatewayClientTests.swift (15 test cases)

#### Initialization Tests (3 tests)
- `testDefaultURLInitialization` - Verifies client initializes with default URL
- `testCustomURLInitialization` - Verifies custom URL can be set during initialization
- `testInitialState` - Verifies initial disconnected state and no error messages

#### Connection Lifecycle Tests (4 tests)
- `testConnectChangesConnectionState` - Verifies connect() sets isConnected to true
- `testDisconnectChangesConnectionState` - Verifies disconnect() sets isConnected to false
- `testErrorCallbackOnConnectionFailure` - Verifies error callback fires on failure
- `testConnectDisconnectConnectCycle` - Tests full state transition cycle

#### Message Handling Tests (2 tests)
- `testSendCommandCreatesMessage` - Verifies sendCommand creates valid message
- `testInvalidJSONHandling` - Verifies graceful handling of invalid JSON

#### Reconnection Logic Tests (3 tests)
- `testReconnectionAttemptsLimit` - Verifies max 5 reconnection attempts
- `testExponentialBackoffTiming` - Verifies exponential backoff calculation
- `testReconnectionErrorMessageIncludesAttemptCount` - Verifies error reporting

#### Robustness Tests (2 tests)
- `testMultipleDisconnectsCalled` - Verifies multiple disconnects don't crash
- Edge cases and error conditions

### 2. GatewayMessageTests.swift (10+ test cases)

#### Encoding Tests (3 tests)
- `testBasicMessageEncoding` - Basic JSON encoding
- `testMessageEncodingWithData` - Encoding with payload
- `testCodingKeysMapping` - Verifies session_id key mapping

#### Decoding Tests (4 tests)
- `testBasicMessageDecoding` - Basic JSON decoding
- `testMessageDecodingWithData` - Decoding with payload
- `testDecodingMissingOptionalFields` - Handles missing optional fields
- `testDecodingWithNullValues` - Handles null values gracefully

#### Round-Trip Tests (2 tests)
- `testRoundTripEncodeDecodeBasic` - Encode/decode consistency
- `testRoundTripWithComplexData` - Complex data consistency

#### Edge Cases (3 tests)
- `testEmptyCommandString` - Empty string handling
- `testLongCommandString` - Large string handling (1000 chars)
- `testSpecialCharactersInCommand` - Special character preservation

#### AnyCodable Tests (2 tests)
- `testAnyCodableMultipleTypes` - Multiple data types
- `testAnyCodableNestedArray` - Nested array structures

#### Error Handling Tests (2 tests)
- `testInvalidJSONDecoding` - Invalid JSON raises error
- `testDecodingMissingCommand` - Missing required field raises error

## Mock Objects

### MockURLSessionWebSocketTask

Provides isolation from real network calls:

```swift
class MockURLSessionWebSocketTask: URLSessionWebSocketTask {
    var isResumed: Bool
    var isCancelled: Bool
    var messageQueue: [URLSessionWebSocketTask.Message]
    var shouldFailOnReceive: Bool
}
```

**Features:**
- Simulates connection success/failure
- Queues messages for testing receive callbacks
- Tracks resume/cancel calls
- No real network I/O

### MockURLSession

Provides mock WebSocket creation:

```swift
class MockURLSession: URLSession {
    var mockWebSocketTask: MockURLSessionWebSocketTask?
    var webSocketURL: URL?
}
```

## Test Categories

### Happy Path Tests
- ✅ Default initialization
- ✅ Custom URL initialization
- ✅ Connect/disconnect cycle
- ✅ Message sending
- ✅ JSON encoding/decoding

### Error Path Tests
- ✅ Connection failures
- ✅ Invalid JSON handling
- ✅ Reconnection with backoff
- ✅ Error message generation
- ✅ Missing required fields

### Edge Cases
- ✅ Empty strings
- ✅ Very long strings (1000+ chars)
- ✅ Special characters
- ✅ Null values
- ✅ Nested structures
- ✅ Multiple disconnect calls

## Data Models

### GatewayMessage

```swift
struct GatewayMessage: Codable, Equatable {
    let sessionId: String?           // Maps to "session_id"
    let command: String
    let data: [String: AnyCodable]?
    let timestamp: Date?
}
```

### AnyCodable

Heterogeneous type support:
- `null` - Null values
- `bool` - Boolean values
- `int` - Integer values
- `double` - Floating point values
- `string` - String values
- `array` - Array structures
- `object` - Dictionary structures

## Running Tests

### Prerequisites
- Xcode 15.0+
- iOS 17.0+ deployment target
- Swift 5.9+

### Run All Tests
```bash
cd momotaro-ios
xcodebuild test -scheme Momotaro-iOS
```

### Run Specific Test Suite
```bash
xcodebuild test -scheme Momotaro-iOS -only-testing Momotaro-iOSTests/GatewayClientTests
```

### Run Single Test
```bash
xcodebuild test -scheme Momotaro-iOS -only-testing Momotaro-iOSTests/GatewayClientTests/testConnectDisconnectConnectCycle
```

## Test Assumptions & Limitations

### Assumptions
1. **@MainActor**: All tests marked with @MainActor for UI state handling
2. **Async/Await**: Tests use modern async/await patterns
3. **Mock Network**: All network calls mocked (no real server required)
4. **Isolated State**: Each test independent with setUp/tearDown

### Limitations
1. Real WebSocket handshake not tested (use integration tests)
2. Real message streaming not tested (use integration tests)
3. Network timing not validated (mock-based testing)
4. Device-specific behavior not covered (unit level)

## Adding New Tests

### Template

```swift
/// Test description
func testFeatureName() async throws {
    // Setup
    let client = GatewayClient(url: URL(string: "ws://localhost:8080")!)
    
    // Action
    client.connect()
    
    // Assertion
    XCTAssertTrue(client.isConnected)
}
```

### Best Practices

1. **One concept per test** - Each test validates one behavior
2. **Descriptive names** - Use `test<Feature><Scenario><Expected>`
3. **Setup/Teardown** - Use override methods for common setup
4. **Assertions** - Multiple assertions OK if testing one concept
5. **Comments** - Explain non-obvious test logic
6. **Isolation** - Each test should be independent

## Continuous Integration

These tests are designed to:
- ✅ Run without external dependencies
- ✅ Complete in < 10 seconds
- ✅ Have deterministic results
- ✅ Work in CI/CD pipelines

## Future Enhancements

### Integration Tests
- Real WebSocket server testing
- Network error simulation
- Message streaming verification
- Reconnection in real conditions

### Performance Tests
- Memory leak detection
- CPU usage under load
- Battery impact assessment
- Network efficiency

### UI Tests
- Gateway status display
- Error message presentation
- Connection state animations
- Message delivery feedback

## Notes

- All tests use ISO8601 date encoding for consistency
- GatewayMessage timestamp includes millisecond precision
- Mock objects don't simulate real WebSocket protocol
- Consider performance impact of 25+ unit tests in CI/CD
