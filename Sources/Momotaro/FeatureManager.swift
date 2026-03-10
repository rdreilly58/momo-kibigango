import Foundation

@MainActor
class FeatureManager: ObservableObject {
    // MARK: - Published Properties
    @Published var messageCount: Int = 0
    @Published var sessionCount: Int = 0
    @Published var features: [Feature: Bool] = [:]
    @Published var error: FeatureError?
    
    // MARK: - Dependencies
    let subscriptionManager: SubscriptionManager
    let securityManager: SecurityManager
    
    // MARK: - Constants
    private let dailyMessageQuota = 100
    private let totalSessionQuota = 3
    
    // MARK: - Initialization
    init(subscriptionManager: SubscriptionManager, securityManager: SecurityManager) {
        self.subscriptionManager = subscriptionManager
        self.securityManager = securityManager
        updateFeatures()
    }
    
    // MARK: - Feature Access
    func canSendMessage() -> Bool {
        let subscription = subscriptionManager.currentSubscription
        
        if subscription?.plan.id == "free" {
            return messageCount < dailyMessageQuota
        }
        
        // Pro tiers can always send
        return subscription?.plan.id == "pro_monthly" || subscription?.plan.id == "pro_annual"
    }
    
    func canCreateSession() -> Bool {
        let subscription = subscriptionManager.currentSubscription
        
        if subscription?.plan.id == "free" {
            return sessionCount < totalSessionQuota
        }
        
        // Pro tiers can create unlimited sessions
        return subscription?.plan.id == "pro_monthly" || subscription?.plan.id == "pro_annual"
    }
    
    func canSearch() -> Bool {
        return subscriptionManager.canAccess(.fullTextSearch)
    }
    
    func canExport() -> Bool {
        return subscriptionManager.canAccess(.messageExport)
    }
    
    func canAccessAnalytics() -> Bool {
        return subscriptionManager.canAccess(.analyticsAccess)
    }
    
    func hasAccess(to feature: Feature) -> Bool {
        switch feature {
        case .messageHistory:
            return canSendMessage()
        case .multipleSessions:
            return canCreateSession()
        case .fullTextSearch:
            return canSearch()
        case .messageExport:
            return canExport()
        case .analyticsAccess:
            return canAccessAnalytics()
        }
    }
    
    // MARK: - Quota Management
    func messageQuotaRemaining() -> Int {
        let subscription = subscriptionManager.currentSubscription
        
        if subscription?.plan.id == "free" {
            return max(0, dailyMessageQuota - messageCount)
        }
        
        // Pro tiers have unlimited quota
        return Int.max
    }
    
    func sessionQuotaRemaining() -> Int {
        let subscription = subscriptionManager.currentSubscription
        
        if subscription?.plan.id == "free" {
            return max(0, totalSessionQuota - sessionCount)
        }
        
        // Pro tiers have unlimited quota
        return Int.max
    }
    
    func incrementMessageCount() throws {
        guard canSendMessage() else {
            error = .messageLimitReached
            throw FeatureError.messageLimitReached
        }
        
        messageCount += 1
    }
    
    func incrementSessionCount() throws {
        guard canCreateSession() else {
            error = .sessionLimitReached
            throw FeatureError.sessionLimitReached
        }
        
        sessionCount += 1
    }
    
    func resetDailyQuotas() {
        messageCount = 0
        sessionCount = 0
        error = nil
    }
    
    // MARK: - Status
    func getFeatureStatus() -> [Feature: FeatureStatus] {
        var status: [Feature: FeatureStatus] = [:]
        
        for feature in Feature.allCases {
            if hasAccess(to: feature) {
                status[feature] = .available
            } else {
                let subscription = subscriptionManager.currentSubscription
                if subscription?.plan.id == "free" {
                    status[feature] = .requiresPro
                } else {
                    status[feature] = .disabled
                }
            }
        }
        
        // Check quota-based status
        if !canSendMessage() && messageCount >= dailyMessageQuota {
            status[.messageHistory] = .quotaExceeded
        }
        
        if !canCreateSession() && sessionCount >= totalSessionQuota {
            status[.multipleSessions] = .quotaExceeded
        }
        
        return status
    }
    
    func refreshFeatures() async {
        updateFeatures()
    }
    
    // MARK: - Internal Helpers
    private func updateFeatures() {
        for feature in Feature.allCases {
            features[feature] = hasAccess(to: feature)
        }
    }
    
    private func checkMessageQuota() -> Bool {
        messageCount < dailyMessageQuota
    }
    
    private func checkSessionQuota() -> Bool {
        sessionCount < totalSessionQuota
    }
}
