# Momotaro iOS — Comprehensive Testing Plan

**Version:** 1.0.0  
**Date Created:** March 10, 2026  
**Last Updated:** March 10, 2026  
**Status:** Production Ready ✅

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Testing Phases](#testing-phases)
3. [Unit Testing (Automated)](#unit-testing-automated)
4. [Simulator Testing](#simulator-testing)
5. [Device Testing](#device-testing)
6. [Manual Test Cases](#manual-test-cases)
7. [Regression Testing](#regression-testing)
8. [Performance Testing](#performance-testing)
9. [Troubleshooting](#troubleshooting)
10. [Sign-Off Checklist](#sign-off-checklist)

---

## 🎯 Overview

### Testing Scope
This plan covers:
- ✅ **Automated Tests** — 248 unit tests (100% pass rate)
- ✅ **Simulator Testing** — iPhone 17 Pro simulator
- ✅ **Device Testing** — Real iPhone (any iOS 17+ device)
- ✅ **Manual Testing** — Feature verification & user flows
- ✅ **Performance Testing** — Memory, battery, network
- ✅ **Regression Testing** — Verify no breaking changes

### Testing Goals
1. Ensure **248/248 unit tests pass** (100%)
2. Verify all features work on simulator
3. Verify all features work on real device
4. Confirm no crashes or errors
5. Validate performance metrics
6. Ensure user experience is smooth

### Test Environment
- **Development Machine:** macOS 14+ with Xcode 15+
- **Simulator:** iPhone 17 Pro (or similar)
- **Device:** iPhone 14+ running iOS 17+
- **Network:** Stable WiFi connection recommended
- **Time Required:** ~3-4 hours per full cycle

---

## 🔄 Testing Phases

### Phase 1: Automated Unit Tests ✅ (15 minutes)
- Run full test suite locally
- Verify 248/248 tests pass
- Check for compiler warnings

### Phase 2: Simulator Testing ✅ (45 minutes)
- Build for simulator
- Test all major features
- Verify UI responsiveness
- Check memory usage

### Phase 3: Device Testing ✅ (45 minutes)
- Build for real device
- Test on actual hardware
- Verify performance
- Test gestures & interactions

### Phase 4: Regression Testing ✅ (30 minutes)
- Verify no breaking changes
- Test previous features
- Check backwards compatibility

### Phase 5: Performance Testing ✅ (15 minutes)
- Memory profiling
- CPU usage monitoring
- Battery drain test
- Network latency check

---

## 🧪 Unit Testing (Automated)

### Current Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| AnalyticsManager | 23 | ✅ PASSING |
| SubscriptionView | 17 | ✅ PASSING |
| SubscriptionManager | 34 | ✅ PASSING |
| FeatureManager | 34 | ✅ PASSING |
| SecurityManager | 28 | ✅ PASSING |
| SessionManager | 20 | ✅ PASSING |
| MessageStore | 22 | ✅ PASSING |
| MessagePersistence | 27 | ✅ PASSING |
| GatewayClient | 20 | ✅ PASSING |
| GatewayMessage | 14 | ✅ PASSING |
| SessionInfo | 4 | ✅ PASSING |
| **TOTAL** | **248** | **✅ 100%** |

### Running Unit Tests Locally

#### Step 1: Open Terminal
```bash
cd ~/momotaro-ios
```

#### Step 2: Run Full Test Suite
```bash
xcodebuild test \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro"
```

#### Step 3: Verify Output
Look for:
```
Test Suite 'All tests' passed at [timestamp].
Executed 248 tests, with 0 failures (0 unexpected) in X.XXX (X.XXX) seconds
```

#### Step 4: Run Individual Test Suites (Optional)
```bash
# Test specific module
xcodebuild test \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro" \
  -only-testing:MomotaroTests/SubscriptionViewTests
```

### Expected Results
- ✅ All 248 tests pass
- ✅ No compiler warnings
- ✅ No skipped tests
- ✅ Execution time: ~2-3 minutes

---

## 📱 Simulator Testing

### Test Environment Setup

#### Step 1: Install Simulator (If Needed)
```bash
# List available simulators
xcrun simctl list devices

# If iPhone 17 Pro not available:
# Open Xcode → Settings → Platforms
# Install iOS 17 runtime
```

#### Step 2: Launch Simulator
```bash
# Option 1: Via Xcode
open -a Simulator

# Option 2: Via Terminal
xcrun simctl boot "iPhone 17 Pro"
```

#### Step 3: Build for Simulator
```bash
cd ~/momotaro-ios

# Clean previous build
xcodebuild clean -workspace Momotaro.xcworkspace -scheme Momotaro

# Build for simulator
xcodebuild build \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro"
```

#### Step 4: Run App on Simulator
```bash
# Option 1: From Xcode
open Momotaro.xcworkspace
# Select Momotaro scheme + iPhone 17 Pro
# Press Play (▶)

# Option 2: Via Command Line
xcodebuild run \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro"
```

### Simulator Test Checklist

#### App Launch & Navigation
- [ ] App launches without crashes
- [ ] Welcome screen displays correctly
- [ ] No console errors or warnings
- [ ] UI loads within 2 seconds

#### Session Management
- [ ] Create new session ("+" button works)
- [ ] Session name saves correctly
- [ ] Can switch between sessions (tap session row)
- [ ] Delete session (swipe left) works
- [ ] Confirm delete dialog appears
- [ ] Session history displays
- [ ] Can view session info (ⓘ icon)

#### Messaging Features
- [ ] Message input field visible
- [ ] Can type messages
- [ ] Send button enabled (not grayed out)
- [ ] Message sends on tap
- [ ] Sent messages appear in history
- [ ] Message timestamps show
- [ ] Long-press shows delete option
- [ ] Can scroll through message history

#### Search Functionality
- [ ] Search icon visible in toolbar
- [ ] Tap search opens search bar
- [ ] Can type search term
- [ ] Results display (if messages exist)
- [ ] Search results highlight matches
- [ ] Clear search (X button) works
- [ ] Search is case-insensitive

#### Subscription Features
- [ ] Settings gear icon visible
- [ ] "Upgrade to Pro" button visible (on free plan)
- [ ] Tap upgrade opens subscription view
- [ ] Plan cards display (Free, Pro Monthly, Pro Annual)
- [ ] Pricing displays correctly
- [ ] Feature comparison shows (table view)
- [ ] "Restore Purchases" button visible
- [ ] Close subscription view (< or outside tap)

#### Purchasing (Sandbox)
- [ ] Can tap "Upgrade to Pro" button
- [ ] Loading spinner appears during purchase
- [ ] Sandbox purchase dialog may appear
- [ ] Handle sandbox purchase (approve/cancel)
- [ ] If approved: subscription UI updates
- [ ] If cancelled: returns to purchase screen
- [ ] No crashes during purchase flow

#### UI Responsiveness
- [ ] Text visible on all screen sizes
- [ ] Buttons tappable and responsive
- [ ] Scrolling is smooth (no jank)
- [ ] No missing UI elements
- [ ] Font sizes appropriate
- [ ] Colors render correctly
- [ ] Dark mode works (if enabled)

#### Performance
- [ ] App responds to taps within 200ms
- [ ] Scrolling smooth (60 FPS)
- [ ] No frozen UI
- [ ] No memory warnings
- [ ] Console clean (no errors)

---

## 📲 Device Testing

### Preparing Your iPhone

#### Step 1: Verify iOS Version
- Settings → General → About
- **Required:** iOS 17.0 or later
- **Recommended:** Latest iOS version

#### Step 2: Enable Developer Mode
- Settings → Privacy & Security → Developer Mode
- Toggle ON
- Confirm the warning dialog
- Restart device (required)

#### Step 3: Trust Developer Certificate
- Connect iPhone to Mac
- Open Xcode
- You'll see "Trust" dialog
- Tap "Trust" on device
- Tap "Trust" in Xcode if prompted

#### Step 4: Register Device with Apple
**Option A: Via Xcode (Automatic)**
1. Xcode → Settings → Accounts
2. Select your Apple ID
3. Click "Manage Certificates"
4. Create development certificate (if needed)

**Option B: Via Apple Developer Portal (Manual)**
1. Visit https://developer.apple.com/account
2. Devices → Add Device
3. Enter iPhone UDID (found in device info)
4. Register device

#### Step 5: Verify Connection
```bash
# List connected devices
xcrun simctl list devices

# Should see your device listed
# Example: "iPhone 15 Pro (A1B2C3D4E5F6) (ready)"
```

### Building for Device

#### Step 1: Change Build Destination
```bash
# In Xcode:
# Top-left dropdown: Change from "iPhone 17 Pro" to your device name
# Example: "Bob's iPhone"
```

#### Step 2: Build for Device
```bash
cd ~/momotaro-ios

# Build for your device
xcodebuild build \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "generic/platform=iOS"
```

#### Step 3: Run on Device
```bash
# Option 1: From Xcode
# Press Play (▶) with device connected

# Option 2: Via Command Line
xcodebuild run \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "generic/platform=iOS"
```

### Device Test Checklist

#### Installation & Launch
- [ ] App installs without errors
- [ ] App launches successfully
- [ ] No crashes on startup
- [ ] Welcome screen displays
- [ ] Console shows no errors

#### Real-World Performance
- [ ] App responsive to touch
- [ ] No lag or delays
- [ ] Scrolling smooth
- [ ] Gestures work (swipe, tap, long-press)
- [ ] No memory warnings
- [ ] Battery usage reasonable (not draining fast)

#### Network Functionality
- [ ] App connects to gateway
- [ ] Messages send successfully
- [ ] Messages receive properly
- [ ] No timeout errors
- [ ] WiFi switching smooth (WiFi ↔ Cellular)
- [ ] Works on both WiFi and cellular

#### Session Management (on device)
- [ ] Create session works
- [ ] Delete session works
- [ ] Session persistence (close app, reopen)
- [ ] Message history preserved

#### Subscription on Device
- [ ] Upgrade button visible
- [ ] Can open subscription view
- [ ] Plans display correctly
- [ ] Can attempt purchase (sandbox mode)
- [ ] Purchase dialog appears
- [ ] Can cancel purchase
- [ ] UI updates correctly

#### Touch & Gestures
- [ ] Tap response: < 200ms
- [ ] Swipe to delete: Works smoothly
- [ ] Long-press: Opens menu correctly
- [ ] Pinch-to-zoom: N/A (not implemented)
- [ ] Keyboard: Shows/hides properly

#### Device Sensors
- [ ] Face ID/Touch ID: Works with subscription
- [ ] Rotation: Handles screen rotation
- [ ] Safe area: Notch/Dynamic Island respected
- [ ] Status bar: Visible and correct

#### Connectivity
- [ ] WiFi on: App works
- [ ] WiFi off: Cellular fallback
- [ ] Cellular off: Shows offline indicator
- [ ] Network changes: Smooth transition
- [ ] Lost connection: Graceful handling

---

## 📋 Manual Test Cases

### Test Case 1: End-to-End User Flow

**Objective:** Verify complete user journey from app launch to subscription

**Steps:**
1. Launch app
2. See welcome screen
3. Create new session ("My First Chat")
4. Send test message ("Hello Momotaro")
5. See message in history
6. Search for "Hello" (should find message)
7. Open subscription view
8. Review plans
9. Close subscription view
10. Delete test session

**Expected Result:**
- ✅ All steps complete without crashes
- ✅ No error messages
- ✅ UI responsive throughout

---

### Test Case 2: Session Management

**Objective:** Verify session create/edit/delete workflows

**Steps:**
1. Create 3 sessions (Free plan limit)
2. Name them: "Test1", "Test2", "Test3"
3. Send message in each session
4. Switch between sessions (tap each)
5. Tap session name to rename
6. Rename "Test1" to "Renamed Session"
7. Delete "Test3" (swipe left)
8. Confirm delete
9. Verify only 2 sessions remain

**Expected Result:**
- ✅ All 3 sessions created
- ✅ Can switch between sessions
- ✅ Rename works
- ✅ Delete works
- ✅ Session count accurate

---

### Test Case 3: Message History & Search

**Objective:** Verify message storage and search

**Steps:**
1. Create session "Search Test"
2. Send 5 messages:
   - "Hello world"
   - "Testing search"
   - "Message number 3"
   - "Hello again"
   - "Final test"
3. Scroll up (view all messages)
4. Open search
5. Search "Hello" (should find 2 results)
6. Search "world" (should find 1 result)
7. Clear search
8. Search "xyz" (should find 0 results)

**Expected Result:**
- ✅ All messages saved
- ✅ Scrolling shows all messages
- ✅ Search finds correct results
- ✅ Search is case-insensitive
- ✅ Clear search works

---

### Test Case 4: Subscription Purchase Flow

**Objective:** Verify in-app purchase (sandbox)

**Prerequisites:**
- Testing on simulator (StoreKit 2 sandbox mode)
- App is signed with development team

**Steps:**
1. Open Settings
2. Tap "Upgrade to Pro"
3. Review Pro Monthly plan ($9.99/mo)
4. Review Pro Annual plan ($79.99/yr with 33% savings)
5. Tap "Upgrade to Pro Monthly"
6. Sandbox purchase dialog appears
7. Tap "Approve" (or "Decline")
8. If approved:
   - Loading spinner shows
   - Subscription updates
   - UI reflects Pro status
9. If declined:
   - Return to purchase screen
   - Pro features not unlocked

**Expected Result:**
- ✅ All plans display
- ✅ Purchase dialog appears
- ✅ Approve/Decline works
- ✅ UI updates correctly
- ✅ No crashes

---

### Test Case 5: Error Handling

**Objective:** Verify app handles errors gracefully

**Steps:**
1. Disable WiFi (put phone in Airplane Mode)
2. Try to send message
3. Observe error handling
4. Enable WiFi again
5. Message should retry/succeed
6. Try to create 4th session (on free plan)
7. See "Session limit" error
8. Dismiss error
9. App remains stable

**Expected Result:**
- ✅ No crashes on error
- ✅ Error messages clear
- ✅ App recovers from errors
- ✅ Can retry operations

---

### Test Case 6: Performance Under Load

**Objective:** Verify app stability with many messages

**Steps:**
1. Create session "Load Test"
2. Send 50+ messages quickly
3. Scroll through all messages
4. Search within session
5. Open/close subscription view
6. Monitor performance

**Expected Result:**
- ✅ App doesn't crash
- ✅ Scrolling remains smooth
- ✅ Search works with many messages
- ✅ No memory warnings

---

## 🔄 Regression Testing

### Regression Test Checklist

Verify all previous features still work after updates:

#### Phase 1 Features (WebSocket & Gateway)
- [ ] App connects to gateway
- [ ] WebSocket connection stable
- [ ] Messages send/receive
- [ ] No connection drops

#### Phase 2 Features (Sessions & Messages)
- [ ] Multiple sessions work
- [ ] Message history saves
- [ ] Can switch sessions
- [ ] Messages persist after reopen

#### Phase 3 Features (Security)
- [ ] Ed25519 authentication
- [ ] Device signing works
- [ ] Secure credentials stored

#### Phase 4 Features (Core Data)
- [ ] Message persistence works
- [ ] Last 100 messages stored
- [ ] Search functionality
- [ ] Delete messages work

#### Phase 5 Features (Feature Gating)
- [ ] Free tier features available
- [ ] Pro features locked on free plan
- [ ] Feature toggles based on subscription

#### Phase 6 Features (Subscriptions)
- [ ] In-app purchase works
- [ ] Subscription state persists
- [ ] Plan comparison displays
- [ ] Restore purchases works

#### Phase 8 Features (Purchase UI) ✨ NEW
- [ ] SubscriptionView displays
- [ ] All plan cards visible
- [ ] Feature comparison table shows
- [ ] Purchase buttons respond

#### Phase 9 Features (Analytics) ✨ NEW
- [ ] Analytics events logged
- [ ] Session tracking works
- [ ] User properties set
- [ ] No crashes from analytics

---

## ⚡ Performance Testing

### Memory Profiling

#### Step 1: Monitor Memory in Xcode
1. Build app for simulator
2. Run app
3. Xcode → Debug → Memory Graph
4. Create 20+ messages
5. Observe memory usage

**Expected:**
- Initial: ~40-50 MB
- After messages: ~60-80 MB
- No memory leaks (flat line)

#### Step 2: Test Memory Cleanup
1. Create session with 50 messages
2. Delete session
3. Check memory graph
4. Should return to baseline

---

### CPU Usage Testing

#### Step 1: Monitor CPU
1. Instruments → CPU Profiler
2. Run app
3. Send messages (monitor CPU)
4. Scroll through history
5. Search messages

**Expected:**
- Idle: <5% CPU
- Messaging: <10% CPU
- Scrolling: <20% CPU
- Search: <15% CPU

---

### Battery Testing

#### Step 1: Monitor Battery on Device
1. Check device battery % before test
2. Run app for 30 minutes
3. Send messages, search, navigate
4. Check battery % after test

**Expected:**
- Battery drain: <10% in 30 minutes
- Device not warm after use
- No excessive background activity

---

### Network Performance

#### Step 1: Monitor Network
1. Instruments → System Trace
2. Send 10 messages
3. Check network activity

**Expected:**
- Message send: <500ms average
- No retries on stable connection
- Efficient data usage

---

## 🆘 Troubleshooting

### Test Fails: Build Error

**Problem:** `xcodebuild build` fails with Swift errors

**Solutions:**
```bash
# Clean everything
tuist clean
rm -rf .xcworkspace DerivedData

# Regenerate and rebuild
tuist generate
xcodebuild clean -workspace Momotaro.xcworkspace
xcodebuild build -workspace Momotaro.xcworkspace
```

### Test Fails: Simulator Not Found

**Problem:** "No matching devices found"

**Solutions:**
```bash
# List simulators
xcrun simctl list devices

# Create simulator if missing
xcrun simctl create "iPhone 17 Pro" com.apple.CoreSimulator.SimDeviceType.iPhone-17-Pro com.apple.CoreSimulator.SimRuntime.iOS-17-0

# Boot simulator
xcrun simctl boot "iPhone 17 Pro"
```

### Test Fails: Device Connection

**Problem:** "Could not prepare device for development"

**Solutions:**
1. Disconnect device from Mac
2. Restart device
3. Reconnect device
4. Trust certificate when prompted
5. Retry build

### Test Fails: Tests Timeout

**Problem:** Tests take too long or hang

**Solutions:**
```bash
# Run with shorter timeout
xcodebuild test \
  -workspace Momotaro.xcworkspace \
  -scheme Momotaro \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro" \
  -maximum-parallel-testing-workers 1
```

### App Crashes During Testing

**Problem:** App crashes with cryptic error

**Solutions:**
1. Check Xcode console for error message
2. Note the crash location
3. Search codebase for that code
4. Add breakpoint
5. Re-run with debugger
6. Inspect variables

---

## ✅ Sign-Off Checklist

### Unit Testing ✅
- [ ] 248/248 tests pass locally
- [ ] No compiler warnings
- [ ] All test modules included
- [ ] No skipped tests

### Simulator Testing ✅
- [ ] App launches without crash
- [ ] All features work on simulator
- [ ] UI responsive and correct
- [ ] No console errors
- [ ] Memory usage acceptable

### Device Testing ✅
- [ ] App installs on real iPhone
- [ ] App launches without crash
- [ ] All features work on device
- [ ] Touch gestures responsive
- [ ] No crashes during extended use
- [ ] Network connectivity works

### Manual Testing ✅
- [ ] Session management works
- [ ] Messaging works end-to-end
- [ ] Search functionality works
- [ ] Purchase flow works (sandbox)
- [ ] Error handling graceful
- [ ] App recovers from errors

### Regression Testing ✅
- [ ] All Phase 1-6 features work
- [ ] No breaking changes
- [ ] Backwards compatibility verified
- [ ] Previous tests still pass

### Performance Testing ✅
- [ ] Memory usage acceptable
- [ ] CPU usage reasonable
- [ ] Battery drain minimal
- [ ] Network latency acceptable
- [ ] No memory leaks detected

### Final Verification ✅
- [ ] Tested on simulator
- [ ] Tested on real device
- [ ] All checklists complete
- [ ] No open issues
- [ ] Ready for beta/release

---

## 📊 Test Result Template

**Date:** March __, 2026  
**Tester:** [Your Name]  
**Device:** [iPhone Model + iOS Version]  
**Build Version:** [Version Number]

### Results Summary
- **Unit Tests:** __/248 passed
- **Simulator Tests:** ✅ PASS / ❌ FAIL
- **Device Tests:** ✅ PASS / ❌ FAIL
- **Manual Tests:** ✅ PASS / ❌ FAIL
- **Performance Tests:** ✅ PASS / ❌ FAIL

### Issues Found
1. [Issue description]
2. [Issue description]
3. [Issue description]

### Sign-Off
- [ ] Tester approves release
- [ ] Ready for beta testing
- [ ] Ready for app store submission

**Tester Signature:** _______________  
**Date:** _______________

---

## 📞 Support & Questions

**Testing Questions?**
- Refer to [INSTALLATION.md](INSTALLATION.md) troubleshooting
- Check Xcode error logs
- Review console output
- Search GitHub Issues

**Issues Found?**
- Document in sign-off checklist
- Create GitHub issue with details
- Include error messages
- Attach screenshots if helpful

---

**Last Updated:** March 10, 2026  
**Status:** Production Ready ✅  
**Next Review:** After Phase 10 completion

🍑 **Happy Testing!**
