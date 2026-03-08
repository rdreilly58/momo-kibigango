import Foundation
import Combine
import Starscream
import Crypto

/// Core OpenClaw gateway manager handling WebSocket connections, authentication, and message routing
@MainActor
class OpenClawManager: NSObject, ObservableObject {
    
    // MARK: - Published Properties
    @Published var isConnected = false
    @Published var connectionStatus: ConnectionStatus = .disconnected
    @Published var currentSession: ChatSession?
    @Published var availableSessions: [ChatSession] = []
    @Published var messages: [ChatMessage] = []
    @Published var systemStatus: SystemStatus?
    
    // MARK: - Private Properties
    private var webSocket: WebSocket?
    private var deviceCredentials: DeviceCredentials?
    private var gatewayConfig: GatewayConfig?
    private var pingTimer: Timer?
    private var reconnectAttempts = 0
    private let maxReconnectAttempts = 5
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Types
    enum ConnectionStatus: String, CaseIterable {
        case disconnected = "Disconnected"
        case connecting = "Connecting"
        case authenticating = "Authenticating"
        case connected = "Connected"
        case reconnecting = "Reconnecting"
        case error = "Error"
        
        var color: Color {
            switch self {
            case .disconnected, .error: return .red
            case .connecting, .authenticating, .reconnecting: return .orange
            case .connected: return .green
            }
        }
    }
    
    struct GatewayConfig: Codable {
        let url: String
        let port: Int
        let useSSL: Bool
        let deviceName: String
        
        var webSocketURL: URL? {
            let scheme = useSSL ? "wss" : "ws"
            return URL(string: "\\(scheme)://\\(url):\\(port)/ws")
        }
    }
    
    struct DeviceCredentials: Codable {
        let deviceId: String
        let privateKey: Data
        let publicKey: Data
        
        static func generate() -> DeviceCredentials {
            let privateKey = Curve25519.Signing.PrivateKey()
            return DeviceCredentials(
                deviceId: UUID().uuidString,
                privateKey: privateKey.rawRepresentation,
                publicKey: privateKey.publicKey.rawRepresentation
            )
        }
    }
    
    // MARK: - Initialization
    override init() {
        super.init()
        loadStoredConfiguration()
    }
    
    func initialize() {
        loadStoredConfiguration()
        if let config = gatewayConfig {
            connect(to: config)
        }
    }
    
    // MARK: - Public Connection Methods
    func setupGateway(url: String, port: Int, useSSL: Bool, deviceName: String) {
        let config = GatewayConfig(
            url: url,
            port: port,
            useSSL: useSSL,
            deviceName: deviceName
        )
        
        self.gatewayConfig = config
        self.deviceCredentials = DeviceCredentials.generate()
        
        saveConfiguration()
        connect(to: config)
    }
    
    func connect() {
        guard let config = gatewayConfig else {
            print("❌ No gateway configuration available")
            return
        }
        connect(to: config)
    }
    
    func disconnect() {
        webSocket?.disconnect()
        pingTimer?.invalidate()
        pingTimer = nil
        updateConnectionStatus(.disconnected)
    }
    
    // MARK: - Message Sending
    func sendMessage(_ text: String, to sessionId: String? = nil) {
        guard isConnected else {
            print("❌ Cannot send message: not connected")
            return
        }
        
        let message = OpenClawMessage(
            type: .chat,
            sessionId: sessionId ?? currentSession?.id,
            content: ["text": text],
            timestamp: Date()
        )
        
        sendMessage(message)
    }
    
    func sendSystemCommand(_ command: String, parameters: [String: Any] = [:]) {
        guard isConnected else {
            print("❌ Cannot send command: not connected")
            return
        }
        
        var content = parameters
        content["command"] = command
        
        let message = OpenClawMessage(
            type: .system,
            content: content,
            timestamp: Date()
        )
        
        sendMessage(message)
    }
    
    // MARK: - Session Management
    func createSession(name: String? = nil) {
        sendSystemCommand("create_session", parameters: [
            "name": name ?? "Mobile Session \\(Date().formatted(.dateTime.hour().minute()))"
        ])
    }
    
