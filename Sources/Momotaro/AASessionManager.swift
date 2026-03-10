import Foundation
import Combine

// MARK: - SessionInfo Model

struct SessionInfo: Codable, Identifiable, Equatable {
    let id: String
    let name: String
    let description: String
    let type: String // "agent", "model", "custom"
    var isActive: Bool
    let createdAt: Date
    var lastUsedAt: Date?
    
    var icon: String {
        type == "agent" ? "🤖" : "⚙️"
    }
    
    enum CodingKeys: String, CodingKey {
        case id, name, description, type
        case isActive = "active"
        case createdAt = "created_at"
        case lastUsedAt = "last_used_at"
    }
}

// MARK: - SessionError

enum SessionError: LocalizedError, Equatable {
    case invalidSession
    case fetchFailed(String)
    case switchFailed(String)
    case notFound
    
    var errorDescription: String? {
        switch self {
        case .invalidSession:
            return "Invalid session"
        case .fetchFailed(let msg):
            return "Failed to fetch sessions: \(msg)"
        case .switchFailed(let msg):
            return "Failed to switch session: \(msg)"
        case .notFound:
            return "Session not found"
        }
    }
}

// MARK: - SessionManager

@MainActor
class SessionManager: NSObject, ObservableObject {
    @Published var availableSessions: [SessionInfo] = []
    @Published var currentSession: SessionInfo?
    @Published var isLoading = false
    @Published var error: SessionError?
    
    private weak var gateway: GatewayClient?
    
    init(gateway: GatewayClient) {
        self.gateway = gateway
        super.init()
    }
    
    // MARK: - Public Methods
    
    /// Fetch all available sessions from the gateway
    func fetchSessions() async {
        isLoading = true
        error = nil
        
        // Send request to gateway
        let message = GatewayMessage(
            type: "list_sessions",
            content: "",
            sessionId: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        gateway?.sendCommand(message.content)
        
        // Simulate network delay
        try? await Task.sleep(nanoseconds: 500_000_000)
        
        // Mock sessions for demonstration
        let mockSessions = [
            SessionInfo(
                id: "session_claude",
                name: "Claude AI",
                description: "Advanced reasoning model",
                type: "agent",
                isActive: true,
                createdAt: Date(),
                lastUsedAt: Date()
            ),
            SessionInfo(
                id: "session_gpt4",
                name: "GPT-4 Turbo",
                description: "OpenAI's latest model",
                type: "agent",
                isActive: false,
                createdAt: Date().addingTimeInterval(-86400),
                lastUsedAt: nil
            ),
            SessionInfo(
                id: "session_local",
                name: "Local Model",
                description: "Self-hosted inference",
                type: "custom",
                isActive: false,
                createdAt: Date().addingTimeInterval(-172800),
                lastUsedAt: nil
            )
        ]
        
        self.availableSessions = mockSessions
        self.currentSession = mockSessions.first(where: { $0.isActive })
        self.isLoading = false
    }
    
    /// Switch to a different session
    func switchSession(to session: SessionInfo) async {
        guard availableSessions.contains(session) else {
            error = .notFound
            return
        }
        
        isLoading = true
        error = nil
        
        let message = GatewayMessage(
            type: "switch_session",
            content: session.id,
            sessionId: session.id,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
        gateway?.sendCommand(message.content)
        
        // Simulate network delay
        try? await Task.sleep(nanoseconds: 300_000_000)
        
        let targetSessionId = session.id
        
        // Update all sessions: set isActive for target, false for others
        var updated: [SessionInfo] = []
        for s in availableSessions {
            var sessionToUpdate = s
            sessionToUpdate.isActive = (s.id == targetSessionId)
            sessionToUpdate.lastUsedAt = Date()
            updated.append(sessionToUpdate)
        }
        
        self.availableSessions = updated
        self.currentSession = self.availableSessions.first(where: { $0.id == targetSessionId })
        self.isLoading = false
    }
    
    /// Get session by ID
    func getSession(id: String) -> SessionInfo? {
        availableSessions.first(where: { $0.id == id })
    }
    
    /// Get all sessions of a specific type
    func getSessionsByType(_ type: String) -> [SessionInfo] {
        availableSessions.filter { $0.type == type }
    }
}
