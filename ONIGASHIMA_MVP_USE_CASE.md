# ONIGASHIMA MVP — USE CASE & TECHNICAL DESIGN

**Date:** Wednesday, March 11, 2026, 2:24 PM EDT  
**Decision:** Approve MVP development track (parallel to Phase 0 marketing)  
**Use Case:** Non-technical customer with iPhone + Mac  
**Timeline:** Start now, MVP ready in 4-6 weeks (not waiting for Phase 0)

---

## 🎯 MVP USE CASE

### Target Customer
- **Device Setup:** Mac (any Intel/Apple Silicon) + iPhone
- **Tech Savviness:** Non-technical (no CLI, no terminal, no config files)
- **Goal:** Run personal AI assistant locally, backup to cloud, get support

### User Journey (Ideal Experience)

**Day 1: Installation (15 minutes)**
```
Customer downloads installer → Runs visual setup wizard → 
System configured (OpenClaw + Momotaro iOS) → 
QR code appears → Scan with iPhone → Done ✓
```

**Day 2+: Daily Use**
```
Ask Momotaro (via iPhone) → AI uses OpenClaw context (Mac) → 
Instant answer with knowledge of calendar, emails, files → 
All data stays on Mac, never leaves device ✓
```

**Features Enabled**
```
✓ Natural language commands on iPhone
✓ Access to Mac data (read-only): calendar, emails, files, GitHub
✓ Automatic syncing (iPhone ↔ Mac)
✓ Automatic backups (encrypted to cloud)
✓ Update notifications (one-click update)
✓ Remote support chat (through RDS, peer-to-peer via Tailscale)
```

---

## 📋 MVP SCOPE (Phase 0 Technical Track)

### What's Included (MVP 1.0)
1. **macOS Installer**
   - Visual wizard (not CLI)
   - One-click OpenClaw setup
   - System requirements check
   - Configuration assistant
   - Success verification

2. **iPhone Companion App**
   - Use existing Momotaro iOS as base
   - Add pairing with Mac via QR code
   - Add command interface
   - Add message history
   - Add support chat (basic)

3. **Cloud Infrastructure (MVP)**
   - User authentication (email/password)
   - Device pairing registry
   - Backup storage (encrypted)
   - Update distribution (simple, not complex)
   - Support chat relay (peer-to-peer via Tailscale)

4. **Automatic Updates**
   - Check for updates daily
   - Download in background
   - One-click install (no complexity)
   - Rollback if needed

5. **Remote Support**
   - Chat interface (built into app + web)
   - Peer-to-peer SSH tunnel (Tailscale)
   - Screen sharing (optional, future)
   - File transfer (sftp via Tailscale)

### What's NOT Included (Phase 1+)
- Hardware pre-configuration (Phase 3)
- Multi-user/team features (Phase 2)
- Custom domains/branding
- Advanced automation
- API marketplace

---

## 🏗️ TECHNICAL ARCHITECTURE

### System Overview
```
┌─────────────┐                          ┌──────────────┐
│   iPhone    │                          │   Mac        │
│ Momotaro    │◄──── Tailscale Mesh ────►│  OpenClaw    │
│   App       │     (encrypted tunnel)   │  + Installer │
└─────────────┘                          └──────────────┘
       │                                         │
       │                                         │
       └─────────────┬──────────────────────────┘
                     │
              ┌──────▼───────┐
              │  Cloud       │
              │  - Auth      │
              │  - Backup    │
              │  - Updates   │
              │  - Support   │
              └──────────────┘
```

### Technology Stack

**macOS Installer**
- Language: SwiftUI (native macOS)
- Framework: AppKit for system tasks
- Distribution: Direct download from website
- Signing: Apple Developer certificate (code signing)
- Size: ~50-100 MB (includes OpenClaw bundle)

**iPhone App**
- Use existing Momotaro iOS (production-ready)
- Add: QR pairing, Tailscale integration, support chat
- Update: WebSocket → supports new pairing flow

