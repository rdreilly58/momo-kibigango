// GatewayMessage - Protocol message for WebSocket communication
//
// Represents messages sent and received via the WebSocket gateway.
// Supports JSON encoding/decoding for network transmission.

import Foundation

/// Message structure for WebSocket gateway communication
/// Conforms to Codable for automatic JSON serialization
struct GatewayMessage: Codable, Equatable {
    /// Unique session identifier
    let sessionId: String?
    
    /// Message command or action type
    let command: String
    
    /// Optional message payload/data
    let data: [String: AnyCodable]?
    
    /// Message timestamp
    let timestamp: Date?
    
    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case command
        case data
        case timestamp
    }
    
    /// Initialize a GatewayMessage
    /// - Parameters:
    ///   - command: The command/action type
    ///   - sessionId: Optional session identifier
    ///   - data: Optional payload dictionary
    ///   - timestamp: Optional timestamp (defaults to now)
    init(command: String, sessionId: String? = nil, data: [String: AnyCodable]? = nil, timestamp: Date? = nil) {
        self.command = command
        self.sessionId = sessionId
        self.data = data
        self.timestamp = timestamp ?? Date()
    }
}

/// Wrapper for Codable Any values
/// Allows encoding/decoding of heterogeneous dictionary values
enum AnyCodable: Codable, Equatable {
    case null
    case bool(Bool)
    case int(Int)
    case double(Double)
    case string(String)
    case array([AnyCodable])
    case object([String: AnyCodable])
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        if container.decodeNil() {
            self = .null
        } else if let bool = try? container.decode(Bool.self) {
            self = .bool(bool)
        } else if let int = try? container.decode(Int.self) {
            self = .int(int)
        } else if let double = try? container.decode(Double.self) {
            self = .double(double)
        } else if let string = try? container.decode(String.self) {
            self = .string(string)
        } else if let array = try? container.decode([AnyCodable].self) {
            self = .array(array)
        } else if let object = try? container.decode([String: AnyCodable].self) {
            self = .object(object)
        } else {
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "Cannot decode AnyCodable")
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        
        switch self {
        case .null:
            try container.encodeNil()
        case .bool(let bool):
            try container.encode(bool)
        case .int(let int):
            try container.encode(int)
        case .double(let double):
            try container.encode(double)
        case .string(let string):
            try container.encode(string)
        case .array(let array):
            try container.encode(array)
        case .object(let object):
            try container.encode(object)
        }
    }
}
