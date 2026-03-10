// Unit tests for GatewayMessage
//
// Tests cover:
// - JSON encoding and decoding
// - CodingKeys mapping (session_id)
// - Handling of optional fields
// - Codable conformance
// - Edge cases (empty data, null values, etc.)

import XCTest
@testable import Momotaro

@MainActor
final class GatewayMessageTests: XCTestCase {
    
    // MARK: - Encoding Tests
    
    /// Test encoding a basic GatewayMessage to JSON
    func testBasicMessageEncoding() throws {
        let message = GatewayMessage(command: "connect", sessionId: "abc123")
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        
        let jsonData = try encoder.encode(message)
        let jsonString = String(data: jsonData, encoding: .utf8)
        
        XCTAssertNotNil(jsonString, "Message should encode to JSON")
        XCTAssertTrue(jsonString?.contains("\"command\":\"connect\"") ?? false)
        XCTAssertTrue(jsonString?.contains("\"session_id\":\"abc123\"") ?? false)
    }
    
    /// Test encoding with data payload
    func testMessageEncodingWithData() throws {
        let payload = ["temperature": AnyCodable.double(72.5), "humidity": AnyCodable.int(45)]
        let message = GatewayMessage(command: "sensor_data", data: payload)
        
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        let jsonData = try encoder.encode(message)
        let jsonString = String(data: jsonData, encoding: .utf8)
        
        XCTAssertNotNil(jsonString)
        XCTAssertTrue(jsonString?.contains("\"command\":\"sensor_data\"") ?? false)
    }
    
    /// Test CodingKeys mapping (session_id key)
    func testCodingKeysMapping() throws {
        let message = GatewayMessage(command: "test", sessionId: "xyz789")
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        
        let jsonData = try encoder.encode(message)
        let jsonString = String(data: jsonData, encoding: .utf8)
        
        // Verify that session_id is used in JSON, not sessionId
        XCTAssertTrue(jsonString?.contains("\"session_id\"") ?? false)
        XCTAssertFalse(jsonString?.contains("\"sessionId\"") ?? false)
    }
    
    // MARK: - Decoding Tests
    
    /// Test decoding a basic JSON message
    func testBasicMessageDecoding() throws {
        let jsonString = """
        {
            "command": "connect",
            "session_id": "test123",
            "timestamp": "2024-03-10T13:41:00Z"
        }
        """
        let jsonData = jsonString.data(using: .utf8)!
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        let message = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertEqual(message.command, "connect")
        XCTAssertEqual(message.sessionId, "test123")
    }
    
    /// Test decoding with data payload
    func testMessageDecodingWithData() throws {
        let jsonString = """
        {
            "command": "sensor_data",
            "data": {
                "temperature": 72.5,
                "humidity": 45,
                "status": "active"
            }
        }
        """
        let jsonData = jsonString.data(using: .utf8)!
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        let message = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertEqual(message.command, "sensor_data")
        XCTAssertNotNil(message.data)
    }
    
    /// Test decoding missing optional fields
    func testDecodingMissingOptionalFields() throws {
        let jsonString = """
        {
            "command": "disconnect"
        }
        """
        let jsonData = jsonString.data(using: .utf8)!
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        let message = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertEqual(message.command, "disconnect")
        XCTAssertNil(message.sessionId, "sessionId should be nil when not provided")
        XCTAssertNil(message.data, "data should be nil when not provided")
    }
    
    /// Test decoding with null values
    func testDecodingWithNullValues() throws {
        let jsonString = """
        {
            "command": "status",
            "session_id": null,
            "data": null
        }
        """
        let jsonData = jsonString.data(using: .utf8)!
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        let message = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertEqual(message.command, "status")
        XCTAssertNil(message.sessionId)
        XCTAssertNil(message.data)
    }
    
    // MARK: - Round-Trip Tests
    
    /// Test encoding then decoding produces equivalent message
    func testRoundTripEncodeDecodeBasic() throws {
        let original = GatewayMessage(command: "test", sessionId: "session123")
        
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        let jsonData = try encoder.encode(original)
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let decoded = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertEqual(original.command, decoded.command)
        XCTAssertEqual(original.sessionId, decoded.sessionId)
    }
    
