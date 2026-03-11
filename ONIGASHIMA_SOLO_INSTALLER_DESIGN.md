# ONIGASHIMA INSTALLER — SOLO BOOTSTRAP VERSION

**Status:** For solo development (Weeks 2-3)  
**Tech:** SwiftUI (macOS app, not DMG installer yet)  
**Scope:** 4 simple screens, basic functionality  
**Polish:** Phase 2 (contractors will improve UI/UX)

---

## Installation Flow (4 Screens)

### Screen 1: Welcome

```
┌─────────────────────────────────────────────┐
│                                             │
│   🍑  ONIGASHIMA                            │
│                                             │
│   Your Personal AI That Actually Knows You  │
│                                             │
│   ┌──────────────────────────────────────┐ │
│   │  This installer will set up          │ │
│   │  Onigashima on your Mac.             │ │
│   │                                      │ │
│   │  After installation:                 │ │
│   │  • Scan QR code with your iPhone     │ │
│   │  • Pair with your Mac                │ │
│   │  • Start using Onigashima!           │ │
│   └──────────────────────────────────────┘ │
│                                             │
│              [Continue →]                  │
│                                             │
└─────────────────────────────────────────────┘
```

**Code Structure:**
```swift
struct WelcomeView: View {
  @State private var showingSettings = false
  
  var body: some View {
    VStack(spacing: 20) {
      Text("🍑 ONIGASHIMA")
        .font(.title)
      Text("Your Personal AI That Actually Knows You")
        .font(.subheadline)
        .foregroundColor(.gray)
      
      VStack(alignment: .leading, spacing: 12) {
        HStack {
          Image(systemName: "checkmark.circle.fill")
            .foregroundColor(.green)
          Text("Scan QR code with your iPhone")
        }
        HStack {
          Image(systemName: "checkmark.circle.fill")
            .foregroundColor(.green)
          Text("Pair with your Mac")
        }
        HStack {
          Image(systemName: "checkmark.circle.fill")
            .foregroundColor(.green)
          Text("Start using Onigashima!")
        }
      }
      
      Spacer()
      
      Button(action: { showingSettings = true }) {
        HStack {
          Text("Continue")
          Image(systemName: "arrow.right")
        }
      }
      .buttonStyle(.borderedProminent)
    }
    .padding(40)
  }
}
```

---

### Screen 2: Configuration

```
┌─────────────────────────────────────────────┐
│  ← Back                                     │
│                                             │
│  📝 Configuration                           │
│                                             │
│  Device Name:                               │
│  ┌──────────────────────────────────────┐  │
│  │ Bob's Mac                            │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  API Server:                                │
│  ┌──────────────────────────────────────┐  │
│  │ https://api.onigashima.app           │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  Install Location:                          │
│  ┌──────────────────────────────────────┐  │
│  │ /Applications/Onigashima             │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  Spacer                                     │
│                                             │
│              [Install →]                   │
│                                             │
└─────────────────────────────────────────────┘
```

**Code Structure:**
```swift
struct ConfigView: View {
  @State private var deviceName = "Mac"
  @State private var apiServer = "https://api.onigashima.app"
  @State private var installPath = "/Applications/Onigashima"
  @State private var isInstalling = false
  
  var body: some View {
    VStack(alignment: .leading, spacing: 20) {
      Text("📝 Configuration")
        .font(.headline)
      
      VStack(alignment: .leading) {
        Text("Device Name")
          .font(.caption)
          .foregroundColor(.gray)
        TextField("e.g., Bob's Mac", text: $deviceName)
          .textFieldStyle(.roundedBorder)
      }
      
      VStack(alignment: .leading) {
        Text("API Server")
          .font(.caption)
          .foregroundColor(.gray)
        TextField("API endpoint", text: $apiServer)
          .textFieldStyle(.roundedBorder)
      }
      
      VStack(alignment: .leading) {
        Text("Install Location")
          .font(.caption)
          .foregroundColor(.gray)
        HStack {
          TextField("Path", text: $installPath)
            .textFieldStyle(.roundedBorder)
          Button(action: browsePath) {
            Image(systemName: "folder")
          }
        }
      }
      
      Spacer()
      
      HStack {
        Button("Back") { /* go back */ }
          .buttonStyle(.bordered)
        Spacer()
        Button(action: installApp) {
          HStack {
            Text("Install")
            Image(systemName: "arrow.right")
          }
        }
        .buttonStyle(.borderedProminent)
      }
    }
    .padding(40)
  }
  
  func browsePath() {
    // Open file browser
  }
  
  func installApp() {
    isInstalling = true
    // Start installation in background
  }
}
```

---

### Screen 3: Installation Progress

```
┌─────────────────────────────────────────────┐
│                                             │
│   ⚙️  Installing...                        │
│                                             │
│   ━━━━━━━━━━━━━━━━━━━━━━━ 75%             │
│                                             │
│   Creating application folder...            │
│                                             │
│   This usually takes 1-2 minutes            │
│                                             │
│   Please wait...                            │
│                                             │
└─────────────────────────────────────────────┘
```

