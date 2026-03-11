// Utilities/Helpers/Constants.swift
// Application configuration constants

import Foundation

struct Constants {
    // MARK: - API Configuration
    
    /// Base URL for API requests
    static let apiBaseURL = "https://api.peaches.com"
    
    /// WebSocket gateway URL for real-time communication
    static let gatewayURL = "wss://gateway.openclaw.local/ws"
    
    // MARK: - App Configuration
    
    /// Application name
    static let appName = "Momotaro"
    
    /// Application version
    static let appVersion = "1.0.0"
    
    /// Build number
    static let buildNumber = "1"
    
    // MARK: - Network Configuration
    
    /// Default timeout for network requests (seconds)
    static let networkTimeout: TimeInterval = 30
    
    /// Maximum retry attempts for failed requests
    static let maxRetries = 3
    
    /// WebSocket reconnection max attempts
    static let maxReconnectionAttempts = 5
    
    // MARK: - Storage Configuration
    
    /// User defaults suite name
    static let userDefaultsSuite = "com.momotaro.app"
    
    /// Cache directory name
    static let cacheDirectory = "MomotaroCache"
    
    // MARK: - Feature Flags
    
    /// Enable debug logging
    static let debugLoggingEnabled = true
    
    /// Enable WebSocket auto-reconnection
    static let websocketAutoReconnect = true
    
    /// Enable local caching
    static let cachingEnabled = true
}
