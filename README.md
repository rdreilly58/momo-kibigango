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
- **OpenClawManager** - WebSocket connection and gateway communication
- **SubscriptionManager** - StoreKit 2 integration for freemium features
- **FeatureManager** - Premium feature gating and entitlement management
- **SecurityManager** - Ed25519 authentication and secure credential storage

### Technology Stack
- **SwiftUI** - Modern declarative UI framework
- **Combine** - Reactive programming and data flow
- **Starscream** - WebSocket client for gateway communication
- **Swift Crypto** - Ed25519 key generation and signature verification
- **StoreKit 2** - Native subscription and in-app purchase management
- **Core Data** - Local storage and offline capability

## 🔐 Security

- **Ed25519 Authentication** - Cryptographic device authentication
- **Keychain Storage** - Secure credential and key management
- **End-to-End Encryption** - All gateway communications are encrypted
- **No Data Collection** - Privacy-first design with local data storage
- **Biometric Protection** - Face ID/Touch ID for sensitive operations

## 📱 Requirements

- iOS 17.0 or later
- iPhone XS or newer (for full feature set)
- OpenClaw gateway (self-hosted)
- Internet connection to reach your gateway

## 🚀 Getting Started

### Prerequisites
- Xcode 15.0 or later
- iOS 17.0 deployment target
- Valid Apple Developer account (for device testing)

### Installation
```bash
git clone https://github.com/rdreilly58/momotaro-ios.git
cd momotaro-ios
open Momotaro.xcodeproj
```

### Configuration
1. Update your team identifier in project settings
2. Configure your OpenClaw gateway URL
3. Build and run on device or simulator

## 🧪 Testing

```bash
# Run unit tests
xcodebuild test -scheme Momotaro -destination 'platform=iOS Simulator,name=iPhone 15 Pro'

# Run UI tests
xcodebuild test -scheme MomotaroUITests -destination 'platform=iOS Simulator,name=iPhone 15 Pro'
```

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