import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var openClawManager: OpenClawManager
    
    var body: some View {
        Group {
            if !appState.isOnboardingComplete {
                OnboardingView()
            } else if !openClawManager.isConnected {
                GatewayConnectionView()
            } else {
                MainTabView()
            }
        }
        .animation(.easeInOut(duration: 0.3), value: appState.isOnboardingComplete)
        .animation(.easeInOut(duration: 0.3), value: openClawManager.isConnected)
    }
}

// MARK: - Main Tab Interface
struct MainTabView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        TabView(selection: $appState.selectedTab) {
            ChatView()
                .tabItem {
                    Label(AppState.MainTab.chat.rawValue, 
                          systemImage: AppState.MainTab.chat.systemImage)
                }
                .tag(AppState.MainTab.chat)
            
            SessionsView()
                .tabItem {
                    Label(AppState.MainTab.sessions.rawValue,
                          systemImage: AppState.MainTab.sessions.systemImage)
                }
                .tag(AppState.MainTab.sessions)
            
            DashboardView()
                .tabItem {
                    Label(AppState.MainTab.dashboard.rawValue,
                          systemImage: AppState.MainTab.dashboard.systemImage)
                }
                .tag(AppState.MainTab.dashboard)
            
            ToolsView()
                .tabItem {
                    Label(AppState.MainTab.tools.rawValue,
                          systemImage: AppState.MainTab.tools.systemImage)
                }
                .tag(AppState.MainTab.tools)
            
            SettingsView()
                .tabItem {
                    Label(AppState.MainTab.settings.rawValue,
                          systemImage: AppState.MainTab.settings.systemImage)
                }
                .tag(AppState.MainTab.settings)
        }
        .tint(.orange) // Momotaro peach theme
    }
}

#Preview {
    ContentView()
        .environmentObject(AppState())
        .environmentObject(OpenClawManager())
        .environmentObject(SubscriptionManager())
}