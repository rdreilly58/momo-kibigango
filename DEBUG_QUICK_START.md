# Code Debugging: Quick Start Guide

**Goal:** Add enterprise-grade debugging to both projects in 1-2 hours  
**Cost:** $0 (all free tiers)  
**Benefit:** 5-10x faster problem resolution

---

## 🚀 Website (Next.js) — Start Here

### Step 1: Install Core Packages (5 min)

```bash
cd ~/.openclaw/workspace/reillydesignstudio

# Install logging
npm install pino pino-http pino-pretty

# Install error tracking
npm install @sentry/nextjs

# Install monitoring
npm install @vercel/analytics @vercel/speed-insights
```

### Step 2: Setup Structured Logging (10 min)

Create `src/lib/logger.ts`:

```typescript
import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: {
    target: 'pino-pretty',
    options: {
      colorize: true,
      singleLine: false,
    },
  },
});
```

Update `src/app/api/contact/route.ts` (as example):

```typescript
import { logger } from '@/lib/logger';

export async function POST(req: Request) {
  const requestId = crypto.randomUUID();
  const log = logger.child({ requestId });
  
  try {
    log.info('Contact form received');
    // ... existing code ...
    log.info('Quote created', { quoteId: result.id });
    return NextResponse.json({ ok: true });
  } catch (error) {
    log.error({ error: error.message }, 'Failed to create quote');
    return NextResponse.json({ error: 'Failed' }, { status: 500 });
  }
}
```

### Step 3: Setup Sentry (10 min)

1. Go to https://sentry.io
2. Sign up (free tier)
3. Create project: "reillydesignstudio"
4. Get DSN (looks like: `https://xxxxx@sentry.io/123456`)

Create `.env.local`:

```
SENTRY_DSN=https://xxxxx@sentry.io/123456
SENTRY_ORG=your-org
SENTRY_PROJECT=reillydesignstudio
SENTRY_AUTH_TOKEN=sntrys_xxxxx (from Settings → Auth Tokens)
```

Update `next.config.ts`:

```typescript
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig: NextConfig = {
  // ... existing config ...
};

export default withSentryConfig(nextConfig, {
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,
  authToken: process.env.SENTRY_AUTH_TOKEN,
});
```

Create `src/instrumentation.ts`:

```typescript
import * as Sentry from "@sentry/nextjs";

export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    Sentry.init({
      dsn: process.env.SENTRY_DSN,
      environment: process.env.NODE_ENV,
      tracesSampleRate: 0.1,
    });
  }
}
```

### Step 4: Add Performance Monitoring (5 min)

Update `src/app/layout.tsx`:

```tsx
import { Analytics } from "@vercel/analytics/react";
import { SpeedInsights } from "@vercel/speed-insights/next";

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
```

### Step 5: Create Health Check (5 min)

Create `src/app/api/health/route.ts`:

```typescript
import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET() {
  try {
    await prisma.$queryRaw`SELECT 1`;
    return NextResponse.json({ status: 'ok' });
  } catch (error) {
    return NextResponse.json(
      { status: 'error', message: error.message },
      { status: 503 }
    );
  }
}
```

### Step 6: Test It Works (2 min)

```bash
# Run dev server
npm run dev

# In another terminal, test:
curl http://localhost:3000/api/health

# Should output:
# {"status":"ok"}
```

---

## 📱 iOS — Start Here

### Step 1: Add Firebase (5 min)

Option A - CocoaPods:

```ruby
# In Podfile
target 'Momotaro-iOS' do
  pod 'Firebase/Crashlytics'
  pod 'Firebase/Analytics'
  pod 'Firebase/Core'
end

pod install
```

Option B - SPM:
1. In Xcode: File → Add Packages
2. Paste: `https://github.com/firebase/firebase-ios-sdk.git`
3. Select version: >= 10.0.0
4. Add to target: Momotaro-iOS

### Step 2: Initialize Firebase (5 min)

Update `Sources/MomotaroApp.swift`:

```swift
import Firebase

@main
struct MomotaroApp: App {
  init() {
    FirebaseApp.configure()
    let _ = Crashlytics.crashlytics()
  }
  
  var body: some Scene {
    WindowGroup {
      ContentView()
    }
  }
}
```

### Step 3: Create Logger Utility (10 min)

Create `Sources/Utilities/Logger.swift`:

```swift
import Foundation
import os
import FirebaseCrashlytics

class AppLogger {
  static let shared = AppLogger()
  private let logger = Logger(subsystem: "com.momotaro.ios", category: "App")
  
  func log(_ message: String, level: OSLogType = .info, context: [String: Any] = [:]) {
    let timestamp = ISO8601DateFormatter().string(from: Date())
    let contextStr = context.isEmpty ? "" : " | \(context)"
    let logMessage = "[\(timestamp)] \(message)\(contextStr)"
    
    os_log("%{public}@", log: logger, type: level, logMessage)
    Crashlytics.crashlytics().log(logMessage)
  }
  
  func error(_ message: String, _ error: Error?, context: [String: Any] = [:]) {
    let errorStr = error.map { "\($0)" } ?? ""
    log("\(message) - \(errorStr)", level: .error, context: context)
    if let error = error {
      Crashlytics.crashlytics().record(error: error)
    }
  }
}

let log = AppLogger.shared
```

