// Utilities/Extensions/String+Extensions.swift
// String utility extensions

import Foundation

extension String {
    /// Check if string contains only numeric characters
    var isNumeric: Bool {
        return Double(self) != nil
    }
    
    /// Check if string is a valid email address
    var isValidEmail: Bool {
        let emailPattern = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
        return NSPredicate(format: "SELF MATCHES %@", emailPattern).evaluate(with: self)
    }
    
    /// Trim whitespace from both ends
    var trimmed: String {
        return trimmingCharacters(in: .whitespaces)
    }
    
    /// Check if string is empty after trimming
    var isTrimmedEmpty: Bool {
        return trimmed.isEmpty
    }
    
    /// Capitalize first character
    var capitalizedFirst: String {
        guard !self.isEmpty else { return self }
        return prefix(1).uppercased() + dropFirst()
    }
    
    /// Get character count excluding whitespace
    var characterCountWithoutSpaces: Int {
        return replacingOccurrences(of: " ", with: "").count
    }
}
