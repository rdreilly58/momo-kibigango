import XCTest
@testable import Momotaro

class GatewayMessageTests: XCTestCase {
    
    // MARK: - Encoding Tests
    
    func testEncodeToJSON() throws {
        let message = GatewayMessage(
            type: "message",
            content: "Hello",
            sessionId: "session123",
            timestamp: "2026-03-10T13:48:00Z"
        )
        let encoder = JSONEncoder()
        let jsonData = try encoder.encode(message)
        let json = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any]
        
        XCTAssertEqual(json?["type"] as? String, "message")
        XCTAssertEqual(json?["content"] as? String, "Hello")
    }
    
    func testEncodeWithSessionID() throws {
        let message = GatewayMessage(
            type: "message",
            content: "Test",
            sessionId: "12345",
            timestamp: "2026-03-10T13:48:00Z"
        )
        let encoder = JSONEncoder()
        let jsonData = try encoder.encode(message)
        let json = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any]
        
        // CodingKeys maps sessionId to session_id
        XCTAssertEqual(json?["session_id"] as? String, "12345")
    }
    
    func testEncodeTimestamp() throws {
        let timestamp = "2026-03-10T13:48:00Z"
        let message = GatewayMessage(
            type: "message",
            content: "Test",
            sessionId: nil,
            timestamp: timestamp
        )
        let encoder = JSONEncoder()
        let jsonData = try encoder.encode(message)
        let json = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any]
        
        XCTAssertEqual(json?["timestamp"] as? String, timestamp)
    }
    
    // MARK: - Decoding Tests
    
    func testDecodeFromJSON() throws {
        let jsonString = """
        {
            "type": "message",
            "content": "Hello",
            "timestamp": "2026-03-10T13:48:00Z"
        }
        """
        let jsonData = jsonString.data(using: .utf8)!
        let decoder = JSONDecoder()
        let message = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertEqual(message.type, "message")
        XCTAssertEqual(message.content, "Hello")
    }
    
    func testDecodingWithAllFields() throws {
        let jsonString = """
        {
            "type": "message",
            "content": "Hello",
            "session_id": "12345",
            "timestamp": "2026-03-10T13:48:00Z"
        }
        """
        let jsonData = jsonString.data(using: .utf8)!
        let decoder = JSONDecoder()
        let message = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertEqual(message.type, "message")
        XCTAssertEqual(message.content, "Hello")
        XCTAssertEqual(message.sessionId, "12345")
        XCTAssertEqual(message.timestamp, "2026-03-10T13:48:00Z")
    }
    
    func testDecodingWithOptionalFields() throws {
        let jsonString = """
        {
            "type": "message",
            "content": "Hello",
            "timestamp": "2026-03-10T13:48:00Z"
        }
        """
        let jsonData = jsonString.data(using: .utf8)!
        let decoder = JSONDecoder()
        let message = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertNil(message.sessionId)
    }
    
    // MARK: - CodingKeys Tests
    
    func testSessionIDMapping() throws {
        let jsonString = """
        {
            "type": "message",
            "content": "Test",
            "session_id": "sess_123",
            "timestamp": "2026-03-10T13:48:00Z"
        }
        """
        let jsonData = jsonString.data(using: .utf8)!
        let decoder = JSONDecoder()
        let message = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertEqual(message.sessionId, "sess_123")
    }
    
    func testAllKeysPresent() throws {
        let jsonString = """
        {
            "type": "message",
            "content": "Test",
            "session_id": "12345",
            "timestamp": "2026-03-10T13:48:00Z"
        }
        """
        let jsonData = jsonString.data(using: .utf8)!
        let decoder = JSONDecoder()
        let message = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertNotNil(message)
        XCTAssertEqual(message.type, "message")
        XCTAssertEqual(message.content, "Test")
    }
    
    // MARK: - Edge Cases
    
    func testEmptyContent() throws {
        let message = GatewayMessage(
            type: "message",
            content: "",
            sessionId: nil,
            timestamp: "2026-03-10T13:48:00Z"
        )
        let encoder = JSONEncoder()
        let jsonData = try encoder.encode(message)
        let json = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any]
        
        XCTAssertEqual(json?["content"] as? String, "")
    }
    
    func testLongContent() throws {
        let longContent = String(repeating: "a", count: 1000)
        let message = GatewayMessage(
            type: "message",
            content: longContent,
            sessionId: nil,
            timestamp: "2026-03-10T13:48:00Z"
        )
        let encoder = JSONEncoder()
        let jsonData = try encoder.encode(message)
        let json = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any]
        
        XCTAssertEqual(json?["content"] as? String, longContent)
    }
    
    func testSpecialCharacters() throws {
        let specialContent = "Hello, 😊🌍\nLine2\t\"quoted\""
        let message = GatewayMessage(
            type: "message",
            content: specialContent,
            sessionId: nil,
            timestamp: "2026-03-10T13:48:00Z"
        )
        let encoder = JSONEncoder()
        let jsonData = try encoder.encode(message)
        let json = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any]
        
        XCTAssertEqual(json?["content"] as? String, specialContent)
    }
    
    func testRoundTripEncodingDecoding() throws {
        let originalMessage = GatewayMessage(
            type: "message",
            content: "Round Trip Test",
            sessionId: "test_123",
            timestamp: "2026-03-10T13:48:00Z"
        )
        
        // Encode
        let encoder = JSONEncoder()
        let jsonData = try encoder.encode(originalMessage)
        
        // Decode
        let decoder = JSONDecoder()
        let decodedMessage = try decoder.decode(GatewayMessage.self, from: jsonData)
        
        XCTAssertEqual(originalMessage.type, decodedMessage.type)
        XCTAssertEqual(originalMessage.content, decodedMessage.content)
        XCTAssertEqual(originalMessage.sessionId, decodedMessage.sessionId)
        XCTAssertEqual(originalMessage.timestamp, decodedMessage.timestamp)
    }
    
    // MARK: - Error Cases
    
    func testInvalidJSON() throws {
        let invalidJsonString = "{ invalid json"
        let invalidJsonData = invalidJsonString.data(using: .utf8)!
        let decoder = JSONDecoder()
        
        XCTAssertThrowsError(try decoder.decode(GatewayMessage.self, from: invalidJsonData))
    }
    
    func testMissingRequiredFields() throws {
        let jsonString = """
        {
            "content": "Missing type and timestamp"
        }
        """
        let jsonData = jsonString.data(using: .utf8)!
        let decoder = JSONDecoder()
        
        XCTAssertThrowsError(try decoder.decode(GatewayMessage.self, from: jsonData))
    }
}
