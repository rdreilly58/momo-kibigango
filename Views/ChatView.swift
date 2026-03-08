import SwiftUI

struct ChatView: View {
    @EnvironmentObject var openClawManager: OpenClawManager
    @EnvironmentObject var subscriptionManager: SubscriptionManager
    @State private var messageText = ""
    @State private var showingSubscriptionSheet = false
    @FocusState private var messageFieldFocused: Bool
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Messages list
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 12) {
                            ForEach(openClawManager.messages) { message in
                                ChatMessageView(message: message)
                            }
                        }
                        .padding()
                    }
                    .onChange(of: openClawManager.messages.count) { _, _ in
                        if let lastMessage = openClawManager.messages.last {
                            withAnimation(.easeInOut(duration: 0.3)) {
                                proxy.scrollTo(lastMessage.id, anchor: .bottom)
                            }
                        }
                    }
                }
                
                Divider()
                
                // Message input
                VStack(spacing: 8) {
                    HStack(spacing: 12) {
                        // Attachment button
                        Button(action: { showAttachmentOptions() }) {
                            Image(systemName: "plus.circle.fill")
                                .font(.title2)
                                .foregroundColor(.orange)
                        }
                        
                        // Message text field
                        TextField("Message Momotaro...", text: $messageText, axis: .vertical)
                            .textFieldStyle(.roundedBorder)
                            .focused($messageFieldFocused)
                            .lineLimit(1...4)
                        
                        // Voice message button (Pro feature)
                        Button(action: { showVoiceMessage() }) {
                            Image(systemName: "mic.fill")
                                .font(.title2)
                                .foregroundColor(subscriptionManager.hasFeature(.voiceMessages) ? .orange : .gray)
                        }
                        .disabled(!subscriptionManager.hasFeature(.voiceMessages))
                        
                        // Send button
                        Button(action: sendMessage) {
                            Image(systemName: "arrow.up.circle.fill")
                                .font(.title2)
                                .foregroundColor(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? .gray : .orange)
                        }
                        .disabled(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                    }
                    .padding(.horizontal)
                    
                    // Session info
                    if let session = openClawManager.currentSession {
                        HStack {
                            Image(systemName: "bubble.left.and.bubble.right")
                                .foregroundColor(.secondary)
                            Text(session.displayName)
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Spacer()
                            Text("\\(openClawManager.messages.count) messages")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .padding(.horizontal)
                        .padding(.bottom, 4)
                    }
                }
                .padding(.top, 8)
                .padding(.bottom)
                .background(.regularMaterial, in: Rectangle())
            }
            .navigationTitle("Chat")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button("New Session") {
                            openClawManager.createSession()
                        }
                        
                        Divider()
                        
                        if !subscriptionManager.hasFeature(.backgroundMonitoring) {
                            Button("Upgrade for Voice & More") {
                                showingSubscriptionSheet = true
                            }
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
        }
        .sheet(isPresented: $showingSubscriptionSheet) {
            SubscriptionView()
        }
    }
    
    private func sendMessage() {
        let trimmedText = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedText.isEmpty else { return }
        
        openClawManager.sendMessage(trimmedText)
        messageText = ""
        messageFieldFocused = true
    }
    
    private func showAttachmentOptions() {
        // Show attachment options (camera, files, etc.)
        // Implementation depends on subscription tier
        if !subscriptionManager.hasFeature(.largeFileUploads) {
            showingSubscriptionSheet = true
        }
    }
    
    private func showVoiceMessage() {
        if !subscriptionManager.hasFeature(.voiceMessages) {
            showingSubscriptionSheet = true
        } else {
            // Show voice recording interface
        }
    }
}

struct ChatMessageView: View {
    let message: ChatMessage
    
    var body: some View {
        HStack(alignment: .top, spacing: 8) {
            if message.isFromUser {
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text(message.content)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(.orange)
                        .foregroundColor(.white)
                        .clipShape(ChatBubbleShape(isFromUser: true))
                    
                    Text(message.timestampFormatted)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                
                // User avatar
                Circle()
                    .fill(.orange.opacity(0.2))
                    .frame(width: 32, height: 32)
                    .overlay(
                        Text("You")
                            .font(.caption2)
                            .fontWeight(.medium)
                            .foregroundColor(.orange)
                    )
            } else {
                // Momotaro avatar
                Circle()
                    .fill(.orange.gradient)
                    .frame(width: 32, height: 32)
                    .overlay(
                        Text("🍑")
                            .font(.caption)
                    )
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(message.content)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(.secondary.opacity(0.1))
                        .clipShape(ChatBubbleShape(isFromUser: false))
                    
                    Text(message.timestampFormatted)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
            }
        }
        .padding(.horizontal, 4)
    }
}

struct ChatBubbleShape: Shape {
    let isFromUser: Bool
    
    func path(in rect: CGRect) -> Path {
        let radius: CGFloat = 16
        let tailSize: CGFloat = 6
        
        var path = Path()
        
        if isFromUser {
            // Right-aligned bubble with tail on bottom right
            path.addRoundedRect(
                in: CGRect(x: 0, y: 0, width: rect.width - tailSize, height: rect.height - tailSize),
                cornerSize: CGSize(width: radius, height: radius)
            )
            
            // Add tail
            path.move(to: CGPoint(x: rect.width - tailSize, y: rect.height - tailSize - radius))
            path.addLine(to: CGPoint(x: rect.width, y: rect.height))
            path.addLine(to: CGPoint(x: rect.width - tailSize, y: rect.height - tailSize))
        } else {
            // Left-aligned bubble with tail on bottom left
            path.addRoundedRect(
                in: CGRect(x: tailSize, y: 0, width: rect.width - tailSize, height: rect.height - tailSize),
                cornerSize: CGSize(width: radius, height: radius)
            )
            
            // Add tail
            path.move(to: CGPoint(x: tailSize, y: rect.height - tailSize - radius))
            path.addLine(to: CGPoint(x: 0, y: rect.height))
            path.addLine(to: CGPoint(x: tailSize, y: rect.height - tailSize))
        }
        
        return path
    }
}

#Preview {
    ChatView()
        .environmentObject(OpenClawManager())
        .environmentObject(SubscriptionManager())
}