import Foundation

/// OpenClaw Gateway WebSocket Client
/// Handles connection, authentication, and message routing
@MainActor
class GatewayClient: NSObject, ObservableObject {
    
    // MARK: - Published Properties
    @Published var isConnected = false
    @Published var connectionStatus = "Disconnected"
    @Published var lastMessage: String = ""
    @Published var error: String?
    @Published var sessionManager: SessionManager?
    @Published var isAuthenticated = false
    
    // MARK: - Private Properties
    private var webSocket: URLSessionWebSocketTask?
    private var gatewayURL: String
    private var sessionToken: String?
    private var reconnectTimer: Timer?
    private var reconnectAttempts = 0
    private let maxReconnectAttempts = 5
    private var receiveTask: Task<Void, Never>?
    private var urlSession: URLSession
    private var securityManager: SecurityManager
    private var messagePersistence: MessagePersistence
    private var deviceId: String
    private var tokenRefreshTimer: Timer?
    
    // MARK: - Callbacks
    var onMessageReceived: ((GatewayMessage) -> Void)?
    var onConnectionStatusChanged: ((Bool) -> Void)?
    var onAuthenticationStatusChanged: ((Bool) -> Void)?
    
    // MARK: - Initialization
    init(gatewayURL: String = "ws://localhost:8080", 
         urlSession: URLSession? = nil,
         securityManager: SecurityManager? = nil,
         messagePersistence: MessagePersistence? = nil) {
        self.gatewayURL = gatewayURL
        self.urlSession = urlSession ?? URLSession(configuration: .default)
        self.securityManager = securityManager ?? SecurityManager()
        self.messagePersistence = messagePersistence ?? MessagePersistence()
        self.deviceId = UUID().uuidString
        super.init()
    }
    
    // MARK: - Public Methods
    
