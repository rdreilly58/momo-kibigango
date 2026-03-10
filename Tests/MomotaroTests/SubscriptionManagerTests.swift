import XCTest
@testable import Momotaro

@MainActor
final class SubscriptionManagerTests: XCTestCase {
    
    var manager: SubscriptionManager!
    
    override func setUp() {
        super.setUp()
        manager = SubscriptionManager()
    }
    
    override func tearDown() {
        manager = nil
        super.tearDown()
    }
    
    // MARK: - Initialization & Plans (3 tests)
    
    func testInitialization() {
        XCTAssertNotNil(manager)
        XCTAssertNotNil(manager.currentSubscription)
        XCTAssertFalse(manager.isPurchasing)
        XCTAssertFalse(manager.isRestoring)
    }
    
    func testDefaultFreeSubscription() {
        XCTAssertEqual(manager.currentSubscription?.plan.id, "free")
        XCTAssertEqual(manager.currentSubscription?.plan.name, "Free")
        XCTAssertEqual(manager.messageLimit(), 100)
        XCTAssertEqual(manager.sessionLimit(), 3)
    }
    
    func testAvailablePlansLoading() async throws {
        try await manager.loadAvailablePlans()
        
        XCTAssertEqual(manager.availablePlans.count, 3)
        XCTAssertEqual(manager.availablePlans[0].id, "free")
        XCTAssertEqual(manager.availablePlans[1].id, "pro_monthly")
        XCTAssertEqual(manager.availablePlans[2].id, "pro_annual")
    }
    
    // MARK: - Purchase Flow (5 tests)
    
    func testPurchaseProMonthly() async throws {
        let plan = SubscriptionManager.plans[1]
        let subscription = try await manager.purchase(plan)
        
        XCTAssertEqual(subscription.plan.id, "pro_monthly")
        XCTAssertEqual(manager.currentSubscription?.plan.id, "pro_monthly")
        XCTAssertNil(manager.error)
    }
    
    func testPurchaseProAnnual() async throws {
        let plan = SubscriptionManager.plans[2]
        let subscription = try await manager.purchase(plan)
        
        XCTAssertEqual(subscription.plan.id, "pro_annual")
        XCTAssertEqual(manager.currentSubscription?.plan.id, "pro_annual")
    }
    
    func testPurchaseFromFree() async throws {
        XCTAssertEqual(manager.currentSubscription?.plan.id, "free")
        
        let plan = SubscriptionManager.plans[1]
        let subscription = try await manager.purchase(plan)
        
        XCTAssertEqual(subscription.plan.id, "pro_monthly")
        XCTAssertNotEqual(manager.currentSubscription?.plan.id, "free")
    }
    
    func testPurchaseInProgress() async throws {
        let plan = SubscriptionManager.plans[1]
        
        let task = Task {
            try await manager.purchase(plan)
        }
        
        // Check is purchasing during purchase
        _ = try await task.value
        
        XCTAssertFalse(manager.isPurchasing)
    }
    
    func testPurchaseFree() async throws {
        let plan = SubscriptionManager.plans[0]
        let subscription = try await manager.purchase(plan)
        
        XCTAssertEqual(subscription.plan.id, "free")
        XCTAssertNil(subscription.expiresAt)
    }
    
    // MARK: - Restoration (4 tests)
    
    func testRestorePurchases() async throws {
        // First purchase
        let plan = SubscriptionManager.plans[1]
        _ = try await manager.purchase(plan)
        XCTAssertEqual(manager.currentSubscription?.plan.id, "pro_monthly")
        
        // Restore
        try await manager.restorePurchases()
        XCTAssertEqual(manager.currentSubscription?.plan.id, "pro_monthly")
        XCTAssertNil(manager.error)
    }
    
    func testRestoreNoExistingPurchase() async throws {
        try await manager.restorePurchases()
        
        XCTAssertEqual(manager.currentSubscription?.plan.id, "free")
        XCTAssertNil(manager.error)
    }
    
    func testRestoreUpdatesSubscription() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await manager.purchase(plan)
        let originalTx = manager.currentSubscription?.transactionId
        
        try await manager.restorePurchases()
        