    func switchToSession(_ session: ChatSession) {
        currentSession = session
        sendSystemCommand("switch_session", parameters: ["sessionId": session.id])
        loadSessionMessages(session.id)
    }
    
    func loadSessionMessages(_ sessionId: String) {
        sendSystemCommand("get_session_history", parameters: [
            "sessionId": sessionId,
            "limit": 50
        ])
    }
    
    // MARK: - Private Implementation
    private func connect(to config: GatewayConfig) {
        guard let url = config.webSocketURL else {
            print("❌ Invalid gateway URL")
            return
        }
        
        updateConnectionStatus(.connecting)
        
        var request = URLRequest(url: url)
        request.setValue("Momotaro/1.0", forHTTPHeaderField: "User-Agent")
        
        webSocket = WebSocket(request: request)
        webSocket?.delegate = self
        webSocket?.connect()
        
        // Setup reconnection timeout
        DispatchQueue.main.asyncAfter(deadline: .now() + 10) { [weak self] in
            if self?.connectionStatus == .connecting {
                self?.handleConnectionTimeout()
            }
        }
    }
    
    private func updateConnectionStatus(_ status: ConnectionStatus) {
        connectionStatus = status
        isConnected = (status == .connected)
        
        if status == .connected {
            reconnectAttempts = 0
            startPingTimer()
        } else {
            pingTimer?.invalidate()
            pingTimer = nil
        }
    }
    
    private func sendMessage(_ message: OpenClawMessage) {
        guard let webSocket = webSocket,
              let jsonData = try? JSONEncoder().encode(message),
              let jsonString = String(data: jsonData, encoding: .utf8) else {
            print("❌ Failed to encode message")
            return
        }
        
        webSocket.write(string: jsonString)
    }
    
    private func handleIncomingMessage(_ data: Data) {
        guard let message = try? JSONDecoder().decode(OpenClawMessage.self, from: data) else {
            print("❌ Failed to decode message")
            return
        }
        
        switch message.type {
        case .chat:
            handleChatMessage(message)
        case .system:
            handleSystemMessage(message)
        case .auth:
            handleAuthMessage(message)
        case .sessions:
            handleSessionsMessage(message)
        case .status:
            handleStatusMessage(message)
        }
    }
    
    private func handleChatMessage(_ message: OpenClawMessage) {
        let chatMessage = ChatMessage(
            id: message.id ?? UUID().uuidString,
            content: message.content["text"] as? String ?? "",
            isFromUser: message.content["fromUser"] as? Bool ?? false,
            timestamp: message.timestamp,
            sessionId: message.sessionId
        )
        
        messages.append(chatMessage)
    }
    
    private func handleSystemMessage(_ message: OpenClawMessage) {
        if let command = message.content["command"] as? String {
            print("📡 System command response: \\(command)")
        }
    }
    
    private func handleAuthMessage(_ message: OpenClawMessage) {
        if message.content["status"] as? String == "authenticated" {
            updateConnectionStatus(.connected)
            loadSessions()
        } else {
            print("❌ Authentication failed")
            updateConnectionStatus(.error)
        }
    }
    
    private func handleSessionsMessage(_ message: OpenClawMessage) {
        if let sessionsData = message.content["sessions"] as? [[String: Any]] {
            availableSessions = sessionsData.compactMap { sessionDict in
                guard let id = sessionDict["id"] as? String,
                      let name = sessionDict["name"] as? String else { return nil }
                
                return ChatSession(
                    id: id,
                    name: name,
                    lastActivity: Date(),
                    isActive: sessionDict["active"] as? Bool ?? false
                )
            }
            
            if currentSession == nil, let firstSession = availableSessions.first {
                switchToSession(firstSession)
            }
        }
    }
    
    private func handleStatusMessage(_ message: OpenClawMessage) {
        // Handle system status updates
        if let statusData = message.content["status"] as? [String: Any] {
            // Update system status
        }
    }
    
