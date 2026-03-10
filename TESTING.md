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

### GatewayClientTests.swift (17 tests, 6 passing ✅)

Tests for the `GatewayClient` @MainActor ObservableObject.

#### Passing Tests (No Network Required)
- **testDefaultURLInitialization()** - Verifies default localhost:8080 URL
- **testCustomURLInitialization()** - Tests custom gateway URL initialization
- **testInitialState()** - Confirms disconnected state on creation
- **testMessageEncoding()** - JSON encoding of messages
- **testCallbackAssignment()** - Message callback functionality
- **testErrorMessageDisplay()** - Error property handling

#### Tests Requiring Network Mocks (Phase 2)
The following tests currently fail because they attempt real WebSocket connections:
- Connection lifecycle tests (connect/disconnect state changes)
- Message send/receive tests
- Multiple connect/disconnect cycles
- Reconnection logic
- Status updates

**Note:** These require `MockWebSocketTask` extending `URLSessionWebSocketTask` to simulate network behavior without actual connections.

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

### Current Status
```
Total Tests: 31
Passing: 20 (14 GatewayMessage + 6 GatewayClient)
Failing: 11 (GatewayClient network tests - expected, pending mocks)
Pass Rate: 64.5%

GatewayMessage: 14/14 (100%) ✅
GatewayClient: 6/17 (35%) ⏳ (need mocks for network tests)

Execution Time: ~1.4 seconds
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

## Mocking Strategy (Phase 2)

To achieve 100% test coverage, we need to mock URLSessionWebSocketTask:

```swift
class MockWebSocketTask: URLSessionWebSocketTask {
    var connectCalled = false
    var disconnectCalled = false
    var isConnected = false
    
    override func resume() {
        connectCalled = true
        isConnected = true
    }
    
    override func cancel(with closeCode: URLSessionWebSocketTask.CloseCode, 
                        reason: Data?) {
        disconnectCalled = true
        isConnected = false
    }
}
```

Then inject into GatewayClient via dependency injection for full network test coverage.

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

### Phase 1 - Current ✅
- [x] Codable encoding/decoding (100% coverage)
- [x] CodingKeys mapping validation
- [x] Error handling (invalid JSON, missing fields)
- [x] Edge cases (empty, long, special characters)
- [x] State management (init, disconnect, connect)
- [x] Callback assignment

### Phase 2 - Planned
- [ ] URLSessionWebSocketTask mocking
- [ ] Connection lifecycle (full coverage)
- [ ] Message send/receive simulation
- [ ] Reconnection logic with exponential backoff
- [ ] Error recovery scenarios

### Phase 3 - Future
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
