import SwiftUI

// MARK: - Main SubscriptionView
@MainActor
struct SubscriptionView: View {
    @EnvironmentObject var subscriptionManager: SubscriptionManager
    @EnvironmentObject var featureManager: FeatureManager
    @State var showingError = false
    @State var errorMessage = ""
    @State var isLoading = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // Current subscription badge
                    CurrentSubscriptionBadge(planName: subscriptionManager.currentSubscription?.plan.name ?? "Free")
                    
                    // Plan cards
                    VStack(spacing: 16) {
                        FreePlanCard()
                        ProMonthlyPlanCard(isLoading: $isLoading) { error in
                            showingError = true
                            errorMessage = error
                        }
                        ProAnnualPlanCard(isLoading: $isLoading) { error in
                            showingError = true
                            errorMessage = error
                        }
                    }
                    
                    // Feature comparison
                    FeatureComparisonTable()
                    
                    // Restore button
                    RestorePurchasesButton(isLoading: $isLoading) { error in
                        if let error = error {
                            showingError = true
                            errorMessage = error
                        }
                    }
                    
                    Spacer()
                }
                .padding()
            }
            .navigationTitle("Plans & Pricing")
            .navigationBarTitleDisplayMode(.inline)
        }
        .alert("Error", isPresented: $showingError) {
            Button("Dismiss") {
                showingError = false
            }
        } message: {
            Text(errorMessage)
        }
    }
}

// MARK: - Current Subscription Badge
struct CurrentSubscriptionBadge: View {
    let planName: String
    
    var badgeColor: Color {
        if planName.contains("Pro") {
            return .blue
        } else {
            return .gray
        }
    }
    
    var badgeText: String {
        planName
    }
    
    var body: some View {
        HStack {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 16))
            Text("Current Plan: \(badgeText)")
                .font(.subheadline)
                .fontWeight(.semibold)
            Spacer()
        }
        .foregroundColor(.white)
        .padding()
        .background(badgeColor)
        .cornerRadius(8)
    }
}

// MARK: - Free Plan Card
struct FreePlanCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Free")
                        .font(.headline)
                    Text("$0/month")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                }
                Spacer()
                Image(systemName: "checkmark.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.green)
            }
            
            Divider()
            
            VStack(alignment: .leading, spacing: 8) {
                FeatureRow(icon: "message", text: "100 messages/day", included: true)
                FeatureRow(icon: "square.grid.2x2", text: "3 sessions", included: true)
                FeatureRow(icon: "magnifyingglass", text: "Search", included: false)
                FeatureRow(icon: "square.and.arrow.up", text: "Export", included: false)
            }
            
            Button(action: {}) {
                Text("Current Plan")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.gray)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
            .disabled(true)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

// MARK: - Pro Monthly Plan Card
struct ProMonthlyPlanCard: View {
    @EnvironmentObject var subscriptionManager: SubscriptionManager
    @Binding var isLoading: Bool
    let onError: (String) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Pro Monthly")
                        .font(.headline)
                    Text("$9.99/month")
                        .font(.subheadline)
                        .foregroundColor(.blue)
                }
                Spacer()
                if isLoading {
                    ProgressView()
                }
            }
            
            Divider()
            
            VStack(alignment: .leading, spacing: 8) {
                FeatureRow(icon: "infinity", text: "Unlimited messages", included: true)
                FeatureRow(icon: "infinity", text: "Unlimited sessions", included: true)
                FeatureRow(icon: "magnifyingglass", text: "Search", included: true)
                FeatureRow(icon: "square.and.arrow.up", text: "Export", included: true)
            }
            
            Button(action: {
                isLoading = true
                Task {
                    do {
                        if let plan = subscriptionManager.availablePlans.first(where: { $0.id == "pro_monthly" }) {
                            try await subscriptionManager.purchase(plan)
                        }
                        isLoading = false
                    } catch {
                        onError("Purchase failed: \(error.localizedDescription)")
                        isLoading = false
                    }
                }
            }) {
                if isLoading {
                    ProgressView()
                        .tint(.white)
                } else {
                    Text("Upgrade to Pro")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                }
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(8)
            .disabled(isLoading)
        }
        .padding()
        .background(Color(.systemBackground))
        .border(Color.blue, width: 2)
        .cornerRadius(12)
    }
}

