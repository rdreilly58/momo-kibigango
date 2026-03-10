import XCTest
@testable import Momotaro

@MainActor
final class FeatureManagerTests: XCTestCase {
    
    var securityManager: SecurityManager!
    var subscriptionManager: SubscriptionManager!
    var featureManager: FeatureManager!
    
    override func setUp() {
        super.setUp()
        securityManager = SecurityManager()
        subscriptionManager = SubscriptionManager()
        featureManager = FeatureManager(
            subscriptionManager: subscriptionManager,
            securityManager: securityManager
        )
    }
    
    override func tearDown() {
        featureManager = nil
        subscriptionManager = nil
        securityManager = nil
        super.tearDown()
    }
    
    // MARK: - Initialization & Setup (3 tests)
    
    func testInitialization() {
        XCTAssertNotNil(featureManager)
        XCTAssertEqual(featureManager.messageCount, 0)
        XCTAssertEqual(featureManager.sessionCount, 0)
    }
    
    func testDependencyInjection() {
        XCTAssertNotNil(featureManager.subscriptionManager)
        XCTAssertNotNil(featureManager.securityManager)
        XCTAssertTrue(featureManager.subscriptionManager === subscriptionManager)
        XCTAssertTrue(featureManager.securityManager === securityManager)
    }
    
    func testDefaultFeatureStatus() {
        let status = featureManager.getFeatureStatus()
        
        // Free tier should have message history and sessions available
        XCTAssertEqual(status[.messageHistory], .available)
        XCTAssertEqual(status[.multipleSessions], .available)
        
        // But search, export, analytics should require pro
        XCTAssertEqual(status[.fullTextSearch], .requiresPro)
        XCTAssertEqual(status[.messageExport], .requiresPro)
        XCTAssertEqual(status[.analyticsAccess], .requiresPro)
    }
    
    // MARK: - Feature Access - Free Tier (5 tests)
    
    func testCanSendMessageFree() {
        XCTAssertTrue(featureManager.canSendMessage())
    }
    
    func testCanCreateSessionFree() {
        XCTAssertTrue(featureManager.canCreateSession())
    }
    
    func testCannotSearchFree() {
        XCTAssertFalse(featureManager.canSearch())
    }
    
    func testCannotExportFree() {
        XCTAssertFalse(featureManager.canExport())
    }
    
    func testCannotAccessAnalyticsFree() {
        XCTAssertFalse(featureManager.canAccessAnalytics())
    }
    
    // MARK: - Feature Access - Pro Tier (5 tests)
    
    func testCanSendMessagePro() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await subscriptionManager.purchase(plan)
        