**Cloud Backend**
- Framework: Node.js + Express (or Python + FastAPI)
- Database: PostgreSQL (managed AWS RDS or DigitalOcean)
- Auth: JWT + OAuth (Google/GitHub optional later)
- Storage: S3 for backups (encrypted, user can export)
- Infrastructure: Docker + Kubernetes or DigitalOcean App Platform

**Networking**
- Primary: Tailscale (zero-trust mesh VPN)
- Backup: Direct connection (if Tailscale fails)
- Encryption: TLS + WireGuard (built into Tailscale)

**Deployment**
- Installer: AWS CloudFront CDN (fast downloads worldwide)
- Backend: AWS Amplify or DigitalOcean App Platform (simple scaling)
- Monitoring: CloudWatch + Datadog (minimal, MVP)

---

## 🔄 MVP WORKFLOW

### 1. Installation (macOS Installer)

**Flow:**
```
1. Download installer (50-100 MB)
2. Run installer
3. Visual wizard shows:
   - Welcome screen
   - System requirements check
   - Installation path selector
   - OpenClaw configuration (API key, etc.)
   - Progress bar
   - Success screen with QR code
4. Generated: Unique installation ID + pairing code
```

**What Happens Behind the Scenes:**
- Download OpenClaw (if needed)
- Install to `/Applications/OpenClaw/`
- Create config file in `~/.openclaw/`
- Generate SSH keypair for iPhone
- Register device with cloud backend
- Create Tailscale VPN config
- Verify everything works

**Result:** Installation ID + QR code displayed for iPhone

---

### 2. iPhone Pairing (Momotaro App)

**Flow:**
```
1. Open Momotaro app
2. Tap "Connect to Mac"
3. Scan QR code from installer
4. App verifies pairing code with cloud
5. App connects to Mac via Tailscale
6. Test connection
7. Show success
```

**What Happens:**
- Scan QR → Extract installation ID + pairing code
- Call cloud API: `POST /api/devices/verify-pairing`
- Cloud validates code + installation ID
- Cloud returns: SSH key, Tailscale config, Mac IP
- App stores credentials (encrypted in Keychain)
- App connects via Tailscale to Mac

**Result:** iPhone paired with Mac, can communicate

---

### 3. Daily Use (Talking to Momotaro)

**Flow (iPhone):**
```
User: "What's on my calendar tomorrow?"
         ↓
    [Send to Mac via Tailscale]
         ↓
    [Mac receives via OpenClaw]
         ↓
    [OpenClaw calls Momotaro + your context]
         ↓
    [Momotaro reads calendar, emails, files]
         ↓
    [Generates personalized response]
         ↓
    [iPhone displays answer]
```

**Implementation:**
- iPhone app sends query to OpenClaw (via Tailscale SSH tunnel)
- OpenClaw processes locally on Mac
- OpenClaw returns response
- iPhone displays with chat history
- All data stays on Mac (except encrypted backups)

---

### 4. Automatic Updates

**Flow:**
```
Mac checks cloud (daily at 2 AM):
  "Is there a new version?"
         ↓
Cloud returns: "Yes, version 1.2.3 available"
         ↓
Mac downloads update in background
         ↓
Notification appears: "Update ready. Click to install."
         ↓
User clicks "Update"
         ↓
Installer runs, system restarts if needed
         ↓
Verification: New version confirmed
         ↓
Success notification
```

**Technical:**
- Version file stored in S3
- Installer distributed via CloudFront CDN
- Update check: HTTP request + version comparison
- Download: Background task (ResumableTask)
- Install: Elevated privileges (only when user clicks)
- Rollback: Keep previous version for 7 days

---

### 5. Remote Support (Chat + Tunneling)

**Support Chat:**
```
User clicks "Support" in app
         ↓
Web form or in-app chat
         ↓
Message sent to RDS support queue
         ↓
Support agent can:
  - Chat with user
  - Review logs
  - Request to create peer tunnel
  - SSH into Mac (with permission)
  - View screen (optional, future)
```

