import SwiftUI

@main
struct MomotaroApp: App {
    @StateObject private var securityManager = SecurityManager()
    @StateObject private var subscriptionManager = SubscriptionManager()
    
    @StateObject private var featureManager: FeatureManager
    
    init() {
        let security = SecurityManager()
        let subscription = SubscriptionManager()
        let feature = FeatureManager(subscriptionManager: subscription, securityManager: security)
        
        _securityManager = StateObject(wrappedValue: security)
        _subscriptionManager = StateObject(wrappedValue: subscription)
        _featureManager = StateObject(wrappedValue: feature)
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(securityManager)
                .environmentObject(subscriptionManager)
                .environmentObject(featureManager)
        }
    }
}
