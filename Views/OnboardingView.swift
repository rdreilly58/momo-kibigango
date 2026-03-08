import SwiftUI

struct OnboardingView: View {
    @EnvironmentObject var appState: AppState
    @State private var currentPage = 0
    private let pages = OnboardingPage.allCases
    
    var body: some View {
        NavigationView {
            VStack {
                TabView(selection: $currentPage) {
                    ForEach(pages.indices, id: \\.self) { index in
                        OnboardingPageView(page: pages[index])
                            .tag(index)
                    }
                }
                .tabViewStyle(.page(indexDisplayMode: .always))
                .indexViewStyle(.page(backgroundDisplayMode: .always))
                
                Spacer()
                
                HStack {
                    if currentPage > 0 {
                        Button("Previous") {
                            withAnimation {
                                currentPage -= 1
                            }
                        }
                        .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    if currentPage < pages.count - 1 {
                        Button("Next") {
                            withAnimation {
                                currentPage += 1
                            }
                        }
                        .fontWeight(.semibold)
                        .foregroundColor(.orange)
                    } else {
                        Button("Get Started") {
                            completeOnboarding()
                        }
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                        .padding()
                        .background(.orange)
                        .cornerRadius(12)
                    }
                }
                .padding()
            }
            .navigationTitle("Welcome to Momotaro")
            .navigationBarTitleDisplayMode(.large)
        }
    }
    
    private func completeOnboarding() {
        withAnimation {
            appState.isOnboardingComplete = true
        }
    }
}

struct OnboardingPageView: View {
    let page: OnboardingPage
    
    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: page.systemImage)
                .font(.system(size: 80))
                .foregroundColor(.orange)
                .padding(.top, 40)
            
            VStack(spacing: 16) {
                Text(page.title)
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .multilineTextAlignment(.center)
                
                Text(page.description)
                    .font(.body)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }
            
            Spacer()
        }
        .padding()
    }
}

enum OnboardingPage: CaseIterable {
    case welcome
    case features
    case privacy
    case gateway
    
    var title: String {
        switch self {
        case .welcome:
            return "Welcome to Momotaro"
        case .features:
            return "AI-Powered Automation"
        case .privacy:
            return "Your Data, Your Control"
        case .gateway:
            return "Connect Your Gateway"
        }
    }
    
    var description: String {
        switch self {
        case .welcome:
            return "Your AI assistant companion, bringing the power of OpenClaw to your iPhone. Named after the legendary peach boy who befriended companions and conquered challenges."
        case .features:
            return "Chat with AI agents, upload files, capture photos for analysis, and automate your workflows. Upgrade to Pro or Enterprise for advanced features like voice messages and Siri Shortcuts."
        case .privacy:
            return "Momotaro connects to your self-hosted OpenClaw gateway. Your conversations and data stay on your servers, not ours. Complete privacy and control over your AI interactions."
        case .gateway:
            return "Ready to connect to your OpenClaw gateway? You'll need your gateway URL and authentication details to get started."
        }
    }
    
    var systemImage: String {
        switch self {
        case .welcome:
            return "hands.sparkles.fill"
        case .features:
            return "brain.head.profile"
        case .privacy:
            return "lock.shield.fill"
        case .gateway:
            return "network"
        }
    }
}

#Preview {
    OnboardingView()
        .environmentObject(AppState())
}