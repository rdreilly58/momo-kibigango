# Code Debug Capabilities Analysis & Recommendations

**Analysis Date:** Sunday, March 15, 2026  
**Scope:** ReillyDesignStudio (Next.js website) + Momotaro-iOS (Swift/iOS)  
**Status:** Current state assessed; comprehensive recommendations provided

---

## Executive Summary

Both projects currently lack **structured debugging, observability, and production monitoring** capabilities. Current state:

| Capability | Website | iOS | Status |
|---|---|---|---|
| **Structured Logging** | ❌ Basic console only | ❌ None | Missing |
| **Error Tracking** | ❌ None | ❌ None | Critical gap |
| **Performance Monitoring** | ❌ None | ❌ None | Critical gap |
| **Real-time Debugging** | ✅ Vercel dev mode | ✅ Xcode debugger | Limited |
| **Crash Reporting** | ❌ None | ❌ None | Critical gap |
| **Request/Response Tracing** | ❌ None | ❌ None | Critical gap |
| **Client Error Tracking** | ❌ None | ❌ None | Critical gap |
| **Health Monitoring** | ❌ None | ❌ None | Missing |
| **Usage Analytics** | ⚠️ GA4 only | ❌ None | Limited |
| **Session Debugging** | ❌ None | ❌ None | Missing |

---

## Part 1: ReillyDesignStudio Website Analysis

### Current State

**Stack:**
```
Next.js 16 → React 19 → Vercel (Production)
├── Backend: Node.js API routes + Prisma ORM
├── Database: PostgreSQL (Neon)
├── Auth: NextAuth (database sessions)
├── Payments: Stripe API
├── Email: Nodemailer
├── Storage: AWS S3
└── Monitoring: GA4 only
```

**Current Debug Capabilities:**
```typescript
// Existing error handling pattern (contact/route.ts)
catch (error) {
  console.error("Contact form error:", error);  // ← Only this
  return NextResponse.json({ error: "Failed to send" }, { status: 500 });
}
```

**Problems:**
1. ❌ **No error context** — Can't identify which user, request, or condition failed
2. ❌ **No structured logging** — Errors disappear in Vercel logs without good search
3. ❌ **No distributed tracing** — Can't follow requests across services
4. ❌ **No client-side error tracking** — Browser crashes/errors unnoticed
5. ❌ **No performance insights** — API response times, DB query times unknown
6. ❌ **No session debugging** — Auth issues hard to diagnose
7. ❌ **No memory/resource monitoring** — Node.js process health unknown
8. ❌ **No uptime monitoring** — Hangs (like /admin) go undetected
9. ❌ **No dependency health** — When Stripe/Neon fails, no auto-alerts
10. ❌ **No developer debugging tools** — Can't quickly trace production issues

### Known Issues Affecting Debugging

From memory: **Admin panel hangs** (`/admin` route)
- Root cause unclear
- Happens inconsistently
- No logging to diagnose
- Could be: NextAuth session, database query, API call, or UI rendering

### Recommended Debug Stack for Website

#### 1. **Structured Logging** (Tier 1: Essential)

**Tool: Pino.js** (fast JSON logger, perfect for Next.js)

```bash
npm install pino pino-http pino-pretty
```

**Setup:**
```typescript
// src/lib/logger.ts
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

// Usage in API routes
import { logger } from '@/lib/logger';

export async function POST(req: Request) {
  const requestId = crypto.randomUUID();
  const log = logger.child({ requestId, endpoint: '/api/contact' });
  
  log.info('Contact form received', { body: req.body });
  
  try {
    const result = await prisma.quote.create({...});
    log.info('Quote created', { quoteId: result.id });
    return NextResponse.json({ ok: true });
  } catch (error) {
    log.error({
      error: error.message,
      stack: error.stack,
      context: 'quote_creation',
      userId: session?.user?.id,
    }, 'Failed to create quote');
    return NextResponse.json({ error: 'Failed' }, { status: 500 });
  }
}
```

**Benefits:**
- ✅ JSON logs parseable by monitoring tools
- ✅ Request IDs for tracing
- ✅ Context information (userId, requestId, etc.)
- ✅ Performance: Pino is 5-10x faster than Winston
- ✅ Works in Vercel serverless environment

---

#### 2. **Error Tracking & Reporting** (Tier 1: Essential)

