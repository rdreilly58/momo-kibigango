# DORA Metrics Training Plan for Leidos

**Prepared for:** Robert Reilly, Team Lead - Principal Software Engineer  
**Date:** March 29, 2026  
**Duration:** 2-4 weeks (self-paced)  
**Level:** Executive/Leadership + Engineering Team

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [The 4 DORA Metrics](#the-4-dora-metrics)
3. [Learning Objectives](#learning-objectives)
4. [Weekly Curriculum](#weekly-curriculum)
5. [Reading Materials](#reading-materials)
6. [Mistakes to Avoid](#mistakes-to-avoid)
7. [Implementation Guide](#implementation-guide)
8. [Leidos Specific Guidance](#leidos-specific-guidance)

---

## Overview

### What are DORA Metrics?

**DORA** = DevOps Research and Assessment

DORA metrics are **4 key measurements** that predict high-performing software teams:

1. **Deployment Frequency** — How often do we deploy to production? (daily? monthly?)
2. **Lead Time for Changes** — How long from code commit to production? (hours? months?)
3. **Change Failure Rate** — What % of deployments cause incidents? (0%? 50%?)
4. **Mean Time to Recover** — How fast do we fix incidents? (minutes? days?)

### Why DORA for Leidos?

**Defense contractors have unique challenges:**
- ✅ Long release cycles (quarterly, annual)
- ✅ Strict compliance & audit requirements
- ✅ Multiple teams & vendors
- ✅ High risk (mission-critical systems)
- ✅ Need to show progress to leadership

**DORA helps because:**
- **Objective metrics** — Not guessing, measuring
- **Throughput + Stability** — Balanced view of performance
- **Predictive** — Correlates with organizational success
- **Industry benchmarks** — Compare to other defense orgs
- **Actionable** — Clear levers to improve

### Research Foundation

DORA research (by Nicole Forsgren, Gene Kim, Jez Humble) surveyed **36,000+ engineers over 7 years**.

Key finding: **High-performing teams are 200x faster at deploying AND more stable.**

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| **Deployment Frequency** | On-demand (multiple/day) | Weekly | Monthly | Quarterly |
| **Lead Time** | <1 hour | <1 day | <1 week | >1 month |
| **Change Failure Rate** | 0-15% | 16-30% | 31-45% | 46-60% |
| **Mean Time to Recover** | <1 hour | 1 hour - 1 day | 1 day - 1 week | >1 week |

---

## The 4 DORA Metrics

### 1. Deployment Frequency

**Definition:** How often do we successfully deploy code to production?

**Why it matters:**
- Frequent deploys = smaller changes = faster feedback = lower risk
- Quarterly releases = big bang = high risk of failure
- Defense systems often monthly/quarterly, but goal is to optimize

**How to measure:**
```
Deployments per week = (total deployments in period) / (number of weeks)

Example:
- Week 1: 3 deploys
- Week 2: 2 deploys  
- Week 3: 5 deploys
- Week 4: 1 deploy
Average: 2.75 deploys/week
```

**For Leidos:**
- **Current state:** Likely quarterly or monthly
- **Ideal state for mission-critical:** Weekly or bi-weekly
- **Improvement:** Automate testing, staging, approval workflows

### 2. Lead Time for Changes

**Definition:** How long does it take from code commit to production?

**Why it matters:**
- Short lead time = fast feedback = faster learning
- Long lead time = stale code in queue = integration problems
- Shows how efficient your process is

**How to measure:**
```
Lead time = (deployment timestamp) - (commit timestamp)

Example:
- Commit: Monday 9 AM
- Deploy: Tuesday 2 PM
- Lead time: 29 hours

Track: P50 (median), P95, P99 percentiles
P50: 29 hours
P95: 48 hours (some changes slower)
P99: 72 hours (rare blocker)
```

**For Leidos:**
- **Current state:** Likely 1-4 weeks
- **Ideal state:** <1 week
- **Improvement:** Parallel review/test, CI/CD automation, smaller PRs

### 3. Change Failure Rate

**Definition:** What percentage of deployments cause incidents/rollbacks?

**Why it matters:**
- High CFR = you're shipping bugs = quick detection = fast recovery (if MTTR short)
- Low CFR = slow, cautious deployment = long lead time
- Balanced: ~20% CFR with fast MTTR is healthy

**How to measure:**
```
CFR = (failed deployments) / (total deployments)

Example:
- Total deploys: 100
- Incidents caused: 15
- CFR: 15%

Failed deploy = causes incident, rollback, hotfix, or SLA miss
```

**For Leidos:**
- **Current state:** Likely 30-50% (big releases, harder to test)
- **Ideal state:** <20%
- **Improvement:** Better testing (unit, integration, staging), automated checks, smaller changes

### 4. Mean Time to Recover

**Definition:** How fast do we fix issues when they happen?

**Why it matters:**
- If you deploy frequently + have failures, you need fast recovery
- Defense systems: Recovery is critical (mission-critical uptime)
- Shows resilience and incident response maturity

**How to measure:**
```
MTTR = (resolution time - incident detection time)

Example:
- Incident detected: 2:00 PM
- Fixed and deployed: 2:45 PM
- MTTR: 45 minutes

Track: Average, P95, P99
```

**For Leidos:**
- **Current state:** Likely 4-24 hours (manual processes, approvals)
- **Ideal state:** <2 hours
- **Improvement:** Automation, runbooks, monitoring, on-call culture

---

## Learning Objectives

By the end of this training, you will:

✅ Understand what DORA metrics are and why they matter  
✅ Know how to measure each metric  
✅ Identify where Leidos currently stands  
✅ Set realistic improvement targets  
✅ Avoid common implementation mistakes  
✅ Create action plan to improve each metric  
✅ Track progress and communicate to leadership  
✅ Use DORA alongside RFC process  

---

## Weekly Curriculum

### Week 1: Foundations (5-7 hours)

**Goal:** Understand DORA, why it matters, and how to measure.

#### Day 1-2: DORA Overview (2 hours)
- **Watch/Read:**
  - Dora.dev guide: https://dora.dev/guides/dora-metrics/
  - Google Cloud blog: https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance
  - Atlassian guide: https://www.atlassian.com/devops/frameworks/dora-metrics

- **Key Concepts:**
  - DORA emerged from 7 years of DevOps research
  - Measures both throughput (deployment frequency + lead time) and stability (failure rate + recovery)
  - Predictive: high DORA = better organizational outcomes
  - Not individual metrics: measure team performance, not personal performance

- **For Leidos:**
  - Defense industry culture: Stability often prioritized over speed
  - DORA shows you can have both: fast AND stable
  - Benchmarks exist for "High Performers"

#### Day 3-4: Measuring Each Metric (3 hours)

**Deployment Frequency:**
- Source: CI/CD system (Jenkins, GitHub Actions, GitLab CI)
- Query: "How many deployments to production in past 4 weeks?"
- Tracking: Count by week, track trend

**Lead Time for Changes:**
- Source: Git commits + CI/CD system
- Query: "From commit to production, what's the average/P95/P99 time?"
- Tracking: Sample 20 deploys, measure each, track trend

**Change Failure Rate:**
- Source: Incident tracking (Jira, PagerDuty, DataDog)
- Query: "Of our 50 deployments, how many caused incidents?"
- Definition: Caused incident, rollback, hotfix, or SLA breach within 7 days
- Tracking: Tag deployments, track which caused incidents

**Mean Time to Recover:**
- Source: Incident management system
- Query: "When incidents happen, how long to fix/deploy?"
- Tracking: From detection to resolution, in hours

**For Leidos:**
- Current measurement: Manual or missing
- First step: Define what "deployment" means (to dev? staging? prod?)
- May need to retrofit data from logs/tickets

#### Day 5: DORA Maturity Model (2 hours)
- **Elite Performers (top 25%):**
  - Deploy on-demand (multiple times per day)
  - Lead time <1 hour
  - CFR 0-15%
  - MTTR <1 hour

- **High Performers (50-75%):**
  - Deploy weekly
  - Lead time <1 day
  - CFR 16-30%
  - MTTR 1 hour - 1 day

- **Medium (25-50%):**
  - Deploy monthly
  - Lead time 1 day - 1 week
  - CFR 31-45%
  - MTTR 1 day - 1 week

- **Low Performers (bottom 25%):**
  - Deploy quarterly or less
  - Lead time >1 month
  - CFR 46-60%
  - MTTR >1 week

- **For Leidos:** Likely Medium-to-Low. Goal: Move to High within 12 months.

---

### Week 2: Current State Assessment (4-6 hours)

**Goal:** Measure Leidos' current DORA metrics.

#### Day 1-2: Data Collection (3 hours)

**Exercise 1: Deployment Frequency**
1. Count Leidos deployments to production in past 4 weeks
2. Calculate per-week average
3. Compare to targets

**Exercise 2: Lead Time**
1. Pick 10 recent deployments
2. Find commit timestamp and deploy timestamp
3. Calculate average, P95, P99
4. Identify bottlenecks (approval wait? test time? merge time?)

**Exercise 3: Change Failure Rate**
1. Count total deployments in past 8 weeks
2. Count how many caused incidents/rollbacks
3. Calculate CFR
4. Identify pattern (what type of changes fail?)

**Exercise 4: Mean Time to Recover**
1. Find 5 recent production incidents
2. Time from detection to fix+deploy
3. Calculate average
4. Identify bottlenecks (detection? diagnosis? approval? deployment?)

**For Leidos:**
- Jira for issue tracking
- GitHub/GitLab for commits
- PagerDuty or Datadog for incidents
- Manual query or tool (Sumo Logic, Grafana)

#### Day 3: Analysis & Reporting (1.5 hours)
- **Create current state report:**
  ```
  LEIDOS DORA METRICS — March 29, 2026
  
  Deployment Frequency: 0.5 per week (every 2 weeks)
    Target: 2 per week (weekly)
    Gap: 4x too slow
  
  Lead Time: P50 = 14 days, P95 = 28 days
    Target: P50 < 1 day, P95 < 2 days
    Gap: Approval process + manual testing blocking
  
  Change Failure Rate: 35%
    Target: <20%
    Gap: Insufficient testing, large changes
  
  MTTR: P50 = 6 hours
    Target: <2 hours
    Gap: Manual incident response, slow approval
  ```

#### Day 4-5: Root Cause Analysis (2 hours)
- **For each gap, ask "why 5 times":**
  ```
  Lead Time is 14 days (target: <1 day)
  
  Why 1: Manual testing and approval process takes 10 days
    Why 2: No automated testing infrastructure
      Why 3: Compliance requires human review
        Why 4: Fear of mistakes on mission-critical system
          Why 5: (root) Lack of confidence in automation
  
  Action: Invest in automated testing + validation
  ```

---

### Week 3: Improvement Planning (5-7 hours)

**Goal:** Create action plan to improve each metric.

#### Day 1-2: Improvement Levers (2 hours)
- **Deployment Frequency:**
  - Lever 1: Automate testing (CI/CD pipeline)
  - Lever 2: Reduce batch size (deploy smaller changes)
  - Lever 3: Parallel workflows (don't wait for approvals serially)
  - Lever 4: Approval automation (policy as code)

- **Lead Time:**
  - Lever 1: Reduce code review time (2-day review → same-day)
  - Lever 2: Automate testing (run tests in parallel, not serially)
  - Lever 3: Staging automation (deploy to staging automatically)
  - Lever 4: Smaller PRs (easier to review + deploy)

- **Change Failure Rate:**
  - Lever 1: Better testing (unit + integration + staging + load tests)
  - Lever 2: Canary deployments (deploy to 1% first, monitor)
  - Lever 3: Smaller changes (easier to test, lower risk)
  - Lever 4: Feature flags (deploy code but don't enable feature)

- **Mean Time to Recover:**
  - Lever 1: Better monitoring + alerts (detect faster)
  - Lever 2: Runbooks (know exactly what to do)
  - Lever 3: Automated rollback (detect + rollback in 5 minutes)
  - Lever 4: On-call culture (expert available, not blocked by approvals)

- **For Leidos:** Defense/compliance likely constrains some levers. Work within constraints.

#### Day 3-4: Create Action Plan (2 hours)
- **Template:**
  ```
  GOAL: Improve Deployment Frequency from 0.5/week to 2/week within 6 months
  
  Month 1 (April):
    - Implement automated unit tests in CI/CD
    - Goal: Catch 50% of bugs automatically
    - Owner: @Engineer1
    - Success: 80% test coverage, <5 min test time
  
  Month 2 (May):
    - Implement staging automation
    - Goal: Automatically deploy to staging after PR approval
    - Owner: @Engineer2
    - Success: All PRs auto-stage, catch integration issues early
  
  Month 3 (June):
    - Implement feature flags
    - Goal: Deploy code without enabling features
    - Owner: @Engineer1
    - Success: 10 feature flags in use, can disable any feature without redeploy
  
  Month 4-6 (July-Sept):
    - Parallel approval process
    - Smaller batch deployments
    - Measure: 2 deployments/week
  ```

#### Day 5: Measurement Dashboard (1.5 hours)
- **What to track:**
  - Weekly graph of each metric (trend)
  - Comparison to target (are we improving?)
  - Incidents caused by changes (CFR tracking)
  - Alert time (how fast we detect)

- **Tools:**
  - GitHub Insights (built-in)
  - Grafana (open source)
  - Datadog (commercial)
  - Sumo Logic (commercial)
  - Even Google Sheets (low-tech but works)

- **For Leidos:**
  - Recommend: Start with manual tracking (Google Sheets)
  - Automate later (GitLab CI has built-in DORA)
  - Share weekly in team meeting

---

### Week 4: Implementation & Mistakes (4-6 hours)

**Goal:** Implement improvements, avoid common mistakes.

#### Day 1-2: Implementation Roadmap (2 hours)
- **Phased approach:**
  - Phase 1 (Month 1): Quick wins (better alerts, runbook automation)
  - Phase 2 (Month 2-3): Medium effort (CI/CD improvements, staging automation)
  - Phase 3 (Month 4-6): Major changes (feature flags, approval process redesign)

- **For Leidos:**
  - Compliance constraints likely require phase-by-phase review
  - Work with security/compliance early
  - Document approval changes

#### Day 3: Common Mistakes to Avoid (2 hours)
- **Read:**
  - Aviator: "Everything Wrong with DORA Metrics"
  - Swarmia: "Your Practical Guide to DORA Metrics"
  - NewRelic: "DORA Metrics Common Misconceptions"
  - Techtarget: "Google Warns Against DORA Misuse"

- **Top Mistakes:**

| Mistake | Why It Fails | Fix |
|---------|-------------|-----|
| **Using for individual performance** | Kills culture, people hide failures | Measure teams, not individuals |
| **No baseline** | Can't track improvement | Measure current state first |
| **Unrealistic targets** | "Elite in 3 months" → demoralization | Incremental improvement (quarterly goals) |
| **Don't analyze together** | "Deploy fast but 50% failures" = not helpful | Look at all 4 together: speed AND stability |
| **Missing data** | Can't measure if you don't track | Define deployment, incident, recovery |
| **Tool obsession** | Spend time on tools not improvement | Start manual (Google Sheets), automate later |
| **No follow-up** | Measure once, forget about it | Weekly tracking + monthly review |
| **Ignore context** | "Why are we deploying weekly?" → pushback | Explain why metrics matter, how they help |
| **Compliance excuse** | "We can't improve DORA, compliance requires..." | Challenge assumption, find compliance-friendly way |
| **Only focus on speed** | 100 deploys/day with 80% failures = bad | Balance: speed AND stability |

#### Day 4-5: Common Pitfalls for Defense (2 hours)
- **Leidos-specific challenges:**

| Challenge | How to Address |
|-----------|---|
| **Quarterly release cycles mandated** | Propose rolling releases (deploy features incrementally within quarter) |
| **Heavy compliance review** | Parallel reviews + automated policy checks reduce review time |
| **Manual testing required** | Automated testing + manual review (run in parallel) |
| **Approval delays** | Approval automation: if policy passes, auto-approve |
| **Mission-critical system** | Feature flags allow fast deployment + safe rollback |
| **Multiple vendors** | Define interfaces, test independently, compose at integration |

---

## Reading Materials

### Essential Reading (Must Read)

1. **DORA Metrics Guide** (40 min)
   - URL: https://dora.dev/guides/dora-metrics/
   - Key: How to measure each metric
   - For Leidos: Official definition and guidance

2. **Atlassian - DORA Metrics** (35 min)
   - URL: https://www.atlassian.com/devops/frameworks/dora-metrics
   - Key: Practical implementation and analysis
   - For Leidos: How to improve in practice

3. **Google Cloud Blog - Four Keys** (30 min)
   - URL: https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance
   - Key: Original Google research
   - Historical context and validation

### Background Reading (Recommended)

4. **Swarmia - Practical Guide to DORA** (45 min)
   - URL: https://www.swarmia.com/blog/dora-metrics/
   - Key: Common mistakes, how to avoid them
   - For Leidos: Anticipate problems

5. **NewRelic - DORA for DevOps Teams** (40 min)
   - URL: https://newrelic.com/blog/observability/dora-metrics
   - Key: Comprehensive guide with examples
   - For Leidos: Detailed measurement walkthrough

6. **LaunchDarkly - DORA Metrics Explained** (30 min)
   - URL: https://launchdarkly.com/blog/dora-metrics/
   - Key: Simple explanation + feature flag strategy
   - Feature flags = critical for defense deployments

7. **Octopus Deploy - 4 DORA Metrics** (35 min)
   - URL: https://octopus.com/devops/metrics/dora-metrics/
   - Key: Throughput vs Stability breakdown
   - For Leidos: Visual charts and examples

### Advanced Reading (Optional)

8. **Aviator - Everything Wrong with DORA** (45 min)
   - URL: https://www.aviator.co/blog/everything-wrong-with-dora-metrics/
   - Counterpoint: limitations and misuse
   - For Leidos: Realistic expectations

9. **Google - Against Metrics Misuse** (40 min)
   - URL: https://www.techtarget.com/searchsoftwarequality/news/366555052/Googles-DORA-DevOps-report-warns-against-metrics-misuse
   - Key: Google's own warnings about misuse
   - For Leidos: Don't do this!

10. **Gitmore - DORA Metrics 2026 Guide** (35 min)
    - URL: https://gitmore.io/blog/dora-metrics-guide
    - Key: 2026 benchmarks and best practices
    - For Leidos: Latest research and recommendations

---

## Mistakes to Avoid

### 🔴 Critical Mistakes (Will Harm Culture)

**1. Using DORA for Individual Performance Evaluation**
- Problem: "Engineer X has low deployment frequency, fire them"
- Reality: Individual metrics don't show full picture
- Fix: Measure teams, optimize processes
- For Leidos: Leadership must understand this is team metric

**2. Chasing Metrics Without Understanding Context**
- Problem: "100 deploys per day!" (but 90% are failed rollbacks)
- Reality: Speed without stability is chaos
- Fix: Always look at all 4 metrics together
- For Leidos: "We deploy weekly but stable" > "Daily but fragile"

**3. No Baseline**
- Problem: "Deployment frequency is high" — compared to what?
- Reality: Can't track improvement without starting point
- Fix: Measure current state first
- For Leidos: "We're at 0.5/week, goal is 2/week within 12 months"

**4. Blaming Compliance for Not Improving**
- Problem: "Compliance requires quarterly releases, nothing we can do"
- Reality: Compliance constrains release, not development
- Fix: Deploy features to staging weekly, release to prod quarterly
- For Leidos: Rolling release within quarterly cycle

### 🟡 Common Mistakes (Will Reduce Effectiveness)

**5. Not Analyzing Root Causes**
- Problem: "Lead time is 2 weeks" — that's all
- Reality: Need to understand why
- Fix: Dig deeper: is it code review? testing? approval? merge conflicts?
- For Leidos: Different bottleneck = different solution

**6. Unrealistic Improvement Targets**
- Problem: "We're at 0.5/week, let's go to 10/week in 3 months"
- Reality: Demoralization when target missed
- Fix: Incremental: month 1 = 0.5 → 1/week, month 2 = 1 → 1.5/week
- For Leidos: Conservative + achievable = better

**7. Tool Obsession**
- Problem: Spend 3 months picking tool, haven't measured yet
- Reality: Google Sheets works fine for tracking
- Fix: Use built-in tools (GitHub, GitLab, Jira)
- For Leidos: Don't buy new tool, use what you have

**8. Not Including Stakeholders in Improvement**
- Problem: "We're improving DORA metrics" but compliance/leadership unaware
- Reality: Changes may require their approval
- Fix: Plan improvements with compliance/security/leadership
- For Leidos: Especially important for defense industry

**9. Measuring Wrong Thing**
- Problem: "Deployment frequency" = number of files changed (not deploys)
- Reality: Definition ambiguity
- Fix: Define: "deployment = production release to live customers"
- For Leidos: Define "production" (staging? dev? live customers?)

**10. Not Tracking Over Time**
- Problem: Measure once, declare victory
- Reality: Metrics regress without attention
- Fix: Weekly dashboard, monthly review
- For Leidos: Quarterly leadership report on progress

### 🟢 Minor Mistakes (Learn from them)

**11. Ignoring Failure Rate in Speed Push**
- Problem: "Deploy faster!" results in 60% failures
- Reality: Fast + broken = not helpful
- Fix: Balance: CFR <20% AND acceptable lead time

**12. Not Explaining Why DORA Matters**
- Problem: "We must improve DORA" — engineers don't understand why
- Reality: No buy-in
- Fix: Explain: faster feedback = happier customers, more time for innovation

**13. Missing Dependencies**
- Problem: "Let's improve lead time" but testing infrastructure is bottleneck
- Reality: Improvement blocked on infrastructure
- Fix: Identify and resolve dependencies first

**14. No Communication**
- Problem: DORA dashboard exists, nobody knows about it
- Reality: No visibility, no accountability
- Fix: Weekly team sync showing progress

**15. Compliance Exceptions**
- Problem: "This change needs manual review because compliance" (not flagged)
- Reality: Can't automate if not tagged
- Fix: Tag deployment reason (policy, manual review, etc.)

---

## Implementation Guide

### For Leidos: DORA Rollout (3 Months)

#### Month 1: Baseline & Measurement
1. **Week 1-2:** Collect current metrics (deployment frequency, lead time, CFR, MTTR)
2. **Week 3:** Analyze root causes
3. **Week 4:** Create measurement dashboard (start simple: Google Sheet)

**Deliverable:** "Current State Report" with baseline metrics

#### Month 2: Quick Wins & Planning
1. **Week 1:** Improve monitoring/alerts (faster incident detection)
2. **Week 2:** Create runbooks (faster incident response)
3. **Week 3:** Begin CI/CD automation (unit tests, automated checks)
4. **Week 4:** Create 6-month improvement roadmap with leadership

**Deliverable:** First metrics improvement, roadmap approved

#### Month 3: Major Improvements
1. **Week 1-2:** Staging automation
2. **Week 3:** Feature flags implementation
3. **Week 4:** Parallel approval process pilot

**Deliverable:** Evidence of improvement in all 4 metrics

### DORA Measurement Template for Leidos

**Weekly Tracking (Google Sheets):**

```
Week of March 24, 2026

DEPLOYMENT FREQUENCY:
- Total production deployments: 2
- Target: 2/week
- Status: ✅ On target

LEAD TIME (P50):
- Average time from commit to deploy: 7 days
- Target: 2 days
- Status: ⚠️ Off target (3.5x too slow)
- Bottleneck: Compliance review (5 days) + testing (2 days)

CHANGE FAILURE RATE:
- Total deployments: 10 (past 2 weeks)
- Failures: 2 (incident + rollback)
- CFR: 20%
- Target: <20%
- Status: ✅ Acceptable

MEAN TIME TO RECOVER:
- Avg time to fix incident: 4 hours
- Target: <2 hours
- Status: ⚠️ Slower than target
- Bottleneck: Approval process (need urgent change approval)

NOTES:
- Started automated testing in CI/CD
- Compliance approved faster review for non-critical components
- Next week: Feature flags for safe deployments
```

### Leidos-Specific Implementation

#### Challenge: Compliance Review
**Problem:** Compliance takes 5+ days, blocks deployment

**Solution Option 1:** Parallel review
- Code review: 2 days (engineers)
- Compliance review: 2 days (parallel, not serial)
- Total: 2 days (vs 4 days serial)

**Solution Option 2:** Approval automation
- Automated policy checks (does change meet compliance?)
- Auto-approve if passes policy
- Manual review only if needed

**Solution Option 3:** Feature flags
- Deploy to staging with feature flag OFF
- Compliance reviews code (already in prod, disabled)
- Enable flag after compliance approval

#### Challenge: Manual Testing
**Problem:** Manual QA takes 3+ days

**Solution:** Automated testing
- Unit tests (run in 5 min)
- Integration tests (run in 15 min)
- Staging deployment (run in 10 min)
- Manual tests only for complex scenarios (parallel with above)
- Reduce manual testing from 3 days to 2 hours

---

## DORA + RFC Integration

### How DORA and RFC Work Together

**RFC:** Defines architectural decisions (what we're building)  
**DORA:** Measures how fast and safely we deliver decisions

**Example: Migration to Kubernetes**

1. **RFC-001:** "Migrate to Kubernetes" (proposes the decision)
   - Discussion: pros/cons, timeline, risks
   - Approval: team agrees this is the right direction

2. **DORA Tracking:** Measure during implementation
   - Deployment frequency: Can we deploy Kubernetes changes weekly?
   - Lead time: How long from PR to production?
   - CFR: Are Kubernetes deployments reliable?
   - MTTR: Can we recover from Kubernetes incidents fast?

3. **Post-Implementation:** Review RFC success
   - RFC-001 Follow-Up: "Kubernetes implementation results"
   - DORA metrics improved? (weekly deploy now possible)
   - Worth the effort? (yes/no)

### Team Cadence

- **Weekly:** DORA dashboard review (5 min) — tracking progress
- **Monthly:** RFC + DORA planning meeting (1 hour) — what to improve next
- **Quarterly:** Leadership review (30 min) — org-level progress report

---

## Success Criteria

Track these over 6 months:

| Metric | Current | 3-Month Target | 6-Month Target |
|--------|---------|----------------|----------------|
| **Deployment Frequency** | 0.5/week | 1/week | 2/week |
| **Lead Time P50** | 14 days | 7 days | 2 days |
| **Change Failure Rate** | 35% | 25% | <20% |
| **MTTR** | 6 hours | 3 hours | 1 hour |
| **Team Morale** | Survey baseline | 10% improvement | 20% improvement |
| **Incident on-call time** | 4 hours/week | 2 hours/week | 1 hour/week |

---

## Next Steps

1. **Measure current state** (Week 1)
   - Collect deployment, lead time, failure, recovery data
   - Create baseline report

2. **Identify top bottleneck** (Week 2)
   - Root cause analysis
   - Pick one thing to improve

3. **Plan improvement** (Week 3)
   - Create 6-month roadmap
   - Get leadership approval

4. **Implement** (Month 2+)
   - Execute improvements
   - Track weekly progress
   - Iterate

---

## Questions?

- DORA is a tool, not dogma
- Adapt to Leidos culture and constraints
- Defense industry can still improve DORA
- Start small, iterate, celebrate progress
- Goal: Faster + more stable + happier team

Good luck! 🍑