    /// Connect to OpenClaw Gateway
    func connect(sessionToken: String? = nil) {
        self.sessionToken = sessionToken
        
        DispatchQueue.main.async {
            self.connectionStatus = "Connecting..."
            self.error = nil
        }
        
        // Create WebSocket connection
        let urlString = gatewayURL.replacingOccurrences(of: "ws://", with: "http://")
                                   .replacingOccurrences(of: "wss://", with: "https://")
        guard let url = URL(string: urlString) else {
            DispatchQueue.main.async {
                self.error = "Invalid gateway URL"
            }
            return
        }
        
        var request = URLRequest(url: url)
        request.timeoutInterval = 5
        
        // Add auth header if token provided
        if let token = sessionToken {
            request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        webSocket = self.urlSession.webSocketTask(with: url)
        webSocket?.resume()
        
        // Signal connected
        DispatchQueue.main.async {
            self.isConnected = true
            self.connectionStatus = "Connected"
            self.reconnectAttempts = 0
            self.onConnectionStatusChanged?(true)
            
            // Initialize session manager if not already done
            if self.sessionManager == nil {
                self.sessionManager = SessionManager(gateway: self)
            }
            
            // Fetch available sessions
            Task {
                await self.sessionManager?.fetchSessions()
            }
        }
        
        // Start receiving messages
        receiveMessages()
    }
    
    /// Disconnect from Gateway
    func disconnect() {
        webSocket?.cancel(with: .goingAway, reason: nil)
        webSocket = nil
        receiveTask?.cancel()
        reconnectTimer?.invalidate()
        stopTokenRefresh()
        
        DispatchQueue.main.async {
            self.isConnected = false
            self.connectionStatus = "Disconnected"
            self.isAuthenticated = false
        }
    }
    
    /// Send message to Gateway
    func sendMessage(_ message: GatewayMessage) {
        guard let jsonData = try? JSONEncoder().encode(message),
              let jsonString = String(data: jsonData, encoding: .utf8) else {
            DispatchQueue.main.async {
                self.error = "Failed to encode message"
            }
            return
        }
        
        let message = URLSessionWebSocketTask.Message.string(jsonString)
        webSocket?.send(message) { error in
            if let error = error {
                DispatchQueue.main.async {
                    self.error = "Send failed: \(error.localizedDescription)"
                }
            }
        }
    }
    
    /// Send authenticated text command
    func sendCommand(_ text: String) async throws {
        let message = GatewayMessage(
            type: "message",
            content: text,
            sessionId: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        // Sign and send
        try await sendAuthenticatedMessage(message)
        
        // Persist to MessagePersistence
        try messagePersistence.saveMessage(message, sessionId: deviceId)
    }
    
    /// Send authenticated message
    private func sendAuthenticatedMessage(_ message: GatewayMessage) async throws {
        // Get signature from SecurityManager
        let messageContent = message.content
        let signature = try await securityManager.signMessage(messageContent)
        let publicKey = try securityManager.retrievePublicKey()
        
        // Create AuthenticatedMessage
        let authenticatedMessage = AuthenticatedMessage(
            deviceId: deviceId,
            publicKey: publicKey.base64EncodedString(),
            message: message,
            signature: signature.base64EncodedString(),
            timestamp: ISO8601DateFormatter().string(from: Date()),
            nonce: UUID().uuidString
        )
        
        // Send over WebSocket
        guard let jsonData = try? JSONEncoder().encode(authenticatedMessage),
              let jsonString = String(data: jsonData, encoding: .utf8) else {
            throw NSError(domain: "GatewayClient", code: -1, userInfo: [NSLocalizedDescriptionKey: "Failed to encode authenticated message"])
        }
        
        let wsMessage = URLSessionWebSocketTask.Message.string(jsonString)
        webSocket?.send(wsMessage) { [weak self] error in
            if let error = error {
                DispatchQueue.main.async {
                    self?.error = "Send failed: \(error.localizedDescription)"
                }
            }
        }
    }
    

    
    // MARK: - Private Methods
    
    private func receiveMessages() {
        receiveTask = Task {
            while !Task.isCancelled {
                do {
                    let message = try await webSocket?.receive()
                    
                    switch message {
                    case .string(let text):
                        handleMessage(text)
                    case .data(let data):
                        if let text = String(data: data, encoding: .utf8) {
                            handleMessage(text)
                        }
                    case .none:
                        break
                    @unknown default:
                        break
                    }
                } catch {
                    if !Task.isCancelled {
                        DispatchQueue.main.async {
                            self.connectionStatus = "Error"
                            self.error = error.localizedDescription
                            self.isConnected = false
                            self.attemptReconnect()
                        }
                    }
                    break
                }
            }
        }
    }
    
    private func handleMessage(_ text: String) {
        guard let jsonData = text.data(using: .utf8),
              let message = try? JSONDecoder().decode(GatewayMessage.self, from: jsonData) else {
            DispatchQueue.main.async {
                self.error = "Failed to decode message"
            }
            return
        }
        
        // Persist received message
        do {
            try messagePersistence.saveMessage(message, sessionId: deviceId)
        } catch {
            DispatchQueue.main.async {
                self.error = "Failed to persist message: \(error.localizedDescription)"
            }
        }
        
        DispatchQueue.main.async {
            self.lastMessage = message.content
            self.onMessageReceived?(message)
        }
    }
    
    private func attemptReconnect() {
        guard reconnectAttempts < maxReconnectAttempts else {
            DispatchQueue.main.async {
                self.error = "Max reconnection attempts reached"
            }
            return
        }
        
        reconnectAttempts += 1
        let delay = Double(reconnectAttempts) * 2.0 // Exponential backoff
        
        DispatchQueue.main.async {
            self.connectionStatus = "Reconnecting (attempt \(self.reconnectAttempts)/\(self.maxReconnectAttempts))..."
            
            self.reconnectTimer?.invalidate()
            self.reconnectTimer = Timer.scheduledTimer(withTimeInterval: delay, repeats: false) { _ in
                self.connect(sessionToken: self.sessionToken)
            }
        }
    }
    
    // MARK: - Session Token Management
    
    /// Attempt to retrieve or refresh session token
    func ensureValidSessionToken() async throws {
        // Check if we have a valid token
        if let currentToken = try securityManager.retrieveSessionToken(),
           securityManager.isTokenValid(currentToken) {
            self.sessionToken = currentToken.token
            self.isAuthenticated = true
            return
        }
        
        // Token expired or missing - request new one
        try await requestSessionToken()
    }
    
    /// Request new session token from Gateway
    private func requestSessionToken() async throws {
        let message = GatewayMessage(
            type: "auth",
            content: "request_token",
            sessionId: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        
        try await sendAuthenticatedMessage(message)
    }
    
    /// Start automatic token refresh (24h)
    func startTokenRefresh() {
        tokenRefreshTimer?.invalidate()
        tokenRefreshTimer = Timer.scheduledTimer(withTimeInterval: 24 * 60 * 60, repeats: true) { [weak self] _ in
            Task {
                do {
                    try await self?.ensureValidSessionToken()
                } catch {
                    DispatchQueue.main.async {
                        self?.error = "Token refresh failed: \(error.localizedDescription)"
                    }
                }
            }
        }
    }
    
    /// Stop automatic token refresh
    func stopTokenRefresh() {
        tokenRefreshTimer?.invalidate()
        tokenRefreshTimer = nil
    }
}

// MARK: - Gateway Message Model

struct GatewayMessage: Codable {
    let type: String
    let content: String
    let sessionId: String?
    let timestamp: String
    
    enum CodingKeys: String, CodingKey {
        case type
        case content
        case sessionId = "session_id"
        case timestamp
    }
}

// MARK: - Connection State

enum ConnectionState {
    case idle
    case connecting
    case connected
    case disconnected
    case error(String)
    
    var displayText: String {
        switch self {
        case .idle:
            return "Not connected"
        case .connecting:
            return "Connecting..."
        case .connected:
            return "Connected"
        case .disconnected:
            return "Disconnected"
        case .error(let message):
            return "Error: \(message)"
        }
    }
}
