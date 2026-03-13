// Services/StorageService.swift
// Local storage service using UserDefaults and file system

import Foundation

/// Service for persisting data locally
struct StorageService {
    private let defaults = UserDefaults.standard
    private let fileManager = FileManager.default
    
    private var documentsDirectory: URL {
        fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }
    
    // MARK: - UserDefaults
    
    /// Store data using UserDefaults
    func persist<T: Codable>(_ data: T, forKey key: String) throws {
        let encoder = JSONEncoder()
        let encoded = try encoder.encode(data)
        defaults.set(encoded, forKey: key)
    }
    
    /// Retrieve data from UserDefaults
    func retrieve<T: Codable>(forKey key: String, as type: T.Type) throws -> T? {
        guard let data = defaults.data(forKey: key) else {
            return nil
        }
        let decoder = JSONDecoder()
        return try decoder.decode(T.self, from: data)
    }
    
    /// Remove data from UserDefaults
    func remove(forKey key: String) {
        defaults.removeObject(forKey: key)
    }
    
    // MARK: - File System
    
    /// Write data to file in documents directory
    func writeToFile<T: Codable>(_ data: T, filename: String) throws {
        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted
        let encoded = try encoder.encode(data)
        
        let fileURL = documentsDirectory.appendingPathComponent(filename)
        try encoded.write(to: fileURL, options: .atomic)
    }
    
    /// Read data from file in documents directory
    func readFromFile<T: Codable>(filename: String, as type: T.Type) throws -> T? {
        let fileURL = documentsDirectory.appendingPathComponent(filename)
        
        guard fileManager.fileExists(atPath: fileURL.path) else {
            return nil
        }
        
        let data = try Data(contentsOf: fileURL)
        let decoder = JSONDecoder()
        return try decoder.decode(T.self, from: data)
    }
    
    /// Delete file from documents directory
    func deleteFile(filename: String) throws {
        let fileURL = documentsDirectory.appendingPathComponent(filename)
        try fileManager.removeItem(at: fileURL)
    }
    
    /// List all files in documents directory
    func listFiles() throws -> [String] {
        return try fileManager.contentsOfDirectory(atPath: documentsDirectory.path)
    }
}