**Recommended: Sentry** (free tier: 5,000 errors/month, perfect for this size)

```bash
npm install @sentry/nextjs
```

**Setup in `next.config.ts`:**
```typescript
import { withSentryConfig } from "@sentry/nextjs";

const config = {
  // ... existing config
};

export default withSentryConfig(config, {
  org: "your-org",
  project: "reillydesignstudio",
  authToken: process.env.SENTRY_AUTH_TOKEN,
});
```

**Instrumentation:**
```typescript
// src/instrumentation.ts
import * as Sentry from "@sentry/nextjs";

export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    Sentry.init({
      dsn: process.env.SENTRY_DSN,
      environment: process.env.NODE_ENV,
      tracesSampleRate: 0.1,
      integrations: [
        new Sentry.Integrations.Http({ tracing: true }),
        new Sentry.Integrations.Postgres({
          usePreparedStatements: true,
        }),
      ],
    });
  }
}
```

**API Route Usage:**
```typescript
import * as Sentry from "@sentry/nextjs";

export async function POST(req: Request) {
  try {
    // ... your code
  } catch (error) {
    Sentry.captureException(error, {
      tags: { endpoint: 'contact' },
      extra: { body: req.body },
    });
    // Error automatically captured with full stack trace
  }
}
```

**Features:**
- ✅ Automatic error capture (400, 500 errors)
- ✅ Browser error tracking (client-side crashes)
- ✅ Distributed tracing (request → API → DB)
- ✅ Performance monitoring (slow routes)
- ✅ Release tracking (know which version errored)
- ✅ Source maps (real line numbers)
- ✅ Alert rules (get notified of issues)
- ✅ Free tier covers this site
- ✅ Dashboard shows error trends

**Why Sentry?**
- Best for Next.js (tight integration)
- Free tier is generous
- No need to store logs (Sentry does)
- Works serverless (Vercel-native)

---

#### 3. **Performance Monitoring** (Tier 1: Essential)

**Tool: Built-in Next.js Analytics + Vercel Speed Insights**

Already partially available; configure in `next.config.ts`:

```typescript
const nextConfig: NextConfig = {
  // Enable Web Vitals tracking
  productionBrowserSourceMaps: true,
  experimental: {
    turbopack: true, // Already in modern Next.js
  },
};
```

**Add to root layout:**
```tsx
// src/app/layout.tsx
import { SpeedInsights } from "@vercel/speed-insights/next";
import { Analytics } from "@vercel/analytics/react";

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics /> {/* Tracks Web Vitals */}
        <SpeedInsights /> {/* Real-time performance data */}
      </body>
    </html>
  );
}
```

**Benefits:**
- ✅ CLS, LCP, FID metrics (Core Web Vitals)
- ✅ See slow routes in real-time
- ✅ Track performance regressions
- ✅ Already included in Vercel

---

#### 4. **Request/Response Tracing** (Tier 2: High Priority)

**Tool: OpenTelemetry + Jaeger (free, self-hosted alternative)**

For now, start with middleware-based tracing:

```typescript
// src/middleware.ts
import { NextRequest, NextResponse } from 'next/server';
import { logger } from '@/lib/logger';

export function middleware(request: NextRequest) {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();

  // Add request ID to response headers
  const response = NextResponse.next();
  response.headers.set('x-request-id', requestId);

  // Log request
  logger.info({
    method: request.method,
    path: request.nextUrl.pathname,
    requestId,
  }, 'Incoming request');

  // Log response timing
  const duration = Date.now() - startTime;
  logger.info({
    duration,
    requestId,
    status: response.status,
  }, 'Request completed');

  return response;
}
```

---

#### 5. **Session Debugging** (Tier 2: High Priority)

**Current issue:** Admin panel hangs

Add to NextAuth configuration:

```typescript
// src/lib/auth.ts
import { logger } from '@/lib/logger';

export const authOptions = {
  // ... existing config
  callbacks: {
    async session({ session, user, token }) {
      logger.info({ userId: user.id }, 'Session created');
      return session;
    },
    async jwt({ token, user }) {
      if (user) {
        logger.info({ userId: user.id }, 'JWT issued');
      }
      return token;
    },
  },
  events: {
    async signIn({ user, account }) {
      logger.info({ userId: user.id, provider: account.provider }, 'User signed in');
    },
    async signOut() {
      logger.info('User signed out');
    },
    async error({ error }) {
      logger.error({ error }, 'Auth error');
    },
  },
};
```

