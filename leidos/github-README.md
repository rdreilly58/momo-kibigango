# Leidos Engineering Notes

**Repository:** [rdreilly58/leidos-engineering-notes](https://github.com/rdreilly58/leidos-engineering-notes)  
**Visibility:** Private  
**Content:** Unclassified engineering notes, processes, and knowledge base  
**Last Updated:** March 22, 2026

## ⚠️ SECURITY NOTICE

**This repository contains UNCLASSIFIED content only.**

- ✅ General engineering notes
- ✅ Public domain algorithms  
- ✅ Open-source contributions
- ✅ Team processes (sanitized)
- ✅ Professional development

**DO NOT COMMIT:**
- Export-controlled information (ITAR/EAR)
- Proprietary algorithms
- Contract-sensitive data
- CUI or FOUO materials
- Classified information

---

## Structure

```
leidos-engineering-notes/
├── README.md                    (This file)
├── SECURITY.md                  (Classification guidelines)
│
├── engineering/                 # Technical notes
│   ├── architectures/          # System design notes
│   ├── tools/                  # Tool evaluation & setup
│   └── techniques/             # Engineering practices
│
├── processes/                   # Team & work processes
│   ├── standups.md            # Daily standup format
│   ├── code-review.md         # Code review guidelines
│   └── onboarding.md          # Team onboarding
│
├── learning/                    # Professional development
│   ├── papers/                # Research papers (public)
│   ├── conferences/           # Conference notes
│   └── skills/                # Skill development
│
└── decisions/                   # Architecture Decision Records
    └── adr-001-example.md     # ADR template
```

## Quick Links

- **Daily Standup Format:** See `processes/standups.md`
- **Code Review Guidelines:** See `processes/code-review.md`
- **Security Classification:** See `SECURITY.md`
- **ADR Template:** See `decisions/adr-001-example.md`

## Contributing

When adding content:
1. Check `SECURITY.md` for classification
2. If CUI → use local workspace only
3. If unclassified → sanitize and commit
4. Use templates for consistency

## Local Sync

This GitHub repo mirrors content from `~/.openclaw/workspace/leidos/`:
- `memory/` → `engineering/` + `learning/`
- `knowledge/` → `engineering/`
- Decisions → `decisions/`
- Personal notes stay local only

## License

Internal use only. Not open source.

---

*Created: March 22, 2026*  
*Last Updated: March 22, 2026*
