import Foundation
import SwiftUI

// MARK: - Core Data Models

/// OpenClaw WebSocket message protocol
struct OpenClawMessage: Codable {
    let id: String?
    let type: MessageType
    let sessionId: String?
    let content: [String: Any]
    let timestamp: Date
    
    enum MessageType: String, Codable {
        case chat = "chat"
        case system = "system" 
        case auth = "auth"
        case sessions = "sessions"
        case status = "status"
    }
    
    init(type: MessageType, sessionId: String? = nil, content: [String: Any], timestamp: Date) {
        self.id = UUID().uuidString
        self.type = type
        self.sessionId = sessionId
        self.content = content
        self.timestamp = timestamp
    }
    
    // Custom encoding/decoding to handle [String: Any]
    enum CodingKeys: String, CodingKey {
        case id, type, sessionId, content, timestamp
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        id = try container.decodeIfPresent(String.self, forKey: .id)
        type = try container.decode(MessageType.self, forKey: .type)
        sessionId = try container.decodeIfPresent(String.self, forKey: .sessionId)
        timestamp = try container.decode(Date.self, forKey: .timestamp)
        
        // Decode content as JSON object
        let contentContainer = try container.nestedContainer(keyedBy: DynamicCodingKey.self, forKey: .content)
        var decodedContent: [String: Any] = [:]
        
        for key in contentContainer.allKeys {
            if let stringValue = try? contentContainer.decode(String.self, forKey: key) {
                decodedContent[key.stringValue] = stringValue
            } else if let intValue = try? contentContainer.decode(Int.self, forKey: key) {
                decodedContent[key.stringValue] = intValue
            } else if let boolValue = try? contentContainer.decode(Bool.self, forKey: key) {
                decodedContent[key.stringValue] = boolValue
            }
        }
        
        content = decodedContent
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        
        try container.encodeIfPresent(id, forKey: .id)
        try container.encode(type, forKey: .type)
        try container.encodeIfPresent(sessionId, forKey: .sessionId)
        try container.encode(timestamp, forKey: .timestamp)
        
        // Encode content as JSON object
        var contentContainer = container.nestedContainer(keyedBy: DynamicCodingKey.self, forKey: .content)
        
        for (key, value) in content {
            let codingKey = DynamicCodingKey(stringValue: key)!
            
            if let stringValue = value as? String {
                try contentContainer.encode(stringValue, forKey: codingKey)
            } else if let intValue = value as? Int {
                try contentContainer.encode(intValue, forKey: codingKey)
            } else if let boolValue = value as? Bool {
                try contentContainer.encode(boolValue, forKey: codingKey)
            }
        }
    }
}

/// Dynamic coding key for flexible JSON parsing
struct DynamicCodingKey: CodingKey {
    var stringValue: String
    var intValue: Int?
    
    init?(stringValue: String) {
        self.stringValue = stringValue
    }
    
    init?(intValue: Int) {
        self.intValue = intValue
        self.stringValue = "\\(intValue)"
    }
}

/// Chat session representation
struct ChatSession: Identifiable, Codable {
    let id: String
    var name: String
    var lastActivity: Date
    var isActive: Bool
    var messageCount: Int = 0
    
    var displayName: String {
        name.isEmpty ? "Session \\(id.prefix(8))" : name
    }
    
    var lastActivityFormatted: String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: lastActivity, relativeTo: Date())
    }
}

/// Individual chat message
struct ChatMessage: Identifiable, Codable {
    let id: String
    var content: String
    let isFromUser: Bool
    let timestamp: Date
    let sessionId: String?
    var attachments: [MessageAttachment] = []
    
    var timestampFormatted: String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        return formatter.string(from: timestamp)
    }
    
    var isRecent: Bool {
        Date().timeIntervalSince(timestamp) < 300 // 5 minutes
    }
}

/// Message attachments (files, images, etc.)
struct MessageAttachment: Identifiable, Codable {
    let id: String
    let name: String
    let type: AttachmentType
    let size: Int64
    let url: String?
    let localPath: String?
    
    enum AttachmentType: String, Codable, CaseIterable {
        case image = "image"
        case document = "document"
        case audio = "audio"
        case video = "video"
        case code = "code"
        case unknown = "unknown"
        
        var systemImage: String {
            switch self {
            case .image: return "photo"
            case .document: return "doc.text"
            case .audio: return "waveform"
            case .video: return "video"
            case .code: return "curlybraces"
            case .unknown: return "questionmark.circle"
            }
        }
        
        var color: Color {
            switch self {
            case .image: return .blue
            case .document: return .orange
            case .audio: return .purple
            case .video: return .red
            case .code: return .green
            case .unknown: return .gray
            }
        }
    }
    