---

#### 6. **Health Monitoring & Uptime** (Tier 2: High Priority)

**Create health check endpoint:**

```typescript
// src/app/api/health/route.ts
import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET() {
  const checks = {
    timestamp: new Date().toISOString(),
    status: 'ok',
    checks: {
      database: 'pending',
      auth: 'pending',
    },
  };

  try {
    // Database check
    await prisma.$queryRaw`SELECT 1`;
    checks.checks.database = 'ok';
  } catch (error) {
    checks.status = 'degraded';
    checks.checks.database = 'error: ' + error.message;
  }

  return NextResponse.json(checks, {
    status: checks.status === 'ok' ? 200 : 503,
  });
}
```

**Monitor with:** Uptime Robot (free tier: 50 monitors)
- Check `https://reillydesignstudio.com/api/health` every 5 minutes
- Alert if down
- Get instant notification of issues

---

#### 7. **Client-Side Error Tracking** (Tier 2: High Priority)

**Sentry already covers this**, but add custom error boundaries:

```tsx
// src/components/ErrorBoundary.tsx
'use client';

import * as Sentry from '@sentry/nextjs';
import { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

class ErrorBoundary extends React.Component<Props> {
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    Sentry.captureException(error, {
      contexts: {
        react: {
          componentStack: errorInfo.componentStack,
        },
      },
    });
  }

  render() {
    if (this.state?.hasError) {
      return this.props.fallback || <div>Something went wrong</div>;
    }
    return this.props.children;
  }
}

export default Sentry.withErrorBoundary(ErrorBoundary);
```

---

#### 8. **Development Debugging Tools** (Tier 2: Nice to Have)

**Install DevTools packages:**

```bash
npm install @next/bundle-analyzer
npm install -D debug
```

**Add to package.json:**

```json
{
  "scripts": {
    "dev": "next dev",
    "dev:debug": "DEBUG=* next dev",
    "analyze": "ANALYZE=true next build"
  }
}
```

**Usage:**
```bash
# See all debugging output
npm run dev:debug

# Analyze bundle sizes
npm run analyze
```

---

### Recommended Implementation Schedule (Website)

**Week 1 (Priority 1):**
- [ ] Install & configure Pino.js structured logging
- [ ] Add Sentry integration
- [ ] Configure Vercel Speed Insights
- [ ] Create `/api/health` endpoint
- [ ] Setup Uptime Robot monitoring

**Week 2 (Priority 2):**
- [ ] Add session debugging to NextAuth
- [ ] Wrap error handling in all API routes with logging
- [ ] Create error boundary components
- [ ] Setup Sentry alert rules

**Week 3+ (Enhancement):**
- [ ] OpenTelemetry integration
- [ ] Custom metrics (business events)
- [ ] Alerting on specific error patterns
- [ ] Performance optimization based on data

---

## Part 2: Momotaro-iOS Analysis

### Current State

**Stack:**
```
Swift + SwiftUI → iOS 17+ → App Store (future)
├── Gateway Client: Custom WebSocket implementation
├── Testing: XCTest with 25+ unit tests
├── Build System: Tuist
├── Storage: Foundation (FileManager)
├── Networking: URLSession + WebSocket
└── Monitoring: Xcode debugger only
```

**Current Debug Capabilities:**
```swift
// Existing pattern
func sendCommand(_ command: String) {
  guard let encoded = command.data(using: .utf8) else { return }
  webSocketTask?.send(.data(encoded))
}
```

**Problems:**
1. ❌ **No error logging** — Connection failures, timeouts silently fail
2. ❌ **No crash reporting** — App crashes on user devices go unnoticed
3. ❌ **No analytics** — No visibility into user behavior/engagement
4. ❌ **No network debugging** — Can't see request/response details
5. ❌ **No performance profiling** — Memory leaks, CPU usage unknown
6. ❌ **No session debugging** — Message delivery issues hard to diagnose
7. ❌ **No remote debugging** — Can only debug on connected Mac
8. ❌ **No user session tracking** — Which users affected by bugs?
9. ❌ **No feature flagging** — Can't A/B test or rollback features
10. ❌ **No observer mode** — Can't see what users see in production

### Recommended Debug Stack for iOS

#### 1. **Crash Reporting & Error Tracking** (Tier 1: Essential)

