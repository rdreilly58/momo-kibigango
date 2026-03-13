// ViewModels/AppState.swift
// Centralized application state management

import Foundation
import SwiftUI

/// Central state management for the application
class AppState: ObservableObject {
    @Published var isLoggedIn = false
    @Published var currentUser: User?
    @Published var networkError: NetworkError?
    @Published var peaches: [Peach] = []
    @Published var connectionState: ConnectionState = .disconnected
    
    private let storageService = StorageService()
    
    init() {
        loadStoredUser()
    }
    
    /// Load user from storage
    private func loadStoredUser() {
        do {
            if let storedUser = try storageService.retrieve(forKey: "currentUser", as: User.self) {
                DispatchQueue.main.async { [weak self] in
                    self?.currentUser = storedUser
                    self?.isLoggedIn = true
                }
            }
        } catch {
            print("Failed to load stored user: \(error.localizedDescription)")
        }
    }
    
    /// Set logged-in user
    func setUser(_ user: User) {
        DispatchQueue.main.async { [weak self] in
            self?.currentUser = user
            self?.isLoggedIn = true
            
            // Persist user to storage
            do {
                try self?.storageService.persist(user, forKey: "currentUser")
            } catch {
                print("Failed to persist user: \(error.localizedDescription)")
            }
        }
    }
    
    /// Clear user and logout
    func logout() {
        DispatchQueue.main.async { [weak self] in
            self?.currentUser = nil
            self?.isLoggedIn = false
            self?.peaches = []
            
            // Remove from storage
            self?.storageService.remove(forKey: "currentUser")
        }
    }
    
    /// Update network error
    func setNetworkError(_ error: NetworkError?) {
        DispatchQueue.main.async { [weak self] in
            self?.networkError = error
        }
    }
    
    /// Update peaches
    func setPeaches(_ peaches: [Peach]) {
        DispatchQueue.main.async { [weak self] in
            self?.peaches = peaches
        }
    }
    
    /// Update connection state
    func setConnectionState(_ state: ConnectionState) {
        DispatchQueue.main.async { [weak self] in
            self?.connectionState = state
        }
    }
    
    /// Clear error
    func clearError() {
        DispatchQueue.main.async { [weak self] in
            self?.networkError = nil
        }
    }
}
