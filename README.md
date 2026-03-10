# 🍑 Momotaro - OpenClaw iOS Client

**Momotaro** is the native iOS client for OpenClaw, bringing AI automation and gateway management to your iPhone and iPad. Named after the legendary Japanese folk hero, Momotaro empowers users to control their self-hosted AI infrastructure from anywhere.

## ✨ Features

### 🆓 Essential Tier (Free)
- Connect to OpenClaw gateway via WebSocket
- Basic chat interface with AI agents
- Session management and switching
- System dashboard and status monitoring
- File uploads up to 10MB

### 💎 Pro Tier ($9.99/month)
- **Voice Messages** - Record and send voice messages with speech-to-text
- **Camera Analysis** - AI-powered photo analysis and OCR capabilities
- **Large File Uploads** - Upload files up to 100MB
- **Background Monitoring** - Gateway health monitoring with smart notifications
- **Enhanced File Management** - Advanced file organization and preview

### 🚀 Enterprise Tier ($19.99/month)
- **Siri Shortcuts** - Create custom voice commands and automation
- **Live Activities** - Real-time status updates in Dynamic Island
- **NFC Automation** - Physical trigger automation with NFC tags
- **Location Features** - Geofenced AI behavior and context awareness
- **Bluetooth LE** - IoT device control and peripheral management
- **Advanced Analytics** - Detailed usage insights and performance metrics

## 🏗️ Architecture

### Core Components
- **GatewayClient** - WebSocket connection and gateway communication (URLSessionWebSocketTask)
- **GatewayMessage** - Codable message model with JSON encoding/decoding
- **OpenClawManager** - High-level gateway management and session handling
- **SubscriptionManager** - StoreKit 2 integration for freemium features
- **FeatureManager** - Premium feature gating and entitlement management
- **SecurityManager** - Ed25519 authentication and secure credential storage

### Technology Stack
- **SwiftUI** - Modern declarative UI framework
- **Combine** - Reactive programming and data flow
- **URLSessionWebSocketTask** - Native WebSocket client for gateway communication
- **Codable** - JSON serialization with CodingKeys mapping
- **Swift Crypto** - Ed25519 key generation and signature verification
- **StoreKit 2** - Native subscription and in-app purchase management
- **Core Data** - Local storage and offline capability

### Testing Infrastructure
- **XCTest** - Native Apple test framework
- **MockWebSocketTask** - Protocol-based WebSocket mocking
- **Dependency Injection** - Testable GatewayClient design
- **100% Unit Test Coverage** - 34/34 tests passing

## 🔐 Security

- **Ed25519 Authentication** - Cryptographic device authentication
- **Keychain Storage** - Secure credential and key management
- **End-to-End Encryption** - All gateway communications are encrypted
- **No Data Collection** - Privacy-first design with local data storage
- **Biometric Protection** - Face ID/Touch ID for sensitive operations

## 📱 Requirements

### Runtime
- iOS 17.0 or later
- iPhone XS or newer (for full feature set)
- OpenClaw gateway (self-hosted)
- Internet connection to reach your gateway

### Development
- Xcode 26.3 or later
- Tuist (for project generation)
- iOS 17+ SDK

## 🚀 Getting Started

### Prerequisites
- Xcode 26.3 or later
- iOS 17.0 deployment target
- Valid Apple Developer account (for device testing)
- Tuist for project generation

### Installation
```bash
git clone https://github.com/rdreilly58/momotaro-ios.git
cd momotaro-ios

# Generate Xcode project from Tuist configuration
tuist generate

# Open workspace
open Momotaro.xcworkspace
```

### Configuration
1. Update your team identifier in project settings
2. Configure your OpenClaw gateway URL in GatewayClient
3. Build and run on device or simulator: `⌘B` or `⌘R`

### Project Structure
```
momotaro-ios/
├── Sources/Momotaro/
│   ├── GatewayClient.swift          # WebSocket client (@MainActor)
│   ├── GatewayMessage.swift         # Message model (Codable)
│   ├── ContentView.swift            # Main UI
│   └── MomotaroApp.swift            # App entry point
├── Tests/MomotaroTests/
│   ├── GatewayClientTests.swift     # 20 unit tests ✅
│   ├── GatewayMessageTests.swift    # 14 unit tests ✅
│   └── Mocks.swift                  # Mock infrastructure
├── Project.swift                     # Tuist project definition
├── TESTING.md                        # Testing guide
└── README.md                         # This file
```

## 🧪 Testing

### Unit Test Suite ✅
- **Status:** 34/34 tests passing (100%)
- **Execution Time:** ~1.0 second (CI/CD ready)
- **Coverage:**
  - GatewayMessageTests: 14/14 (Codable, encoding/decoding, edge cases)
  - GatewayClientTests: 20/20 (Initialization, messages, callbacks, state)

### Running Tests
```bash
# Run all unit tests
xcodebuild test \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro'

# Run specific test suite
xcodebuild test \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  -only-testing "MomotaroTests/GatewayMessageTests"

# Run specific test
xcodebuild test \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  -only-testing "MomotaroTests/GatewayMessageTests/testRoundTripEncodingDecoding"
```

### Test Documentation
See [TESTING.md](TESTING.md) for comprehensive testing guide, architecture, best practices, and future phases.

## 📦 Build & Release

### Development
```bash
xcodebuild -scheme Momotaro -configuration Debug build
```

### App Store Release
```bash
xcodebuild -scheme Momotaro -configuration Release archive -archivePath build/Momotaro.xcarchive
xcodebuild -exportArchive -archivePath build/Momotaro.xcarchive -exportPath build/ -exportOptionsPlist ExportOptions.plist
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🍑 About Momotaro

Momotaro (桃太郎) is a legendary figure from Japanese folklore, known as the "Peach Boy" who was born from a giant peach. Just as Momotaro befriended animals and fought demons, this app befriends your devices and fights the complexity of AI automation.

## 🔗 Links

- **OpenClaw Gateway**: [https://github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)
- **Website**: [https://reillydesignstudio.com](https://reillydesignstudio.com)
- **Support**: [rdreilly2010@gmail.com](mailto:rdreilly2010@gmail.com)

---

*Built with ❤️ by Robert Reilly | Reilly Design Studio LLC*