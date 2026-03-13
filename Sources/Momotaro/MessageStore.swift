import Foundation
import CoreData

// MARK: - StoredMessage Model

struct StoredMessage: Identifiable {
    let id: String
    let content: String
    let type: String
    let sessionId: String?
    let timestamp: Date
    var isRead: Bool
}

// MARK: - MessageStore

@MainActor
class MessageStore: NSObject, ObservableObject {
    @Published var messages: [StoredMessage] = []
    @Published var error: String?
    @Published var messageCount = 0
    
    private let container: NSPersistentContainer
    private var viewContext: NSManagedObjectContext {
        container.viewContext
    }
    
    override init() {
        // Create Core Data container with programmatic model
        self.container = NSPersistentContainer(name: "Momotaro", managedObjectModel: MessageStore.createModel())
        
        super.init()
        setupCoreData()
    }
    
    // For testing with in-memory store
    init(inMemory: Bool = false) {
        let container = NSPersistentContainer(name: "Momotaro", managedObjectModel: MessageStore.createModel())
        
        if inMemory {
            let description = NSPersistentStoreDescription()
            description.type = NSInMemoryStoreType
            container.persistentStoreDescriptions = [description]
        }
        
        self.container = container
        super.init()
        setupCoreData()
    }
    
    // MARK: - Model Creation
    
    static func createModel() -> NSManagedObjectModel {
        let model = NSManagedObjectModel()
        
        // Create MessageEntity
        let messageEntity = NSEntityDescription()
        messageEntity.name = "MessageEntity"
        messageEntity.managedObjectClassName = "MessageEntity"
        
        // Add attributes
        let id = NSAttributeDescription()
        id.name = "id"
        id.attributeType = .stringAttributeType
        id.isOptional = false
        
        let content = NSAttributeDescription()
        content.name = "content"
        content.attributeType = .stringAttributeType
        content.isOptional = false
        
        let type = NSAttributeDescription()
        type.name = "type"
        type.attributeType = .stringAttributeType
        type.isOptional = false
        
        let sessionId = NSAttributeDescription()
        sessionId.name = "sessionId"
        sessionId.attributeType = .stringAttributeType
        sessionId.isOptional = true
        
        let timestamp = NSAttributeDescription()
        timestamp.name = "timestamp"
        timestamp.attributeType = .dateAttributeType
        timestamp.isOptional = false
        
        let isRead = NSAttributeDescription()
        isRead.name = "isRead"
        isRead.attributeType = .booleanAttributeType
        isRead.isOptional = false
        
        messageEntity.properties = [id, content, type, sessionId, timestamp, isRead]
        
        model.entities = [messageEntity]
        return model
    }
    
    // MARK: - Setup
    
    private func setupCoreData() {
        container.loadPersistentStores { _, error in
            if let error = error {
                print("Core Data error: \(error)")
            }
        }
        
        viewContext.automaticallyMergesChangesFromParent = true
    }
    
    // MARK: - Save Operations
    
    func saveMessage(_ message: GatewayMessage, sessionId: String? = nil) {
        let newMessage = NSEntityDescription.insertNewObject(
            forEntityName: "MessageEntity",
            into: viewContext
        )
        
        newMessage.setValue(UUID().uuidString, forKey: "id")
        newMessage.setValue(message.content, forKey: "content")
        newMessage.setValue(message.type, forKey: "type")
        newMessage.setValue(sessionId ?? message.sessionId, forKey: "sessionId")
        newMessage.setValue(Date(), forKey: "timestamp")
        newMessage.setValue(false, forKey: "isRead")
        
        save()
    }
    
    func saveMultipleMessages(_ messages: [GatewayMessage], sessionId: String? = nil) {
        for message in messages {
            saveMessage(message, sessionId: sessionId)
        }
    }
    
    // MARK: - Fetch Operations
    
    func fetchAllMessages() {
        let request = NSFetchRequest<NSFetchRequestResult>(entityName: "MessageEntity")
        request.sortDescriptors = [NSSortDescriptor(key: "timestamp", ascending: false)]
        
        do {
            let results = try viewContext.fetch(request) as? [NSManagedObject] ?? []
            messages = results.compactMap { mapToStoredMessage($0) }
            messageCount = messages.count
        } catch {
            self.error = "Failed to fetch messages: \(error.localizedDescription)"
        }
    }
    
