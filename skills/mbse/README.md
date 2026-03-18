# MBSE — Model-Based Systems Engineering

Lightweight YAML-based framework for defining system requirements, architecture, behaviors, tests, and risks with full traceability.

## Quick Start

### 1. Run Analysis
```bash
python3 mbse-analyze /path/to/model.yaml
```

### 2. Validate Model
```bash
bash mbse validate /path/to/model.yaml
```

### 3. View Status
```bash
bash mbse status /path/to/model.yaml
```

### 4. Check Traceability
```bash
bash mbse trace /path/to/model.yaml
```

## Example Models

- **ReillyDesignStudio:** `../../reillydesignstudio/model.yaml`
- **Momotaro iOS:** `../../momotaro-ios/model.yaml`

## Documentation

- **SKILL.md** — Complete command reference and usage guide
- **schema.yaml** — Full YAML schema with all fields

## CLI Tool

```bash
./mbse <command> <model.yaml> [options]
```

### Commands
- `analyze` — Comprehensive system analysis
- `trace` — Requirement traceability
- `coverage` — Test coverage analysis
- `matrix` — Requirements Traceability Matrix (RTM)
- `validate` — Validate YAML schema
- `status` — System status dashboard
- `risks` — Risk analysis & mitigation
- `diagrams` — Generate SysML diagrams (coming soon)
- `export` — Export to various formats (coming soon)

## Model Structure

```yaml
system:
  # System metadata

requirements:
  # What the system must do

architecture:
  # How the system is organized

behaviors:
  # How system components interact

tests:
  # How requirements are verified

risks:
  # Identified risks & mitigation

decisions:
  # Architecture Decision Records (ADRs)
```

## Features

✅ **Requirement Traceability** — Req → Architecture → Tests  
✅ **Ownership Tracking** — Every item has an owner  
✅ **Status Management** — Draft → Active → Verified → Deprecated  
✅ **Risk Assessment** — Identify, track, mitigate risks  
✅ **Decision Documentation** — Capture architectural decisions  
✅ **Test Coverage Analysis** — Identify verification gaps  
✅ **Git-friendly** — YAML in version control  
✅ **CLI-first** — No heavyweight tools needed  

## Requirements Analysis (ReillyDesignStudio)

| Status | Count |
|--------|-------|
| Implemented | 8 |
| In-progress | 2 |
| Proposed | 1 |
| **Total** | **11** |

## Requirements Analysis (Momotaro iOS)

| Status | Count |
|--------|-------|
| Implemented | 2 |
| In-progress | 4 |
| Proposed | 6 |
| **Total** | **12** |

## Why MBSE?

Traditional approach:
- Requirements in Jira
- Architecture in Confluence
- Tests in separate test management
- Decisions scattered in PRs & Slack
- **No single source of truth**
- **Manual traceability**
- **Easy to lose context**

MBSE approach:
- Single YAML model file
- Machine-readable format
- Automatic traceability
- Version controlled
- Analyzable & reportable
- Team alignment

## When to Use MBSE

✅ **Use MBSE for:**
- Complex systems with many interconnected parts
- Safety-critical or high-risk systems
- Multi-team collaboration
- Requirement traceability is important
- Architecture needs documentation
- Risk management is critical

🔄 **Can use alongside:**
- Jira for sprint tracking
- Confluence for detailed docs
- GitHub for code
- Your test framework

❌ **Skip MBSE for:**
- Very small projects (<5 requirements)
- Internal tools that don't change
- Throwaway prototypes

## Next Steps

1. **Review Models**
   ```bash
   python3 mbse-analyze ../../reillydesignstudio/model.yaml
   python3 mbse-analyze ../../momotaro-ios/model.yaml
   ```

2. **Update Models** — As you implement features, update model.yaml
   ```bash
   # Edit model.yaml
   git add model.yaml
   git commit -m "docs: Mark REQ-001 as implemented"
   ```

3. **Track Progress** — Run analysis weekly
   ```bash
   python3 mbse-analyze model.yaml
   ```

4. **Trace Requirements** — Before implementing, check traceability
   ```bash
   bash mbse trace model.yaml | grep "REQ-XXX"
   ```

## Tips

- Keep model.yaml in root of project
- Update status when features are implemented
- Mark tests passed/failed as they run
- Update risk status as mitigations are completed
- Use architecture decision records (ADRs) to capture design choices

## Files

```
mbse/
├── README.md                # This file
├── SKILL.md                 # Complete documentation
├── schema.yaml              # YAML schema
├── mbse                     # Bash CLI tool
├── mbse-analyze             # Python analyzer
└── examples/
    └── (model examples)
```

## Help

```bash
bash mbse help
python3 mbse-analyze --help
```

---

**For more details, see SKILL.md**

🔧 Model-Based Systems Engineering made simple.