**Tool: Crashlytics** (free, part of Firebase, best for iOS)

**Installation via CocoaPods:**
```ruby
# Podfile
target 'Momotaro-iOS' do
  pod 'Firebase/Crashlytics'
  pod 'Firebase/Analytics'
  pod 'Firebase/Core'
end
```

**Or via SPM:**
```swift
// In Xcode: File → Add Packages
// URL: https://github.com/firebase/firebase-ios-sdk.git
// Version: >= 10.0.0
```

**Setup:**
```swift
// MomotaroApp.swift
import Firebase

@main
struct MomotaroApp: App {
  init() {
    FirebaseApp.configure()
    // Enable automatic crash collection
    let _ = Crashlytics.crashlytics()
  }
  
  var body: some Scene {
    WindowGroup {
      ContentView()
        .onAppear {
          // Log app startup
          Analytics.logEvent("app_launch", parameters: nil)
        }
    }
  }
}
```

**Usage in code:**
```swift
import FirebaseCrashlytics

// Catch exceptions
do {
  try parseMessage(data)
} catch {
  Crashlytics.crashlytics().record(error: error)
  logger.error("Failed to parse message: \(error)")
}

// Log custom events
Crashlytics.crashlytics().log("WebSocket connection established")

// Set user info
Crashlytics.crashlytics().setUserID("user_12345")
```

**Features:**
- ✅ Automatic crash detection (segfaults, exceptions)
- ✅ Symbolication (get real line numbers)
- ✅ Breadcrumbs (what happened before crash)
- ✅ User identification (which users affected)
- ✅ Custom key-value pairs
- ✅ Free tier (unlimited crashes)
- ✅ Works offline (sends on reconnect)

---

#### 2. **Structured Logging** (Tier 1: Essential)

**Create custom logger utility:**

```swift
// Sources/Utilities/Logger.swift
import Foundation
import os

class AppLogger {
  static let shared = AppLogger()
  
  private let logger = Logger(subsystem: "com.momotaro.ios", category: "App")
  
  enum LogLevel {
    case debug
    case info
    case warning
    case error
  }
  
  func log(
    level: LogLevel,
    _ message: String,
    context: [String: Any] = [:]
  ) {
    let contextStr = context.isEmpty ? "" : " | \(context)"
    let timestamp = ISO8601DateFormatter().string(from: Date())
    let logMessage = "[\(timestamp)] [\(level)] \(message)\(contextStr)"
    
    switch level {
    case .debug:
      logger.debug("\(logMessage)")
    case .info:
      logger.info("\(logMessage)")
    case .warning:
      logger.warning("\(logMessage)")
    case .error:
      logger.error("\(logMessage)")
    }
    
    // Also send to Crashlytics
    Crashlytics.crashlytics().log(logMessage)
  }
}

// Easy access
let log = AppLogger.shared
```

**Usage:**
```swift
// GatewayClient.swift
func connect() {
  log.log(.info, "Attempting WebSocket connection", context: [
    "url": url.absoluteString,
    "attempt": reconnectAttempts
  ])
  
  do {
    webSocketTask = try urlSession.webSocketTask(with: url)
    webSocketTask?.resume()
    log.log(.info, "WebSocket connected")
  } catch {
    log.log(.error, "Connection failed", context: [
      "error": error.localizedDescription
    ])
  }
}
```

---

#### 3. **Network Request Debugging** (Tier 1: Essential)

**Create URLSession interceptor:**

```swift
// Sources/Networking/NetworkLogger.swift
class NetworkLogger: URLSessionDelegate {
  func urlSession(
    _ session: URLSession,
    didReceive challenge: URLAuthenticationChallenge,
    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
  ) {
    log.log(.info, "SSL Challenge", context: [
      "host": challenge.protectionSpace.host
    ])
    completionHandler(.performDefaultHandling, nil)
  }
  
  func urlSession(
    _ session: URLSession,
    webSocketTask: URLSessionWebSocketTask,
    didOpenWithProtocol protocol: String?
  ) {
    log.log(.info, "WebSocket opened", context: [
      "protocol": `protocol` ?? "none"
    ])
  }
  
  func urlSession(
    _ session: URLSession,
    webSocketTask: URLSessionWebSocketTask,
    didCloseWith closeCode: URLSessionWebSocketTask.CloseCode,
    reason: Data?
  ) {
    let reasonStr = reason.flatMap { String(data: $0, encoding: .utf8) } ?? "none"
    log.log(.info, "WebSocket closed", context: [
      "closeCode": closeCode.rawValue,
      "reason": reasonStr
    ])
  }
}
```

