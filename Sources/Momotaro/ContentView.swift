import SwiftUI

struct ContentView: View {
    @StateObject private var gateway = GatewayClient()
    @State private var messageInput = ""
    @State private var messages: [GatewayMessage] = []
    @State private var gatewayURL = "ws://localhost:8080"
    @State private var showSettings = false
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Header
                VStack(spacing: 8) {
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("🍑 Momotaro")
                                .font(.headline)
                            Text(gateway.connectionStatus)
                                .font(.caption)
                                .foregroundStyle(gateway.isConnected ? .green : .red)
                        }
                        Spacer()
                        Button(action: { showSettings = true }) {
                            Image(systemName: "gear")
                                .foregroundStyle(.blue)
                        }
                    }
                    .padding()
                    
                    // Connection button
                    HStack(spacing: 8) {
                        Button(action: {
                            if gateway.isConnected {
                                gateway.disconnect()
                            } else {
                                gateway.connect()
                            }
                        }) {
                            HStack {
                                Image(systemName: gateway.isConnected ? "checkmark.circle.fill" : "circle")
                                Text(gateway.isConnected ? "Connected" : "Connect")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(gateway.isConnected ? .green : .blue)
                            .foregroundStyle(.white)
                            .cornerRadius(8)
                        }
                    }
                    .padding(.horizontal)
                    .padding(.bottom)
                }
                .background(Color(.systemGray6))
                
                // Messages display
                if messages.isEmpty {
                    VStack(spacing: 16) {
                        Spacer()
                        Image(systemName: "bubble.right")
                            .font(.system(size: 40))
                            .foregroundStyle(.gray)
                        Text("No messages yet")
                            .foregroundStyle(.secondary)
                        Text("Connect and send a message to get started")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        Spacer()
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    ScrollViewReader { reader in
                        ScrollView {
                            VStack(alignment: .leading, spacing: 8) {
                                ForEach(Array(messages.enumerated()), id: \.offset) { index, message in
                                    MessageBubble(message: message)
                                        .id(index)
                                }
                            }
                            .padding()
                            .onChange(of: messages.count) {
                                withAnimation {
                                    reader.scrollTo(messages.count - 1, anchor: .bottom)
                                }
                            }
                        }
                    }
                }
                
                // Error display
                if let error = gateway.error {
                    VStack(spacing: 8) {
                        HStack {
                            Image(systemName: "exclamationmark.circle.fill")
                                .foregroundStyle(.red)
                            Text(error)
                                .font(.caption)
                            Spacer()
                            Button(action: { gateway.error = nil }) {
                                Image(systemName: "xmark.circle.fill")
                                    .foregroundStyle(.gray)
                            }
                        }
                        .padding()
                        .background(Color(.systemRed).opacity(0.1))
                        .cornerRadius(8)
                        .padding()
                    }
                }
                
                // Message input
                VStack(spacing: 8) {
                    HStack(spacing: 8) {
                        TextField("Send a message...", text: $messageInput)
                            .textFieldStyle(.roundedBorder)
                            .disabled(!gateway.isConnected)
                        
                        Button(action: sendMessage) {
                            Image(systemName: "arrow.up.circle.fill")
                                .font(.system(size: 20))
                                .foregroundStyle(gateway.isConnected ? .blue : .gray)
                        }
                        .disabled(!gateway.isConnected || messageInput.isEmpty)
                    }
                    .padding()
                }
                .background(Color(.systemGray6))
            }
            .navigationTitle("OpenClaw Client")
            .sheet(isPresented: $showSettings) {
                SettingsView(gatewayURL: $gatewayURL, gateway: gateway)
            }
            .onAppear {
                gateway.onMessageReceived = { message in
                    messages.append(message)
                }
            }
        }
    }
    
    private func sendMessage() {
        guard !messageInput.isEmpty, gateway.isConnected else { return }
        gateway.sendCommand(messageInput)
        messageInput = ""
    }
}

// MARK: - Message Bubble

struct MessageBubble: View {
    let message: GatewayMessage
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(message.type)
                .font(.caption2)
                .foregroundStyle(.secondary)
            
            Text(message.content)
                .font(.body)
                .padding()
                .background(Color(.systemBlue).opacity(0.1))
                .cornerRadius(12)
        }
    }
}

// MARK: - Settings View

struct SettingsView: View {
    @Binding var gatewayURL: String
    @ObservedObject var gateway: GatewayClient
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            Form {
                Section("Gateway Configuration") {
                    TextField("Gateway URL", text: $gatewayURL)
                        .disabled(gateway.isConnected)
                        .textInputAutocapitalization(.never)
                    
                    Text("Example: ws://localhost:8080")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                
                Section("Connection Info") {
                    LabeledContent("Status", value: gateway.connectionStatus)
                    LabeledContent("Connected", value: gateway.isConnected ? "Yes" : "No")
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

#Preview {
    ContentView()
}