    private func authenticate() {
        guard let credentials = deviceCredentials else {
            print("❌ No device credentials available")
            return
        }
        
        updateConnectionStatus(.authenticating)
        
        let authMessage = OpenClawMessage(
            type: .auth,
            content: [
                "deviceId": credentials.deviceId,
                "publicKey": credentials.publicKey.base64EncodedString(),
                "timestamp": Date().timeIntervalSince1970
            ],
            timestamp: Date()
        )
        
        sendMessage(authMessage)
    }
    
    private func loadSessions() {
        sendSystemCommand("list_sessions")
    }
    
    private func startPingTimer() {
        pingTimer = Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { [weak self] _ in
            self?.sendPing()
        }
    }
    
    private func sendPing() {
        webSocket?.write(ping: Data())
    }
    
    private func handleConnectionTimeout() {
        print("⏰ Connection timeout")
        updateConnectionStatus(.error)
        attemptReconnection()
    }
    
    private func attemptReconnection() {
        guard reconnectAttempts < maxReconnectAttempts else {
            print("❌ Max reconnection attempts reached")
            updateConnectionStatus(.error)
            return
        }
        
        reconnectAttempts += 1
        updateConnectionStatus(.reconnecting)
        
        let delay = TimeInterval(min(reconnectAttempts * 2, 30))
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            self?.connect()
        }
    }
    
    private func saveConfiguration() {
        // Save gateway config and device credentials to keychain/UserDefaults
        if let configData = try? JSONEncoder().encode(gatewayConfig) {
            UserDefaults.standard.set(configData, forKey: "gateway_config")
        }
        
        if let credentialsData = try? JSONEncoder().encode(deviceCredentials) {
            // Store in keychain for security
            KeychainManager.store(data: credentialsData, for: "device_credentials")
        }
    }
    
    private func loadStoredConfiguration() {
        // Load gateway config
        if let configData = UserDefaults.standard.data(forKey: "gateway_config"),
           let config = try? JSONDecoder().decode(GatewayConfig.self, from: configData) {
            gatewayConfig = config
        }
        
        // Load device credentials from keychain
        if let credentialsData = KeychainManager.retrieve(for: "device_credentials"),
           let credentials = try? JSONDecoder().decode(DeviceCredentials.self, from: credentialsData) {
            deviceCredentials = credentials
        }
    }
}

// MARK: - WebSocket Delegate
extension OpenClawManager: WebSocketDelegate {
    nonisolated func didReceive(event: Starscream.WebSocketEvent, client: Starscream.WebSocketClient) {
        DispatchQueue.main.async { [weak self] in
            self?.handleWebSocketEvent(event)
        }
    }
    
    private func handleWebSocketEvent(_ event: WebSocketEvent) {
        switch event {
        case .connected(let headers):
            print("🟢 WebSocket connected: \\(headers)")
            authenticate()
            
        case .disconnected(let reason, let code):
            print("🔴 WebSocket disconnected: \\(reason) (code: \\(code))")
            updateConnectionStatus(.disconnected)
            
        case .text(let string):
            if let data = string.data(using: .utf8) {
                handleIncomingMessage(data)
            }
            
        case .binary(let data):
            handleIncomingMessage(data)
            
        case .ping(_):
            webSocket?.write(pong: Data())
            
        case .pong(_):
            break // Pong received
            
        case .viabilityChanged(let isViable):
            print("📶 Connection viability changed: \\(isViable)")
            
        case .reconnectSuggested(let suggested):
            if suggested && !isConnected {
                attemptReconnection()
            }
            
        case .cancelled:
            print("🚫 WebSocket connection cancelled")
            updateConnectionStatus(.disconnected)
            
        case .error(let error):
            print("❌ WebSocket error: \\(error?.localizedDescription ?? "Unknown")")
            updateConnectionStatus(.error)
            attemptReconnection()
            
        case .peerClosed:
            print("👋 Peer closed connection")
            updateConnectionStatus(.disconnected)
        }
    }
}