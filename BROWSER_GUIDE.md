# 🌐 OpenClaw Managed Browser Guide

**Installed & Running:** Saturday, March 14, 2026 at 5:30 PM EDT

---

## ✅ Status: LIVE & READY

```
Profile:        openclaw
Status:         🟢 Running
Browser:        Chrome (Google Chrome)
CDP Port:       18800
CDP URL:        http://127.0.0.1:18800
User Data:      ~/.openclaw/browser/openclaw/user-data
```

---

## 🎯 What You Can Do

The OpenClaw managed browser gives you **direct browser control** for:

- ✅ **Navigate URLs** — Open websites in the browser
- ✅ **Take Screenshots** — Capture page state at any time
- ✅ **Fill Forms** — Automate input fields with JSON
- ✅ **Click Elements** — Interact with buttons, links, etc.
- ✅ **Type Text** — Type in input fields, search boxes
- ✅ **Drag & Drop** — Simulate user interactions
- ✅ **Hover Elements** — Trigger hover states
- ✅ **Wait for Elements** — Wait for page states, selectors, load conditions
- ✅ **Get Snapshots** — AI-powered element detection (refs)
- ✅ **Console Logs** — Read JavaScript console output
- ✅ **Network Requests** — Monitor network activity
- ✅ **Download Files** — Click links and save downloads
- ✅ **PDF Export** — Save pages as PDF
- ✅ **Handle Dialogs** — Accept/dismiss alerts, confirms, prompts
- ✅ **Manage Cookies** — Read/write session data
- ✅ **Evaluate JS** — Run custom JavaScript on the page
- ✅ **Profiles** — Multiple browser profiles for different contexts

---

## 🚀 Quick Start Examples

### **1. Navigate to a URL**
```bash
openclaw browser open https://www.reillydesignstudio.com
```

### **2. Take a Screenshot**
```bash
openclaw browser screenshot
# Returns: MEDIA:~/.openclaw/media/browser/[timestamp].jpg
```

### **3. Get Page Snapshot (AI Element Detection)**
```bash
openclaw browser snapshot
# Returns JSON with numbered refs for all clickable elements
```

### **4. Click an Element**
```bash
openclaw browser snapshot    # Get the ref numbers
openclaw browser click 12    # Click element ref #12
```

### **5. Type Text**
```bash
openclaw browser type 5 "hello world"  # Type into element ref #5
openclaw browser type 5 "hello" --submit  # Type and submit
```

### **6. Fill a Form**
```bash
openclaw browser fill --fields '[
  {"ref":"1","value":"Bob Reilly"},
  {"ref":"2","value":"bob@example.com"},
  {"ref":"3","value":"Message here"}
]'
```

### **7. Wait for Something**
```bash
openclaw browser wait --text "Login successful"
openclaw browser wait --selector "button.submit"
openclaw browser wait --url "https://www.reillydesignstudio.com/dashboard"
```

### **8. Get Console Logs**
```bash
openclaw browser console
openclaw browser console --level error  # Only errors
```

### **9. Get Network Requests**
```bash
openclaw browser requests
# Shows all HTTP requests made by the page
```

### **10. Save as PDF**
```bash
openclaw browser pdf
# Returns: MEDIA:~/.openclaw/media/browser/[timestamp].pdf
```

---

## 📋 Use Cases for ReillyDesignStudio

### **Use Case 1: Debug Admin Panel Hanging**
```bash
# Step 1: Open admin page
openclaw browser open https://www.reillydesignstudio.com/admin

# Step 2: Wait and watch for load
openclaw browser wait --selector "input[type=email]" --timeout 5000
# (If timeout: element never appeared = auth flow broken)

# Step 3: Capture network requests
openclaw browser requests
# Shows if Stripe, Google OAuth, or DB requests are failing

# Step 4: Check console for errors
openclaw browser console --level error
# Reveals JavaScript errors blocking the page
```

### **Use Case 2: Test Google OAuth Login**
```bash
# Step 1: Navigate to admin
openclaw browser open https://www.reillydesignstudio.com/admin

# Step 2: Get page snapshot to find Google login button
openclaw browser snapshot

# Step 3: Click Google login button
openclaw browser click 7  # (assuming ref #7 is the button)

# Step 4: Wait for Google login redirect
openclaw browser wait --url "accounts.google.com"

# Step 5: Take screenshot to see Google form
openclaw browser screenshot
```

