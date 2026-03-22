# Work Organization Strategy for Leidos
## Team Lead - Principal Software Engineer, Airborne & Mission Solutions

*Created: March 22, 2026*  
*For: Bob Reilly (Robert.D.Reilly@Leidos.com)*  
*Position: Defense Sector, Decision Advantage Business Area*

---

## Executive Summary

This document provides a comprehensive organization strategy for your new role at Leidos, balancing security requirements of defense work with practical engineering needs. The recommended approach uses a **hybrid model** combining local workspace for sensitive/personal notes with GitHub for shareable, unclassified work.

### Key Recommendations
1. **Primary Storage:** Workspace subdirectory for CUI/sensitive content + GitHub private repo for unclassified work
2. **Platform:** GitHub Enterprise (if Leidos provides) or personal GitHub private repo
3. **Security:** Strict separation of classified, CUI, and public content
4. **Integration:** Seamless connection with existing memory system (MEMORY.md, daily notes)

---

## 1. Storage Architecture Comparison

| Aspect | Workspace Only | GitHub Only | **Hybrid (Recommended)** |
|--------|----------------|-------------|-------------------------|
| **Security** | ✅ Excellent (local) | ❌ Risk for CUI | ✅ Best of both |
| **Collaboration** | ❌ None | ✅ Easy team access | ✅ Selective sharing |
| **Version Control** | ⚠️ Manual git | ✅ Automatic | ✅ Full git features |
| **Backup** | ⚠️ Local only | ✅ Cloud redundancy | ✅ Multiple layers |
| **Search** | ✅ Local tools | ✅ GitHub search | ✅ Both available |
| **Access** | ⚠️ Device-specific | ✅ Anywhere | ✅ Flexible |
| **Compliance** | ✅ Full control | ⚠️ Depends on setup | ✅ Segregated properly |
| **Integration** | ✅ Direct with Momo | ❌ Requires sync | ✅ Selective sync |

---

## 2. Security Classification Framework

### Defense Sector Content Types

#### 🔴 **Classified Information**
- **Storage:** NEVER in personal systems
- **Access:** SCIF only, government-furnished equipment
- **Examples:** SECRET/TS materials, classified program details

#### 🟡 **Controlled Unclassified Information (CUI)**
- **Storage:** Local workspace ONLY (not GitHub)
- **Requirements:** NIST 800-171 compliance
- **Examples:** 
  - Export-controlled technical data (ITAR/EAR)
  - Proprietary Leidos algorithms
  - Contract-sensitive information
  - For Official Use Only (FOUO) content
  - Personnel/HR sensitive data

#### 🟢 **Unclassified Public Release**
- **Storage:** GitHub private repo acceptable
- **Examples:**
  - General engineering notes
  - Public domain algorithms
  - Open-source contributions
  - Professional development
  - Team processes (sanitized)

### Security Decision Tree

```
Is it classified?
├─ YES → SCIF only, stop here
└─ NO → Continue
   │
   Contains CUI markers? (FOUO, proprietary, export-controlled)
   ├─ YES → Workspace only
   └─ NO → Continue
      │
      Contains company IP or sensitive architecture?
      ├─ YES → Workspace only
      └─ NO → GitHub private repo OK
```

---

## 3. Recommended Directory Structure

### A. Workspace Structure (`~/.openclaw/workspace/leidos/`)

```
leidos/
├── .gitignore                    # Exclude sensitive files
├── README.md                     # Local navigation guide
├── security-classification.md    # Quick reference for what goes where
│
├── memory/                       # Work-specific memories
│   ├── daily/                   # Daily work logs
│   │   └── 2026-03-22.md
│   ├── meetings/                # Meeting notes (sanitized)
│   └── decisions/               # Architecture decisions
│
├── cui/                         # CUI/sensitive content (NEVER sync)
│   ├── .no-sync               # Marker file
│   ├── contracts/
│   ├── proprietary/
│   └── export-controlled/
│
├── projects/                    # Active project work
│   ├── project-alpha/          # Codenames for sensitive work
│   └── project-beta/
│
├── knowledge/                   # Technical learning
│   ├── systems/                # System architectures
│   ├── tools/                  # Tool configurations
│   └── processes/              # Team processes
│
└── personal/                    # Your notes, reviews, goals
    ├── 1-on-1s/
    ├── performance/
    └── career-development/
```

