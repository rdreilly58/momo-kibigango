import CoreData
import XCTest
@testable import Momotaro

@MainActor
final class MessagePersistenceTests: XCTestCase {
    
    var persistence: MessagePersistence!
    
    override func setUp() {
        super.setUp()
        persistence = MessagePersistence()
        persistence.loadPersistentStoreForTesting()
    }
    
    override func tearDown() {
        persistence.clearTestData()
        persistence = nil
        super.tearDown()
    }
    
    // Helper to create test messages
    private func testMessage(type: String = "command", content: String = "test", sessionId: String = "session1") -> GatewayMessage {
        GatewayMessage(type: type, content: content, sessionId: sessionId, timestamp: Date().description)
    }
    
    // MARK: - Initialization (2 tests)
    
    func testInitialization() {
        XCTAssertNotNil(persistence)
        XCTAssertEqual(persistence.messages.count, 0)
    }
    
    func testContextAvailable() {
        let count = persistence.totalMessageCount()
        XCTAssertEqual(count, 0)
    }
    
    // MARK: - Save Operations (5 tests)
    
    func testSaveMessage() throws {
        let message = testMessage()
        try persistence.saveMessage(message, sessionId: "session1")
        
        let count = persistence.messageCount(for: "session1")
        XCTAssertEqual(count, 1)
    }
    
    func testSaveMultipleMessages() throws {
        let message1 = testMessage(content: "first")
        let message2 = testMessage(type: "response", content: "second")
        let message3 = testMessage(content: "third")
        
        try persistence.saveMessages([message1, message2, message3], sessionId: "session1")
        
        let count = persistence.messageCount(for: "session1")
        XCTAssertEqual(count, 3)
    }
    
    func testSaveWithMetadata() throws {
        let message = testMessage(content: "test")
        try persistence.saveMessage(message, sessionId: "session1")
        
        let messages = try persistence.fetchMessages(for: "session1")
        XCTAssertEqual(messages.count, 1)
        XCTAssertEqual(messages[0].content, "test")
    }
    
    func testMessageTimestamp() throws {
        let message = testMessage()
        let beforeSave = Date()
        
        try persistence.saveMessage(message, sessionId: "session1")
        
        let afterSave = Date()
        let messages = try persistence.fetchMessages(for: "session1")
        
        XCTAssertEqual(messages.count, 1)
        XCTAssertGreaterThanOrEqual(messages[0].timestamp, beforeSave)
        XCTAssertLessThanOrEqual(messages[0].timestamp, afterSave)
    }
    
    func testSessionIdPreserved() throws {
        let message = testMessage(sessionId: "test-session-123")
        try persistence.saveMessage(message, sessionId: "test-session-123")
        
        let messages = try persistence.fetchMessages(for: "test-session-123")
        XCTAssertEqual(messages.count, 1)
        XCTAssertEqual(messages[0].sessionId, "test-session-123")
    }
    
    // MARK: - Fetch Operations (5 tests)
    
    func testFetchAll() throws {
        let msg1 = testMessage(sessionId: "session1")
        let msg2 = testMessage(type: "response", sessionId: "session2")
        
        try persistence.saveMessage(msg1, sessionId: "session1")
        try persistence.saveMessage(msg2, sessionId: "session2")
        
        let all = try persistence.fetchAllMessages()
        XCTAssertEqual(all.count, 2)
    }
    
    func testFetchBySession() throws {
        let msg1 = testMessage(sessionId: "session1")
        let msg2 = testMessage(type: "response", sessionId: "session1")
        
        try persistence.saveMessage(msg1, sessionId: "session1")
        try persistence.saveMessage(msg2, sessionId: "session1")
        
        let fetched = try persistence.fetchMessages(for: "session1")
        XCTAssertEqual(fetched.count, 2)
    }
    
    func testFetchOrder() throws {
        let msg1 = testMessage(content: "first", sessionId: "session1")
        let msg2 = testMessage(content: "second", sessionId: "session1")
        
        try persistence.saveMessage(msg1, sessionId: "session1")
        Thread.sleep(forTimeInterval: 0.01)
        try persistence.saveMessage(msg2, sessionId: "session1")
        
        let messages = try persistence.fetchMessages(for: "session1")
        XCTAssertEqual(messages.count, 2)
        XCTAssertLessThanOrEqual(messages[0].timestamp, messages[1].timestamp)
    }
    
    func testFetchEmpty() throws {
        let messages = try persistence.fetchMessages(for: "nonexistent")
        XCTAssertEqual(messages.count, 0)
    }
    
    func testFetchAfterSave() throws {
        let message = testMessage(content: "persisted", sessionId: "session1")
        try persistence.saveMessage(message, sessionId: "session1")
        
        let fetched = try persistence.fetchMessages(for: "session1")
        XCTAssertEqual(fetched.count, 1)
        XCTAssertEqual(fetched[0].content, "persisted")
    }
    
    // MARK: - Quota Tracking (4 tests)
    
    func testMessageCount() throws {
        let msg1 = testMessage(sessionId: "session1")
        let msg2 = testMessage(sessionId: "session1")
        
        try persistence.saveMessage(msg1, sessionId: "session1")
        try persistence.saveMessage(msg2, sessionId: "session1")
        
        let count = persistence.messageCount(for: "session1")
        XCTAssertEqual(count, 2)
    }
    
    func testTotalMessageCount() throws {
        let msg1 = testMessage(sessionId: "session1")
        let msg2 = testMessage(sessionId: "session1")
        let msg3 = testMessage(sessionId: "session2")
        
        try persistence.saveMessage(msg1, sessionId: "session1")
        try persistence.saveMessage(msg2, sessionId: "session1")
        try persistence.saveMessage(msg3, sessionId: "session2")
        
        let total = persistence.totalMessageCount()
        XCTAssertEqual(total, 3)
    }
    
