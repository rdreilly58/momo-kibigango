---
title: Ingest Workflow
type: concept
created: 2026-05-03
updated: 2026-05-03
tags: [workflow, ingest, knowledge-management]
---

# Ingest Workflow

How to add a new document, article, spec, or external source to the memory system.
Run this workflow when Bob drops a file, pastes a link, or says "remember this doc."

_See [[glossary]] for entity types. See [[overview]] for system architecture._

---

## When to Ingest

Trigger this workflow for:
- Technical specs, RFCs, training docs
- Articles, blog posts, research papers worth keeping
- Meeting notes with decisions or commitments
- System documentation (external tools, APIs)
- Any source Bob explicitly says to remember

**Don't ingest:** ephemeral context, one-off answers, conversational notes (use daily session notes instead).

---

## Ingest Steps

### 1. Read the source
Read the full document. Note: key facts, decisions, entities (people, tools, concepts), contradictions with existing memory.

### 2. Check the glossary
Before writing anything, check [[glossary]] for canonical terms. If new terms appear that should be canonical, add them.

### 3. Create or update entity pages
For each significant entity encountered:

| Entity type | Create/update file in... | When |
|-------------|--------------------------|------|
| `concept` | `memory/` | New domain idea or definition |
| `tool` | `memory/` | New tool or service profile |
| `decision` | `memory/decisions/` | Architectural or strategic choice |
| `lesson` | `memory/lessons-learned.md` | Root cause + prevention |
| `project` | Claude Code memory | New project context |
| `reference` | Claude Code memory | New external system pointer |

Use the standard frontmatter format:
```yaml
---
title: <entity name>
type: <entity type>
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [<source filename or URL>]
tags: [<relevant tags>]
---
```

### 4. Add cross-references
Use `[[filename-without-extension]]` backlinks to connect related pages.
- New concept pages should link to related concepts
- Update existing pages that relate to the new source
- Add the new page to [[overview]] if it's project-level

### 5. Update glossary if needed
If the source introduced new canonical terms, add them to [[glossary]].

### 6. Log the ingest
Append to `memory/YYYY-MM-DD.md` (today's daily note):
```
## Ingest: <source title>
- Source: <filename or URL>
- Key facts: <2-3 bullet points>
- Pages created/updated: <list>
```

---

## Ingest Checklist

```
[ ] Read full source
[ ] Checked glossary for existing canonical terms
[ ] Created/updated entity pages (concept, tool, decision, etc.)
[ ] Added [[backlinks]] between related pages
[ ] Updated overview.md if project-level
[ ] Updated glossary if new terms introduced
[ ] Logged in today's daily note
```

---

## Quick Ingest (Short Sources)

For short articles or snippets (< 500 words), you can skip entity pages and just:
1. Extract key facts into a `concept` or `reference` memory file
2. Add to Claude Code memory via `memory_store`
3. Log in daily note

---

## Large Batch Ingest

For multiple related sources (e.g., a full spec suite):
1. Ingest one source at a time — don't batch
2. Let cross-references accumulate naturally across ingests
3. Run [[memory-lint]] after batch to check consistency

---

_Cross-references: [[glossary]] · [[overview]] · [[CROSS-AGENT-MEMORY]]_