### **Use Case 3: Monitor Vercel Deployment**
```bash
# Step 1: Open Vercel dashboard
openclaw browser open https://vercel.com/reillydesignstudio/deployments

# Step 2: Wait for deployment status to load
openclaw browser wait --text "✅ Ready"

# Step 3: Take screenshot to capture status
openclaw browser screenshot

# Step 4: Extract deployment info
openclaw browser snapshot  # Get refs for build info
```

### **Use Case 4: Test Stripe Integration**
```bash
# Step 1: Navigate to shop page
openclaw browser open https://www.reillydesignstudio.com/shop

# Step 2: Click "Buy" button
openclaw browser snapshot
openclaw browser click 5  # Find the button first

# Step 3: Fill checkout form
openclaw browser fill --fields '[
  {"ref":"10","value":"4242424242424242"},
  {"ref":"11","value":"12/25"},
  {"ref":"12","value":"123"}
]'

# Step 4: Submit and check for success
openclaw browser type 15 "Pay now" --submit
openclaw browser wait --text "Payment successful"
openclaw browser screenshot
```

### **Use Case 5: Scrape Portfolio Data**
```bash
# Step 1: Navigate to portfolio
openclaw browser open https://www.reillydesignstudio.com/portfolio

# Step 2: Get all portfolio items
openclaw browser snapshot --format aria  # More detailed

# Step 3: Extract specific data
openclaw browser evaluate --fn '(el) => el.innerText' --ref 3
# Get text content of element ref #3

# Step 4: Take screenshot for manual review
openclaw browser screenshot --full-page
```

---

## 🎮 Advanced Commands

### **Multiple Tabs**
```bash
# Open multiple tabs
openclaw browser open https://example.com
openclaw browser open https://google.com

# List all tabs
openclaw browser tabs

# Focus a specific tab
openclaw browser focus 71394795FF0E161EBB3C1DE820C2600D

# Close a tab
openclaw browser close 71394795FF0E161EBB3C1DE820C2600D
```

### **Handle Dialogs (Alerts/Confirms)**
```bash
# Arm dialog handler
openclaw browser dialog --accept  # Accept next alert/confirm
openclaw browser dialog --dismiss  # Dismiss next alert
openclaw browser dialog --prompt "My answer"  # Answer prompt

# Then trigger the dialog
openclaw browser click 5  # Click button that triggers dialog
```

### **Drag & Drop**
```bash
# Get refs from snapshot
openclaw browser snapshot

# Drag element ref #5 to element ref #10
openclaw browser drag 5 10
```

### **Hover Element**
```bash
openclaw browser hover 7
```

### **Press Keys**
```bash
openclaw browser press Enter
openclaw browser press Escape
openclaw browser press Tab
```

### **Manage Cookies**
```bash
# Read cookies
openclaw browser cookies

# Set a cookie
openclaw browser storage set-cookie "session" "abc123" --domain example.com
```

### **Resize Viewport**
```bash
openclaw browser resize 1280 720   # Desktop
openclaw browser resize 375 667    # Mobile
openclaw browser resize 768 1024   # Tablet
```

### **Record Trace (Debugging)**
```bash
openclaw browser trace start
# ... do stuff in browser ...
openclaw browser trace stop
# Opens trace file in Playwright Inspector
```

---

## 🔍 Snapshot Modes

When you take a snapshot, you get numbered refs for each element:

```bash
# AI-powered (understands button labels, context)
openclaw browser snapshot
# Returns: { "1": "Google Login", "2": "Create Account", "3": "Email Field" }

# Accessibility tree (ARIA labels)
openclaw browser snapshot --format aria

# Efficient mode (faster, less detail)
openclaw browser snapshot --efficient

# With custom limit
openclaw browser snapshot --limit 50  # Top 50 elements only

# With labels shown
openclaw browser snapshot --labels
```

---

## 📸 Screenshots & PDFs