**Code Structure:**
```swift
struct ProgressView: View {
  @State private var progress: Double = 0.0
  @State private var status = "Creating application folder..."
  
  var body: some View {
    VStack(spacing: 20) {
      Text("⚙️ Installing...")
        .font(.headline)
      
      ProgressView(value: progress)
        .tint(.blue)
      
      Text(status)
        .font(.caption)
        .foregroundColor(.gray)
      
      Text("This usually takes 1-2 minutes")
        .font(.caption2)
        .foregroundColor(.gray)
    }
    .padding(40)
    .onAppear {
      startInstallation()
    }
  }
  
  func startInstallation() {
    // Simulate progress updates
    let steps = [
      (0.2, "Creating application folder..."),
      (0.4, "Copying files..."),
      (0.6, "Configuring system..."),
      (0.8, "Setting up auto-start..."),
      (1.0, "Finalizing...")
    ]
    
    for (prog, stat) in steps {
      DispatchQueue.main.asyncAfter(deadline: .now() + Double(prog) * 5) {
        withAnimation {
          progress = prog
          status = stat
        }
      }
    }
  }
}
```

---

### Screen 4: Success

```
┌─────────────────────────────────────────────┐
│                                             │
│   ✅ Installation Complete!                │
│                                             │
│   Onigashima is ready to use.               │
│                                             │
│   ┌──────────────────────────────────────┐ │
│   │                                      │ │
│   │      [QR CODE IMAGE HERE]            │ │
│   │      (showing pairing QR)            │ │
│   │                                      │ │
│   └──────────────────────────────────────┘ │
│                                             │
│   Next Steps:                               │
│   1. Open Onigashima app on your iPhone    │
│   2. Tap "Pair with Mac"                   │
│   3. Scan this QR code                     │
│                                             │
│   Need help?                                │
│   Visit: onigashima.app/support            │
│                                             │
│              [Launch Onigashima]           │
│                                             │
└─────────────────────────────────────────────┘
```

**Code Structure:**
```swift
struct SuccessView: View {
  @State private var qrCode: NSImage? = nil
  let pairingCode: String // passed from installation
  
  var body: some View {
    VStack(spacing: 24) {
      Text("✅ Installation Complete!")
        .font(.headline)
      
      VStack(spacing: 12) {
        Text("Onigashima is ready to use.")
          .foregroundColor(.gray)
        
        if let qrCode = qrCode {
          Image(nsImage: qrCode)
            .interpolation(.none)
            .resizable()
            .aspectRatio(contentMode: .fit)
            .frame(width: 200, height: 200)
            .border(Color.gray, width: 10)
        }
        
        VStack(alignment: .leading, spacing: 8) {
          HStack {
            Text("1.").fontWeight(.bold)
            Text("Open Onigashima app on your iPhone")
          }
          HStack {
            Text("2.").fontWeight(.bold)
            Text("Tap \"Pair with Mac\"")
          }
          HStack {
            Text("3.").fontWeight(.bold)
            Text("Scan this QR code")
          }
        }
        .font(.caption)
        
        Link("Need help? Visit onigashima.app/support",
             destination: URL(string: "https://onigashima.app/support")!)
          .font(.caption2)
          .foregroundColor(.blue)
      }
      
      Spacer()
      
      Button(action: launchApp) {
        HStack {
          Image(systemName: "play.fill")
          Text("Launch Onigashima")
        }
      }
      .buttonStyle(.borderedProminent)
    }
    .padding(40)
    .onAppear {
      generateQRCode()
    }
  }
  
  func generateQRCode() {
    // Generate QR code from pairing code
    // Store in qrCode variable
  }
  
  func launchApp() {
    NSWorkspace.shared.open(URL(fileURLWithPath: "/Applications/Onigashima/Onigashima.app"))
  }
}
```

---

## Installation Implementation Checklist

### Week 2 Tasks (March 16-22)

- [ ] **Setup SwiftUI macOS project**
  - Create new Xcode project (macOS target)
  - Setup app icons
  - Configure code signing

- [ ] **Build WelcomeView**
  - Simple text + button
  - Navigation to ConfigView

- [ ] **Build ConfigView**
  - TextFields for device name, API, path
  - File browser for path selection
  - Submit button to trigger installation

- [ ] **Build ProgressView**
  - Progress bar animation
  - Status message updates
  - Actual installation steps (copy files, setup permissions)

- [ ] **Build SuccessView**
  - QR code generation (use CIFilter)
  - Display pairing code
  - Launch button

- [ ] **Installation Logic**
  - Create /Applications/Onigashima folder
  - Copy necessary files
  - Setup launch agent (auto-start on boot)
  - Create config file with API endpoint

- [ ] **Testing**
  - Test on local Mac
  - Verify files created correctly
  - Verify launch agent works
  - Verify QR code displays

---

## File Structure

```
Onigashima.app/
├── Contents/
│   ├── MacOS/
│   │   └── Onigashima (executable)
│   ├── Resources/
│   │   └── (icons, assets)
│   └── Info.plist
│
/Applications/Onigashima/ (created by installer)
├── config.json
├── onigashima-core (main app)
└── launch-agent.plist
```

---

## Phase 2 Polish (Contractors, Weeks 5-12)

When contractors join, they will:
- [ ] Professional UI redesign
- [ ] Error handling screens
- [ ] System requirement checks
- [ ] Code signing + notarization
- [ ] DMG installer packaging
- [ ] Progress animations
- [ ] Accessibility features
- [ ] Localization (if needed)

---

## Success Criteria (Week 2)

✅ Installer builds and runs  
✅ Creates `/Applications/Onigashima` folder  
✅ Copies required files  
✅ Launches app on completion  
✅ QR code displays (valid pairing code)  
✅ Can be run multiple times without errors

---

**Status:** Ready to build (Week 2)  
**Owner:** Bob  
**Tech:** SwiftUI (macOS)  
**Effort:** 15-20 hours solo
