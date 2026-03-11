// ViewModels/PeachViewModel.swift
// ViewModel for managing peach-related operations

import Foundation
import SwiftUI

/// ViewModel for managing peach data and operations
class PeachViewModel: ObservableObject {
    @Published var peaches: [Peach] = []
    @Published var filteredPeaches: [Peach] = []
    @Published var errorMessage: String?
    @Published var isLoading = false
    
    private let networkService: NetworkService
    private let storageService = StorageService()
    
    init(networkService: NetworkService = NetworkService()) {
        self.networkService = networkService
        loadPeaches()
    }
    
    // MARK: - Data Loading
    
    /// Load peaches from network
    func loadPeaches() {
        isLoading = true
        
        networkService.fetchPeaches { [weak self] result in
            DispatchQueue.main.async { [weak self] in
                self?.isLoading = false
                
                switch result {
                case .success(let peaches):
                    self?.peaches = peaches
                    self?.filteredPeaches = peaches
                    self?.errorMessage = nil
                    
                    // Cache peaches
                    try? self?.storageService.writeToFile(peaches, filename: "peaches.json")
                    
                case .failure(let error):
                    self?.errorMessage = error.errorDescription ?? "Unknown error"
                    
                    // Load from cache if network fails
                    if let cachedPeaches: [Peach] = try? self?.storageService.readFromFile(filename: "peaches.json") {
                        self?.peaches = cachedPeaches
                        self?.filteredPeaches = cachedPeaches
                    }
                }
            }
        }
    }
    
    // MARK: - Sorting
    
    /// Sort peaches by specified criteria
    func sortPeaches(by criteria: SortCriteria) {
        peaches.sort { criteria.compare($0, $1) }
        filteredPeaches = peaches
    }
    
    /// Sort peaches by name ascending
    func sortByName() {
        sortPeaches(by: .byName)
    }
    
    /// Sort peaches by ripeness descending
    func sortByRipeness() {
        sortPeaches(by: .byRipeness)
    }
}

// MARK: - Filtering Extension

extension PeachViewModel {
    /// Filter peaches by search query
    func filterPeaches(with query: String) {
        guard !query.trimmingCharacters(in: .whitespaces).isEmpty else {
            filteredPeaches = peaches
            return
        }
        
        let lowercaseQuery = query.lowercased()
        filteredPeaches = peaches.filter { peach in
            peach.name.lowercased().contains(lowercaseQuery) ||
            peach.color.lowercased().contains(lowercaseQuery)
        }
    }
    
    /// Filter peaches by ripeness range
    func filterPeaches(minRipeness: Int, maxRipeness: Int) {
        filteredPeaches = peaches.filter { peach in
            peach.ripeness >= minRipeness && peach.ripeness <= maxRipeness
        }
    }
    
    /// Filter peaches by color
    func filterPeaches(byColor color: String) {
        filteredPeaches = peaches.filter { $0.color.lowercased() == color.lowercased() }
    }
}

// MARK: - Statistics Extension

extension PeachViewModel {
    /// Get average ripeness of all peaches
    var averageRipeness: Int {
        guard !peaches.isEmpty else { return 0 }
        let sum = peaches.reduce(0) { $0 + $1.ripeness }
        return sum / peaches.count
    }
    
    /// Get peaches above a certain ripeness level
    func ripePeaches(minRipeness: Int = 75) -> [Peach] {
        peaches.filter { $0.ripeness >= minRipeness }
    }
    
    /// Get count of peaches by color
    func countByColor() -> [String: Int] {
        var colorCount: [String: Int] = [:]
        for peach in peaches {
            colorCount[peach.color, default: 0] += 1
        }
        return colorCount
    }
}