### Step 4: Add to Gateway Client (15 min)

Update `Sources/GatewayClient.swift`:

```swift
import FirebaseCrashlytics

class GatewayClient {
  // ... existing code ...
  
  func connect() async {
    log.log("Attempting WebSocket connection", context: [
      "url": url.absoluteString,
      "attempt": reconnectAttempts
    ])
    
    do {
      webSocketTask = try urlSession.webSocketTask(with: url)
      webSocketTask?.resume()
      isConnected = true
      log.log("✅ WebSocket connected")
      Crashlytics.crashlytics().log("✅ WebSocket connected")
    } catch {
      isConnected = false
      log.error("❌ Connection failed", error, context: [
        "attempt": reconnectAttempts
      ])
      await reconnect()
    }
  }
  
  func send(command: String) {
    guard isConnected else {
      log.log("⚠️ Send attempted while disconnected", context: [
        "command": command.prefix(50) // Log first 50 chars
      ])
      return
    }
    
    guard let data = command.data(using: .utf8) else {
      log.error("Failed to encode command", nil)
      return
    }
    
    webSocketTask?.send(.data(data)) { error in
      if let error = error {
        log.error("Send failed", error)
      } else {
        log.log("Message sent", context: ["length": data.count])
      }
    }
  }
  
  func disconnect() {
    log.log("Disconnecting from WebSocket")
    webSocketTask?.cancel(with: .goingAway, reason: nil)
    isConnected = false
  }
}
```

### Step 5: Test It Works (2 min)

Run on simulator:

```bash
cd ~/.openclaw/workspace/momotaro-ios
xcodebuild -scheme Momotaro-iOS -destination 'generic/platform=iOS Simulator' -configuration Debug
```

Monitor logs in Xcode Console (Cmd+Shift+C) — you should see log messages.

---

## 🔍 Verify Everything Works

### Website

```bash
# Terminal 1: Start dev server
cd ~/.openclaw/workspace/reillydesignstudio
npm run dev:debug

# Terminal 2: Make a test request
curl -X POST http://localhost:3000/api/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","message":"Hello"}'

# Terminal 1: You should see:
# [timestamp] Contact form received
# [timestamp] Quote created
```

### iOS

1. Open Xcode
2. Run on simulator
3. Xcode Console (Cmd+Shift+C) should show log messages
4. Try connecting/disconnecting — logs appear

---

## 📊 Next: Setup Dashboards

### Sentry Dashboard

1. Go to https://sentry.io
2. Click "Issues" — see all errors
3. Click on error → see full stack trace + context
4. Setup Alert: Settings → Alerts → Create alert rule
5. Alert on: Any event
6. Notify: Your email

### Crashlytics Dashboard

1. Go to https://console.firebase.google.com
2. Select project
3. Analytics → Crashlytics
4. See crashes by version, device, OS

---

## 🎯 What You Now Have

| Capability | Before | After |
|---|---|---|
| **Error visibility** | ❌ Missing | ✅ Real-time alerts |
| **Log searching** | ❌ None | ✅ Full logs with context |
| **Crash reports** | ❌ Missing | ✅ All crashes tracked |
| **Performance data** | ❌ None | ✅ Response times visible |
| **User context** | ❌ Unknown | ✅ Track by user/session |
| **Health monitoring** | ❌ None | ✅ /api/health endpoint |
| **Time to discover error** | ❌ Minutes to hours | ✅ Seconds (automatic alerts) |

---

## 💰 Cost Summary

- **Sentry:** Free tier (5,000 errors/month) ✅
- **Crashlytics:** Free tier (unlimited) ✅
- **Vercel:** Already included ✅
- **Firebase Analytics:** Free tier ✅
- **Total cost:** **$0**

---

## 🚨 Troubleshooting

### Sentry not capturing errors?
```typescript
// Test if it works
throw new Error("Test error");
// Check Sentry dashboard after 30 seconds
```

### iOS logs not appearing?
```swift
// Check iOS logs in Xcode
Cmd+Shift+C to open console
Restart simulator
Try connecting again
```

### Health check returning 503?
```bash
# Check database connection
npx prisma db push

# Verify .env has DATABASE_URL
cat .env
```

---

## 📝 What to Do Next

1. ✅ Install packages
2. ✅ Setup Sentry + Firebase
3. ✅ Run both projects
4. ✅ Create test errors to verify
5. ✅ Share links with team
6. ✅ Setup alerts on your phone
7. 📅 Schedule weekly review of error trends

**Time to complete:** 1-2 hours  
**Ongoing time:** 15 minutes/week to review

---

## 🎯 Success: The /admin Hang Issue

With these tools in place, **the /admin hang will be visible**:

1. Next time it happens → Sentry captures it
2. You see exact timing breakdown
3. See if frontend or backend hangs
4. See which database query is slow
5. Fix it with confidence

**Today:** Debug manually  
**Tomorrow:** Get alerts when it fails, with full context

🍑 Ready? Let's start!
