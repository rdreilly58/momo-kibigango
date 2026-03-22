# 🐛 Website & Browser Debug Skills Guide

**Installed:** Saturday, March 14, 2026 at 5:34 PM EDT

---

## ✅ 5 Debug Skills Now Available

| Skill | Rating | Purpose | Status |
|-------|--------|---------|--------|
| **web-perf** | 1.097 | Page performance analysis | ✅ Ready |
| **website-monitor** | 0.995 | Website health & uptime | ✅ Ready |
| **agent-browser** | 1.436 | Browser automation & control | ✅ Ready |
| **security-monitor** | 1.113 | Security scanning & audits | ✅ Ready |
| **uptime-kuma** | 1.133 | Uptime monitoring & alerts | ✅ Ready |

---

## 🎯 Skill 1: web-perf (Performance Analysis)

**Purpose:** Analyze website performance, Lighthouse scores, Core Web Vitals

### Quick Start
```bash
cat ~/.openclaw/workspace/skills/web-perf/SKILL.md
```

### Use Cases for ReillyDesignStudio

**Check homepage performance:**
```bash
# Command (see SKILL.md for exact syntax)
# web-perf https://www.reillydesignstudio.com
```

**What it measures:**
- ⏱️ Page load time
- 🎯 Core Web Vitals (LCP, FID, CLS)
- 🔍 Lighthouse scores
- 📊 Performance metrics by device
- 🖼️ Image optimization
- 🔄 First Contentful Paint (FCP)
- ⚡ Total Blocking Time (TBT)

**Tomorrow: Check admin page performance**
```bash
# web-perf https://www.reillydesignstudio.com/admin
# See if slow load time is part of the hanging issue
```

---

## 🌐 Skill 2: website-monitor (Health & Uptime)

**Purpose:** Monitor website status, uptime, SSL certificates, response times

### Quick Start
```bash
cat ~/.openclaw/workspace/skills/website-monitor/SKILL.md
```

### Use Cases for ReillyDesignStudio

**Monitor production site:**
```bash
# Continuous monitoring
# website-monitor https://www.reillydesignstudio.com --continuous

# Single check
# website-monitor https://www.reillydesignstudio.com
```

**What it checks:**
- ✅ HTTP status (200, 404, 500, etc.)
- ⏱️ Response time
- 🔒 SSL certificate validity
- 🔄 Redirect chains
- 📍 DNS resolution
- 🌍 Global availability (multiple regions)
- ⚠️ Content validation (check for expected text)

**Setup for daily monitoring:**
```bash
# Create scheduled check every hour
# website-monitor https://www.reillydesignstudio.com --interval 3600
```

---

## 🤖 Skill 3: agent-browser (Browser Automation)

**Purpose:** Control browser programmatically for testing, scraping, form filling

### Quick Start
```bash
cat ~/.openclaw/workspace/skills/agent-browser/SKILL.md
```

### Use Cases for ReillyDesignStudio

**Test admin login flow:**
```bash
# Navigate to admin page
# agent-browser https://www.reillydesignstudio.com/admin
# Wait for Google login button
# Click login
# Verify success/error
```

**Test full purchase flow:**
```bash
# agent-browser https://www.reillydesignstudio.com/shop
# Click "Buy" button
# Fill payment form
# Submit
# Check for success page
```

**Scrape portfolio data:**
```bash
# agent-browser https://www.reillydesignstudio.com/portfolio
# Extract project titles, descriptions, images
# Save to JSON
```

**Key capabilities:**
- Navigate pages
- Click buttons, links
- Fill forms with data
- Take screenshots
- Extract page content
- Handle modals/dialogs
- Track network requests
- Monitor console logs

---

## 🔐 Skill 4: security-monitor (Security Scanning)

**Purpose:** Scan for security vulnerabilities, misconfigurations, compliance issues

### Quick Start
```bash
cat ~/.openclaw/workspace/skills/security-monitor/SKILL.md
```

### Use Cases for ReillyDesignStudio

**Audit production site:**
```bash
# Full security scan
# security-monitor https://www.reillydesignstudio.com --full
```

**What it checks:**
- 🔒 SSL/TLS configuration
- 🛡️ CORS policy
- 🔑 Authentication headers
- 📋 Security headers (CSP, X-Frame-Options, etc.)
- 🔗 Mixed content (HTTP/HTTPS)
- 🚨 Known vulnerabilities in dependencies
- 🔓 Exposed secrets (API keys, tokens)
- ⚙️ Server configuration issues

**Check specific areas:**
```bash
# Check SSL certificate
# security-monitor https://www.reillydesignstudio.com --ssl-check

# Check headers
# security-monitor https://www.reillydesignstudio.com --headers

# Dependency vulnerability scan
# security-monitor /path/to/project --dependencies
```

---

## ⏰ Skill 5: uptime-kuma (Monitoring & Alerts)

**Purpose:** Continuous uptime monitoring with alerts and dashboards

### Quick Start
```bash
cat ~/.openclaw/workspace/skills/uptime-kuma/SKILL.md
```

### Use Cases for ReillyDesignStudio

**Setup production monitoring:**
```bash
# Start Uptime Kuma
# uptime-kuma start

# Add monitor for production site
# uptime-kuma add-monitor \
#   --name "ReillyDesignStudio Production" \
#   --url https://www.reillydesignstudio.com \
#   --interval 60

# Add email alerts
# uptime-kuma notify email robert@reillydesignstudio.com \
#   --on-down
```

**Key features:**
- ⏱️ Check every 60 seconds
- 📊 Uptime dashboard
- 📧 Email alerts on outage
- 📱 Slack/SMS notifications
- 📈 Uptime history & reports
- 🌍 Global monitoring
- 🔄 Automatic retries
- 📋 Incident logging

