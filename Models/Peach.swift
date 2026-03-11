// Models/Peach.swift
// Data model representing a peach with Codable support for JSON serialization

import Foundation

/// Represents a peach entity in the Momotaro application
/// Conforms to Codable for easy JSON encoding/decoding
struct Peach: Codable, Identifiable {
    let id: String
    let name: String
    let ripeness: Int // 0-100 scale
    let color: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case ripeness
        case color
    }
    
    init(id: String, name: String, ripeness: Int, color: String) {
        self.id = id
        self.name = name
        self.ripeness = max(0, min(100, ripeness)) // Clamp to 0-100
        self.color = color
    }
}
