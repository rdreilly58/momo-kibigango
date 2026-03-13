import XCTest
@testable import Momotaro

@MainActor
final class SecurityManagerTests: XCTestCase {
    
    var manager: SecurityManager!
    
    override func setUp() {
        super.setUp()
        manager = SecurityManager()
    }
    
    override func tearDown() {
        // Clean up Keychain items after each test
        try? manager.clearSessionToken()
        manager = nil
        super.tearDown()
    }
    
    // MARK: - Initialization & Setup (2 tests)
    
    func testInitialization() {
        XCTAssertNotNil(manager)
        XCTAssertFalse(manager.isAuthenticated)
        XCTAssertNil(manager.currentToken)
    }
    
    func testInitialStateNotAuthenticated() {
        XCTAssertFalse(manager.isAuthenticated)
        XCTAssertNil(manager.error)
    }
    
    // MARK: - Keypair Generation (4 tests)
    
    func testGenerateKeyPair() async throws {
        let keypair = try await manager.generateKeyPair()
        
        XCTAssertNotNil(keypair)
        XCTAssertFalse(keypair.publicKey.isEmpty)
        XCTAssertFalse(keypair.privateKey.isEmpty)
    }
    
    func testKeyPairConsistency() async throws {
        let keypair = try await manager.generateKeyPair()
        
        XCTAssertNotEqual(keypair.publicKey, keypair.privateKey)
    }
    
    func testKeyPairDataSize() async throws {
        let keypair = try await manager.generateKeyPair()
        
        // Ed25519 keys are 32 bytes
        XCTAssertEqual(keypair.publicKey.count, 32)
        XCTAssertEqual(keypair.privateKey.count, 32)
    }
    
    func testMultipleKeyPairGeneration() async throws {
        let keypair1 = try await manager.generateKeyPair()
        let keypair2 = try await manager.generateKeyPair()
        
        XCTAssertNotEqual(keypair1.publicKey, keypair2.publicKey)
        XCTAssertNotEqual(keypair1.privateKey, keypair2.privateKey)
    }
    
    // MARK: - Keychain Storage (6 tests)
    
