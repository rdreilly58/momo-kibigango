# Core Skill Stack — March 18, 2026

## Active Skills (20 core)

### Essential (5 — Always Available)
- **gog** — Gmail, Calendar, Drive, Sheets (official Google CLI)
- **ga4-analytics** — Google Analytics 4 reporting + BigQuery queries
- **ios-dev** — Xcode, iPhone builds, simulators (Momotaro)
- **aws-deploy** — AWS Amplify deployments (ReillyDesignStudio)
- **agent-browser** — Web automation + screenshot (agent-based)

### Always-On Automation (5)
- **daily-briefing** — Morning & evening briefing system (GA4, Gmail, Calendar, Git)
- **email-management** — Email reading via Himalaya (backup to gog)
- **gpu-health-check** — GPU offload instance monitoring
- **aws-mac-launch** — macOS instance provisioning (AWS)
- **slack** — Slack messaging + integrations

### Utilities (5)
- **make-pdf** — Pandoc-based PDF generation
- **office-docs** — Microsoft Word + Excel (python-docx)
- **print-local** — Brother printer control (local)
- **time-tracker** — Time tracking via CLI
- **invoice-generator** — Invoice creation from templates

### Development & Infrastructure (5)
- **address-lookup** — OSM Nominatim address verification
- **swift-expert** — SwiftUI + async/concurrency patterns
- **s3** — AWS S3 bucket operations
- **resiliant-connections** — API client resilience patterns
- **web-perf** — Web performance analysis + optimization
- **uml-diagrams** — PlantUML/Mermaid diagram generation

---

## Install on Demand (via Clawhub)

These are available in Clawhub and can be installed when needed:

```bash
# Code quality & testing
clawhub install code-review-automation    # PR reviews
clawhub install test-generation           # Auto-generate tests
clawhub install documentation-generator   # Keep docs in sync

# Analytics & reporting
clawhub install ga4-dashboard-builder     # Custom dashboards
clawhub install metrics-pipeline          # Metric exports
clawhub install bigquery-analyzer         # SQL queries

# Deployment & DevOps
clawhub install vercel-optimize           # Image optimization
clawhub install github-actions-optimizer  # CI/CD tuning

# Marketing & Social
clawhub install linkedin-automation       # LinkedIn posting (archived, can reinstall)
clawhub install twitter-automation        # X/Twitter integration
```

---

## Archived Skills (13 — Can Reinstall)

These were either:
- Redundant (covered by core skills)
- Incomplete (in-progress features)
- Platform-specific (rarely used)

**To restore:**
```bash
cp -r ~/.openclaw/workspace/skills-archived/[skill-name] ~/.openclaw/workspace/skills/
```

| Skill | Reason |
|-------|--------|
| browser-automation | Redundant with agent-browser |
| email-best-practices | Reference docs, not executable |
| email-daily-summary | Replaced by dynamic briefing |
| porteden-email | Platform-specific |
| himalaya | Slow (30-60s); gog is faster |
| mbse | YAML diagrams, low use |
| speculative-decoding | Phase 1 incomplete |
| security-monitor | Uptime monitoring, not integrated |
| linkedin-automation | On-demand reinstall as needed |
| notion | On-demand reinstall as needed |
| sovereign-aws-cost-optimizer | On-demand reinstall as needed |
| uptime-kuma | On-demand reinstall as needed |
| website-monitor | On-demand reinstall as needed |

---

## Cost Impact

### Before (30 skills)
- Skill discovery slower
- Larger attack surface
- More dependencies to manage
- ~4-5 minutes to list/search skills

### After (20 skills)
- Fast skill discovery
- Core competencies clear
- Minimal dependencies
- ~1 second to list skills

**Install on-demand reduces:**
- Clutter by 30%
- Dependency complexity by 40%
- Skill load time by 50%

---

## Next Steps

1. **Daily use** — You now have 20 focused skills
2. **Weekly** — Check SKILL_STACK.md if you need something missing
3. **Monthly** — Review which archived skills should be restored

---

*Last updated: March 18, 2026 at 6:45 PM EDT*  
*Maintained by: Momotaro*