**Use in GatewayClient:**
```swift
let networkLogger = NetworkLogger()
let session = URLSession(
  configuration: .default,
  delegate: networkLogger,
  delegateQueue: .main
)
```

---

#### 4. **Performance Monitoring** (Tier 2: High Priority)

**Add performance tracking:**

```swift
// Sources/Utilities/PerformanceTracker.swift
class PerformanceTracker {
  private var markers: [String: Date] = [:]
  
  func mark(_ name: String) {
    markers[name] = Date()
  }
  
  func measure(_ name: String, from start: String) {
    guard let startTime = markers[start] else { return }
    let duration = Date().timeIntervalSince(startTime)
    
    log.log(.info, "Performance: \(name)", context: [
      "duration_ms": Int(duration * 1000)
    ])
    
    // Also send to Crashlytics
    if duration > 1.0 { // Log if > 1 second
      Crashlytics.crashlytics().log("⚠️ Slow operation: \(name) (\(duration)s)")
    }
  }
}

let perf = PerformanceTracker.shared
```

**Usage:**
```swift
perf.mark("message_parse_start")
let parsed = try parseGatewayMessage(data)
perf.measure("Message parsing", from: "message_parse_start")
```

---

#### 5. **Memory & Resource Monitoring** (Tier 2: High Priority)

**Track resource usage:**

```swift
// Sources/Utilities/ResourceMonitor.swift
import Foundation

class ResourceMonitor {
  func logMemoryUsage() {
    var info = task_vm_info_data_t()
    var count = mach_msg_type_number_t(MemoryLayout<task_vm_info>.size)/4
    
    let kerr = withUnsafeMutablePointer(to: &info) {
      $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
        task_info(
          mach_task_self_,
          task_flavor_t(TASK_VM_INFO),
          $0,
          &count
        )
      }
    }
    
    if kerr == KERN_SUCCESS {
      let usedMemory = Double(info.phys_footprint) / 1_024_000 // MB
      log.log(.info, "Memory usage", context: [
        "memory_mb": String(format: "%.1f", usedMemory)
      ])
      
      if usedMemory > 150 { // Alert if > 150MB
        log.log(.warning, "High memory usage detected")
      }
    }
  }
}
```

---

#### 6. **Analytics & User Tracking** (Tier 2: High Priority)

**Use Firebase Analytics:**

```swift
import FirebaseAnalytics

// Track important events
Analytics.logEvent("message_sent", parameters: [
  "message_length": message.count,
  "connection_state": "connected"
])

Analytics.logEvent("gateway_connection_error", parameters: [
  "error_type": "timeout",
  "retry_attempt": reconnectAttempts
])

// Track user
Analytics.setUserID("user_12345")
Analytics.setUserProperty("app_version", value: "1.0.0")
```

---

#### 7. **Unit & Integration Testing** (Already Good, Enhance)

**Current:** 25+ unit tests in place ✅

**Enhance with:**

```swift
// Tests/GatewayClientTests+Debug.swift
import XCTest

class GatewayClientDebugTests: XCTestCase {
  func testConnectionFailureDiagnostics() {
    let client = GatewayClient()
    
    // Test case: connection timeout
    let expectation = XCTestExpectation(description: "Connection timeout")
    
    client.connect()
    
    // Should fail after timeout
    DispatchQueue.main.asyncAfter(deadline: .now() + 5) {
      XCTAssertFalse(client.isConnected)
      expectation.fulfill()
    }
    
    wait(for: [expectation], timeout: 6)
  }
  
  func testMessageQueueUnderPressure() {
    let client = GatewayClient()
    
    // Send 1000 messages rapidly
    for i in 0..<1000 {
      client.send(command: "test_\(i)")
    }
    
    // Assert queue doesn't overflow
    XCTAssertLessThan(client.queueSize, 2000)
  }
}
```

---

#### 8. **Xcode Console Debugging** (Already Available, Tips)

**Enhanced debugging in Xcode:**

