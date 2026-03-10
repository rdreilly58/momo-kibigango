import Foundation

// MARK: - Analytics Event
struct AnalyticsEvent: Codable, Equatable {
    let name: String
    let params: [String: String]
    let timestamp: Date
    
    init(name: String, params: [String: String] = [:]) {
        self.name = name
        self.params = params
        self.timestamp = Date()
    }
    
    enum CodingKeys: String, CodingKey {
        case name
        case params
        case timestamp
    }
}

// MARK: - Analytics Manager
@MainActor
class AnalyticsManager: ObservableObject {
    static let shared = AnalyticsManager()
    
    @Published var isReady = true
    @Published var eventCount = 0
    
    private var eventQueue: [AnalyticsEvent] = []
    private var userProperties: [String: String] = [:]
    private var sessionId = UUID().uuidString
    private var userId: String?
    
    // MARK: - Initialization
    init() {
        isReady = true
    }
    
    // MARK: - Event Logging
    func logEvent(_ name: String, parameters: [String: Any]? = nil) {
        var stringParams: [String: String] = [:]
        if let parameters = parameters {
            for (key, value) in parameters {
                stringParams[key] = String(describing: value)
            }
        }
        
        let event = AnalyticsEvent(name: name, params: stringParams)
        eventQueue.append(event)
        eventCount = eventQueue.count
    }
    
    func logScreenView(_ screenName: String) {
        logEvent("screen_view", parameters: ["screen_name": screenName])
    }
    
    func logPurchaseEvent(productId: String, price: Double) {
        logEvent("purchase_completed", parameters: [
            "product_id": productId,
            "price": price
        ])
    }
    
    func logError(code: String, message: String) {
        logEvent("error_occurred", parameters: [
            "error_code": code,
            "error_message": message
        ])
    }
    
    func logFeatureUsage(_ feature: String, enabled: Bool) {
        logEvent("feature_accessed", parameters: [
            "feature_name": feature,
            "enabled": enabled
        ])
    }
    
    func logMessageCount(count: Int, sessionId: String) {
        logEvent("message_history_viewed", parameters: [
            "message_count": count,
            "session_id": sessionId
        ])
    }
    
    // MARK: - User Properties
    func setUserProperty(_ name: String, value: String) {
        userProperties[name] = value
    }
    
    func getUserProperty(_ name: String) -> String? {
        return userProperties[name]
    }
    
    func setUserId(_ id: String) {
        userId = id
        setUserProperty("device_id", value: id)
    }
    
    func clearUserId() {
        userId = nil
        userProperties.removeValue(forKey: "device_id")
    }
    
    // MARK: - Session Management
    func getSessionId() -> String {
        return sessionId
    }
    
    func resetSession() {
        sessionId = UUID().uuidString
    }
    
    // MARK: - Queue Management
    func getEventQueue() -> [AnalyticsEvent] {
        return eventQueue
    }
    
    func clearEventQueue() {
        eventQueue.removeAll()
        eventCount = 0
    }
    
    func getUserProperties() -> [String: String] {
        return userProperties
    }
}
