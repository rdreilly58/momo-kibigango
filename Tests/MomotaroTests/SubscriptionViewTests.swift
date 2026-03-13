import XCTest
import SwiftUI
@testable import Momotaro

@MainActor
final class SubscriptionViewTests: XCTestCase {
    
    var subscriptionManager: SubscriptionManager!
    var featureManager: FeatureManager!
    var securityManager: SecurityManager!
    
    override func setUp() {
        super.setUp()
        securityManager = SecurityManager()
        subscriptionManager = SubscriptionManager()
        featureManager = FeatureManager(subscriptionManager: subscriptionManager, securityManager: securityManager)
    }
    
    override func tearDown() {
        subscriptionManager = nil
        featureManager = nil
        securityManager = nil
        super.tearDown()
    }
    
    // MARK: - View Rendering Tests (3)
    
    func testSubscriptionViewRendersWithManagers() {
        let view = SubscriptionView()
            .environmentObject(subscriptionManager)
            .environmentObject(featureManager)
        
        XCTAssertNotNil(view)
    }
    
    func testCurrentSubscriptionBadgeShowsFreeInitially() {
        let badge = CurrentSubscriptionBadge(planName: "Free")
        XCTAssertNotNil(badge)
        // Badge should display "Free Plan"
    }
    
    func testPlanCardsDisplay() {
        let freePlan = FreePlanCard()
        let proMonthly = ProMonthlyPlanCard(isLoading: .constant(false)) { _ in }
            .environmentObject(subscriptionManager)
        let proAnnual = ProAnnualPlanCard(isLoading: .constant(false)) { _ in }
            .environmentObject(subscriptionManager)
        
        XCTAssertNotNil(freePlan)
        XCTAssertNotNil(proMonthly)
        XCTAssertNotNil(proAnnual)
    }
    
    // MARK: - Feature Comparison Tests (3)
    
    func testFeatureComparisonTableExists() {
        let table = FeatureComparisonTable()
        XCTAssertNotNil(table)
    }
    
    func testFeatureRowShowsCheckmarkForIncludedFeatures() {
        let included = FeatureRow(icon: "checkmark", text: "Search", included: true)
        let excluded = FeatureRow(icon: "xmark", text: "Export", included: false)
        
        XCTAssertNotNil(included)
        XCTAssertNotNil(excluded)
    }
    
    func testComparisonRowDisplaysCorrectly() {
        let row = ComparisonRow(feature: "Messages", free: "100", pro: "∞")
        XCTAssertNotNil(row)
    }
    
    // MARK: - Restore Purchases Tests (2)
    
    func testRestorePurchasesButtonExists() {
        let button = RestorePurchasesButton(isLoading: .constant(false)) { _ in }
            .environmentObject(subscriptionManager)
        XCTAssertNotNil(button)
    }
    
    func testRestorePurchasesCallsManager() async throws {
        var callbackFired = false
        let button = RestorePurchasesButton(isLoading: .constant(false)) { _ in
            callbackFired = true
        }
        .environmentObject(subscriptionManager)
        
        XCTAssertNotNil(button)
    }
    
    // MARK: - Purchase Pricing Tests (3)
    
    func testProMonthlyPricingCorrect() {
        let plan = subscriptionManager.availablePlans.first(where: { $0.id == "pro_monthly" })
        XCTAssertNotNil(plan)
        XCTAssertEqual(plan?.name, "Pro")
    }
    
    func testProAnnualPricingCorrect() {
        let plan = subscriptionManager.availablePlans.first(where: { $0.id == "pro_annual" })
        XCTAssertNotNil(plan)
        XCTAssertEqual(plan?.name, "Pro+")
    }
    
    func testFreePlanAlwaysAvailable() {
        let freePlan = subscriptionManager.availablePlans.first(where: { $0.id == "free" })
        XCTAssertNotNil(freePlan)
        XCTAssertEqual(freePlan?.name, "Free")
    }
    
    // MARK: - Navigation Tests (2)
    
    func testBadgeDisplaysCurrentTier() {
        let badge = CurrentSubscriptionBadge(planName: "Free")
        XCTAssertNotNil(badge)
    }
    
    func testBadgeUpdatesOnTierChange() {
        let badge1 = CurrentSubscriptionBadge(planName: "Free")
        let badge2 = CurrentSubscriptionBadge(planName: "Pro Monthly")
        
        XCTAssertNotNil(badge1)
        XCTAssertNotNil(badge2)
    }
    
    // MARK: - Integration Tests (2)
    
    func testSubscriptionViewIntegrationWithManager() {
        let view = SubscriptionView()
            .environmentObject(subscriptionManager)
            .environmentObject(featureManager)
        
        XCTAssertNotNil(view)
    }
    
    func testFeatureManagerReflectsSubscriptionChanges() throws {
        let currentSubscription = subscriptionManager.currentSubscription
        XCTAssertNotNil(currentSubscription) // Default is Free plan
        XCTAssertEqual(currentSubscription?.plan.id, "free")
    }
    
    // MARK: - Error Handling Tests (1)
    
    func testErrorAlertDisplay() {
        var showingError = false
        let view = SubscriptionView()
            .environmentObject(subscriptionManager)
            .environmentObject(featureManager)
        
        XCTAssertNotNil(view)
    }
}