    /// Test round-trip with complex data
    func testRoundTripWithComplexData() throws {
        let payload: [String: AnyCodable] = [
            "string": AnyCodable.string("hello"),
            "number": AnyCodable.int(42),
            "float": AnyCodable.double(3.14),
            "bool": AnyCodable.bool(true),
            "null": AnyCodable.null
        ]
        let original = GatewayMessage(
            command: "complex",
            sessionId: "sess456",
            data: payload
        )
        
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        let jsonData = try encoder.encode(original)
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let decoded = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertEqual(original.command, decoded.command)
        XCTAssertEqual(original.sessionId, decoded.sessionId)
    }
    
    // MARK: - Edge Cases
    
    /// Test empty command string
    func testEmptyCommandString() throws {
        let message = GatewayMessage(command: "")
        
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        let jsonData = try encoder.encode(message)
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let decoded = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertEqual(decoded.command, "")
    }
    
    /// Test very long command string
    func testLongCommandString() throws {
        let longCommand = String(repeating: "a", count: 1000)
        let message = GatewayMessage(command: longCommand)
        
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        let jsonData = try encoder.encode(message)
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let decoded = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertEqual(decoded.command.count, 1000)
    }
    
    /// Test special characters in command
    func testSpecialCharactersInCommand() throws {
        let command = "test:command.with-special_chars@123"
        let message = GatewayMessage(command: command)
        
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        let jsonData = try encoder.encode(message)
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let decoded = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertEqual(decoded.command, command)
    }
    
    // MARK: - AnyCodable Tests
    
    /// Test AnyCodable encoding various types
    func testAnyCodableMultipleTypes() throws {
        let values: [String: AnyCodable] = [
            "string": AnyCodable.string("test"),
            "int": AnyCodable.int(123),
            "double": AnyCodable.double(45.67),
            "bool": AnyCodable.bool(true),
            "null": AnyCodable.null
        ]
        
        let encoder = JSONEncoder()
        let jsonData = try encoder.encode(values)
        
        let decoder = JSONDecoder()
        let decoded = try decoder.decode([String: AnyCodable].self, from: jsonData)
        
        XCTAssertEqual(decoded["string"], AnyCodable.string("test"))
        XCTAssertEqual(decoded["int"], AnyCodable.int(123))
    }
    
    /// Test AnyCodable with nested arrays
    func testAnyCodableNestedArray() throws {
        let array = AnyCodable.array([
            AnyCodable.string("first"),
            AnyCodable.int(2),
            AnyCodable.double(3.0)
        ])
        
        let encoder = JSONEncoder()
        let jsonData = try encoder.encode(array)
        
        let decoder = JSONDecoder()
        let decoded = try decoder.decode(AnyCodable.self, from: jsonData)
        
        if case .array(let items) = decoded {
            XCTAssertEqual(items.count, 3)
        } else {
            XCTFail("Expected array type")
        }
    }
    
    // MARK: - Equality Tests
    
    /// Test message equality
    func testMessageEquality() throws {
        let message1 = GatewayMessage(command: "test", sessionId: "sess1")
        let message2 = GatewayMessage(command: "test", sessionId: "sess1")
        
        // Note: Equality may differ based on timestamp
        // This test assumes timestamps are similar enough
        XCTAssertEqual(message1.command, message2.command)
        XCTAssertEqual(message1.sessionId, message2.sessionId)
    }
    
    // MARK: - Invalid JSON Handling
    
    /// Test decoding invalid JSON raises error
    func testInvalidJSONDecoding() throws {
        let invalidJSON = "{ invalid json }"
        let jsonData = invalidJSON.data(using: .utf8)!
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        XCTAssertThrowsError(
            try decoder.decode(GatewayMessage.self, from: jsonData),
            "Should throw error for invalid JSON"
        )
    }
    
    /// Test decoding missing required command field
    func testDecodingMissingCommand() throws {
        let jsonString = """
        {
            "session_id": "test123"
        }
        """
        let jsonData = jsonString.data(using: .utf8)!
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        XCTAssertThrowsError(
            try decoder.decode(GatewayMessage.self, from: jsonData),
            "Should throw error when command is missing"
        )
    }
}
