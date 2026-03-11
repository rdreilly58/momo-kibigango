// Services/GatewayService.swift
// Service for handling OpenClaw gateway messages

import Foundation

/// Service for parsing and routing gateway messages
struct GatewayService {
    
    /// Message types supported by the gateway
    enum MessageType: String {
        case command = "command"
        case notification = "notification"
        case response = "response"
        case error = "error"
    }
    
    /// Parse a JSON string into a dictionary
    func parseMessage(_ jsonString: String) -> [String: Any]? {
        guard let data = jsonString.data(using: .utf8) else {
            return nil
        }
        
        do {
            if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] {
                return json
            }
        } catch {
            print("Failed to parse message: \(error.localizedDescription)")
        }
        
        return nil
    }
    
    /// Route a message based on its type and content
    func routeMessage(_ message: GatewayMessage, handler: @escaping (MessageType, [String: Any]) -> Void) {
        guard let messageType = MessageType(rawValue: message.messageType) else {
            print("Unknown message type: \(message.messageType)")
            return
        }
        
        let payload: [String: Any] = [
            "id": message.id.uuidString,
            "content": message.content,
            "timestamp": message.timestamp.timeIntervalSince1970
        ]
        
        handler(messageType, payload)
    }
    
    /// Handle command messages
    func handleCommand(_ content: String) -> String {
        // Process command and return response
        return "Command processed: \(content)"
    }
    
    /// Handle notification messages
    func handleNotification(_ content: String) {
        print("Notification received: \(content)")
    }
    
    /// Handle error messages
    func handleError(_ content: String) {
        print("Error from gateway: \(content)")
    }
}