    func testStorePublicKey() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        let retrieved = try manager.retrievePublicKey()
        XCTAssertEqual(retrieved, keypair.publicKey)
    }
    
    func testStorePrivateKey() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        let retrieved = try manager.retrievePrivateKey()
        XCTAssertEqual(retrieved, keypair.privateKey)
    }
    
    func testRetrievePublicKey() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        let publicKey = try manager.retrievePublicKey()
        XCTAssertNotNil(publicKey)
        XCTAssertEqual(publicKey.count, 32)
    }
    
    func testRetrievePrivateKey() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        let privateKey = try manager.retrievePrivateKey()
        XCTAssertNotNil(privateKey)
        XCTAssertEqual(privateKey.count, 32)
    }
    
    func testKeychainPersistence() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        // Create new manager instance
        let newManager = SecurityManager()
        
        let retrievedPublic = try newManager.retrievePublicKey()
        XCTAssertEqual(retrievedPublic, keypair.publicKey)
    }
    
    func testDeleteKeychainItems() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        // Verify stored
        let stored = try manager.retrievePublicKey()
        XCTAssertEqual(stored, keypair.publicKey)
        
        // Delete and verify error
        try manager.clearSessionToken()
        
        // Public key should still be there (only token is cleared)
        let stillThere = try manager.retrievePublicKey()
        XCTAssertEqual(stillThere, keypair.publicKey)
    }
    
    // MARK: - Message Signing (5 tests)
    
    func testSignMessage() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        let message = "Hello, World!"
        let signature = try await manager.signMessage(message)
        
        XCTAssertNotNil(signature)
        XCTAssertFalse(signature.isEmpty)
    }
    
    func testSignEmptyMessage() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        let signature = try await manager.signMessage("")
        XCTAssertNotNil(signature)
    }
    
    func testSignLongMessage() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        let longMessage = String(repeating: "A", count: 1024)
        let signature = try await manager.signMessage(longMessage)
        
        XCTAssertNotNil(signature)
        XCTAssertEqual(signature.count, 64) // Ed25519 signatures are 64 bytes
    }
    
    func testSignatureVerification() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        let message = "Test message"
        let signature = try await manager.signMessage(message)
        
        let isValid = manager.verifySignature(signature, for: message, publicKey: keypair.publicKey)
        XCTAssertTrue(isValid)
    }
    
    func testInvalidSignatureRejection() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        let message = "Test message"
        var signature = try await manager.signMessage(message)
        
        // Tamper with signature
        signature[0] = signature[0] ^ 0xFF
        
        let isValid = manager.verifySignature(signature, for: message, publicKey: keypair.publicKey)
        XCTAssertFalse(isValid)
    }
    
    // MARK: - Session Token Management (6 tests)
    
    func testStoreSessionToken() async throws {
        let token = SessionToken(
            token: "test_token",
            expiresAt: Date().addingTimeInterval(3600),
            createdAt: Date()
        )
        
        try manager.storeSessionToken(token)
        
        XCTAssertEqual(manager.currentToken?.token, "test_token")
        XCTAssertTrue(manager.isAuthenticated)
    }
    
    func testRetrieveSessionToken() async throws {
        let token = SessionToken(
            token: "test_token",
            expiresAt: Date().addingTimeInterval(3600),
            createdAt: Date()
        )
        
        try manager.storeSessionToken(token)
        let retrieved = try manager.retrieveSessionToken()
        
        XCTAssertEqual(retrieved?.token, "test_token")
    }
    
    func testTokenExpiration() async throws {
        let expiredToken = SessionToken(
            token: "expired_token",
            expiresAt: Date().addingTimeInterval(-3600), // Expired 1 hour ago
            createdAt: Date().addingTimeInterval(-7200)
        )
        
        try manager.storeSessionToken(expiredToken)
        let retrieved = try manager.retrieveSessionToken()
        
        XCTAssertNil(retrieved)
    }
    
    func testTokenValidation() async throws {
        let validToken = SessionToken(
            token: "valid",
            expiresAt: Date().addingTimeInterval(3600),
            createdAt: Date()
        )
        
        let isValid = manager.isTokenValid(validToken)
        XCTAssertTrue(isValid)
    }
    
    func testTokenRefresh() async throws {
        let oldToken = SessionToken(
            token: "old_token",
            expiresAt: Date().addingTimeInterval(3600),
            createdAt: Date()
        )
        
        try manager.storeSessionToken(oldToken)
        let newToken = try manager.refreshToken(currentToken: oldToken)
        
        XCTAssertNotEqual(newToken.token, oldToken.token)
        XCTAssertTrue(newToken.expiresAt > oldToken.expiresAt)
    }
    
    func testClearSessionToken() async throws {
        let token = SessionToken(
            token: "test_token",
            expiresAt: Date().addingTimeInterval(3600),
            createdAt: Date()
        )
        
        try manager.storeSessionToken(token)
        XCTAssertTrue(manager.isAuthenticated)
        
        try manager.clearSessionToken()
        
        XCTAssertFalse(manager.isAuthenticated)
        XCTAssertNil(manager.currentToken)
    }
    
    // MARK: - Error Handling (3 tests)
    
    func testVerificationWithoutPublicKey() async throws {
        let invalidKey = Data()
        let signature = Data(repeating: 0, count: 64)
        
        let isValid = manager.verifySignature(signature, for: "test", publicKey: invalidKey)
        XCTAssertFalse(isValid)
    }
    
    func testExpiredTokenError() async throws {
        let expiredToken = SessionToken(
            token: "expired",
            expiresAt: Date().addingTimeInterval(-1),
            createdAt: Date()
        )
        
        try manager.storeSessionToken(expiredToken)
        let retrieved = try manager.retrieveSessionToken()
        
        XCTAssertNil(retrieved)
        XCTAssertEqual(manager.error, SecurityError.tokenExpired)
    }
    
    func testTokenRefreshEdgeCases() async throws {
        // Refresh with minimal expiration time
        let almostExpiredToken = SessionToken(
            token: "almost_expired",
            expiresAt: Date().addingTimeInterval(1),
            createdAt: Date().addingTimeInterval(-86399)
        )
        
        let newToken = try manager.refreshToken(currentToken: almostExpiredToken)
        XCTAssertTrue(newToken.expiresAt > almostExpiredToken.expiresAt)
    }
    
    // MARK: - Edge Cases (4 tests)
    
    func testConcurrentKeyGeneration() async throws {
        async let key1 = manager.generateKeyPair()
        async let key2 = manager.generateKeyPair()
        
        let (k1, k2) = try await (key1, key2)
        
        XCTAssertNotEqual(k1.publicKey, k2.publicKey)
    }
    
    func testKeychainItemEncoding() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        // Retrieve and verify encoding integrity
        let retrieved = try manager.retrievePublicKey()
        XCTAssertEqual(retrieved, keypair.publicKey)
        
        // Sign with stored key and verify
        let signature = try await manager.signMessage("test")
        let isValid = manager.verifySignature(signature, for: "test", publicKey: retrieved)
        XCTAssertTrue(isValid)
    }
    
    func testSpecialCharacterSigning() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        let specialMessage = "Hello 🍑 World™ © 2026"
        let signature = try await manager.signMessage(specialMessage)
        
        let isValid = manager.verifySignature(signature, for: specialMessage, publicKey: keypair.publicKey)
        XCTAssertTrue(isValid)
    }
    
    func testLargeMessagePerformance() async throws {
        let keypair = try await manager.generateKeyPair()
        try manager.storeKeyPair(keypair)
        
        let largeMessage = String(repeating: "X", count: 10000)
        
        let start = Date()
        let signature = try await manager.signMessage(largeMessage)
        let duration = Date().timeIntervalSince(start)
        
        XCTAssertNotNil(signature)
        XCTAssertLessThan(duration, 5.0) // Should complete in under 5 seconds
    }
}
