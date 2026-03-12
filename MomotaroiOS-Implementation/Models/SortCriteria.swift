// Models/SortCriteria.swift
// Enumeration for peach sorting options

import Foundation

/// Defines sorting criteria for peach lists
enum SortCriteria {
    case byName
    case byRipeness
    case byColor
    
    /// Comparator function for sorting
    func compare(_ lhs: Peach, _ rhs: Peach) -> Bool {
        switch self {
        case .byName:
            return lhs.name < rhs.name
        case .byRipeness:
            return lhs.ripeness > rhs.ripeness
        case .byColor:
            return lhs.color < rhs.color
        }
    }
}