        XCTAssertTrue(featureManager.canSendMessage())
    }
    
    func testCanCreateSessionPro() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await subscriptionManager.purchase(plan)
        
        XCTAssertTrue(featureManager.canCreateSession())
    }
    
    func testCanSearchPro() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await subscriptionManager.purchase(plan)
        
        XCTAssertTrue(featureManager.canSearch())
    }
    
    func testCanExportPro() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await subscriptionManager.purchase(plan)
        
        XCTAssertTrue(featureManager.canExport())
    }
    
    func testCanAccessAnalyticsPro() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await subscriptionManager.purchase(plan)
        
        XCTAssertTrue(featureManager.canAccessAnalytics())
    }
    
    // MARK: - Quota Management (4 tests)
    
    func testMessageQuotaIncrement() throws {
        XCTAssertEqual(featureManager.messageCount, 0)
        
        try featureManager.incrementMessageCount()
        
        XCTAssertEqual(featureManager.messageCount, 1)
    }
    
    func testMessageQuotaExceeded() throws {
        // Increment up to limit
        for _ in 0..<100 {
            try featureManager.incrementMessageCount()
        }
        
        // Next increment should fail
        XCTAssertFalse(featureManager.canSendMessage())
        
        do {
            try featureManager.incrementMessageCount()
            XCTFail("Should have thrown messageLimitReached")
        } catch FeatureError.messageLimitReached {
            XCTAssertNotNil(featureManager.error)
        }
    }
    
    func testSessionQuotaIncrement() throws {
        XCTAssertEqual(featureManager.sessionCount, 0)
        
        try featureManager.incrementSessionCount()
        
        XCTAssertEqual(featureManager.sessionCount, 1)
    }
    
    func testSessionQuotaExceeded() throws {
        // Increment up to limit
        try featureManager.incrementSessionCount()
        try featureManager.incrementSessionCount()
        try featureManager.incrementSessionCount()
        
        // Next increment should fail
        XCTAssertFalse(featureManager.canCreateSession())
        
        do {
            try featureManager.incrementSessionCount()
            XCTFail("Should have thrown sessionLimitReached")
        } catch FeatureError.sessionLimitReached {
            XCTAssertNotNil(featureManager.error)
        }
    }
    
    // MARK: - Quota Remaining (2 tests)
    
    func testMessageQuotaRemaining() {
        XCTAssertEqual(featureManager.messageQuotaRemaining(), 100)
        
        try? featureManager.incrementMessageCount()
        
        XCTAssertEqual(featureManager.messageQuotaRemaining(), 99)
    }
    
    func testSessionQuotaRemaining() {
        XCTAssertEqual(featureManager.sessionQuotaRemaining(), 3)
        
        try? featureManager.incrementSessionCount()
        
        XCTAssertEqual(featureManager.sessionQuotaRemaining(), 2)
    }
    
    // MARK: - Daily Reset (2 tests)
    
    func testResetDailyQuotas() throws {
        try featureManager.incrementMessageCount()
        try featureManager.incrementSessionCount()
        
        XCTAssertEqual(featureManager.messageCount, 1)
        XCTAssertEqual(featureManager.sessionCount, 1)
        
        featureManager.resetDailyQuotas()
        
        XCTAssertEqual(featureManager.messageCount, 0)
        XCTAssertEqual(featureManager.sessionCount, 0)
    }
    
    func testQuotasResetDaily() throws {
        // Fill up quotas
        for _ in 0..<100 {
            try featureManager.incrementMessageCount()
        }
        for _ in 0..<3 {
            try featureManager.incrementSessionCount()
        }
        
        XCTAssertFalse(featureManager.canSendMessage())
        XCTAssertFalse(featureManager.canCreateSession())
        
        // Reset
        featureManager.resetDailyQuotas()
        
        XCTAssertTrue(featureManager.canSendMessage())
        XCTAssertTrue(featureManager.canCreateSession())
    }
    
    // MARK: - Feature Status (3 tests)
    
    func testGetFeatureStatus() {
        let status = featureManager.getFeatureStatus()
        
        XCTAssertEqual(status.count, Feature.allCases.count)
        XCTAssertNotNil(status[.messageHistory])
        XCTAssertNotNil(status[.multipleSessions])
        XCTAssertNotNil(status[.fullTextSearch])
        XCTAssertNotNil(status[.messageExport])
        XCTAssertNotNil(status[.analyticsAccess])
    }
    
    func testFeatureStatusUpdates() async throws {
        var status = featureManager.getFeatureStatus()
        XCTAssertEqual(status[.fullTextSearch], .requiresPro)
        
        // Upgrade to pro
        let plan = SubscriptionManager.plans[1]
        _ = try await subscriptionManager.purchase(plan)
        
        await featureManager.refreshFeatures()
        status = featureManager.getFeatureStatus()
        
        XCTAssertEqual(status[.fullTextSearch], .available)
    }
    
    func testFeatureEnumeration() {
        let status = featureManager.getFeatureStatus()
        
        XCTAssertEqual(Feature.allCases.count, 5)
        XCTAssertEqual(status.count, 5)
    }
    
    // MARK: - Integration (2 tests)
    
    func testIntegrationWithSubscription() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await subscriptionManager.purchase(plan)
        
        XCTAssertTrue(featureManager.canSearch())
        XCTAssertTrue(featureManager.canExport())
        XCTAssertEqual(featureManager.messageQuotaRemaining(), Int.max)
        XCTAssertEqual(featureManager.sessionQuotaRemaining(), Int.max)
    }
    
    func testIntegrationWithSecurity() {
        let hasSecurityManager = featureManager.securityManager !== nil
        XCTAssertTrue(hasSecurityManager)
    }
    
    // MARK: - Error Handling (2 tests)
    
    func testQuotaExceededError() throws {
        // Fill up message quota
        for _ in 0..<100 {
            try featureManager.incrementMessageCount()
        }
        
        do {
            try featureManager.incrementMessageCount()
            XCTFail("Should throw messageLimitReached")
        } catch FeatureError.messageLimitReached {
            XCTAssertEqual(featureManager.error, FeatureError.messageLimitReached)
        }
    }
    
    func testProRequiredError() {
        XCTAssertFalse(featureManager.canSearch())
        XCTAssertFalse(featureManager.canExport())
        XCTAssertFalse(featureManager.canAccessAnalytics())
    }
    
    // MARK: - Quota Status (4 tests)
    
    func testMessageQuotaStatusAvailable() {
        let status = featureManager.getFeatureStatus()
        XCTAssertEqual(status[.messageHistory], .available)
    }
    
    func testMessageQuotaStatusExceeded() throws {
        for _ in 0..<100 {
            try featureManager.incrementMessageCount()
        }
        
        let status = featureManager.getFeatureStatus()
        XCTAssertEqual(status[.messageHistory], .quotaExceeded)
    }
    
    func testSessionQuotaStatusAvailable() {
        let status = featureManager.getFeatureStatus()
        XCTAssertEqual(status[.multipleSessions], .available)
    }
    
    func testSessionQuotaStatusExceeded() throws {
        for _ in 0..<3 {
            try featureManager.incrementSessionCount()
        }
        
        let status = featureManager.getFeatureStatus()
        XCTAssertEqual(status[.multipleSessions], .quotaExceeded)
    }
    
    // MARK: - Pro Tier Unlimited Quotas (2 tests)
    
    func testProUnlimitedMessages() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await subscriptionManager.purchase(plan)
        
        // Pro should allow unlimited messages
        for _ in 0..<1000 {
            try featureManager.incrementMessageCount()
        }
        
        XCTAssertTrue(featureManager.canSendMessage())
        XCTAssertEqual(featureManager.messageQuotaRemaining(), Int.max)
    }
    
    func testProUnlimitedSessions() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await subscriptionManager.purchase(plan)
        
        // Pro should allow unlimited sessions
        for _ in 0..<100 {
            try featureManager.incrementSessionCount()
        }
        
        XCTAssertTrue(featureManager.canCreateSession())
        XCTAssertEqual(featureManager.sessionQuotaRemaining(), Int.max)
    }
}
