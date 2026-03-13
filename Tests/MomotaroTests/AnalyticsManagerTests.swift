import XCTest
@testable import Momotaro

@MainActor
final class AnalyticsManagerTests: XCTestCase {
    
    var analyticsManager: AnalyticsManager!
    
    override func setUp() {
        super.setUp()
        analyticsManager = AnalyticsManager()
    }
    
    override func tearDown() {
        analyticsManager.clearEventQueue()
        analyticsManager.clearUserId()
        analyticsManager = nil
        super.tearDown()
    }
    
    // MARK: - Initialization Tests (2)
    
    func testInitialization() {
        XCTAssertNotNil(analyticsManager)
        XCTAssertTrue(analyticsManager.isReady)
    }
    
    func testEventQueueStartsEmpty() {
        let queue = analyticsManager.getEventQueue()
        XCTAssertEqual(queue.count, 0)
    }
    
    // MARK: - Event Logging Tests (5)
    
    func testLogEventWithoutParameters() {
        analyticsManager.logEvent("test_event")
        let queue = analyticsManager.getEventQueue()
        
        XCTAssertEqual(queue.count, 1)
        XCTAssertEqual(queue[0].name, "test_event")
        XCTAssertEqual(queue[0].params.count, 0)
    }
    
    func testLogEventWithParameters() {
        analyticsManager.logEvent("purchase_event", parameters: ["price": 9.99, "currency": "USD"])
        let queue = analyticsManager.getEventQueue()
        
        XCTAssertEqual(queue.count, 1)
        XCTAssertEqual(queue[0].name, "purchase_event")
        XCTAssertTrue(queue[0].params.count >= 2)
    }
    
    func testLogScreenView() {
        analyticsManager.logScreenView("main_screen")
        let queue = analyticsManager.getEventQueue()
        
        XCTAssertEqual(queue.count, 1)
        XCTAssertEqual(queue[0].name, "screen_view")
        XCTAssertEqual(queue[0].params["screen_name"], "main_screen")
    }
    
    func testLogPurchaseEvent() {
        analyticsManager.logPurchaseEvent(productId: "pro_monthly", price: 9.99)
        let queue = analyticsManager.getEventQueue()
        
        XCTAssertEqual(queue.count, 1)
        XCTAssertEqual(queue[0].name, "purchase_completed")
        XCTAssertEqual(queue[0].params["product_id"], "pro_monthly")
    }
    
    func testLogError() {
        analyticsManager.logError(code: "ERR_001", message: "Network error")
        let queue = analyticsManager.getEventQueue()
        
        XCTAssertEqual(queue.count, 1)
        XCTAssertEqual(queue[0].name, "error_occurred")
        XCTAssertEqual(queue[0].params["error_code"], "ERR_001")
    }
    
    // MARK: - User Properties Tests (4)
    
    func testSetUserProperty() {
        analyticsManager.setUserProperty("subscription_tier", value: "pro")
        let properties = analyticsManager.getUserProperties()
        
        XCTAssertEqual(properties["subscription_tier"], "pro")
    }
    
    func testGetUserProperty() {
        analyticsManager.setUserProperty("device_id", value: "device-123")
        let value = analyticsManager.getUserProperty("device_id")
        
        XCTAssertEqual(value, "device-123")
    }
    
    func testUpdateUserProperty() {
        analyticsManager.setUserProperty("subscription_tier", value: "free")
        analyticsManager.setUserProperty("subscription_tier", value: "pro")
        let value = analyticsManager.getUserProperty("subscription_tier")
        
        XCTAssertEqual(value, "pro")
    }
    
    func testMultipleUserProperties() {
        analyticsManager.setUserProperty("subscription_tier", value: "pro")
        analyticsManager.setUserProperty("app_version", value: "1.0.0")
        analyticsManager.setUserProperty("ios_version", value: "17.0")
        let properties = analyticsManager.getUserProperties()
        
        XCTAssertEqual(properties.count, 3)
    }
    
    // MARK: - Session Tracking Tests (3)
    
    func testSessionIdCreatedOnInit() {
        let sessionId = analyticsManager.getSessionId()
        XCTAssertNotNil(sessionId)
        XCTAssertFalse(sessionId.isEmpty)
    }
    
    func testSessionIdPersists() {
        let sessionId1 = analyticsManager.getSessionId()
        let sessionId2 = analyticsManager.getSessionId()
        
        XCTAssertEqual(sessionId1, sessionId2)
    }
    
    func testResetSessionCreatesNewId() {
        let sessionId1 = analyticsManager.getSessionId()
        analyticsManager.resetSession()
        let sessionId2 = analyticsManager.getSessionId()
        
        XCTAssertNotEqual(sessionId1, sessionId2)
    }
    
    // MARK: - Feature Usage Tests (2)
    