    func fetchMessages(for sessionId: String) -> [StoredMessage] {
        let request = NSFetchRequest<NSFetchRequestResult>(entityName: "MessageEntity")
        request.predicate = NSPredicate(format: "sessionId == %@", sessionId)
        request.sortDescriptors = [NSSortDescriptor(key: "timestamp", ascending: false)]
        
        do {
            let results = try viewContext.fetch(request) as? [NSManagedObject] ?? []
            return results.compactMap { mapToStoredMessage($0) }
        } catch {
            self.error = "Failed to fetch session messages: \(error.localizedDescription)"
            return []
        }
    }
    
    var lastMessage: StoredMessage? {
        let request = NSFetchRequest<NSFetchRequestResult>(entityName: "MessageEntity")
        request.sortDescriptors = [NSSortDescriptor(key: "timestamp", ascending: false)]
        request.fetchLimit = 1
        
        do {
            let results = try viewContext.fetch(request) as? [NSManagedObject] ?? []
            return results.first.flatMap { mapToStoredMessage($0) }
        } catch {
            return nil
        }
    }
    
    // MARK: - Search Operations
    
    func searchMessages(query: String) -> [StoredMessage] {
        let request = NSFetchRequest<NSFetchRequestResult>(entityName: "MessageEntity")
        request.predicate = NSPredicate(format: "content CONTAINS[cd] %@", query)
        request.sortDescriptors = [NSSortDescriptor(key: "timestamp", ascending: false)]
        
        do {
            let results = try viewContext.fetch(request) as? [NSManagedObject] ?? []
            return results.compactMap { mapToStoredMessage($0) }
        } catch {
            self.error = "Search failed: \(error.localizedDescription)"
            return []
        }
    }
    
    // MARK: - Delete Operations
    
    func deleteMessage(_ id: String) {
        let request = NSFetchRequest<NSFetchRequestResult>(entityName: "MessageEntity")
        request.predicate = NSPredicate(format: "id == %@", id)
        
        do {
            let results = try viewContext.fetch(request) as? [NSManagedObject] ?? []
            for result in results {
                viewContext.delete(result)
            }
            save()
        } catch {
            self.error = "Failed to delete message: \(error.localizedDescription)"
        }
    }
    
    func deleteOldMessages(olderThan date: Date) {
        let request = NSFetchRequest<NSFetchRequestResult>(entityName: "MessageEntity")
        request.predicate = NSPredicate(format: "timestamp < %@", date as NSDate)
        
        do {
            let results = try viewContext.fetch(request) as? [NSManagedObject] ?? []
            for result in results {
                viewContext.delete(result)
            }
            save()
        } catch {
            self.error = "Failed to delete old messages: \(error.localizedDescription)"
        }
    }
    
    func deleteAllMessages() {
        let request = NSFetchRequest<NSFetchRequestResult>(entityName: "MessageEntity")
        
        do {
            let results = try viewContext.fetch(request) as? [NSManagedObject] ?? []
            for result in results {
                viewContext.delete(result)
            }
            save()
        } catch {
            self.error = "Failed to delete all messages: \(error.localizedDescription)"
        }
    }
    
    func deleteMessages(for sessionId: String) {
        let request = NSFetchRequest<NSFetchRequestResult>(entityName: "MessageEntity")
        request.predicate = NSPredicate(format: "sessionId == %@", sessionId)
        
        do {
            let results = try viewContext.fetch(request) as? [NSManagedObject] ?? []
            for result in results {
                viewContext.delete(result)
            }
            save()
        } catch {
            self.error = "Failed to delete session messages: \(error.localizedDescription)"
        }
    }
    
    // MARK: - Private Helpers
    
    private func mapToStoredMessage(_ object: NSManagedObject) -> StoredMessage? {
        guard let id = object.value(forKey: "id") as? String,
              let content = object.value(forKey: "content") as? String,
              let type = object.value(forKey: "type") as? String,
              let timestamp = object.value(forKey: "timestamp") as? Date else {
            return nil
        }
        
        let sessionId = object.value(forKey: "sessionId") as? String
        let isRead = (object.value(forKey: "isRead") as? Bool) ?? false
        
        return StoredMessage(
            id: id,
            content: content,
            type: type,
            sessionId: sessionId,
            timestamp: timestamp,
            isRead: isRead
        )
    }
    
    private func save() {
        do {
            try viewContext.save()
            fetchAllMessages() // Refresh published property
        } catch {
            self.error = "Failed to save: \(error.localizedDescription)"
        }
    }
}


