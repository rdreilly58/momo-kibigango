import Foundation
import CryptoKit

// MARK: - Models

struct Ed25519KeyPair {
    let publicKey: Data
    let privateKey: Data
}

struct SessionToken: Codable {
    let token: String
    let expiresAt: Date
    let createdAt: Date
}

enum SecurityError: Error, Equatable {
    case keyGenerationFailed
    case keychainError(String)
    case signingFailed
    case invalidToken
    case tokenExpired
    case noPublicKeyFound
    case noPrivateKeyFound
}

// MARK: - SecurityManager

@MainActor
class SecurityManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var error: SecurityError?
    @Published var currentToken: SessionToken?
    
    private let keychainPublicKeyKey = "com.momotaro.device.publicKey"
    private let keychainPrivateKeyKey = "com.momotaro.device.privateKey"
    private let keychainTokenKey = "com.momotaro.session.token"
    
    // MARK: - Initialization
    
    init() {
        // Load existing token on init
        if let token = try? retrieveSessionToken() {
            self.currentToken = token
            self.isAuthenticated = isTokenValid(token)
        }
    }
    
    // MARK: - Keypair Management
    
    func generateKeyPair() async throws -> Ed25519KeyPair {
        do {
            let privateKey = Curve25519.Signing.PrivateKey()
            let publicKey = privateKey.publicKey
            
            return Ed25519KeyPair(
                publicKey: publicKey.rawRepresentation,
                privateKey: privateKey.rawRepresentation
            )
        } catch {
            self.error = .keyGenerationFailed
            throw SecurityError.keyGenerationFailed
        }
    }
    
    func storeKeyPair(_ keypair: Ed25519KeyPair) throws {
        do {
            try storeInKeychain(key: keychainPublicKeyKey, value: keypair.publicKey)
            try storeInKeychain(key: keychainPrivateKeyKey, value: keypair.privateKey)
        } catch {
            self.error = .keychainError("Failed to store keypair")
            throw error
        }
    }
    
    func retrievePublicKey() throws -> Data {
        do {
            return try retrieveFromKeychain(key: keychainPublicKeyKey)
        } catch {
            self.error = .noPublicKeyFound
            throw SecurityError.noPublicKeyFound
        }
    }
    
    func retrievePrivateKey() throws -> Data {
        do {
            return try retrieveFromKeychain(key: keychainPrivateKeyKey)
        } catch {
            self.error = .noPrivateKeyFound
            throw SecurityError.noPrivateKeyFound
        }
    }
    
    // MARK: - Message Signing
    
    func signMessage(_ message: String) async throws -> Data {
        let privateKeyData = try retrievePrivateKey()
        let privateKey = try Curve25519.Signing.PrivateKey(rawRepresentation: privateKeyData)
        
        let messageData = message.data(using: .utf8) ?? Data()
        let signature = try privateKey.signature(for: messageData)
        
        return signature
    }
    
    func verifySignature(_ signature: Data, for message: String, publicKey: Data) -> Bool {
        do {
            let publicKeyObj = try Curve25519.Signing.PublicKey(rawRepresentation: publicKey)
            let messageData = message.data(using: .utf8) ?? Data()
            
            return publicKeyObj.isValidSignature(signature, for: messageData)
        } catch {
            return false
        }
    }
    
    // MARK: - Session Token Management
    
    func storeSessionToken(_ token: SessionToken) throws {
        do {
            let data = try JSONEncoder().encode(token)
            try storeInKeychain(key: keychainTokenKey, value: data)
            self.currentToken = token
            self.isAuthenticated = true
        } catch {
            self.error = .keychainError("Failed to store token")
            throw error
        }
    }
    
    func retrieveSessionToken() throws -> SessionToken? {
        do {
            let data = try retrieveFromKeychain(key: keychainTokenKey)
            let token = try JSONDecoder().decode(SessionToken.self, from: data)
            
            if !isTokenValid(token) {
                self.error = .tokenExpired
                return nil
            }
            
            return token
        } catch {
            // No token found is not an error
            return nil
        }
    }
    
    func isTokenValid(_ token: SessionToken) -> Bool {
        return token.expiresAt > Date()
    }
    
    func clearSessionToken() throws {
        do {
            try deleteFromKeychain(key: keychainTokenKey)
            self.currentToken = nil
            self.isAuthenticated = false
        } catch {
            self.error = .keychainError("Failed to clear token")
            throw error
        }
    }
    
    func refreshToken(currentToken: SessionToken) throws -> SessionToken {
        // Generate new token valid for 24 hours
        let newToken = SessionToken(
            token: UUID().uuidString,
            expiresAt: Date().addingTimeInterval(24 * 60 * 60),
            createdAt: Date()
        )
        
        try storeSessionToken(newToken)
        return newToken
    }
    
    // MARK: - Keychain Operations
    
    private func storeInKeychain(key: String, value: Data) throws {
        // Delete existing item first
        _ = SecItemDelete([
            kSecClass: kSecClassGenericPassword,
            kSecAttrAccount: key
        ] as CFDictionary)
        
        let query = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrAccount: key,
            kSecValueData: value
        ] as CFDictionary
        
        let status = SecItemAdd(query, nil)
        guard status == errSecSuccess else {
            throw SecurityError.keychainError("Failed to store in Keychain: \(status)")
        }
    }
    
    private func retrieveFromKeychain(key: String) throws -> Data {
        let query = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrAccount: key,
            kSecReturnData: true
        ] as CFDictionary
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query, &result)
        
        guard status == errSecSuccess,
              let data = result as? Data else {
            throw SecurityError.keychainError("Failed to retrieve from Keychain: \(status)")
        }
        
        return data
    }
    
    private func deleteFromKeychain(key: String) throws {
        let query = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrAccount: key
        ] as CFDictionary
        
        let status = SecItemDelete(query)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw SecurityError.keychainError("Failed to delete from Keychain: \(status)")
        }
    }
}
