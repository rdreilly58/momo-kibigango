# RFC (Request for Comments) Training Plan for Leidos

**Prepared for:** Robert Reilly, Team Lead - Principal Software Engineer  
**Date:** March 29, 2026  
**Duration:** 2-4 weeks (self-paced)  
**Level:** Executive/Leadership

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Learning Objectives](#learning-objectives)
3. [Weekly Curriculum](#weekly-curriculum)
4. [Reading Materials](#reading-materials)
5. [Mistakes to Avoid](#mistakes-to-avoid)
6. [Implementation Guide](#implementation-guide)
7. [Team Rollout Strategy](#team-rollout-strategy)

---

## Overview

### What is RFC?

RFC (Request for Comments) is a **structured documentation and decision-making process** used in engineering teams to:

- **Propose** significant technical or organizational changes
- **Gather feedback** from stakeholders before implementation
- **Build consensus** across teams
- **Create permanent records** of architectural decisions
- **Improve communication** in growing organizations

### Why RFC for Leidos?

As a **Team Lead at a defense contractor**, RFC is critical because:

1. **Cross-functional coordination** — Multiple teams, vendors, compliance needs
2. **Decision traceability** — Regulatory and audit requirements
3. **Risk mitigation** — Major decisions documented and reviewed
4. **Scaled communication** — Clear expectations across distributed teams
5. **Knowledge preservation** — Decisions documented for future teams

### Key Difference: RFC vs Design Docs

| Aspect | RFC | Design Doc |
|--------|-----|-----------|
| Scope | Organization-wide | Project/feature level |
| Audience | All stakeholders | Core team + reviewers |
| Timeline | 1-4 weeks discussion | 1-2 weeks |
| Approval | Consensus/decision | Team agreement |
| Visibility | Public/shared | Team-internal |

**For Leidos:** Use RFC for strategic decisions, use Design Docs for implementation details.

---

## Learning Objectives

By the end of this training, you will:

✅ Understand when to write an RFC  
✅ Master the RFC structure and format  
✅ Know how to solicit meaningful feedback  
✅ Manage the RFC lifecycle (draft → discussion → approved → implemented)  
✅ Avoid common pitfalls that derail RFCs  
✅ Build a healthy RFC culture in your team  
✅ Implement RFC process at Leidos  

---

## Weekly Curriculum

### Week 1: Foundations (5-7 hours)

**Goal:** Understand RFC purpose, benefits, and when to use it.

#### Day 1-2: RFC Origins & Purpose (2 hours)
- **Read:** 
  - RFC history: https://en.wikipedia.org/wiki/Request_for_Comments
  - IETF RFC process: https://www.ietf.org/process/rfcs/
  - Why RFC matters: Candost's "How and Why RFCs Fail"

- **Key Takeaways:**
  - RFC originated with IETF in 1969 — 50+ years of proven effectiveness
  - "Request for Comments" doesn't mean feedback is optional — decisions must be made
  - RFC is a *decision-making process*, not just documentation
  - Bad RFC culture → abandoned process → wasted time

#### Day 3-4: When to Write an RFC (2 hours)
- **Scenarios where RFC is essential:**
  - ✅ Major architectural changes (>2 weeks dev time)
  - ✅ Changes affecting multiple teams
  - ✅ Technology stack changes (languages, frameworks, DBs)
  - ✅ Organizational/process changes (deployment, on-call, planning)
  - ✅ Security or compliance decisions
  - ✅ Major refactoring or deprecations

- **Scenarios where RFC is overkill:**
  - ❌ Small bug fixes or routine features
  - ❌ Changes only affecting one person
  - ❌ Obvious improvements with zero controversy
  - ❌ Urgent incident responses (post-incident: use RFC to prevent recurrence)

- **Decision Tree:**
  ```
  Is this decision reversible in <1 day?
    → NO: Consider RFC
  Does this affect >1 team?
    → YES: Definitely RFC
  Could this cause major outage if wrong?
    → YES: RFC is mandatory
  Is team alignment unclear?
    → YES: RFC builds alignment
  ```

#### Day 5: RFC Culture (3 hours)
- **Read:**
  - LeadDev: "A Thorough Team Guide to RFCs"
  - Medium: "A Thorough Team Guide to RFCs"
  - Candost blog: "How and Why RFCs Fail"

- **Critical Success Factors:**
  1. **Trust** — Must be blameless culture, no politics
  2. **Psychological safety** — People must feel safe proposing ideas AND criticizing
  3. **Good faith** — Assume everyone wants best outcome
  4. **Time investment** — Must allocate real time to review and discussion
  5. **Clear decision-making** — Not just consensus, but clear final decision

- **Red Flags (RFC will fail if):**
  - ❌ Organization doesn't trust each other
  - ❌ Politics/fiefdoms create fear of feedback
  - ❌ No clear decision-maker (endless discussion)
  - ❌ Senior engineers dismiss junior feedback
  - ❌ No time allocated for review

---

### Week 2: RFC Structure & Writing (6-8 hours)

**Goal:** Learn the RFC template, write your first draft RFC.

#### Day 1-2: RFC Template (2 hours)
- **Standard RFC Sections:**

```markdown
# RFC-NNN: Title of Decision

## Summary
1-paragraph executive summary. What's being proposed?

## Motivation
Why are we doing this? What problem does it solve?
- Current state/pain points
- Impact if we don't act
- Opportunity/benefit

## Proposed Solution
What exactly are we proposing?
- High-level approach
- Key components
- How it works

## Alternatives Considered
What other options were evaluated?
- Alternative A: pros/cons
- Alternative B: pros/cons
- Alternative C: pros/cons
- Why chosen solution wins

## Implementation Plan
How will we execute?
- Phase 1: ...
- Phase 2: ...
- Timeline
- Resource requirements
- Success criteria

## Risks & Mitigations
What could go wrong?
- Risk 1: mitigation
- Risk 2: mitigation
- Failure scenarios

## Tradeoffs
What are we giving up?
- Performance vs maintainability
- Cost vs capability
- Speed vs quality

## Success Metrics
How will we know this worked?
- KPI 1
- KPI 2
- Measurement method

## Decision & Timeline
- Decision deadline
- Who makes final decision
- Current status (DRAFT → DISCUSSION → APPROVED → IMPLEMENTED)
```

- **Examples to read:**
  - Sourcegraph RFC examples
  - Uber RFC process
  - Google Design Docs

#### Day 3-4: Writing Your First RFC (3 hours)
- **Exercise:** Pick a recent decision and write it as an RFC
  - For Leidos: "Standardize on Language X for new projects"
  - For Leidos: "Implement RFC process for Airborne team"
  - For Leidos: "Move to microservices for Mission Control component"

- **Checklist:**
  - [ ] Summary is 1 paragraph (not 3)
  - [ ] Motivation is personal and concrete (not vague)
  - [ ] Alternatives section has ≥2 real alternatives
  - [ ] Risks section has ≥3 realistic risks
  - [ ] Success metrics are measurable
  - [ ] No jargon or acronyms without definition
  - [ ] Tone is collaborative, not dictatorial

- **Writing Tips:**
  - Write for a **skeptical reader** — convince them
  - Use **concrete examples** not abstract language
  - **Be honest about tradeoffs** — no solution is perfect
  - **Show your work** — why you rejected other options
  - **Anticipate objections** and address them upfront

#### Day 5: Formatting & Publishing (1 hour)
- **Tools:**
  - Google Docs (easy collaboration)
  - GitHub wiki (version control)
  - Confluence (team knowledge base)
  - GitBook (professional publishing)

- **For Leidos:** 
  - **Recommendation:** GitHub org for decision records
  - Use Markdown for version control
  - Branch: `rfc/number-title`
  - Versioning: RFC-001, RFC-002, etc.

- **Metadata to include:**
  - Authors
  - Date created
  - Status (DRAFT → DISCUSSION → APPROVED → IMPLEMENTED → DEPRECATED)
  - Review deadline
  - Decision maker(s)

---

### Week 3: RFC Discussion & Decision (5-7 hours)

**Goal:** Master the review process, handle feedback, make decisions.

#### Day 1-2: Soliciting Feedback (2 hours)
- **Who to include:**
  - Direct team members (required)
  - Affected teams (required)
  - Subject matter experts (required)
  - Cross-functional (product, security, infra)
  - Skeptics and contrarians (essential!)

- **How to ask for feedback:**
  - **DON'T:** "Here's my decision, feedback welcome"
  - **DO:** "I'm uncertain about X, need your expertise on Y"
  - **DON'T:** "Anyone have thoughts?"
  - **DO:** "@Alice, what's the security impact? @Bob, can we do this in 2 weeks?"

- **Review timeline:**
  - Draft period: 2-3 days (author refines)
  - Discussion period: 1-2 weeks (team reviews)
  - Decision: by explicit date (not "whenever")

- **Red flags in feedback:**
  - Feedback with no reasoning → ask "why?"
  - Feedback attacking author → address in team norms
  - "I'm not sure" without concrete concerns → dig deeper
  - Late feedback after deadline → decide how to handle

#### Day 3-4: Handling Feedback (2 hours)
- **Feedback types & responses:**

| Feedback Type | Response | Example |
|---------------|----------|---------|
| **Clarification** | Answer directly | "What's the cost?" → Calculate & share |
| **Minor concern** | Acknowledge & incorporate | "Typo on page 3" → Fix it |
| **Major concern** | Address in RFC or async | "Security issue!" → Call meeting |
| **Alternative idea** | Discuss in alternatives section | "Use tool B instead?" → Analyze together |
| **Approval** | Record in RFC status | "Looks good!" → Note who approved |
| **Disagreement** | Acknowledge, explain decision | "I think this is wrong" → Discuss trade-offs |

- **How to update RFC based on feedback:**
  - Keep change history (don't erase feedback)
  - Add "Updates" section noting feedback incorporated
  - If major changes: extend discussion deadline
  - Transparency: "After discussion, decided to..."

- **How to handle unresolvable disagreement:**
  - RFC is NOT about unanimous agreement
  - Goal: Best decision with informed team
  - Document dissenting view (record "I disagree because...")
  - Decision maker has final say
  - Commitment: "Even if you disagree, will you support this?"

#### Day 5: Making the Decision (1 hour)
- **Good decision-making:**
  - [ ] Have ≥2 weeks of discussion
  - [ ] All major concerns raised & documented
  - [ ] Alternatives clearly evaluated
  - [ ] Risks understood
  - [ ] Clear decision-maker identified
  - [ ] Implementation plan realistic

- **Mark RFC status:**
  - **APPROVED:** Ready to implement
  - **DEFERRED:** Good idea, wrong timing
  - **REJECTED:** Decision made, not moving forward
  - **SUPERSEDED:** Replaced by RFC-NNN

- **Communicate decision:**
  - Email summarizing decision
  - Link to final RFC
  - Thank reviewers explicitly
  - Next steps: who implements, timeline
  - Schedule post-mortem if implementation needed

---

### Week 4: Implementation & Mistakes (4-6 hours)

**Goal:** Track implementation, learn from mistakes, build healthy RFC culture.

#### Day 1-2: Tracking Implementation (2 hours)
- **After approval:**
  - Create tracking ticket (Jira, GitHub Issues)
  - Link to RFC
  - Update RFC with status quarterly
  - Track key metrics from RFC success criteria
  - Report back to team: "RFC-005 implementation: on track, 80% complete"

- **For Leidos:**
  - JIRA link in RFC
  - Status updates monthly
  - Post-implementation review at 6 months
  - Document lessons learned

#### Day 3: Common Mistakes to Avoid (2 hours)
- **Read:** 
  - Candost: "How and Why RFCs Fail"
  - Jacobian: "RFC processes are a poor fit"
  - Aviator: "Everything Wrong with DORA Metrics" (similar failure patterns)

- **Top 10 RFC Mistakes:**

| Mistake | Why It Fails | Fix |
|---------|-------------|-----|
| **No decision maker** | Endless discussion | Name explicit approver |
| **Too vague scope** | Unclear what's being decided | Be specific: "Deploy to Kubernetes" not "Infrastructure changes" |
| **Author decides first** | RFC feels like notification | Genuinely seek input, keep options open |
| **No deadline** | Discussion drifts | "Decision by March 29" |
| **Ignore dissent** | Lose trust, poor decision | Address concerns in writing, even if disagree |
| **Tool-obsessed** | Spend time on tool not content | Pick GitHub/Docs/Confluence, move on |
| **No follow-up** | Nobody knows if it worked | Report back at 6 months |
| **Too rigid** | Can't adapt | Build flexibility into "Implementation" section |
| **Exclude stakeholders** | Surprise people at execution | Include affected teams in review |
| **Perfect docs** | Analysis paralysis | Good enough now, refine during implementation |

#### Day 4-5: Building RFC Culture (2 hours)
- **How to introduce RFC at Leidos:**
  - Start with 1-2 team pilots
  - Write first RFC as team (collaborative)
  - Celebrate good RFCs and feedback
  - Iterate on process
  - Document Leidos RFC guidelines (in GitHub)

- **Culture practices:**
  - Monthly "RFC review" meeting (15 min)
  - Recognize great feedback givers
  - Learn from implementation (post-mortems)
  - Keep feedback respectful (code of conduct)

---

## Reading Materials

### Essential Reading (Must Read)

1. **Candost - How and Why RFCs Fail** (30 min)
   - URL: https://candost.blog/how-and-why-rfcs-fail/
   - Key insight: RFC requires trust and clear decision-making
   - For Leidos: Understand prerequisites

2. **LeadDev - A Thorough Team Guide to RFCs** (45 min)
   - URL: https://leaddev.com/software-quality/thorough-team-guide-rfcs
   - Key insight: When to write, how to solicit feedback, building culture
   - For Leidos: Framework for team introduction

3. **Pragmatic Engineer - Scaling Engineering Teams via Writing** (30 min)
   - URL: https://blog.pragmaticengineer.com/scaling-engineering-teams-via-writing-things-down-rfcs/
   - Key insight: RFC is scaling tool for large orgs
   - For Leidos: Why this matters now

### Background Reading (Recommended)

4. **IETF RFC Overview** (20 min)
   - URL: https://www.ietf.org/process/rfcs/
   - Context: Original RFC from 1969
   - Historical perspective

5. **Wikipedia - Request for Comments** (15 min)
   - URL: https://en.wikipedia.org/wiki/Request_for_Comments
   - Standards track, experimental, informational
   - Historical evolution

6. **Fuchsia - RFC Best Practices** (20 min)
   - URL: https://fuchsia.dev/fuchsia-src/contribute/governance/rfcs/best_practices
   - Concrete tips: stable links, versioning, templates
   - Implementation guide

### Advanced Reading (Optional)

7. **Jacobian - RFCs are a poor fit for most orgs** (45 min)
   - URL: https://jacobian.org/2023/dec/1/against-rfcs/
   - Counterpoint: when RFC fails
   - For Leidos: Anticipate challenges

8. **Slab - RFC Library** (20 min)
   - URL: https://slab.com/library/rfcs/
   - Templates and examples
   - Tool overview

9. **Google Engineering Practices** (60 min)
   - URL: https://google.github.io/eng-practices/
   - Design docs at scale
   - Code review practices

### Practical Examples (Study)

- **Sourcegraph RFCs:** https://github.com/sourcegraph/rfcs
- **Uber RFC Process:** https://www.uber.com/en-US/blog/... (look for RFC posts)
- **Real RFC examples:** Search GitHub for "RFC-" in organization repos

---

## Mistakes to Avoid

### 🔴 Critical Mistakes (Will Kill RFC Process)

**1. No Clear Decision-Maker**
- Problem: Endless discussion, no closure
- Fix: Name explicit approver: "CEO approves", "Tech lead approves"
- For Leidos: "Division Chief approves" or "Principal Engineer final say"

**2. RFC as Notification, Not Discussion**
- Problem: Author says "here's my plan, any objections?"
- Fix: Genuinely uncertain sections: "I'm unsure about X, help me decide"
- For Leidos: Especially important for junior engineers to speak up

**3. No Timeline / Endless Discussion**
- Problem: Discussion drifts for months, opportunity passes
- Fix: "Decision by April 15" — firm deadline
- For Leidos: Important for fast-moving project cycles

**4. Ignoring Dissent**
- Problem: Senior person proposes, junior people quiet, wrong decision
- Fix: Explicitly ask skeptics, document their concerns
- For Leidos: Defense industry needs thorough risk assessment

**5. Too Vague / Not Actionable**
- Problem: "We should improve deployment" — too broad
- Fix: "Migrate from manual deploy to Jenkins CI/CD by June 30"
- For Leidos: Specificity is compliance requirement

### 🟡 Common Mistakes (Will Reduce Effectiveness)

**6. Author Didn't Consider Alternatives**
- Problem: "Here's solution A" with no B or C
- Fix: Research ≥2 alternatives, explain why not chosen
- Example: "Considered Kubernetes, Docker Swarm, manual Ansible — chose K8s because..."

**7. Feedback Ignored / Not Incorporated**
- Problem: Feedback given, author doesn't respond
- Fix: Update RFC with changes, explain reasoning
- For Leidos: Stakeholders will feel heard or dismissed

**8. Success Metrics Missing**
- Problem: After implementation, nobody knows if it worked
- Fix: "We'll measure: deployment frequency, change lead time, incident rate"
- For Leidos: Critical for DORA metrics integration

**9. No Implementation Plan**
- Problem: "Yes, approved. Now what?"
- Fix: Phase 1, Phase 2, owners, timeline, dependencies
- For Leidos: Defense contracts require detailed planning

**10. Tool Obsession**
- Problem: Hours debating GitHub vs Confluence vs Docs
- Fix: Pick one, use it, iterate later
- For Leidos: GitHub is recommended (version control)

### 🟢 Minor Mistakes (Learn from them)

**11. Scope Creep During Discussion**
- Problem: Discussion expands into 5 decisions instead of 1
- Fix: "That's great, let's capture for RFC-006"
- Create new RFC for related but separate decision

**12. Feedback with No Reasoning**
- Problem: "I disagree" with no explanation
- Fix: "I disagree because X, Y, Z"
- Push back: "Can you help me understand why?"

**13. No Follow-Up After Approval**
- Problem: RFC approved, implemented, nobody reports back
- Fix: "3-month implementation report due"
- For Leidos: Track metrics, learn, improve process

**14. Perfect Documentation**
- Problem: RFC takes 3 weeks to finalize before sharing
- Fix: "Good enough now, refine during discussion"
- Move fast, feedback sharpens ideas

**15. Didn't Update RFC Based on Feedback**
- Problem: Discussion happens, RFC unchanged
- Fix: "Updated RFC with feedback from @Alice, @Bob"
- Document change history

---

## Implementation Guide

### For Leidos: Rolling Out RFC

#### Phase 1: Pilot (Week 1-2)
1. Pick your team (Airborne & Mission Solutions preferred)
2. Create RFC template (see below)
3. Write first RFC together (collaborative drafting)
4. Get feedback from peers and leadership
5. Document Leidos RFC process

#### Phase 2: Expand (Week 3-4)
1. Train other team leads on RFC
2. Set expectation: "All major decisions ≥ 1 week discussion"
3. Create GitHub org for RFCs (rdreilly58/leidos-rfc-decisions)
4. Link to project management (Jira)

#### Phase 3: Scale (Month 2+)
1. Monthly "RFC review" 15-min meeting
2. Celebrate good RFCs
3. Document lessons learned
4. Iterate on template

### RFC Template for Leidos

```markdown
# RFC-XXX: [Title]

**Status:** DRAFT | DISCUSSION | APPROVED | IMPLEMENTED | SUPERSEDED  
**Author:** [Your Name]  
**Date Created:** [Date]  
**Decision Deadline:** [Date — 1-2 weeks out]  
**Decision Maker:** [Name/Title]  
**Related Issues:** JIRA-123, JIRA-456  

## Summary

[1 paragraph: what, why, when. A VP could understand this.]

## Motivation

**Current State:**
- [Pain point 1]
- [Pain point 2]
- [Impact if unchanged]

**Opportunity:**
- [What we'd gain]
- [Why now]

## Proposed Solution

**High-Level:**
- [What we're doing]
- [How it works]
- [Key phases]

**Technical Details:**
- [If needed]

## Alternatives Considered

| Alternative | Pros | Cons | Why Not? |
|-------------|------|------|---------|
| A: ... | [pros] | [cons] | [decision] |
| B: ... | [pros] | [cons] | [decision] |
| Chosen: C | [pros] | [cons] | [reasons] |

## Implementation Plan

**Phase 1:** [Do X by date Y]  
**Phase 2:** [Do A by date B]  
**Timeline:** [Overall completion date]  
**Resources:** [People, budget, infrastructure]  
**Success Criteria:** [Measurable goals]  

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| [Risk 1] | [High/Med/Low] | [How we'll prevent/handle] |
| [Risk 2] | ... | ... |

## Tradeoffs

**Performance vs Simplicity:**  
- Chosen: Simplicity (trade: 10% slower, but +40% maintainability)

**Cost vs Capability:**  
- Chosen: Capability (trade: +$50K/year, but enables X revenue)

## Success Metrics

- KPI 1: [How we measure]
- KPI 2: [How we measure]
- Measurement method: [Tool/process]
- Review date: [6 months out]

## Questions & Feedback Needed

@[Person]: How does this affect [System]?  
@[Person]: Can we deliver in [Timeline]?  
All: Am I missing any risks?  

---

## Discussion Notes

[Feedback will be added here]

## Decision

**Status:** APPROVED  
**Decision Maker:** [Name]  
**Decided:** [Date]  
**Reasoning:** [Why this was chosen]  

Next Steps:  
- Owner: [Person]
- JIRA ticket: [Link]
- Kickoff: [Date]

## Implementation Status

[Updates as implementation progresses]
- Week 1: ✅ Started Phase 1
- Week 2: ✅ Completed X, hit issue Y, mitigating with Z
- etc.
```

---

## Team Rollout Strategy

### Week 1: Foundation
- [ ] Share this training plan with team
- [ ] Have team read "How and Why RFCs Fail" (30 min)
- [ ] Discuss: "When would RFC help us?"

### Week 2: Practice
- [ ] Pick recent decision to document as RFC
- [ ] Draft RFC together (1 hour)
- [ ] Get feedback from 3 people (async)
- [ ] Discuss feedback as team (30 min)
- [ ] Refine RFC

### Week 3: Implementation
- [ ] Create Leidos RFC GitHub repo
- [ ] Merge first RFC
- [ ] Set expectation for future RFCs
- [ ] Plan next 3 RFCs

### Ongoing
- [ ] Monthly RFC review (15 min)
- [ ] Track metrics: RFC count, approval time, implementation success
- [ ] Improve template based on feedback
- [ ] Share learnings with broader Leidos org

---

## Success Metrics for RFC Adoption

Track these over 3-6 months:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **RFC Count** | 1-2 per month | GitHub repo count |
| **Approval Time** | 1-2 weeks | Decision date - creation date |
| **Implementation Success** | >80% | RFC goals achieved vs planned |
| **Team Participation** | >60% of team gives feedback | RFC comments per RFC |
| **Culture Improvement** | Qualitative | Team survey on decision clarity |

---

## Next Steps

1. **Review this plan** (1 hour)
2. **Read essential materials** (Week 1-2)
3. **Pick first RFC topic** — "Leidos RFC Process" is good candidate!
4. **Draft RFC** (Week 2)
5. **Get team feedback** (Week 3)
6. **Launch with team** (Week 4)

---

## Questions?

- RFC is a tool, not dogma
- Adapt to Leidos culture
- Start small (1-2 RFCs)
- Iterate and improve
- Good luck! 🍑