**Monitor critical endpoints:**
```bash
# uptime-kuma add-monitor --url https://www.reillydesignstudio.com/api/health
# uptime-kuma add-monitor --url https://www.reillydesignstudio.com/admin
# uptime-kuma add-monitor --url https://www.reillydesignstudio.com/shop
```

---

## 🎯 Tomorrow's Debug Workflow (5:00 AM)

### **Step 1: Performance Check**
```bash
# Check if page is slow or hanging
# web-perf https://www.reillydesignstudio.com/admin
# If LCP > 5s, performance is the issue
```

### **Step 2: Health Check**
```bash
# Verify page is responding
# website-monitor https://www.reillydesignstudio.com/admin
# If status 200 but content wrong, it's a rendering issue
```

### **Step 3: Browser Debug**
```bash
# Use agent-browser to step through the page
# agent-browser https://www.reillydesignstudio.com/admin
# Take screenshots, check for auth elements
# Monitor network requests during load
```

### **Step 4: Security Check**
```bash
# Verify no auth/cert issues
# security-monitor https://www.reillydesignstudio.com/admin
# Check for CORS, auth headers, certificate validity
```

### **Step 5: Continuous Monitoring**
```bash
# Setup Uptime Kuma for ongoing monitoring
# uptime-kuma start
# uptime-kuma add-monitor --url https://www.reillydesignstudio.com/admin
```

---

## 🔗 Integration with OpenClaw Managed Browser

You now have **two powerful browser automation systems:**

### **OpenClaw Managed Browser** (Native, Built-in)
- Real Chrome browser running
- CDP connection (low-level)
- Perfect for quick tests
- Commands: `openclaw browser [command]`

### **agent-browser Skill** (Programmatic)
- Higher-level automation
- Better for complex workflows
- Built-in reporting
- Configured scripts

### **Use both together:**
```bash
# 1. Start OpenClaw browser
openclaw browser open https://www.reillydesignstudio.com/admin

# 2. Take diagnostic screenshots
openclaw browser screenshot

# 3. Then use agent-browser for structured testing
# agent-browser https://www.reillydesignstudio.com/admin --test-auth
```

---

## 📊 Recommended Daily Monitoring Setup

### **Morning (7:00 AM)**
1. Run `web-perf` check on homepage
2. Run `website-monitor` on all critical endpoints
3. Check `security-monitor` for vulnerabilities

### **Throughout Day**
1. `uptime-kuma` running continuously (alerts on outage)
2. Manual `agent-browser` tests as needed

### **Evening (5:00 PM)**
1. Generate performance report
2. Review uptime history
3. Check for any security issues

---

## 🛠️ Configuration

Each skill has a SKILL.md file with detailed documentation:

```bash
# Read detailed guides
cat ~/.openclaw/workspace/skills/web-perf/SKILL.md
cat ~/.openclaw/workspace/skills/website-monitor/SKILL.md
cat ~/.openclaw/workspace/skills/agent-browser/SKILL.md
cat ~/.openclaw/workspace/skills/security-monitor/SKILL.md
cat ~/.openclaw/workspace/skills/uptime-kuma/SKILL.md
```

---

## 📈 Sample Reports

### **Performance Report**
```
Page: https://www.reillydesignstudio.com/admin
─────────────────────────────────────
Lighthouse Score:         72/100
First Contentful Paint:   2.3s
Largest Contentful Paint: 4.1s
Cumulative Layout Shift:  0.05
Total Blocking Time:      150ms
─────────────────────────────────────
Status: ⚠️ GOOD (could be optimized)
```

### **Health Report**
```
Endpoint: https://www.reillydesignstudio.com/admin
─────────────────────────────────────
HTTP Status:   200 OK
Response Time: 3.2s
SSL Cert:      ✅ Valid until 2027-03-14
Uptime:        99.98% (last 7 days)
DNS:           ✅ Resolves correctly
─────────────────────────────────────
Status: ✅ HEALTHY
```

### **Security Report**
```
Domain: reillydesignstudio.com
─────────────────────────────────────
SSL/TLS:           ✅ Modern (TLS 1.3)
Security Headers:  ⚠️ Missing CSP
CORS:              ✅ Configured
Auth:              ✅ Proper headers
Mixed Content:     ✅ None
Known Vulns:       ✅ None detected
─────────────────────────────────────
Risk Level: LOW
```

---

## ✅ Total Debug Toolkit Summary

You now have **comprehensive debugging coverage:**

| Layer | Tool | Purpose |
|-------|------|---------|
| **Browser Control** | OpenClaw Browser | Direct Chrome control |
| **Browser Automation** | agent-browser | Programmatic testing |
| **Performance** | web-perf | Lighthouse & metrics |
| **Availability** | website-monitor | Status & response time |
| **Security** | security-monitor | Vulnerability scanning |
| **Uptime** | uptime-kuma | Continuous monitoring |
| **Scripts** | Playwright skill | Complex automation |

---

## 🚀 Ready to Debug

Your complete debugging suite is installed and ready:

```bash
# Start debugging
openclaw browser open https://www.reillydesignstudio.com/admin
openclaw browser screenshot

# Then run checks
# web-perf https://www.reillydesignstudio.com/admin
# website-monitor https://www.reillydesignstudio.com/admin
# agent-browser https://www.reillydesignstudio.com/admin
```

**At 5:00 AM, you'll have all the tools to pinpoint the admin panel issue!** 🍑

---

**Status: ✅ INSTALLED & OPERATIONAL**
- 14 skills now installed (5 new debug skills)
- Browser automation ready (OpenClaw + agent-browser + Playwright)
- Performance monitoring active (web-perf)
- Security scanning available (security-monitor)
- Uptime alerts ready (uptime-kuma)
