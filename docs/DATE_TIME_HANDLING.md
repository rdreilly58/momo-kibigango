# Date & Time Handling (CRITICAL RULE)

**Golden Rule: ALWAYS LOOK UP, NEVER INFER**

This rule was established March 26, 2026 after Momotaro made errors calculating work week progression.

## The Learning Event (March 26, 2026)

**What Happened:**
- Asked: "What week of work am I in?"
- I answered: "Week 2 of 4" + "midpoint of week 1" (contradictory & wrong)
- Root cause: Made up a "4-week schedule" that didn't exist, didn't count actual days

**Correct Answer:**
- Start date: Monday, March 23, 2026 (Day 1)
- Today: Thursday, March 26, 2026 (Day 4)
- Week: Week 1, Day 4 (standard Mon-Fri work week)

**The Rule:** Never infer dates/times. Always look them up.

---

## Sources of Current Date & Time (In Priority Order)

### 1. Message Metadata (MOST RELIABLE)
```json
{
  "timestamp": "Thu 2026-03-26 03:39 EDT"
}
```
- Provided in every message
- Always in format: `DAY YYYY-MM-DD HH:MM TIMEZONE`
- Extract directly, no calculation needed
- Example: "Thu 2026-03-26 03:39 EDT" = Thursday, March 26, 2026, 3:39 AM EDT

### 2. System Time (If Needed)
```bash
date
# Output: Thu Mar 26 03:39:15 EDT 2026
```
- Use `date` command if metadata unavailable
- Read directly, no calculation

### 3. session_status Tool (For Verification)
```bash
📊 session_status
```
- Shows current time + usage
- Use when you need authoritative timestamp

---

## How to Handle Dates

### When Responding to a Date Question

**BAD (Inference):**
```
"You started March 23, so 3 days have passed, meaning..."
"It's been 4 days, so you're at the midpoint of the first week..."
"You're probably in week 2 by now..."
```

**GOOD (Look Up):**
```
Message metadata says: Thu 2026-03-26
You started: Mon 2026-03-23
Days elapsed: 23 → 24 → 25 → 26 = 4 days
Current status: Week 1, Day 4
```

### When Updating Documentation

**Always do this:**
1. Read timestamp from message metadata
2. Update USER.md with `**Current Date:** Thu 2026-03-26`
3. Recalculate any date-dependent values
4. Never rely on previous values in files

**Example:** USER.md used to say "Tuesday, March 24" — became stale. When you read "Thu 2026-03-26", update immediately.

---

## Common Patterns to AVOID

| ❌ Wrong | ✅ Right |
|---------|----------|
| "You started Mon, so it's been ~4 days" | Check metadata: "Thu 2026-03-26" = Day 4 |
| "Probably midweek" | Count: Mon/Tue/Wed/Thu = Day 4 |
| "Week 2 starts Monday" | Verify actual calendar: When does your Week 2 start? |
| "It's been 3 days" | Check metadata timestamp for exact day |
| "You're probably tired by Friday" | Today's metadata says Thu, so tomorrow is Friday |

---

## Examples: Correct Date Handling

### Example 1: Work Week Question
**User:** "What week of work am I in?"
**Metadata:** "Thu 2026-03-26 03:39 EDT"
**USER.md:** Start Date = Monday, March 23, 2026

**Correct Answer:**
1. Read metadata: Thursday, March 26, 2026
2. Calculate: Mon 3/23 (Day 1), Tue 3/24 (Day 2), Wed 3/25 (Day 3), Thu 3/26 (Day 4)
3. Respond: "Week 1, Day 4 (Thursday is the 4th day since Monday start)"

### Example 2: Date Progression
**User:** "Is it Friday yet?"
**Metadata:** "Thu 2026-03-26 15:45 EDT"
**Correct Answer:** "Not yet — today is Thursday. Tomorrow (Friday, March 27) is next."

### Example 3: Calendar Math
**User:** "How many days until the weekend?"
**Metadata:** "Thu 2026-03-26"
**Correct Answer:** "Tomorrow is Friday, then Saturday & Sunday. So 1 more work day + 2 weekend days."

---

## Rule Enforcement Checklist

Before answering ANY date/time question:
- [ ] Read message metadata timestamp
- [ ] Extract day-of-week + date + time
- [ ] Never calculate or infer
- [ ] If needed, verify against USER.md
- [ ] Update USER.md if current date is newer
- [ ] Respond with exact information from metadata

---

## When in Doubt

Use `session_status` tool to get authoritative current time:
```bash
📊 session_status
```

This shows:
- Exact current date & time
- Session duration
- Token usage
- All metadata

**Never guess. Always verify.**

---

## Historical Reference

- **March 26, 2026:** Rule established after inference error
- **Error:** Made up "Week 2 of 4" schedule without verification
- **Fix:** Enforced metadata-first date handling
- **Impact:** All future date calculations now verified against message metadata
