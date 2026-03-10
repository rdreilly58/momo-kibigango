---
name: ios-dev
description: Build, test, and manage iOS apps with Xcode. Use when building iPhone/iPad apps, creating archives, running tests, launching simulators, or opening projects in Xcode.
---

# iOS Development

Build and manage iOS projects with Xcode from the command line.

**Requirements:**
- Xcode installed (✓ installed: v26.3)
- iOS project with .xcodeproj file

## Quick Commands

```bash
# List available schemes
bash {baseDir}/scripts/xcode-build.sh ~/MyApp list

# Build for device
bash {baseDir}/scripts/xcode-build.sh ~/MyApp build

# Build for release
bash {baseDir}/scripts/xcode-build.sh ~/MyApp build --release

# Create archive (for App Store export)
bash {baseDir}/scripts/xcode-build.sh ~/MyApp archive

# Run unit tests
bash {baseDir}/scripts/xcode-build.sh ~/MyApp test

# Build and run on simulator
bash {baseDir}/scripts/xcode-build.sh ~/MyApp simulator

# Open in Xcode
bash {baseDir}/scripts/xcode-build.sh ~/MyApp open

# Clean build folder
bash {baseDir}/scripts/xcode-build.sh ~/MyApp clean
```

## Options

```bash
--scheme NAME           # Specify Xcode scheme (auto-detected if omitted)
--device NAME           # Simulator device name (default: iPhone 16)
--config DEBUG|Release  # Build configuration (default: Debug)
--release               # Shorthand for --config Release
```

## Examples

```bash
# Build Momotaro for iOS
bash {baseDir}/scripts/xcode-build.sh ~/momotaro-ios build --scheme Momotaro

# Create archive for TestFlight
bash {baseDir}/scripts/xcode-build.sh ~/momotaro-ios archive --release

# Run tests
bash {baseDir}/scripts/xcode-build.sh ~/momotaro-ios test

# Build and launch on iPhone 15 Pro Max simulator
bash {baseDir}/scripts/xcode-build.sh ~/momotaro-ios simulator --device "iPhone 15 Pro Max"

# Clean and rebuild
bash {baseDir}/scripts/xcode-build.sh ~/momotaro-ios clean
bash {baseDir}/scripts/xcode-build.sh ~/momotaro-ios build --release
```

## Xcode Info

```
Version: Xcode 26.3
Build: 17C519
Developer Tools: /Applications/Xcode.app/Contents/Developer
```

## Available Simulators

```bash
# List available simulators
xcrun simctl list devices

# Boot a simulator
xcrun simctl boot "iPhone 16"

# Install app on simulator
xcrun simctl install "iPhone 16" /path/to/App.app

# Launch app on simulator
xcrun simctl launch "iPhone 16" com.example.app.bundleid
```

## Signing & Provisioning

For App Store deployment:
1. Configure signing in Xcode (Team ID, provisioning profiles)
2. Create archive: `xcode-build.sh archive --release`
3. Export using: `xcodebuild -exportArchive`

Or use Xcode Organizer GUI:
```bash
bash {baseDir}/scripts/xcode-build.sh ~/MyApp open
# Xcode → Window → Organizer → Select Archive → Export
```

## Common Build Issues

**"No Xcode project found"**
```bash
# Verify project structure
ls -la ~/MyApp/*.xcodeproj
```

**Simulator not available**
```bash
# List and boot simulator
xcrun simctl list devices
xcrun simctl boot "iPhone 16"
```

**Signing certificate missing**
```bash
# Check provisioning profiles
ls ~/Library/MobileDevice/Provisioning\ Profiles/
# Configure in Xcode: Project → Signing & Capabilities
```