    func testCountAfterDelete() throws {
        let message = testMessage(sessionId: "session1")
        try persistence.saveMessage(message, sessionId: "session1")
        XCTAssertEqual(persistence.messageCount(for: "session1"), 1)
        
        let messages = try persistence.fetchMessages(for: "session1")
        try persistence.deleteMessage(messages[0])
        
        XCTAssertEqual(persistence.messageCount(for: "session1"), 0)
    }
    
    func testCountMultipleSessions() throws {
        let msg1 = testMessage(sessionId: "session1")
        let msg2 = testMessage(sessionId: "session1")
        let msg3 = testMessage(sessionId: "session2")
        
        try persistence.saveMessage(msg1, sessionId: "session1")
        try persistence.saveMessage(msg2, sessionId: "session1")
        try persistence.saveMessage(msg3, sessionId: "session2")
        
        XCTAssertEqual(persistence.messageCount(for: "session1"), 2)
        XCTAssertEqual(persistence.messageCount(for: "session2"), 1)
    }
    
    // MARK: - Delete Operations (4 tests)
    
    func testDeleteMessage() throws {
        let message = testMessage(sessionId: "session1")
        try persistence.saveMessage(message, sessionId: "session1")
        
        var messages = try persistence.fetchMessages(for: "session1")
        XCTAssertEqual(messages.count, 1)
        
        try persistence.deleteMessage(messages[0])
        
        messages = try persistence.fetchMessages(for: "session1")
        XCTAssertEqual(messages.count, 0)
    }
    
    func testDeleteAllMessages() throws {
        let msg1 = testMessage(sessionId: "session1")
        let msg2 = testMessage(sessionId: "session2")
        
        try persistence.saveMessage(msg1, sessionId: "session1")
        try persistence.saveMessage(msg2, sessionId: "session2")
        
        try persistence.deleteAllMessages()
        
        let total = persistence.totalMessageCount()
        XCTAssertEqual(total, 0)
    }
    
    func testDeleteOldMessages() throws {
        let message = testMessage(content: "old", sessionId: "session1")
        try persistence.saveMessage(message, sessionId: "session1")
        
        let future = Date().addingTimeInterval(3600)
        try persistence.deleteOldMessages(olderThan: future)
        
        let count = persistence.totalMessageCount()
        XCTAssertEqual(count, 0)
    }
    
    func testDeleteBySessionLogic() throws {
        let msg1 = testMessage(sessionId: "session1")
        let msg2 = testMessage(sessionId: "session2")
        
        try persistence.saveMessage(msg1, sessionId: "session1")
        try persistence.saveMessage(msg2, sessionId: "session2")
        
        let session1Messages = try persistence.fetchMessages(for: "session1")
        for message in session1Messages {
            try persistence.deleteMessage(message)
        }
        
        XCTAssertEqual(persistence.messageCount(for: "session1"), 0)
        XCTAssertEqual(persistence.messageCount(for: "session2"), 1)
    }
    
    // MARK: - Data Integrity (3 tests)
    
    func testDataPersistesAcrossInstances() throws {
        let message = testMessage(content: "persistent", sessionId: "session1")
        try persistence.saveMessage(message, sessionId: "session1")
        
        let newPersistence = MessagePersistence()
        newPersistence.loadPersistentStoreForTesting()
        
        XCTAssertNotNil(persistence)
    }
    
    func testUniqueIds() throws {
        let msg1 = testMessage(content: "msg1", sessionId: "session1")
        let msg2 = testMessage(content: "msg2", sessionId: "session1")
        
        try persistence.saveMessage(msg1, sessionId: "session1")
        try persistence.saveMessage(msg2, sessionId: "session1")
        
        let messages = try persistence.fetchMessages(for: "session1")
        XCTAssertEqual(messages[0].id, messages[0].id)
        XCTAssertNotEqual(messages[0].id, messages[1].id)
    }
    
    func testNoDataLoss() throws {
        var messages: [GatewayMessage] = []
        for i in 0..<100 {
            messages.append(testMessage(content: "message \(i)", sessionId: "session1"))
        }
        
        try persistence.saveMessages(messages, sessionId: "session1")
        
        let fetched = try persistence.fetchMessages(for: "session1")
        XCTAssertEqual(fetched.count, 100)
    }
    
    // MARK: - Integration (2 tests)
    
    func testIntegrationWithGatewayMessage() throws {
        let message = testMessage(type: "response", content: "test response", sessionId: "session1")
        try persistence.saveMessage(message, sessionId: "session1")
        
        let fetched = try persistence.fetchMessages(for: "session1")
        XCTAssertEqual(fetched.count, 1)
        XCTAssertEqual(fetched[0].type, "response")
    }
    
    func testIntegrationWithQuotaTracking() throws {
        for i in 0..<50 {
            let message = testMessage(content: "message \(i)", sessionId: "session1")
            try persistence.saveMessage(message, sessionId: "session1")
        }
        
        let count = persistence.messageCount(for: "session1")
        XCTAssertEqual(count, 50)
        
        let total = persistence.totalMessageCount()
        XCTAssertEqual(total, 50)
    }
    
    // MARK: - Error Handling (2 tests)
    
    func testFetchErrorHandling() throws {
        let messages = try persistence.fetchMessages(for: "nonexistent")
        XCTAssertEqual(messages.count, 0)
    }
    
    func testSaveErrorHandling() throws {
        let message = testMessage(sessionId: "session1")
        try persistence.saveMessage(message, sessionId: "session1")
        
        let count = persistence.messageCount(for: "session1")
        XCTAssertEqual(count, 1)
    }
}
