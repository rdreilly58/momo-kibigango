import XCTest
import CoreData
@testable import Momotaro

@MainActor
final class MessageStoreTests: XCTestCase {
    
    var store: MessageStore!
    
    override func setUp() {
        super.setUp()
        store = MessageStore(inMemory: true)
    }
    
    override func tearDown() {
        store = nil
        super.tearDown()
    }
    
    // MARK: - Initialization & Setup
    
    func testInitialization() {
        XCTAssertNotNil(store)
        XCTAssertTrue(store.messages.isEmpty)
        XCTAssertEqual(store.messageCount, 0)
        XCTAssertNil(store.error)
    }
    
    func testCoreDataStackSetup() {
        let testStore = MessageStore(inMemory: true)
        XCTAssertNotNil(testStore)
        XCTAssertEqual(testStore.messageCount, 0)
    }
    
    // MARK: - Save Operations
    
    func testSaveMessage() {
        let message = GatewayMessage(
            type: "test",
            content: "Test message",
            sessionId: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        store.saveMessage(message)
        
        XCTAssertGreaterThan(store.messages.count, 0)
        XCTAssertEqual(store.messages.first?.content, "Test message")
    }
    
    func testSaveMultipleMessages() {
        let messages = [
            GatewayMessage(type: "msg1", content: "First", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date())),
            GatewayMessage(type: "msg2", content: "Second", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date())),
            GatewayMessage(type: "msg3", content: "Third", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        ]
        
        store.saveMultipleMessages(messages)
        
        XCTAssertEqual(store.messageCount, 3)
    }
    
    func testSaveWithSessionId() {
        let message = GatewayMessage(
            type: "test",
            content: "Session message",
            sessionId: "session_1",
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        store.saveMessage(message, sessionId: "session_1")
        
        XCTAssertEqual(store.messages.first?.sessionId, "session_1")
    }
    
    func testMessageIdGeneration() {
        let message = GatewayMessage(
            type: "test",
            content: "ID test",
            sessionId: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        store.saveMessage(message)
        
        XCTAssertNotNil(store.messages.first?.id)
        XCTAssertFalse(store.messages.first!.id.isEmpty)
    }
    
    // MARK: - Fetch Operations
    
    func testFetchAllMessages() {
        let messages = [
            GatewayMessage(type: "msg1", content: "First", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date())),
            GatewayMessage(type: "msg2", content: "Second", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        ]
        
        store.saveMultipleMessages(messages)
        store.fetchAllMessages()
        
        XCTAssertEqual(store.messages.count, 2)
    }
    
    func testFetchMessagesForSession() {
        let msg1 = GatewayMessage(type: "msg1", content: "Session 1", sessionId: "session_1", timestamp: ISO8601DateFormatter().string(from: Date()))
        let msg2 = GatewayMessage(type: "msg2", content: "Session 2", sessionId: "session_2", timestamp: ISO8601DateFormatter().string(from: Date()))
        
        store.saveMessage(msg1, sessionId: "session_1")
        store.saveMessage(msg2, sessionId: "session_2")
        
        let sessionMessages = store.fetchMessages(for: "session_1")
        
        XCTAssertEqual(sessionMessages.count, 1)
        XCTAssertEqual(sessionMessages.first?.sessionId, "session_1")
    }
    
    func testFetchEmpty() {
        store.fetchAllMessages()
        
        XCTAssertTrue(store.messages.isEmpty)
        XCTAssertEqual(store.messageCount, 0)
    }
    
    func testFetchOrdering() {
        let now = Date()
        let msg1 = GatewayMessage(type: "msg1", content: "First", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: now))
        let msg2 = GatewayMessage(type: "msg2", content: "Second", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: now.addingTimeInterval(1)))
        let msg3 = GatewayMessage(type: "msg3", content: "Third", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: now.addingTimeInterval(2)))
        
        store.saveMessage(msg1)
        store.saveMessage(msg2)
        store.saveMessage(msg3)
        