// MARK: - Pro Annual Plan Card
struct ProAnnualPlanCard: View {
    @EnvironmentObject var subscriptionManager: SubscriptionManager
    @Binding var isLoading: Bool
    let onError: (String) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Pro Annual")
                        .font(.headline)
                    Text("$79.99/year")
                        .font(.subheadline)
                        .foregroundColor(.green)
                }
                Spacer()
                if isLoading {
                    ProgressView()
                }
            }
            
            Divider()
            
            VStack(alignment: .leading, spacing: 8) {
                FeatureRow(icon: "infinity", text: "Unlimited messages", included: true)
                FeatureRow(icon: "infinity", text: "Unlimited sessions", included: true)
                FeatureRow(icon: "magnifyingglass", text: "Search", included: true)
                FeatureRow(icon: "square.and.arrow.up", text: "Export", included: true)
                FeatureRow(icon: "sparkles", text: "Save 33% vs monthly", included: true)
            }
            
            Button(action: {
                isLoading = true
                Task {
                    do {
                        if let plan = subscriptionManager.availablePlans.first(where: { $0.id == "pro_annual" }) {
                            try await subscriptionManager.purchase(plan)
                        }
                        isLoading = false
                    } catch {
                        onError("Purchase failed: \(error.localizedDescription)")
                        isLoading = false
                    }
                }
            }) {
                if isLoading {
                    ProgressView()
                        .tint(.white)
                } else {
                    Text("Upgrade to Pro Annual")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                }
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.green)
            .foregroundColor(.white)
            .cornerRadius(8)
            .disabled(isLoading)
        }
        .padding()
        .background(Color(.systemBackground))
        .border(Color.green, width: 2)
        .cornerRadius(12)
    }
}

// MARK: - Feature Row
struct FeatureRow: View {
    let icon: String
    let text: String
    let included: Bool
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: included ? "checkmark.circle.fill" : "xmark.circle")
                .foregroundColor(included ? .green : .gray)
                .font(.system(size: 16))
            Text(text)
                .font(.subheadline)
            Spacer()
        }
    }
}

// MARK: - Feature Comparison Table
struct FeatureComparisonTable: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Feature Comparison")
                .font(.headline)
            
            VStack(spacing: 0) {
                // Header
                HStack {
                    Text("Feature")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                    Spacer()
                    Text("Free")
                        .font(.caption)
                        .fontWeight(.semibold)
                    Spacer()
                    Text("Pro")
                        .font(.caption)
                        .fontWeight(.semibold)
                }
                .padding()
                .background(Color(.systemGray6))
                
                Divider()
                
                // Rows
                ComparisonRow(feature: "Messages/day", free: "100", pro: "∞")
                Divider()
                ComparisonRow(feature: "Sessions", free: "3", pro: "∞")
                Divider()
                ComparisonRow(feature: "Search", free: "❌", pro: "✅")
                Divider()
                ComparisonRow(feature: "Export", free: "❌", pro: "✅")
                Divider()
                ComparisonRow(feature: "Analytics", free: "❌", pro: "✅")
            }
            .background(Color(.systemBackground))
            .cornerRadius(8)
        }
        .padding()
    }
}

struct ComparisonRow: View {
    let feature: String
    let free: String
    let pro: String
    
    var body: some View {
        HStack {
            Text(feature)
                .font(.subheadline)
            Spacer()
            Text(free)
                .font(.caption)
            Spacer()
            Text(pro)
                .font(.caption)
        }
        .padding()
    }
}

// MARK: - Restore Purchases Button
struct RestorePurchasesButton: View {
    @EnvironmentObject var subscriptionManager: SubscriptionManager
    @Binding var isLoading: Bool
    let onError: (String?) -> Void
    
    var body: some View {
        Button(action: {
            isLoading = true
            Task {
                do {
                    try await subscriptionManager.restorePurchases()
                    isLoading = false
                    onError(nil)
                } catch {
                    onError("Restore failed: \(error.localizedDescription)")
                    isLoading = false
                }
            }
        }) {
            if isLoading {
                ProgressView()
                    .tint(.blue)
            } else {
                Text("Restore Purchases")
                    .font(.subheadline)
                    .fontWeight(.semibold)
            }
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.systemGray6))
        .foregroundColor(.blue)
        .cornerRadius(8)
        .disabled(isLoading)
    }
}

#Preview {
    SubscriptionView()
        .environmentObject(SubscriptionManager())
        .environmentObject(FeatureManager(subscriptionManager: SubscriptionManager(), securityManager: SecurityManager()))
}