### **Screenshot Options**
```bash
# Single viewport
openclaw browser screenshot

# Full page (scrolls and stitches)
openclaw browser screenshot --full-page

# Specific element by ref
openclaw browser screenshot --ref 7

# High quality
openclaw browser screenshot --quality high

# Output location
openclaw browser screenshot
# Always outputs to: ~/.openclaw/media/browser/[timestamp].jpg
```

### **PDF Export**
```bash
openclaw browser pdf
# Saves entire page as PDF to: ~/.openclaw/media/browser/[timestamp].pdf
```

---

## 🔐 Browser Profiles

Create separate profiles for different contexts:

```bash
# List profiles
openclaw browser profiles

# Create new profile
openclaw browser create-profile my-test-profile

# Use different profile
openclaw browser --browser-profile my-test-profile open https://example.com

# Delete profile
openclaw browser delete-profile my-test-profile

# Reset profile (clear cookies, cache)
openclaw browser reset-profile openclaw
```

---

## 🎯 Tomorrow's Admin Debug Plan

**At 5:00 AM, use this workflow:**

```bash
# Step 1: Navigate to admin
openclaw browser open https://www.reillydesignstudio.com/admin

# Step 2: Wait 10 seconds, check if page loads
openclaw browser wait --timeout 10000 --selector "input[type=email]"

# Step 3: If that fails, capture debug info
openclaw browser screenshot           # What does it show?
openclaw browser console --level error  # Any JS errors?
openclaw browser requests               # What network calls failed?

# Step 4: Check authentication element
openclaw browser snapshot --labels     # See if auth components loaded

# Step 5: Save all diagnostics
openclaw browser screenshot --full-page
# Save outputs to memory for analysis
```

---

## 📊 Real-World Example Workflow

**Testing the full ReillyDesignStudio payment flow:**

```bash
# 1. Start fresh
openclaw browser reset-profile openclaw
openclaw browser open https://www.reillydesignstudio.com/shop

# 2. Find and click "Buy" button
openclaw browser snapshot --labels
openclaw browser click 5  # (ref #5 = Buy button)

# 3. Wait for Stripe checkout to load
openclaw browser wait --text "Card information"

# 4. Fill payment form
openclaw browser fill --fields '[
  {"ref":"10","value":"4242 4242 4242 4242"},
  {"ref":"11","value":"12/25"},
  {"ref":"12","value":"123"}
]'

# 5. Submit payment
openclaw browser click 20  # (ref #20 = Pay button)

# 6. Wait for success
openclaw browser wait --text "Order confirmed" --timeout 10000

# 7. Verify (screenshot + console check)
openclaw browser screenshot --full-page
openclaw browser console
```

---

## 🛠️ Troubleshooting

### **Browser Won't Start**
```bash
openclaw browser stop
openclaw browser start
```

### **Port Already in Use**
```bash
# Reset browser profile
openclaw browser reset-profile openclaw

# Or use different port (in config)
# See: ~/.openclaw/config/openclaw.json
```

### **Screenshot Not Saving**
```bash
# Verify media directory exists
ls -la ~/.openclaw/media/browser/

# Or specify output manually
openclaw browser screenshot --full-page
# (always outputs to default location)
```

### **Element Not Found**
```bash
# Refresh snapshot to get latest refs
openclaw browser snapshot

# Check if element is visible
openclaw browser scrollintoview 12

# Try waiting for it
openclaw browser wait --selector "button.login"
```

---

## 📚 Documentation

- **Official Docs:** https://docs.openclaw.ai/cli/browser
- **CLI Help:** `openclaw browser --help`
- **Command Help:** `openclaw browser [command] --help`

---

## ✅ Ready to Use

Your OpenClaw managed browser is:
- ✅ Running and responsive
- ✅ Connected to Chrome DevTools Protocol
- ✅ Ready for automation and testing
- ✅ Configured with default profile
- ✅ Can create multiple profiles for different contexts

**Start using it:**
```bash
openclaw browser open https://www.reillydesignstudio.com
openclaw browser snapshot
openclaw browser screenshot
```

---

**Status: INSTALLED & OPERATIONAL** 🍑

Use this with Playwright for comprehensive browser automation testing!
