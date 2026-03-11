// Models/User.swift
// User authentication model with token management

import Foundation

/// Represents a user entity with authentication credentials
struct User: Codable, Identifiable {
    let id: String
    let username: String
    let email: String
    let token: String
    let isAdmin: Bool
    
    enum CodingKeys: String, CodingKey {
        case id
        case username
        case email
        case token
        case isAdmin = "is_admin"
    }
    
    init(id: String, username: String, email: String, token: String, isAdmin: Bool = false) {
        self.id = id
        self.username = username
        self.email = email
        self.token = token
        self.isAdmin = isAdmin
    }
}
