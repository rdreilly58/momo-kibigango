import Foundation
import StoreKit

@MainActor
class SubscriptionManager: ObservableObject {
    // MARK: - Published Properties
    @Published var currentSubscription: Subscription?
    @Published var availablePlans: [SubscriptionPlan] = []
    @Published var isPurchasing = false
    @Published var isRestoring = false
    @Published var error: SubscriptionError?
    
    // MARK: - Static Plans
    static let plans: [SubscriptionPlan] = [
        SubscriptionPlan(
            id: "free",
            name: "Free",
            description: "Essential features",
            price: nil,
            productId: nil,
            features: ["Message history (100 messages)", "3 sessions", "Limited search"]
        ),
        SubscriptionPlan(
            id: "pro_monthly",
            name: "Pro",
            description: "Unlimited everything",
            price: "$9.99/month",
            productId: "com.momotaro.subscription.pro.monthly",
            features: ["Unlimited message history", "Unlimited sessions", "Full-text search", "Export messages"]
        ),
        SubscriptionPlan(
            id: "pro_annual",
            name: "Pro+",
            description: "Best value",
            price: "$79.99/year",
            productId: "com.momotaro.subscription.pro.annual",
            features: ["Unlimited message history", "Unlimited sessions", "Full-text search", "Export messages"]
        )
    ]
    
    // MARK: - Properties
    private var lastStatusCheckTime: Date = .distantPast
    private let statusCheckCacheDuration: TimeInterval = 3600 // 1 hour
    
    // MARK: - Initialization
    init() {
        self.availablePlans = Self.plans
        loadFreeSubscription()
        Task {
            try? await checkSubscriptionStatus()
        }
    }
    
    // MARK: - Plan Management
    func loadAvailablePlans() async throws {
        self.availablePlans = Self.plans
    }
    
    // MARK: - Purchase
    func purchase(_ plan: SubscriptionPlan) async throws -> Subscription {
        isPurchasing = true
        defer { isPurchasing = false }
        
        // Free plan doesn't require purchase
        if plan.id == "free" {
            loadFreeSubscription()
            if let subscription = currentSubscription {
                return subscription
            }
            throw SubscriptionError.purchaseFailed("Failed to create free subscription")
        }
        
        // For paid plans, simulate purchase in test environment
        // In production, this would use StoreKit 2 to request purchase
        guard let productId = plan.productId else {
            throw SubscriptionError.productNotFound
        }
        
        // Create subscription for paid plans
        let subscription = Subscription(
            plan: plan,
            purchaseDate: Date(),
            expiresAt: Date().addingTimeInterval(plan.id == "pro_annual" ? 365 * 24 * 3600 : 30 * 24 * 3600),
            autoRenews: true,
            transactionId: UUID().uuidString
        )
        
        self.currentSubscription = subscription
        self.error = nil
        return subscription
    }
    
    // MARK: - Restoration
    func restorePurchases() async throws {
        isRestoring = true
        defer { isRestoring = false }
        
        // In a real app, this would query StoreKit for previous purchases
        // For now, we'll check if there's a cached subscription and validate it
        if let currentSubscription = currentSubscription,
           currentSubscription.plan.id != "free",
           isSubscriptionValid() {
            self.error = nil
            return
        }
        
        // No purchases to restore
        loadFreeSubscription()
        self.error = nil
    }
    
    // MARK: - Subscription Status
    func checkSubscriptionStatus() async throws {
        // Check if we should skip due to caching
        let timeSinceLastCheck = Date().timeIntervalSince(lastStatusCheckTime)
        if timeSinceLastCheck < statusCheckCacheDuration {
            return
        }
        
        lastStatusCheckTime = Date()
        
        // Validate current subscription
        if let subscription = currentSubscription {
            if isSubscriptionValid() {
                self.error = nil
            } else if subscription.plan.id != "free" {
                // Subscription expired, fall back to free
                loadFreeSubscription()
                self.error = SubscriptionError.invalidReceipt
            }
        }
    }
    
    func isSubscriptionValid() -> Bool {
        guard let subscription = currentSubscription else {
            return false
        }
        
        if subscription.plan.id == "free" {
            return true
        }
        
        if let expiresAt = subscription.expiresAt {
            return Date() < expiresAt
        }
        
        return true
    }
    
    // MARK: - Feature Access
    func canAccess(_ feature: Feature) -> Bool {
        guard let subscription = currentSubscription else {
            return false
        }
        
        if subscription.plan.id == "free" {
            // Free tier has limited features
            switch feature {
            case .messageHistory:
                return true
            case .multipleSessions:
                return true
            case .fullTextSearch:
                return false
            case .messageExport:
                return false
            case .analyticsAccess:
                return false
            }
        }
        
        // Pro tiers have all features
        if subscription.plan.id == "pro_monthly" || subscription.plan.id == "pro_annual" {
            return true
        }
        
        return false
    }
    
    func messageLimit() -> Int {
        guard let subscription = currentSubscription else {
            return 0
        }
        
        switch subscription.plan.id {
        case "free":
            return 100
        case "pro_monthly", "pro_annual":
            return Int.max
        default:
            return 0
        }
    }
    
    func sessionLimit() -> Int {
        guard let subscription = currentSubscription else {
            return 0
        }
        
        switch subscription.plan.id {
        case "free":
            return 3
        case "pro_monthly", "pro_annual":
            return Int.max
        default:
            return 0
        }
    }
    
    // MARK: - Internal Helpers
    private func loadFreeSubscription() {
        let freePlan = Self.plans.first { $0.id == "free" }!
        self.currentSubscription = Subscription(
            plan: freePlan,
            purchaseDate: Date(),
            expiresAt: nil,
            autoRenews: false,
            transactionId: nil
        )
    }
    
    private func validateReceipt() -> Bool {
        // In a real app, this would validate the receipt with App Store or backend
        // For now, we check if subscription exists and hasn't expired
        guard let subscription = currentSubscription else {
            return false
        }
        
        if subscription.plan.id == "free" {
            return true
        }
        
        if let expiresAt = subscription.expiresAt {
            return Date() < expiresAt
        }
        
        return true
    }
    
    private func parseSubscriptionFromReceipt() throws -> Subscription {
        // In a real app, this would parse the actual receipt
        // For now, return current subscription or free tier
        if let subscription = currentSubscription {
            return subscription
        }
        
        let freePlan = Self.plans.first { $0.id == "free" }!
        return Subscription(
            plan: freePlan,
            purchaseDate: Date(),
            expiresAt: nil,
            autoRenews: false,
            transactionId: nil
        )
    }
}
