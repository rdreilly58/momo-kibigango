# Momotaro iOS — Installation & Setup Guide

![Momotaro Badge](https://img.shields.io/badge/Status-Ready%20for%20Beta-brightgreen)
![iOS](https://img.shields.io/badge/iOS-17%2B-blue)
![Swift](https://img.shields.io/badge/Swift-5.9%2B-orange)
![Tests](https://img.shields.io/badge/Tests-248%2F248-success)

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Installation Checklist](#pre-installation-checklist)
3. [Step-by-Step Installation](#step-by-step-installation)
4. [Configuration](#configuration)
5. [Building & Running](#building--running)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

---

## 🔧 System Requirements

### macOS Environment
- **macOS:** 14.0 (Sonoma) or later
- **Xcode:** 15.0 or later (with iOS 17+ SDK)
- **CocoaPods:** Optional (we use Tuist for dependency management)

### iOS Device / Simulator
- **Minimum iOS:** iOS 17.0
- **Recommended:** iPhone 14 Pro or later
- **Storage:** ~500MB for app + data

### Development Tools
- Git (for cloning the repository)
- Terminal or command-line interface

---

## ✅ Pre-Installation Checklist

Before starting, ensure you have:

- [ ] Xcode 15.0+ installed
- [ ] Git configured with GitHub access
- [ ] macOS 14.0 or later
- [ ] ~2GB free disk space for project files
- [ ] Internet connection (for package downloads)
- [ ] Apple Developer account (for device deployment)

---

## 📦 Step-by-Step Installation

### Step 1: Clone the Repository

```bash
# Navigate to your preferred projects directory
cd ~/Projects

# Clone the Momotaro iOS repository
git clone https://github.com/rdreilly58/momotaro-ios.git
cd momotaro-ios
```

### Step 2: Verify Prerequisites

```bash
# Check Xcode version
xcode-select --print-path

# Verify Swift version
swift --version

# Expected output: Swift version 5.9 or later
```

### Step 3: Install Tuist (Dependency Manager)

Momotaro uses **Tuist** for efficient project generation. Install it:

```bash
# Install Tuist via Homebrew
brew install tuist

# Verify installation
tuist --version
```

If you don't have Homebrew, install it first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 4: Generate Xcode Project

```bash
# From the momotaro-ios directory
tuist generate

# Expected output:
# ✔ Success
#   Project generated.
```

This creates `Momotaro.xcworkspace` with all dependencies properly configured.

### Step 5: Verify Installation

```bash
# Run the build test (no actual compile yet)
tuist graph

# This shows the project structure and validates your setup
```

---

## ⚙️ Configuration

### 1. Google Analytics Setup (Optional but Recommended)

To enable GA4 analytics:

1. **Obtain Service Account Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a service account with Editor role on your GA4 property
   - Download the JSON key file

2. **Place the Key:**
   ```bash
   mkdir -p ~/.openclaw/workspace/secrets
   cp ~/Downloads/ga4-service-account.json ~/.openclaw/workspace/secrets/
   ```

3. **Grant Permissions:**
   - Navigate to Google Analytics Admin
   - Property → Property Access Management
   - Add service account email with "Viewer" role

### 2. In-App Purchases Configuration (Production Only)

For the Play/Pro subscription plans, you'll need:

1. **App Store Connect Access**
2. **Bundle ID:** `com.example.momotaro` (configure in Xcode)
3. **In-App Purchase Products:** Already configured in code

For testing:
- Use iOS Simulator (no IAP charges)
- Sandbox testing available with TestFlight

### 3. Optional: Push Notifications

To enable push notifications:

1. Add your Apple Developer Team ID in Xcode
2. Enable "Push Notifications" capability
3. Configure server-side push token handling

---

## 🚀 Building & Running

### Method 1: Using Xcode (Recommended for Beginners)

```bash
# Open the workspace
open Momotaro.xcworkspace
```

Then in Xcode:
1. Select `Momotaro` scheme (top-left)
2. Select target: **iPhone 17 Pro** or your connected device
3. Press **Play** (▶) or press `Cmd + R`

### Method 2: Command Line

```bash
# Build for simulator
xcodebuild build \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro"

# Run tests
xcodebuild test \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro"
```

### Method 3: Using Tuist (Fastest)

```bash
# Generate, build, and run in one command
tuist run Momotaro
```

---

## 📱 First Launch

On first run, you'll see:

1. **Welcome Screen** — Momotaro introduction
2. **Free Plan Selected** — 100 messages/day, 3 sessions
3. **Message Input Ready** — Start chatting!

### Available Features (Free Plan)
- ✅ 100 messages per day
- ✅ 3 active sessions
- ✅ Message history (limited)
- ✅ Basic search

### Upgrade to Pro
- Tap **"Upgrade to Pro"** button in settings
- Choose Monthly ($9.99) or Annual ($79.99)
- Unlock: unlimited messages, sessions, export, advanced search

---

## 🧪 Running Tests

Verify everything works with the full test suite:

```bash
# Run all tests (248 unit tests)
xcodebuild test \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro"

# Expected output:
# Test Suite 'All tests' passed at ...
# Tests: 248/248 passing ✅
```

### Test Coverage by Module

| Module | Tests | Status |
|--------|-------|--------|
| Analytics | 23 | ✅ |
| Security | 28 | ✅ |
| Subscriptions | 51 | ✅ |
| Sessions | 20 | ✅ |
| Messages | 49 | ✅ |
| Gateway | 34 | ✅ |
| Features | 34 | ✅ |
| UI | 17 | ✅ |
| **Total** | **248** | **100%** |

---

## 🔧 Troubleshooting

### Issue: `tuist: command not found`

**Solution:**
```bash
# Install Tuist
brew install tuist

# Or reinstall if already installed
brew reinstall tuist
```

### Issue: Xcode Build Fails with Swift Errors

**Solution:**
```bash
# Clean and regenerate
tuist clean
rm -rf .xcworkspace
tuist generate

# Then rebuild
xcodebuild clean
xcodebuild build -workspace Momotaro.xcworkspace -scheme Momotaro
```

### Issue: "Module 'Momotaro' not found"

**Solution:**
```bash
# Regenerate project files
tuist generate

# If still failing, clear Xcode cache
rm -rf ~/Library/Developer/Xcode/DerivedData
xcodebuild -workspace Momotaro.xcworkspace -scheme Momotaro -resolvePackageDependencies
```

### Issue: Simulator Won't Launch

**Solution:**
```bash
# Kill all simulator processes
killall "Simulator"

# Or reset simulator state
xcrun simctl erase all

# Relaunch simulator
open -a Simulator
```

### Issue: In-App Purchase Testing Not Working

**Solution:**
- Use iOS Simulator (StoreKit 2 simulation included)
- On device: Use TestFlight for sandbox testing
- Purchase flow logs visible in Xcode console

### Issue: Tests Fail with "XCTAssertNil failed"

**Solution:**
```bash
# Ensure clean state before running tests
xcodebuild clean -workspace Momotaro.xcworkspace -scheme Momotaro
xcodebuild test -workspace Momotaro.xcworkspace -scheme Momotaro
```

---

## 📚 Project Structure

```
momotaro-ios/
├── Sources/Momotaro/
│   ├── AnalyticsManager.swift      # GA4 analytics tracking
│   ├── SubscriptionManager.swift   # In-app purchases
│   ├── SubscriptionView.swift      # Purchase UI
│   ├── SecurityManager.swift       # Auth & encryption
│   ├── GatewayClient.swift         # WebSocket connection
│   ├── MessagePersistence.swift    # Core Data storage
│   ├── MessageStore.swift          # Message database
│   ├── FeatureManager.swift        # Feature gating
│   ├── ContentView.swift           # Main UI
│   └── ... (23 total files)
│
├── Tests/MomotaroTests/
│   ├── AnalyticsManagerTests.swift (23 tests)
│   ├── SubscriptionViewTests.swift (17 tests)
│   ├── SecurityManagerTests.swift  (28 tests)
│   └── ... (11 total test files)
│
├── Project.swift                    # Tuist configuration
├── Tuist/                          # Tuist templates
└── Documentation/
    ├── INSTALLATION.md
    ├── OPERATIONS.md
    └── TESTING.md
```

---

## 🚀 Next Steps

### 1. Explore the App
- Open a session and send messages
- Try upgrading to Pro plan
- Check message history and search

### 2. Review Code
```bash
# Explore key managers
open Sources/Momotaro/SubscriptionManager.swift
open Sources/Momotaro/GatewayClient.swift
```

### 3. Run Tests Regularly
```bash
# Before each commit
xcodebuild test -workspace Momotaro.xcworkspace -scheme Momotaro
```

### 4. Deploy to Device
```bash
# Select your connected iPhone in Xcode
# Change destination from simulator to device
# Press Play (Cmd+R)
```

### 5. Submit to App Store
- Use Xcode → Product → Archive
- Follow App Store Connect review guidelines
- Include required screenshots and description

---

## 📖 Additional Resources

- **[Testing Documentation](TESTING.md)** — Complete test suite overview
- **[Operations Guide](OPERATIONS.md)** — User features & troubleshooting
- **[GitHub Repository](https://github.com/rdreilly58/momotaro-ios)**
- **[Swift Documentation](https://developer.apple.com/swift/)**
- **[iOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/ios)**

---

## 💬 Support & Feedback

Found an issue? Have suggestions?

1. **Check Existing Issues:** [GitHub Issues](https://github.com/rdreilly58/momotaro-ios/issues)
2. **Create New Issue:** Include device, iOS version, steps to reproduce
3. **Code Questions:** Review inline documentation in source files

---

## ✨ Success Checklist

After installation, verify:

- [ ] Project generates without errors (`tuist generate`)
- [ ] All 248 tests pass (`xcodebuild test`)
- [ ] App launches on simulator
- [ ] Can send messages and view history
- [ ] Purchase UI displays correctly
- [ ] No console warnings or errors

**✅ Ready to use Momotaro!** 🍑

---

**Last Updated:** March 10, 2026
**Version:** 1.0.0
**Status:** Production Ready ✅