    var sizeFormatted: String {
        ByteCountFormatter.string(fromByteCount: size, countStyle: .file)
    }
}

/// System status information
struct SystemStatus: Codable {
    let gatewayVersion: String
    let uptime: TimeInterval
    let cpuUsage: Double
    let memoryUsage: Double
    let activeConnections: Int
    let activeSessions: Int
    
    var uptimeFormatted: String {
        let formatter = DateComponentsFormatter()
        formatter.allowedUnits = [.day, .hour, .minute]
        formatter.unitsStyle = .abbreviated
        return formatter.string(from: uptime) ?? "Unknown"
    }
    
    var cpuUsageFormatted: String {
        String(format: "%.1f%%", cpuUsage * 100)
    }
    
    var memoryUsageFormatted: String {
        String(format: "%.1f%%", memoryUsage * 100)
    }
}

/// Feature entitlement for subscription tiers
enum FeatureEntitlement: String, CaseIterable {
    case voiceMessages = "voice_messages"
    case cameraAnalysis = "camera_analysis" 
    case largeFileUploads = "large_file_uploads"
    case backgroundMonitoring = "background_monitoring"
    case siriShortcuts = "siri_shortcuts"
    case liveActivities = "live_activities"
    case nfcAutomation = "nfc_automation"
    case locationFeatures = "location_features"
    case bluetoothLE = "bluetooth_le"
    case advancedAnalytics = "advanced_analytics"
    
    var displayName: String {
        switch self {
        case .voiceMessages: return "Voice Messages"
        case .cameraAnalysis: return "Camera Analysis"
        case .largeFileUploads: return "Large File Uploads"
        case .backgroundMonitoring: return "Background Monitoring"
        case .siriShortcuts: return "Siri Shortcuts"
        case .liveActivities: return "Live Activities"
        case .nfcAutomation: return "NFC Automation"
        case .locationFeatures: return "Location Features"
        case .bluetoothLE: return "Bluetooth LE"
        case .advancedAnalytics: return "Advanced Analytics"
        }
    }
    
    var description: String {
        switch self {
        case .voiceMessages: return "Send voice messages and use speech-to-text"
        case .cameraAnalysis: return "AI-powered photo analysis and OCR"
        case .largeFileUploads: return "Upload files up to 100MB"
        case .backgroundMonitoring: return "Monitor gateway status in background"
        case .siriShortcuts: return "Create custom Siri shortcuts"
        case .liveActivities: return "Real-time status in Dynamic Island"
        case .nfcAutomation: return "Automate with NFC tags"
        case .locationFeatures: return "Location-based automation"
        case .bluetoothLE: return "Control IoT devices"
        case .advancedAnalytics: return "Detailed usage analytics"
        }
    }
    
    var systemImage: String {
        switch self {
        case .voiceMessages: return "mic.fill"
        case .cameraAnalysis: return "camera.fill"
        case .largeFileUploads: return "arrow.up.doc.fill"
        case .backgroundMonitoring: return "bell.fill"
        case .siriShortcuts: return "shortcuts"
        case .liveActivities: return "dial.high"
        case .nfcAutomation: return "wave.3.right"
        case .locationFeatures: return "location.fill"
        case .bluetoothLE: return "bluetooth"
        case .advancedAnalytics: return "chart.bar.fill"
        }
    }
    
    var requiredTier: SubscriptionTier {
        switch self {
        case .voiceMessages, .cameraAnalysis, .largeFileUploads, .backgroundMonitoring:
            return .pro
        case .siriShortcuts, .liveActivities, .nfcAutomation, .locationFeatures, .bluetoothLE, .advancedAnalytics:
            return .enterprise
        }
    }
}

/// Subscription tier definitions
enum SubscriptionTier: String, CaseIterable {
    case free = "free"
    case pro = "pro"
    case enterprise = "enterprise"
    
    var displayName: String {
        switch self {
        case .free: return "Momotaro Essential"
        case .pro: return "Momotaro Pro"
        case .enterprise: return "Momotaro Enterprise"
        }
    }
    
    var monthlyPrice: Decimal {
        switch self {
        case .free: return 0
        case .pro: return 9.99
        case .enterprise: return 19.99
        }
    }
    
    var priceFormatted: String {
        if self == .free {
            return "Free"
        }
        return "$\\(monthlyPrice)/month"
    }
    
    var color: Color {
        switch self {
        case .free: return .gray
        case .pro: return .blue
        case .enterprise: return .purple
        }
    }
    
    var entitledFeatures: Set<FeatureEntitlement> {
        let allFeatures = Set(FeatureEntitlement.allCases)
        
        switch self {
        case .free:
            return Set() // No premium features
        case .pro:
            return Set(allFeatures.filter { $0.requiredTier == .pro })
        case .enterprise:
            return allFeatures // All features
        }
    }
}