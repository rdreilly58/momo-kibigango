import SwiftUI

@main
struct MomotaroApp: App {
    @StateObject private var appState = AppState()
    @StateObject private var openClawManager = OpenClawManager()
    @StateObject private var subscriptionManager = SubscriptionManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .environmentObject(openClawManager)
                .environmentObject(subscriptionManager)
                .onAppear {
                    configureAppearance()
                    openClawManager.initialize()
                }
        }
    }
    
    private func configureAppearance() {
        // Configure the app's visual appearance
        let appearance = UITabBarAppearance()
        appearance.configureWithOpaqueBackground()
        UITabBar.appearance().standardAppearance = appearance
        UITabBar.appearance().scrollEdgeAppearance = appearance
        
        // Navigation bar appearance
        let navAppearance = UINavigationBarAppearance()
        navAppearance.configureWithOpaqueBackground()
        UINavigationBar.appearance().standardAppearance = navAppearance
        UINavigationBar.appearance().scrollEdgeAppearance = navAppearance
    }
}

// MARK: - App State Management
class AppState: ObservableObject {
    @Published var isOnboardingComplete = false
    @Published var selectedTab: MainTab = .chat
    @Published var showingSettings = false
    @Published var showingGatewaySetup = false
    
    enum MainTab: String, CaseIterable {
        case chat = "Chat"
        case sessions = "Sessions" 
        case dashboard = "Dashboard"
        case tools = "Tools"
        case settings = "Settings"
        
        var systemImage: String {
            switch self {
            case .chat: return "message.fill"
            case .sessions: return "rectangle.stack.fill"
            case .dashboard: return "chart.line.uptrend.xyaxis"
            case .tools: return "wrench.and.screwdriver.fill"
            case .settings: return "gear"
            }
        }
    }
}