### B. GitHub Repository Structure (`leidos-engineering-notes`)

```
leidos-engineering-notes/        # Private repo
├── README.md                    # Professional intro
├── SECURITY.md                  # What NOT to put here
│
├── onboarding/                  # Team onboarding docs
│   ├── new-engineer-guide.md
│   ├── tool-setup.md
│   └── team-processes.md
│
├── architecture/                # Sanitized architecture notes
│   ├── patterns/               # Design patterns used
│   ├── decisions/              # ADRs (sanitized)
│   └── diagrams/               # Public-safe diagrams
│
├── learning/                    # Professional development
│   ├── courses/
│   ├── conferences/
│   └── certifications/
│
├── processes/                   # Team processes
│   ├── code-review.md
│   ├── deployment.md
│   └── incident-response.md
│
└── tools/                       # Tool configurations
    ├── ide-setup/
    ├── scripts/                # Utility scripts
    └── templates/              # Document templates
```

---

## 4. Documentation Templates

### A. README.md Template (GitHub)

```markdown
# Engineering Notes - Robert Reilly
## Principal Software Engineer, Leidos

**Security Notice:** This repository contains ONLY unclassified, publicly releasable information. 
No CUI, proprietary algorithms, or sensitive data permitted.

### Repository Structure
- `/onboarding` - New team member resources
- `/architecture` - Design patterns and decisions (sanitized)
- `/learning` - Professional development tracking
- `/processes` - Team workflows and standards

### Contact
- Work: Robert.D.Reilly@Leidos.com
- GitHub: [your-github-handle]

### Last Updated
March 2026
```

### B. Daily Work Log Template

```markdown
# Work Log: 2026-03-22

## Morning Standup
- **Yesterday:** [Completed items]
- **Today:** [Planned work]
- **Blockers:** [Any impediments]

## Tasks
- [ ] Review architecture proposal (Project Alpha)
- [ ] Team lead sync - 10am
- [ ] Code review for [sanitized description]

## Meetings
### 10:00 - Team Sync
- Discussed: [public-safe summary]
- Action items: [assigned tasks]

## Technical Notes
- Investigated [technology/pattern]
- Solution: [approach without proprietary details]

## Learning
- Read: [article/documentation]
- Key insight: [lesson learned]

## EOD Summary
- Completed: X of Y planned tasks
- Tomorrow focus: [priority items]
```

### C. Architecture Decision Record (ADR) Template

```markdown
# ADR-001: [Decision Title]

## Status
Proposed | Accepted | Deprecated

## Context
[Background information - sanitized for public repo]

## Decision
[What was decided - no proprietary details]

## Consequences
- **Positive:** [Benefits]
- **Negative:** [Trade-offs]
- **Neutral:** [Other impacts]

## References
- [Public documentation links]
- [Open standards referenced]
```

---

## 5. Security Guidelines

### DO Store in GitHub
✅ General engineering best practices  
✅ Public domain algorithms and patterns  
✅ Open-source tool configurations  
✅ Sanitized architecture decisions  
✅ Professional development plans  
✅ Team processes (non-sensitive)  
✅ Conference notes and learnings  

### DON'T Store in GitHub
❌ Anything marked CUI, FOUO, or proprietary  
❌ Customer names or contract details  
❌ Specific system architectures  
❌ Network diagrams or IP addresses  
❌ Security vulnerabilities  
❌ Employee personal information  
❌ Export-controlled technical data  
❌ Proprietary algorithms or source code  

### Security Practices
1. **Two-Factor Authentication:** Mandatory on all accounts
2. **Commit Signing:** Use GPG keys for commits
3. **Access Control:** Private repos, minimal collaborators
4. **Regular Audits:** Monthly review of repo contents
5. **Incident Response:** Delete and report any accidental CUI upload

---

## 6. Integration with Existing Memory System

### Workspace Integration Points

```markdown
# In MEMORY.md (main workspace)
## Work - Leidos
- Started: March 21, 2026
- Role: Team Lead - Principal Software Engineer
- Work notes: `~/.openclaw/workspace/leidos/`
- GitHub: https://github.com/[username]/leidos-engineering-notes (unclassified only)
- Key projects: [Project Alpha, Project Beta] (details in local workspace)
```

### Daily Note References