```swift
// Add to schemes for easier debugging
// Edit Scheme → Run → Arguments → Add:
// LLDB commands at launch:
// settings set target.process.stop-on-exec true

// In code, add breakpoint actions:
po GatewayClient.shared.isConnected  // Check state
po GatewayClient.shared.reconnectAttempts
po GatewayClient.shared.lastError
```

---

### Recommended Implementation Schedule (iOS)

**Week 1 (Priority 1):**
- [ ] Add Firebase/Crashlytics
- [ ] Implement custom AppLogger
- [ ] Add network logging
- [ ] Setup performance tracking

**Week 2 (Priority 2):**
- [ ] Add memory monitoring
- [ ] Implement Firebase Analytics events
- [ ] Create debug utility functions
- [ ] Add test coverage for error scenarios

**Week 3+ (Enhancement):**
- [ ] Feature flags (Firebase Remote Config)
- [ ] A/B testing framework
- [ ] Advanced profiling (Instruments)

---

## Part 3: Cross-Project Debugging Solutions

### Option 1: Local Multi-Project Debugging

**Setup simultaneous debugging:**

```bash
# Terminal 1: Run website
cd ~/.openclaw/workspace/reillydesignstudio
npm run dev:debug

# Terminal 2: Run iOS simulator
cd ~/.openclaw/workspace/momotaro-ios
xcodebuild -scheme Momotaro-iOS -destination 'generic/platform=iOS Simulator' -configuration Debug

# Terminal 3: Monitor logs
tail -f ~/Library/Logs/com.apple.dt.Xcode/Xcode.log
```

### Option 2: Unified Logging Dashboard

**Create monitoring dashboard** that pulls from:
- Vercel logs (API errors)
- Sentry (application errors)
- Crashlytics (iOS crashes)
- CloudWatch (AWS/database)

**Example setup:**
```javascript
// monitoring-dashboard.js (Node.js script)
const sentry = require('@sentry/node');
const admin = require('firebase-admin');

// Aggregate errors from all sources
setInterval(async () => {
  // Get Sentry events
  const sentryEvents = await fetchSentryEvents();
  
  // Get Crashlytics events
  const crashEvents = await admin.crashlytics().getEvents();
  
  // Combine and display
  const allErrors = [...sentryEvents, ...crashEvents].sort(byTimestamp);
  console.table(allErrors);
}, 60000); // Every minute
```

---

## Part 4: Debugging Common Issues

### Website: Admin Panel Hangs (/admin)

**Debugging steps with new tools:**

```typescript
// 1. Add detailed logging to admin layout
// src/app/admin/layout.tsx
import { logger } from '@/lib/logger';

export default async function AdminLayout({ children }) {
  const startTime = Date.now();
  logger.info('AdminLayout rendering started');
  
  // Check session
  const session = await getSession();
  logger.info({ sessionExists: !!session }, 'Session check');
  
  // Check database
  try {
    const userCount = await prisma.user.count();
    logger.info({ userCount }, 'Database check passed');
  } catch (error) {
    logger.error({ error }, 'Database check failed');
  }
  
  const duration = Date.now() - startTime;
  logger.info({ duration }, 'AdminLayout rendering complete');
  
  return (
    <div>
      {children}
    </div>
  );
}
```

**With Sentry:**
- All errors/hangs automatically captured
- Can see exact timing breakdown
- See if it's server-side or client-side
- Check Sentry dashboard for "admin" tag

### iOS: WebSocket Connection Failures

**With logging + Crashlytics:**

```swift
func receive() async {
  let startTime = Date()
  log.log(.info, "Message receive loop starting")
  
  while true {
    do {
      let message = try await webSocketTask?.receive()
      let duration = Date().timeIntervalSince(startTime)
      
      log.log(.info, "Message received", context: [
        "duration_ms": Int(duration * 1000)
      ])
      
      handle(message)
    } catch URLError.badServerResponse {
      log.log(.error, "Bad server response")
      Crashlytics.crashlytics().record(error: error)
      break
    } catch {
      log.log(.error, "WebSocket error", context: [
        "error": error.localizedDescription
      ])
      await reconnect()
    }
  }
}
```

---

## Part 5: Tool Comparison & Recommendations

### Error Tracking
| Tool | Website | iOS | Cost | Recommendation |
|---|---|---|---|---|
| **Sentry** | ✅ Excellent | ⚠️ Fair | Free tier | Primary for website |
| **Crashlytics** | ⚠️ Fair | ✅ Excellent | Free | Primary for iOS |
| **Datadog** | ✅ Excellent | ✅ Excellent | $$$ | Enterprise-grade |
| **New Relic** | ✅ Good | ✅ Good | $$ | Mid-market option |

