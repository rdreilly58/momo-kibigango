import Foundation

// MARK: - SubscriptionPlan
/// Represents a subscription plan tier
struct SubscriptionPlan: Identifiable, Hashable, Codable {
    let id: String
    let name: String
    let description: String
    let price: String?
    let productId: String?
    let features: [String]
    
    init(id: String, name: String, description: String, price: String? = nil, productId: String? = nil, features: [String]) {
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.productId = productId
        self.features = features
    }
    
    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
    
    static func == (lhs: SubscriptionPlan, rhs: SubscriptionPlan) -> Bool {
        lhs.id == rhs.id
    }
}

// MARK: - Subscription
/// Represents an active subscription
struct Subscription: Equatable, Codable {
    let plan: SubscriptionPlan
    let purchaseDate: Date
    let expiresAt: Date?
    let autoRenews: Bool
    let transactionId: String?
    
    static func == (lhs: Subscription, rhs: Subscription) -> Bool {
        lhs.plan.id == rhs.plan.id &&
        lhs.purchaseDate == rhs.purchaseDate &&
        lhs.expiresAt == rhs.expiresAt &&
        lhs.autoRenews == rhs.autoRenews &&
        lhs.transactionId == rhs.transactionId
    }
}

// MARK: - Feature
/// Features available based on subscription tier
enum Feature: String, Hashable, CaseIterable {
    case messageHistory
    case multipleSessions
    case fullTextSearch
    case messageExport
    case analyticsAccess
}

// MARK: - SubscriptionError
/// Errors that can occur during subscription operations
enum SubscriptionError: Error, Equatable {
    case productNotFound
    case purchaseFailed(String)
    case restorationFailed
    case invalidReceipt
    case noSubscription
    case networkError
    case storeKitError(String)
    
    static func == (lhs: SubscriptionError, rhs: SubscriptionError) -> Bool {
        switch (lhs, rhs) {
        case (.productNotFound, .productNotFound),
             (.restorationFailed, .restorationFailed),
             (.invalidReceipt, .invalidReceipt),
             (.noSubscription, .noSubscription),
             (.networkError, .networkError):
            return true
        case (.purchaseFailed(let a), .purchaseFailed(let b)):
            return a == b
        case (.storeKitError(let a), .storeKitError(let b)):
            return a == b
        default:
            return false
        }
    }
}

// MARK: - FeatureStatus
/// Status of a feature (available, quota exceeded, requires pro, or disabled)
enum FeatureStatus: String, CaseIterable {
    case available
    case quotaExceeded
    case requiresPro
    case disabled
}

// MARK: - FeatureError
/// Errors related to feature access and quotas
enum FeatureError: Error, Equatable {
    case quotaExceeded(String)
    case requiresProSubscription
    case sessionLimitReached
    case messageLimitReached
    case unauthorized
}
