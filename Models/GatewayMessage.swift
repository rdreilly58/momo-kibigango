// Models/GatewayMessage.swift
// OpenClaw gateway message structure with validation

import Foundation

/// Represents a message from the OpenClaw gateway
/// Includes proper Codable support, validation, and error handling
struct GatewayMessage: Codable, Identifiable {
    let id: UUID
    let messageType: String
    let content: String
    let timestamp: Date
    
    enum CodingKeys: String, CodingKey {
        case id
        case messageType = "type"
        case content
        case timestamp
    }
    
    enum ValidationError: Error, LocalizedError {
        case emptyContent
        case invalidMessageType
        
        var errorDescription: String? {
            switch self {
            case .emptyContent:
                return "Message content cannot be empty."
            case .invalidMessageType:
                return "Message type must be non-empty."
            }
        }
    }
    
    /// Initialize a GatewayMessage with validation
    init(id: UUID = UUID(), messageType: String, content: String, timestamp: Date = Date()) throws {
        guard !content.trimmingCharacters(in: .whitespaces).isEmpty else {
            throw ValidationError.emptyContent
        }
        guard !messageType.trimmingCharacters(in: .whitespaces).isEmpty else {
            throw ValidationError.invalidMessageType
        }
        
        self.id = id
        self.messageType = messageType
        self.content = content
        self.timestamp = timestamp
    }
}