**Peer Tunnel (for advanced support):**
```
User clicks "Allow Remote Access"
         ↓
Tailscale grants support agent access
         ↓
Agent can SSH to Mac (read-only by default)
         ↓
Agent can view logs, restart services
         ↓
When done, agent loses access
         ↓
User gets confirmation
```

---

## 📊 MVP REQUIREMENTS

### Mac Installer
- [ ] SwiftUI UI (5-7 screens)
- [ ] System requirements check (macOS 11+, 8GB RAM, 50GB disk)
- [ ] OpenClaw download + verify (if not installed)
- [ ] Configuration wizard (API keys, paths)
- [ ] SSH keypair generation
- [ ] Tailscale config generation
- [ ] Device registration with cloud
- [ ] QR code generation for iPhone pairing
- [ ] Error handling + rollback
- [ ] Logging + diagnostics
- [ ] Code signing (Apple Developer cert)
- [ ] Documentation + help

### iPhone App Updates
- [ ] QR code scanner (use Momotaro-iOS camera API)
- [ ] Pairing flow (verify with cloud backend)
- [ ] Tailscale integration (use existing Tailscale SDK)
- [ ] Support chat UI (add to existing app)
- [ ] Remote tunnel requests (optional for MVP, can add later)
- [ ] Better error messages (non-technical friendly)

### Cloud Backend (MVP)
- [ ] Auth endpoints: `/api/auth/register`, `/api/auth/login`
- [ ] Device endpoints:
  - `POST /api/devices/register` (installer registration)
  - `POST /api/devices/verify-pairing` (iPhone pairing)
  - `GET /api/devices/{id}` (get device info)
  - `PUT /api/devices/{id}/status` (heartbeat)
- [ ] Backup endpoints:
  - `POST /api/backups` (upload encrypted backup)
  - `GET /api/backups` (list backups)
  - `POST /api/backups/{id}/restore` (restore backup)
- [ ] Updates:
  - `GET /api/versions/latest` (check for updates)
  - `GET /api/versions/{version}/download` (download URL)
- [ ] Support:
  - `POST /api/support/messages` (send support message)
  - `GET /api/support/messages` (get conversation)
  - `POST /api/support/tunnel-request` (request remote access)
- [ ] Health:
  - `GET /api/health` (system status)
  - `GET /api/metrics` (basic metrics)

### Database Schema (MVP)
- `users` (id, email, password_hash, created_at)
- `devices` (id, user_id, installation_id, device_name, mac_address, os_version, tailscale_ip, created_at, last_seen)
- `pairings` (id, device_id, pairing_code, expires_at, verified_at)
- `backups` (id, device_id, timestamp, size, encrypted_key, s3_path, created_at)
- `support_messages` (id, device_id, user_message, agent_message, created_at, resolved_at)
- `versions` (id, version_string, release_date, download_url, release_notes, is_latest)

---

## ⏱️ DEVELOPMENT TIMELINE (MVP Track)

### Phase 0.1: Technical Design (This Week - March 11-15)
- [ ] Detailed architecture docs (Momotaro + Claude Code)
- [ ] Database schema design
- [ ] API specification (OpenAPI)
- [ ] Installer workflow design
- [ ] Pairing flow design
- [ ] Security review
- **Deliverable:** Ready for development

### Phase 0.2: MVP Backend (Week 2-3 - March 16-29)
- [ ] Cloud infrastructure setup (AWS/DigitalOcean)
- [ ] Database setup + migrations
- [ ] Auth endpoints (register, login)
- [ ] Device registration endpoints
- [ ] Basic API structure
- [ ] Deployment pipeline
- **Deliverable:** Working backend API