**Recommendation:** Use both Sentry + Crashlytics (free, specialized)

### Logging
| Tool | Use Case | Cost | Recommendation |
|---|---|---|---|
| **Pino** | Structured logging | Free | Start here |
| **Winston** | General logging | Free | Alternative |
| **Bunyan** | JSON logging | Free | Alternative |
| **Datadog** | Centralized | $$$ | Later upgrade |

**Recommendation:** Pino + Vercel Logs (integrated, free)

### Performance Monitoring
| Tool | Type | Cost | Recommendation |
|---|---|---|---|
| **Vercel Speed Insights** | Frontend | Free | Already available |
| **New Relic APM** | Backend | $$ | If issues appear |
| **Datadog APM** | Full stack | $$$ | Enterprise option |

**Recommendation:** Vercel + GA4 (already have)

---

## Part 6: Implementation Roadmap

### Phase 1: Foundation (Week 1-2) — $0
- [x] Structured logging (Pino)
- [x] Error tracking (Sentry for web, Crashlytics for iOS)
- [x] Basic monitoring

**Time:** 6-8 hours  
**Cost:** Free  
**Impact:** Immediate visibility into errors

### Phase 2: Enhancement (Week 3-4) — $0
- [x] Request tracing
- [x] Performance tracking
- [x] Analytics events
- [x] Health checks

**Time:** 8-10 hours  
**Cost:** Free  
**Impact:** Proactive monitoring, early problem detection

### Phase 3: Advanced (Week 5+) — Free to $$$
- [x] Feature flags (Firebase Remote Config — free)
- [x] A/B testing (free tier)
- [x] Custom metrics dashboard
- [x] Alerting automation

**Time:** 10-15 hours  
**Cost:** Free initially, upgrade as needed  
**Impact:** Data-driven decisions, rapid iteration

---

## Part 7: Quick Reference: Tools to Install

### Website (Next.js)
```bash
# Essential
npm install pino pino-http
npm install @sentry/nextjs
npm install @vercel/analytics @vercel/speed-insights

# Optional but recommended
npm install -D debug
npm install @next/bundle-analyzer
```

### iOS
```bash
# Via CocoaPods
pod 'Firebase/Crashlytics'
pod 'Firebase/Analytics'

# Via SPM (Xcode)
Add https://github.com/firebase/firebase-ios-sdk.git
```

### Monitoring
```bash
# Uptime Robot (free tier: https://uptimerobot.com)
# Create monitor for: https://reillydesignstudio.com/api/health
```

---

## Part 8: Success Metrics

### What to Track After Implementation

**Website:**
- [ ] Time to discover errors (current: unknown → target: <5 min)
- [ ] Crash-free users (baseline: unknown → target: 99%)
- [ ] P95 API response time (baseline: unknown → target: <200ms)
- [ ] Failed requests % (baseline: unknown → target: <0.1%)

**iOS:**
- [ ] Crash-free users (baseline: unknown → target: 99.5%)
- [ ] Session duration (baseline: N/A → track)
- [ ] Feature adoption (baseline: N/A → track)
- [ ] Error frequency (baseline: unknown → target: <0.5%)

**Business:**
- [ ] Mean time to recovery (MTTR) — target: <15 minutes
- [ ] Issue detection latency — target: <5 minutes
- [ ] Development velocity — target: 20% improvement
- [ ] User satisfaction — track from support tickets

---

## Conclusion

**Current State:** Both projects lack structured debugging and observability  
**Critical Gap:** No error tracking, no crash reporting, no performance insights  
**Solution Cost:** $0 (all tools have free tiers)  
**Implementation Time:** 8-20 hours total  
**Expected ROI:** 5-10x faster issue resolution

**Start with Phase 1 immediately** — basic logging + error tracking will immediately improve visibility into the /admin hang issue and any production problems.

---

## Next Steps

1. **This week:** Install Pino + Sentry + Crashlytics
2. **Next week:** Add request tracing + health monitoring
3. **Week 3:** Setup alerts and dashboards
4. **Ongoing:** Review logs weekly, adjust as needed

🍑 Ready to implement? Let me know which piece to start with first!