```markdown
# In daily notes (memory/2026-03-22.md)
## Work
- See detailed log: `~/.openclaw/workspace/leidos/memory/daily/2026-03-22.md`
- GitHub commits: [link to today's commits]
- CUI work: Check local workspace (not synced)
```

### Automated Sync Script

```bash
#!/bin/bash
# sync-work-notes.sh - Selective sync to GitHub

# Only sync non-CUI directories
cd ~/.openclaw/workspace/leidos
rsync -av --exclude="cui/" --exclude="*.secret" \
  projects/ ~/repos/leidos-engineering-notes/architecture/

# Commit and push
cd ~/repos/leidos-engineering-notes
git add .
git commit -m "Update: $(date +%Y-%m-%d) work notes"
git push
```

---

## 7. Implementation Checklist

### Week 1: Foundation
- [ ] Create workspace directory structure
- [ ] Set up `.gitignore` for sensitive content
- [ ] Create GitHub private repository
- [ ] Enable 2FA on GitHub account
- [ ] Configure GPG commit signing
- [ ] Create initial README.md files
- [ ] Set up security classification guide

### Week 2: Process
- [ ] Establish daily note routine
- [ ] Create first ADR
- [ ] Set up automated backup (local)
- [ ] Configure selective sync script
- [ ] Document team processes
- [ ] Create onboarding template

### Week 3: Refinement
- [ ] Review and audit all content
- [ ] Get team feedback on structure
- [ ] Refine templates based on use
- [ ] Set up knowledge management system
- [ ] Create project tracking method

### Month 2: Optimization
- [ ] Evaluate what's working
- [ ] Adjust directory structure
- [ ] Improve automation scripts
- [ ] Consider GitHub Actions for checks
- [ ] Plan for long-term archival

---

## 8. Alternative Approaches

### Option A: Maximum Security (Air-Gapped)
- **Pros:** Zero risk of leaks, full compliance
- **Cons:** No collaboration, no cloud backup
- **Best for:** Highly classified work only

### Option B: GitLab Self-Hosted
- **Pros:** More control, on-premise option
- **Cons:** Maintenance overhead, less integration
- **Best if:** Leidos provides internal GitLab

### Option C: Confluence/SharePoint
- **Pros:** Enterprise features, audit trails
- **Cons:** Less developer-friendly, corporate lock-in
- **Consider if:** Required by Leidos IT

### Option D: Obsidian + Sync
- **Pros:** Great for knowledge management
- **Cons:** Not built for code/engineering
- **Good for:** Personal note-taking layer

---

## 9. Long-Term Archival Strategy

### Quarterly Backups
1. **Local Archive:** Tar + encrypt sensitive workspace
2. **GitHub Archive:** Download repository backup
3. **External Drive:** Encrypted backup of both
4. **Cloud Storage:** Non-CUI content only (encrypted)

### Annual Review
- Purge outdated CUI content (follow retention policy)
- Archive completed projects
- Update security classifications
- Refresh encryption keys
- Document lessons learned

### Career Portfolio
- Extract sanitized best work for portfolio
- Document major achievements (public-safe)
- Maintain professional development record
- Keep certifications and training logs

---

## 10. Decision Tree Summary

```
Starting new task/document
│
Is it for Leidos work?
├─ NO → Use main workspace
└─ YES → Continue
   │
   Is it classified?
   ├─ YES → STOP - Use SCIF systems only
   └─ NO → Continue
      │
      Contains CUI/FOUO/Proprietary?
      ├─ YES → leidos/cui/ directory (local only)
      └─ NO → Continue
         │
         Would it benefit team?
         ├─ YES → GitHub private repo + local
         └─ NO → leidos/personal/ directory
```

---

## Final Recommendations

1. **Start with hybrid approach** - Local workspace for sensitive + GitHub for sharable
2. **Err on side of caution** - When in doubt, keep it local
3. **Regular reviews** - Monthly audit of GitHub content
4. **Clear labeling** - Mark all documents with classification
5. **Automate carefully** - Scripts should exclude sensitive directories
6. **Team alignment** - Share approach with team for consistency
7. **Future-proof** - Design for easy migration/archival

This strategy provides security for defense work while maintaining productivity and collaboration where appropriate. Adjust based on specific Leidos policies once you receive them.

---

*Remember: Your reputation and security clearance depend on proper information handling. When in doubt, ask your FSO (Facility Security Officer) or supervisor.*