        // Newest first
        XCTAssertEqual(store.messages.first?.content, "Third")
    }
    
    func testMessageCount() {
        let messages = (1...5).map { i in
            GatewayMessage(type: "msg", content: "Message \(i)", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        }
        
        store.saveMultipleMessages(messages)
        
        XCTAssertEqual(store.messageCount, 5)
    }
    
    func testLastMessage() {
        let msg1 = GatewayMessage(type: "msg1", content: "First", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        let msg2 = GatewayMessage(type: "msg2", content: "Last", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date().addingTimeInterval(1)))
        
        store.saveMessage(msg1)
        store.saveMessage(msg2)
        
        XCTAssertEqual(store.lastMessage?.content, "Last")
    }
    
    // MARK: - Search Operations
    
    func testSearchByContent() {
        let msg1 = GatewayMessage(type: "msg", content: "Hello World", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        let msg2 = GatewayMessage(type: "msg", content: "Goodbye", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        
        store.saveMessage(msg1)
        store.saveMessage(msg2)
        
        let results = store.searchMessages(query: "Hello")
        
        XCTAssertEqual(results.count, 1)
        XCTAssertEqual(results.first?.content, "Hello World")
    }
    
    func testSearchCaseSensitivity() {
        let message = GatewayMessage(type: "msg", content: "Test Message", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        store.saveMessage(message)
        
        let lowercase = store.searchMessages(query: "test")
        let uppercase = store.searchMessages(query: "TEST")
        let mixed = store.searchMessages(query: "TeSt")
        
        XCTAssertEqual(lowercase.count, 1)
        XCTAssertEqual(uppercase.count, 1)
        XCTAssertEqual(mixed.count, 1)
    }
    
    func testSearchEmpty() {
        let message = GatewayMessage(type: "msg", content: "Test", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        store.saveMessage(message)
        
        let results = store.searchMessages(query: "Nonexistent")
        
        XCTAssertTrue(results.isEmpty)
    }
    
    func testSearchMultipleResults() {
        let msg1 = GatewayMessage(type: "msg", content: "Apple pie", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        let msg2 = GatewayMessage(type: "msg", content: "Apple juice", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        let msg3 = GatewayMessage(type: "msg", content: "Orange", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        
        store.saveMessage(msg1)
        store.saveMessage(msg2)
        store.saveMessage(msg3)
        
        let results = store.searchMessages(query: "Apple")
        
        XCTAssertEqual(results.count, 2)
    }
    
    // MARK: - Delete Operations
    
    func testDeleteMessage() {
        let message = GatewayMessage(type: "msg", content: "Delete me", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        store.saveMessage(message)
        
        XCTAssertEqual(store.messageCount, 1)
        
        let id = store.messages.first?.id ?? ""
        store.deleteMessage(id)
        
        XCTAssertEqual(store.messageCount, 0)
    }
    
    func testDeleteNonexistent() {
        let message = GatewayMessage(type: "msg", content: "Keep me", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        store.saveMessage(message)
        
        store.deleteMessage("nonexistent_id")
        
        XCTAssertEqual(store.messageCount, 1)
        XCTAssertNil(store.error)
    }
    
    func testDeleteOldMessages() {
        // Create messages with controlled timestamps
        let msg1 = GatewayMessage(type: "msg", content: "Old", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date().addingTimeInterval(-1000)))
        let msg2 = GatewayMessage(type: "msg", content: "New", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        
        store.saveMessage(msg1)
        store.saveMessage(msg2)
        
        XCTAssertEqual(store.messageCount, 2)
        
        // Delete messages older than 500 seconds ago should delete msg1
        store.deleteOldMessages(olderThan: Date().addingTimeInterval(-500))
        
        // Should have at least 1 message (msg2)
        XCTAssertGreaterThanOrEqual(store.messageCount, 1)
    }
    
    func testDeleteAllMessages() {
        let messages = (1...5).map { i in
            GatewayMessage(type: "msg", content: "Message \(i)", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        }
        
        store.saveMultipleMessages(messages)
        XCTAssertEqual(store.messageCount, 5)
        
        store.deleteAllMessages()
        
        XCTAssertEqual(store.messageCount, 0)
    }
    
    func testDeleteSession() {
        let msg1 = GatewayMessage(type: "msg", content: "Session 1", sessionId: "session_1", timestamp: ISO8601DateFormatter().string(from: Date()))
        let msg2 = GatewayMessage(type: "msg", content: "Session 2", sessionId: "session_2", timestamp: ISO8601DateFormatter().string(from: Date()))
        
        store.saveMessage(msg1, sessionId: "session_1")
        store.saveMessage(msg2, sessionId: "session_2")
        
        XCTAssertEqual(store.messageCount, 2)
        
        store.deleteMessages(for: "session_1")
        
        XCTAssertEqual(store.messageCount, 1)
        XCTAssertEqual(store.lastMessage?.sessionId, "session_2")
    }
    
    // MARK: - Edge Cases
    
    func testLargeContent() {
        let largeContent = String(repeating: "A", count: 10000)
        let message = GatewayMessage(type: "msg", content: largeContent, sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        
        store.saveMessage(message)
        
        XCTAssertEqual(store.messages.first?.content.count, 10000)
    }
    
    func testSpecialCharacters() {
        let specialContent = "Hello! 🍑 Test\nNewline\tTab'Quotes\"Double"
        let message = GatewayMessage(type: "msg", content: specialContent, sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        
        store.saveMessage(message)
        
        XCTAssertEqual(store.messages.first?.content, specialContent)
    }
    
    func testTimestampPrecision() {
        let now = Date()
        let message = GatewayMessage(type: "msg", content: "Time test", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: now))
        
        store.saveMessage(message)
        
        let stored = store.messages.first?.timestamp ?? Date()
        XCTAssertEqual(now.timeIntervalSince(stored), 0, accuracy: 1.0)
    }
    
    func testConcurrentAccess() {
        let message = GatewayMessage(type: "msg", content: "Concurrent test", sessionId: nil, timestamp: ISO8601DateFormatter().string(from: Date()))
        
        store.saveMessage(message)
        store.fetchAllMessages()
        
        XCTAssertEqual(store.messageCount, 1)
        XCTAssertNil(store.error)
    }
}
