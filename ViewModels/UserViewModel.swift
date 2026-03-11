// ViewModels/UserViewModel.swift
// ViewModel for user authentication and management

import Foundation
import SwiftUI

/// ViewModel for managing user authentication
class UserViewModel: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var errorMessage: String?
    @Published var isLoading = false
    
    private let storageService = StorageService()
    
    // MARK: - Authentication
    
    /// Authenticate user with credentials
    func authenticate(username: String, password: String) {
        isLoading = true
        errorMessage = nil
        
        // Simulate network request
        DispatchQueue.global().asyncAfter(deadline: .now() + 1.0) { [weak self] in
            DispatchQueue.main.async { [weak self] in
                // Mock authentication - replace with real API call
                if username.count >= 3 && password.count >= 6 {
                    let user = User(
                        id: UUID().uuidString,
                        username: username,
                        email: "\(username)@example.com",
                        token: "token_\(UUID().uuidString)"
                    )
                    
                    self?.setUser(user)
                    self?.isLoading = false
                } else {
                    self?.errorMessage = "Invalid username or password"
                    self?.isLoading = false
                }
            }
        }
    }
    
    /// Set authenticated user
    private func setUser(_ user: User) {
        currentUser = user
        isAuthenticated = true
        
        // Persist user
        do {
            try storageService.persist(user, forKey: "currentUser")
        } catch {
            errorMessage = "Failed to save user: \(error.localizedDescription)"
        }
    }
    
    /// Logout current user
    func logout() {
        currentUser = nil
        isAuthenticated = false
        storageService.remove(forKey: "currentUser")
    }
    
    /// Load stored user if exists
    func loadStoredUser() {
        do {
            if let user = try storageService.retrieve(forKey: "currentUser", as: User.self) {
                currentUser = user
                isAuthenticated = true
            }
        } catch {
            print("Failed to load stored user: \(error.localizedDescription)")
        }
    }
    
    /// Change user password
    func changePassword(currentPassword: String, newPassword: String) {
        guard isAuthenticated else {
            errorMessage = "User not authenticated"
            return
        }
        
        // Validate passwords
        guard currentPassword.count >= 6 else {
            errorMessage = "Current password is invalid"
            return
        }
        
        guard newPassword.count >= 6 else {
            errorMessage = "New password must be at least 6 characters"
            return
        }
        
        // Simulate password change
        isLoading = true
        DispatchQueue.global().asyncAfter(deadline: .now() + 1.0) { [weak self] in
            DispatchQueue.main.async { [weak self] in
                self?.isLoading = false
                self?.errorMessage = nil
                // In real app, update on server
            }
        }
    }
    
    /// Check if user token is still valid
    func isTokenValid() -> Bool {
        return isAuthenticated && currentUser?.token != nil
    }
}
