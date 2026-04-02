# DORA Metrics — Quick Reference for Leidos

## The 4 DORA Metrics
1. **Deployment Frequency** — How often we deploy to production (daily? monthly?)
2. **Lead Time for Changes** — Time from code commit to production (hours? months?)
3. **Change Failure Rate** — % of deployments causing incidents (0%? 50%?)
4. **Mean Time to Recover (MTTR)** — How fast we fix incidents (minutes? days?)

## Performance Levels
| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| Deploy Frequency | On-demand (multiple/day) | Weekly-Monthly | Monthly-Quarterly | >6 months |
| Lead Time | <1 hour | 1 day-1 week | 1 week-1 month | >1 month |
| Change Failure Rate | 0-5% | 5-10% | 10-15% | >15% |
| MTTR | <1 hour | <1 day | <1 week | >1 week |

## Why DORA at Leidos (Defense)
- Long release cycles (quarterly/annual) — DORA gives objective measurement
- Strict compliance & audit requirements
- Need to show measurable progress to leadership
- Predicts organizational performance

## Training Plan
- **Duration:** 2-4 weeks (self-paced)
- **Full plan:** `leidos/training/DORA_TRAINING_PLAN.md` (805 lines)
- **Week 1:** Learn the 4 metrics + definitions
- **Week 2:** Baseline current team performance
- **Week 3:** Implementation (lightweight measurement)
- **Week 4:** First review + adjustments

## RFC Process (Related)
- **Full plan:** `leidos/training/RFC_TRAINING_PLAN.md` (723 lines)
- RFC = Request for Comments — structured proposal process for technical decisions
- Bob is implementing both DORA + RFC as part of Leidos leadership strategy

## Key Resources
- Book: "Accelerate" by Nicole Forsgren, Jez Humble, Gene Kim
- DORA Quick Check: https://dora.dev/quickcheck/
- Leidos leadership strategy: `leidos/knowledge/LEADERSHIP_STRATEGY.md`