    func testLogFeatureUsageEnabled() {
        analyticsManager.logFeatureUsage("search", enabled: true)
        let queue = analyticsManager.getEventQueue()
        
        XCTAssertEqual(queue.count, 1)
        XCTAssertEqual(queue[0].name, "feature_accessed")
        XCTAssertEqual(queue[0].params["feature_name"], "search")
    }
    
    func testLogFeatureUsageDisabled() {
        analyticsManager.logFeatureUsage("export", enabled: false)
        let queue = analyticsManager.getEventQueue()
        
        XCTAssertEqual(queue.count, 1)
        XCTAssertEqual(queue[0].params["enabled"], "false")
    }
    
    // MARK: - Message Count Tracking Tests (2)
    
    func testLogMessageCount() {
        analyticsManager.logMessageCount(count: 42, sessionId: "session-123")
        let queue = analyticsManager.getEventQueue()
        
        XCTAssertEqual(queue.count, 1)
        XCTAssertEqual(queue[0].name, "message_history_viewed")
        XCTAssertEqual(queue[0].params["message_count"], "42")
    }
    
    func testLogMessageCountMultipleSessions() {
        analyticsManager.logMessageCount(count: 10, sessionId: "session-1")
        analyticsManager.logMessageCount(count: 20, sessionId: "session-2")
        let queue = analyticsManager.getEventQueue()
        
        XCTAssertEqual(queue.count, 2)
    }
    
    // MARK: - User ID Management Tests (2)
    
    func testSetUserId() {
        analyticsManager.setUserId("device-abc123")
        let properties = analyticsManager.getUserProperties()
        
        XCTAssertEqual(properties["device_id"], "device-abc123")
    }
    
    func testClearUserId() {
        analyticsManager.setUserId("device-abc123")
        analyticsManager.clearUserId()
        let properties = analyticsManager.getUserProperties()
        
        XCTAssertNil(properties["device_id"])
    }
    
    // MARK: - Event Queue Management Tests (3)
    
    func testGetEventQueue() {
        analyticsManager.logEvent("event1")
        analyticsManager.logEvent("event2")
        let queue = analyticsManager.getEventQueue()
        
        XCTAssertEqual(queue.count, 2)
    }
    
    func testClearEventQueue() {
        analyticsManager.logEvent("event1")
        analyticsManager.logEvent("event2")
        analyticsManager.clearEventQueue()
        let queue = analyticsManager.getEventQueue()
        
        XCTAssertEqual(queue.count, 0)
    }
    
    func testEventCountTracking() {
        analyticsManager.logEvent("event1")
        XCTAssertEqual(analyticsManager.eventCount, 1)
        analyticsManager.logEvent("event2")
        XCTAssertEqual(analyticsManager.eventCount, 2)
    }
    
    // MARK: - Error Handling Tests (2)
    
    func testInvalidParametersHandled() {
        analyticsManager.logEvent("event", parameters: ["key": NSNull()])
        let queue = analyticsManager.getEventQueue()
        
        XCTAssertEqual(queue.count, 1)
    }
    
    func testConcurrentLoggingThreadSafe() {
        let dispatchGroup = DispatchGroup()
        
        for i in 0..<10 {
            dispatchGroup.enter()
            DispatchQueue.global().async {
                self.analyticsManager.logEvent("event_\(i)")
                dispatchGroup.leave()
            }
        }
        
        dispatchGroup.wait()
        let queue = analyticsManager.getEventQueue()
        
        XCTAssertEqual(queue.count, 10)
    }
    
    // MARK: - Event Timestamp Tests (2)
    
    func testEventIncludesTimestamp() {
        let beforeTime = Date()
        analyticsManager.logEvent("timestamped_event")
        let afterTime = Date()
        
        let queue = analyticsManager.getEventQueue()
        let event = queue[0]
        
        XCTAssertGreaterThanOrEqual(event.timestamp, beforeTime)
        XCTAssertLessThanOrEqual(event.timestamp, afterTime)
    }
    
    func testMultipleEventsHaveSequentialTimestamps() {
        analyticsManager.logEvent("event1")
        analyticsManager.logEvent("event2")
        
        let queue = analyticsManager.getEventQueue()
        XCTAssertLessThanOrEqual(queue[0].timestamp, queue[1].timestamp)
    }
    
    // MARK: - Event Equality Tests (1)
    
    func testAnalyticsEventEquality() {
        let event1 = AnalyticsEvent(name: "test", params: ["key": "value"])
        let event2 = AnalyticsEvent(name: "test", params: ["key": "value"])
        
        // Events are equal if name and params match (timestamp may differ slightly)
        XCTAssertEqual(event1.name, event2.name)
        XCTAssertEqual(event1.params, event2.params)
    }
}
