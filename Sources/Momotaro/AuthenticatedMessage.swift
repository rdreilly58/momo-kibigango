// AuthenticatedMessage.swift
// Defines a Codable structure for authenticated messages

import Foundation

struct AuthenticatedMessage: Codable {
    let deviceId: String
    let publicKey: String
    let message: GatewayMessage
    let signature: String
    let timestamp: String
    let nonce: String
}