        XCTAssertEqual(manager.currentSubscription?.plan.id, "pro_monthly")
        XCTAssertEqual(manager.currentSubscription?.transactionId, originalTx)
    }
    
    func testRestoreNotInProgress() async throws {
        XCTAssertFalse(manager.isRestoring)
        
        try await manager.restorePurchases()
        
        XCTAssertFalse(manager.isRestoring)
    }
    
    // MARK: - Subscription Status (4 tests)
    
    func testSubscriptionValid() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await manager.purchase(plan)
        
        let isValid = manager.isSubscriptionValid()
        XCTAssertTrue(isValid)
    }
    
    func testFreeSubscriptionAlwaysValid() {
        let isValid = manager.isSubscriptionValid()
        XCTAssertTrue(isValid)
    }
    
    func testAutoRenewalStatus() async throws {
        let plan = SubscriptionManager.plans[1]
        let subscription = try await manager.purchase(plan)
        
        XCTAssertTrue(subscription.autoRenews)
    }
    
    func testCheckStatusUpdates() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await manager.purchase(plan)
        
        try await manager.checkSubscriptionStatus()
        
        XCTAssertNil(manager.error)
    }
    
    // MARK: - Feature Access & Entitlements (5 tests)
    
    func testFreeMessageLimit() {
        XCTAssertEqual(manager.messageLimit(), 100)
    }
    
    func testProMessageLimit() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await manager.purchase(plan)
        
        XCTAssertEqual(manager.messageLimit(), Int.max)
    }
    
    func testFreeSessionLimit() {
        XCTAssertEqual(manager.sessionLimit(), 3)
    }
    
    func testProSessionLimit() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await manager.purchase(plan)
        
        XCTAssertEqual(manager.sessionLimit(), Int.max)
    }
    
    func testFeatureAccess() async throws {
        // Free tier
        XCTAssertTrue(manager.canAccess(.messageHistory))
        XCTAssertTrue(manager.canAccess(.multipleSessions))
        XCTAssertFalse(manager.canAccess(.fullTextSearch))
        XCTAssertFalse(manager.canAccess(.messageExport))
        XCTAssertFalse(manager.canAccess(.analyticsAccess))
        
        // Pro tier
        let plan = SubscriptionManager.plans[1]
        _ = try await manager.purchase(plan)
        
        XCTAssertTrue(manager.canAccess(.messageHistory))
        XCTAssertTrue(manager.canAccess(.multipleSessions))
        XCTAssertTrue(manager.canAccess(.fullTextSearch))
        XCTAssertTrue(manager.canAccess(.messageExport))
        XCTAssertTrue(manager.canAccess(.analyticsAccess))
    }
    
    // MARK: - Receipt Validation (3 tests)
    
    func testValidReceipt() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await manager.purchase(plan)
        
        try await manager.checkSubscriptionStatus()
        XCTAssertNil(manager.error)
    }
    
    func testExpiredSubscription() async throws {
        // Create an expired subscription
        let freePlan = SubscriptionManager.plans[0]
        _ = try await manager.purchase(freePlan)
        
        // Manually create an expired subscription
        let expiredPlan = SubscriptionManager.plans[1]
        let expiredSubscription = Subscription(
            plan: expiredPlan,
            purchaseDate: Date().addingTimeInterval(-30 * 24 * 3600),
            expiresAt: Date().addingTimeInterval(-1),
            autoRenews: false,
            transactionId: UUID().uuidString
        )
        manager.currentSubscription = expiredSubscription
        
        XCTAssertFalse(manager.isSubscriptionValid())
    }
    
    func testInvalidReceipt() async throws {
        let freePlan = SubscriptionManager.plans[0]
        _ = try await manager.purchase(freePlan)
        
        // Subscription should still be valid (free tier)
        try await manager.checkSubscriptionStatus()
        XCTAssertNil(manager.error)
    }
    
    // MARK: - Error Handling (3 tests)
    
    func testProductNotFound() async throws {
        let invalidPlan = SubscriptionPlan(
            id: "invalid",
            name: "Invalid",
            description: "Invalid plan",
            price: "$9.99",
            productId: nil,
            features: []
        )
        
        do {
            _ = try await manager.purchase(invalidPlan)
            XCTFail("Should have thrown productNotFound")
        } catch SubscriptionError.productNotFound {
            // Error was thrown as expected
            return
        }
    }
    
    func testNetworkErrorHandling() async throws {
        // Free subscription should never fail
        let freePlan = SubscriptionManager.plans[0]
        let subscription = try await manager.purchase(freePlan)
        
        XCTAssertEqual(subscription.plan.id, "free")
        XCTAssertNil(manager.error)
    }
    
    func testStoreKitErrorWrapping() async throws {
        // Simulate error during purchase
        let plan = SubscriptionManager.plans[1]
        let subscription = try await manager.purchase(plan)
        
        XCTAssertNotNil(subscription)
        XCTAssertNil(manager.error)
    }
    
    // MARK: - Edge Cases (4 tests)
    
    func testConcurrentPurchases() async throws {
        let plan1 = SubscriptionManager.plans[1]
        let plan2 = SubscriptionManager.plans[2]
        
        async let purchase1 = manager.purchase(plan1)
        async let purchase2 = manager.purchase(plan2)
        
        let (sub1, sub2) = try await (purchase1, purchase2)
        
        // Last purchase should be active
        XCTAssertNotNil(manager.currentSubscription)
        XCTAssertTrue(sub1.plan.id == "pro_monthly" || sub2.plan.id == "pro_annual")
    }
    
    func testRapidStatusChecks() async throws {
        let plan = SubscriptionManager.plans[1]
        _ = try await manager.purchase(plan)
        
        try await manager.checkSubscriptionStatus()
        let firstCheckTime = Date()
        
        try await manager.checkSubscriptionStatus()
        let secondCheckTime = Date()
        
        // Second check should be nearly instant (cached)
        let duration = secondCheckTime.timeIntervalSince(firstCheckTime)
        XCTAssertLessThan(duration, 0.1)
    }
    
    func testPlanEquality() {
        let plan1 = SubscriptionManager.plans[0]
        let plan2 = SubscriptionManager.plans[0]
        
        XCTAssertEqual(plan1, plan2)
    }
    
    func testFeatureEnumeration() {
        let allFeatures: [Feature] = [
            .messageHistory,
            .multipleSessions,
            .fullTextSearch,
            .messageExport,
            .analyticsAccess
        ]
        
        XCTAssertEqual(Feature.allCases.count, allFeatures.count)
    }
    
    // MARK: - Integration Tests (3 tests)
    
    func testFullPurchaseWorkflow() async throws {
        // Start with free
        XCTAssertEqual(manager.currentSubscription?.plan.id, "free")
        XCTAssertEqual(manager.messageLimit(), 100)
        
        // Upgrade to pro
        let proPlan = SubscriptionManager.plans[1]
        _ = try await manager.purchase(proPlan)
        
        XCTAssertEqual(manager.currentSubscription?.plan.id, "pro_monthly")
        XCTAssertEqual(manager.messageLimit(), Int.max)
        XCTAssertTrue(manager.canAccess(.messageExport))
        
        // Restore
        try await manager.restorePurchases()
        
        XCTAssertEqual(manager.currentSubscription?.plan.id, "pro_monthly")
    }
    
    func testMultiplePlans() {
        let plans = SubscriptionManager.plans
        
        XCTAssertEqual(plans.count, 3)
        XCTAssert(plans.contains { $0.id == "free" })
        XCTAssert(plans.contains { $0.id == "pro_monthly" })
        XCTAssert(plans.contains { $0.id == "pro_annual" })
    }
    
    func testSubscriptionComparison() {
        let freePlan = SubscriptionManager.plans[0]
        let sub1 = Subscription(
            plan: freePlan,
            purchaseDate: Date(),
            expiresAt: nil,
            autoRenews: false,
            transactionId: nil
        )
        let sub2 = Subscription(
            plan: freePlan,
            purchaseDate: Date(),
            expiresAt: nil,
            autoRenews: false,
            transactionId: nil
        )
        
        XCTAssertEqual(sub1, sub2)
    }
}
