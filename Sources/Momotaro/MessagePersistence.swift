import Foundation

// MARK: - PersistenceError
enum PersistenceError: Error, Equatable {
    case failedToSave
    case failedToFetch
    case invalidData
    case corruptedStore
    case notFound
}

// MARK: - MessageData
struct MessageData: Identifiable, Equatable {
    let id: String
    let content: String
    let timestamp: Date
    let sessionId: String
    let isReceived: Bool
    let type: String
    let metadata: String?
    
    init(id: String = UUID().uuidString, content: String, timestamp: Date = Date(), sessionId: String, isReceived: Bool = false, type: String, metadata: String? = nil) {
        self.id = id
        self.content = content
        self.timestamp = timestamp
        self.sessionId = sessionId
        self.isReceived = isReceived
        self.type = type
        self.metadata = metadata
    }
}

// MARK: - MessagePersistence
@MainActor
class MessagePersistence: NSObject, ObservableObject {
    @Published var messages: [MessageData] = []
    @Published var error: PersistenceError?
    
    private var messageStore: [MessageData] = []
    
    // MARK: - Initialization
    override init() {
        super.init()
    }
    
    // MARK: - CRUD Operations
    func saveMessage(_ message: GatewayMessage, sessionId: String) throws {
        let messageData = MessageData(
            content: message.content,
            timestamp: Date(),
            sessionId: sessionId,
            isReceived: false,
            type: message.type
        )
        
        messageStore.append(messageData)
        self.error = nil
    }
    
    func fetchMessages(for sessionId: String) throws -> [MessageData] {
        let filtered = messageStore.filter { $0.sessionId == sessionId }
        let sorted = filtered.sorted { $0.timestamp < $1.timestamp }
        return sorted
    }
    
    func fetchAllMessages() throws -> [MessageData] {
        return messageStore.sorted { $0.timestamp < $1.timestamp }
    }
    
    func deleteMessage(_ message: MessageData) throws {
        messageStore.removeAll { $0.id == message.id }
        self.error = nil
    }
    
    func deleteAllMessages() throws {
        messageStore.removeAll()
        self.error = nil
    }
    
    // MARK: - Quota Tracking
    func messageCount(for sessionId: String) -> Int {
        return messageStore.filter { $0.sessionId == sessionId }.count
    }
    
    func totalMessageCount() -> Int {
        return messageStore.count
    }
    
    // MARK: - Batch Operations
    func saveMessages(_ messages: [GatewayMessage], sessionId: String) throws {
        for message in messages {
            try saveMessage(message, sessionId: sessionId)
        }
    }
    
    func deleteOldMessages(olderThan date: Date) throws {
        messageStore.removeAll { $0.timestamp < date }
        self.error = nil
    }
    
    // MARK: - Testing
    func loadPersistentStoreForTesting() {
        messageStore.removeAll()
    }
    
    func clearTestData() {
        messageStore.removeAll()
    }
}