### Phase 1: Installer + App (Weeks 4-6 - March 30 - April 13)
- [ ] macOS installer UI (SwiftUI)
- [ ] Installer flow (setup wizard)
- [ ] iPhone app updates (pairing + support)
- [ ] Tailscale integration (both sides)
- [ ] Testing + refinement
- **Deliverable:** Alpha MVP (internal testing)

### Phase 2: Polish + Beta (Weeks 7-9 - April 14-27)
- [ ] Bug fixes + refinement
- [ ] Documentation
- [ ] Beta testing (10-20 users)
- [ ] Support infrastructure
- [ ] Marketing materials
- **Deliverable:** Beta MVP (ready for limited release)

### Phase 3: Launch (Week 10 - April 28+)
- [ ] Public launch to first 100 customers
- [ ] Monitor stability
- [ ] Gather feedback
- [ ] Plan Phase 1 features
- **Deliverable:** MVP live

---

## 💰 COST ESTIMATE (MVP Track)

### Development
- Backend engineer: 3-4 weeks @ $120/hr = $14K-$19K
- Frontend (installer): 3-4 weeks @ $120/hr = $14K-$19K
- DevOps (infrastructure setup): 1-2 weeks @ $150/hr = $6K-$12K
- QA/Testing: 1-2 weeks @ $80/hr = $4K-$8K
- **Total Dev:** $38K-$58K

### Infrastructure (3 months)
- AWS/DigitalOcean: $500/month = $1.5K
- S3 storage (backups): $100/month = $300
- CDN (downloads): $200/month = $600
- Monitoring: $100/month = $300
- **Total Infrastructure:** $2.7K

### Third-party Services
- Tailscale (team plan): $10/month = $30
- Apple Developer cert: $99/year = $8
- GitHub (private repo): Free
- **Total Services:** $38

### **Total MVP Cost:** $40.7K-$60.7K

---

## 🚀 SUCCESS CRITERIA (MVP Launch)

**Technical:**
- ✓ Installer works on Intel + Apple Silicon Macs
- ✓ iPhone pairing completes in 2-3 minutes
- ✓ Messages go through Tailscale tunnel reliably
- ✓ Automatic updates work (test with at least 5 users)
- ✓ Backups work (test restore)
- ✓ Support chat functional
- ✓ 99.5% uptime during beta (2 weeks)

**User Experience:**
- ✓ Non-technical user can install without help
- ✓ Error messages are clear + actionable
- ✓ Support response time < 24 hours
- ✓ NPS > 50 from beta testers
- ✓ Setup time < 15 minutes (installer + pairing)

**Business:**
- ✓ 20-50 beta signups
- ✓ 15+ reviews/testimonials
- ✓ $0 acquisition cost (word of mouth)
- ✓ Clear feedback on Phase 1 features
- ✓ Pricing validated ($99/year + $899 hardware)

---

## 📞 NEXT STEP: TECHNICAL DESIGN

**Action:** Spawn Claude Code to create:
1. Detailed technical architecture document
2. API specification (OpenAPI/Swagger)
3. Database schema (SQL)
4. Installer wireframes
5. Backend starter code (Node.js/Express skeleton)

**Estimated time:** 2-3 hours (Claude Code)

**Deliverable:** Ready for development to start Monday, March 13

---

## 🍑 Summary

**MVP Strategy:**
- Don't wait for Phase 0 (marketing) to finish
- Build MVP in parallel (developer track)
- Use MVP to validate Phase 0 assumptions
- Gather real user feedback early
- Iterate based on actual behavior

**Timeline:**
- Week 1: Technical design (now)
- Week 2-3: Backend development
- Week 4-6: Installer + app
- Week 7-9: Polish + beta
- Week 10: Launch to 100 customers

**By April 28:** First 100 customers using MVP
**By May:** Real revenue + feedback for Phase 1

This is the fastest path to revenue and market validation.

---

**Created:** March 11, 2026, 2:24 PM EDT  
**Owner:** Bob Reilly + Momotaro  
**Status:** Ready for technical development
