---
name: mbse
description: "Model-Based Systems Engineering (MBSE) — Define system requirements, architecture, behaviors, tests, and risks in YAML. Auto-generate traceability matrices, coverage reports, and analysis."
metadata:
  {
    "openclaw": { "emoji": "🔧", "requires": { "bins": ["bash", "grep", "awk"] } },
  }
---

# MBSE — Model-Based Systems Engineering

A lightweight, CLI-first YAML-based model-driven engineering framework for defining systems, requirements, architecture, and tests with full traceability.

## What is MBSE?

Model-Based Systems Engineering is a formalized discipline that:
- **Defines** system requirements, behavior, and architecture in structured models
- **Traces** requirements through architecture components to verification tests
- **Analyzes** coverage gaps, risks, and design decisions
- **Enables** teams to reason about complex systems with precision
- **Supports** automated validation and reporting

Unlike traditional documentation, MBSE models are **machine-readable, traceable, and analyzable**.

## Quick Start

### 1. Create a System Model

```yaml
system:
  name: MySystem
  version: "1.0"
  status: active

requirements:
  - id: REQ-001
    title: "User Authentication"
    status: implemented
    priority: CRITICAL
    traces_to: [ARCH-001, TEST-001]

architecture:
  components:
    - id: ARCH-001
      name: "Auth Service"
      realizes: [REQ-001]
      depends_on: []

tests:
  - id: TEST-001
    name: "Auth Test"
    verifies: [REQ-001]
    status: passed
```

### 2. Run Analysis

```bash
# Analyze model
mbse analyze model.yaml

# Show traceability
mbse trace model.yaml

# Check test coverage
mbse coverage model.yaml

# View system status
mbse status model.yaml
```

### 3. View Reports

```bash
# Generate Requirements Traceability Matrix
mbse matrix model.yaml

# Check risks
mbse risks model.yaml

# Validate schema
mbse validate model.yaml
```

## Model Schema

The YAML schema defines 8 sections:

### System Metadata
```yaml
system:
  name: string
  version: string
  description: string
  owner: string
  status: draft | active | deprecated
```

### Requirements
```yaml
requirements:
  - id: REQ-001
    title: string
    category: Functional | Non-Functional | Security | Performance
    priority: CRITICAL | HIGH | MEDIUM | LOW
    status: proposed | approved | implemented | verified | deprecated
    traces_to: [ARCH-001, TEST-001]
    acceptance_criteria: [...]
    risk_level: LOW | MEDIUM | HIGH | CRITICAL
```

### Architecture Components
```yaml
architecture:
  components:
    - id: ARCH-001
      name: string
      type: Service | Module | Database | API | UI | External
      realizes: [REQ-001, REQ-002]
      depends_on: [ARCH-002]
      interfaces: [...]
      technology_stack: [...]
  
  interactions:
    - from: ARCH-001
      to: ARCH-002
      protocol: HTTP | gRPC | WebSocket | Direct
      frequency: sync | async | event-driven
```

### Behaviors
```yaml
behaviors:
  - id: BEHAV-001
    name: string
    type: Use-Case | Workflow | State-Machine | Scenario
    actors: [User, System]
    steps:
      - step: 1
        description: string
        component: ARCH-001
        action: string
        condition: optional
    success_criteria: [...]
```

### Tests
```yaml
tests:
  - id: TEST-001
    name: string
    type: Unit | Integration | System | Acceptance | Performance
    verifies: [REQ-001]
    exercises: [ARCH-001]
    status: draft | ready | passed | failed | skipped
    coverage_percentage: 95
    test_procedure: [...]
```

### Risks
```yaml
risks:
  - id: RISK-001
    title: string
    probability: LOW | MEDIUM | HIGH
    impact: LOW | MEDIUM | HIGH | CRITICAL
    mitigation_strategy: string
    status: identified | mitigated | resolved | accepted
```

### Architecture Decisions (ADRs)
```yaml
decisions:
  - id: ADR-001
    title: string
    status: proposed | accepted | superseded | deprecated
    context: string
    decision: string
    rationale: string
    consequences: string
    related_requirements: [REQ-001]
```

## Commands

### `mbse analyze`
Comprehensive system analysis report including:
- Requirements status breakdown
- Architecture overview
- Test coverage statistics
- Risk assessment summary
- Traceability overview

```bash
mbse analyze project-model.yaml
```

**Output:**
```
📊 MBSE Analysis Report
=======================

System: MySystem (v1.0)

📋 Requirements: 15 total
🏗️  Architecture Components: 8
✅ Tests: 12
⚠️  Risks: 3
📌 Architecture Decisions: 4
```

### `mbse trace`
Shows requirement traceability details:
- Maps each requirement to architecture components
- Shows which tests verify each requirement
- Identifies traceability gaps

```bash
mbse trace project-model.yaml
```

**Output:**
```
🔗 Requirement Traceability
============================

📌 Requirement: REQ-001
   Title: User Authentication
   Status: implemented
   Traces to:
     → ARCH-001
     → ARCH-002
```

### `mbse coverage`
Test coverage analysis:
- Requirements covered by tests
- Test count vs requirement count
- Coverage percentage

```bash
mbse coverage project-model.yaml
```

**Output:**
```
📈 Test Coverage Analysis
=========================
Total Requirements: 15
Total Tests: 12
Estimated Coverage: ~80%
```

### `mbse matrix`
Generates Requirements Traceability Matrix (RTM):
- Maps each requirement to architecture and tests
- Shows coverage and relationships
- Can be exported to CSV/JSON

```bash
mbse matrix project-model.yaml
```

### `mbse validate`
Validates YAML model against schema:
- Checks for required sections
- Validates ID formats
- Reports structural errors

```bash
mbse validate project-model.yaml
```

**Output:**
```
✔️  Validating model structure...

✅ system section found
✅ requirements section found
✅ architecture section found
✅ tests section found

✅ Model validation passed
```

### `mbse status`
System status dashboard:
- Overall project health
- Key metrics
- Implementation status

```bash
mbse status project-model.yaml
```

**Output:**
```
📊 System Status Dashboard
==========================

System: MySystem
Status: active

📈 Key Metrics
  Requirements: 15
  Architecture Components: 8
  Tests: 12
  Identified Risks: 3
```

### `mbse risks`
Risk analysis report:
- High-risk items
- Mitigation strategies
- Coverage by requirements

```bash
mbse risks project-model.yaml
```

**Output:**
```
⚠️  Risk Analysis Report
=======================

Found 3 risks

Risk details:
  • Risk: RISK-001
    Title: Database Connection Failures
    Probability: MEDIUM
    Status: mitigated
```

### `mbse diagrams`
Auto-generate SysML/architecture diagrams:
- Component diagram (Mermaid)
- Sequence diagrams for behaviors
- State machines for workflows

```bash
mbse diagrams project-model.yaml
```

### `mbse export`
Export model to various formats:
- JSON — Machine-readable format
- HTML — Formatted report
- Mermaid — Diagram syntax
- SysML — Papyrus-compatible format

```bash
mbse export project-model.yaml --format html > report.html
mbse export project-model.yaml --format json > model.json
```

## Typical Workflow

### 1. Define the System Model

Create `model.yaml` with all system information:
```bash
cat > model.yaml << 'EOF'
system:
  name: MyProduct
  version: "1.0"
  status: active

requirements:
  # ... requirements

architecture:
  components:
    # ... components

tests:
  # ... tests
EOF
```

### 2. Validate the Model

```bash
mbse validate model.yaml
```

### 3. Analyze Requirements Coverage

```bash
mbse coverage model.yaml
```

### 4. Check Traceability

```bash
mbse trace model.yaml
```

### 5. Review Risks

```bash
mbse risks model.yaml
```

### 6. Generate Report

```bash
mbse export model.yaml --format html > report.html
open report.html
```

### 7. Version Control

```bash
git add model.yaml
git commit -m "docs: Update system model and requirements"
```

## File Organization

Recommended project structure:

```
project/
├── model.yaml                    # Main system model
├── docs/
│   ├── diagrams/
│   │   ├── architecture.md       # Component diagrams
│   │   └── behaviors.md          # Sequence diagrams
│   └── requirements/
│       ├── functional.md         # Detailed requirements
│       └── non-functional.md
├── src/
│   └── (implementation)
├── tests/
│   └── (test code)
└── generated/
    ├── requirements-matrix.csv   # Auto-generated RTM
    ├── coverage-report.json      # Coverage analysis
    └── report.html               # Full report
```

## Examples

### ReillyDesignStudio

```bash
cd reillydesignstudio
mbse analyze model.yaml
mbse coverage model.yaml
mbse matrix model.yaml
```

### Momotaro iOS

```bash
cd momotaro-ios
mbse analyze model.yaml
mbse risks model.yaml
mbse trace model.yaml
```

## Use Cases

### 1. Requirements Validation
Ensure all requirements are traceable to architecture and tests:
```bash
mbse trace model.yaml | grep -v "→"  # Find untraced requirements
```

### 2. Test Coverage Analysis
Find under-tested requirements:
```bash
mbse coverage model.yaml
```

### 3. Risk Assessment
Track mitigation progress:
```bash
mbse risks model.yaml
```

### 4. Architecture Review
Verify component dependencies:
```bash
mbse trace model.yaml | grep "depends_on"
```

### 5. Decision Tracking
Document key architectural decisions:
```bash
mbse export model.yaml --format html  # See ADR section
```

## Best Practices

### 1. Keep IDs Consistent
- Requirements: `REQ-XXX`
- Architecture: `ARCH-XXX`
- Tests: `TEST-XXX`
- Risks: `RISK-XXX`
- Decisions: `ADR-XXX`

### 2. Update on Changes
Model should stay in sync with implementation:
- Feature added? Add requirement + tests
- Architecture changed? Update components + ADR
- Risk mitigated? Update risk status

### 3. Version Control
Commit model changes with code:
```bash
git add model.yaml
git commit -m "docs: Add REQ-XXX for feature YYY"
```

### 4. Review Traceability
Regularly check for gaps:
```bash
mbse trace model.yaml | grep "^ *-" | wc -l  # All items traced?
```

### 5. Track Coverage
Monitor test coverage over time:
```bash
mbse coverage model.yaml  # Check percentage monthly
```

## Integration with Other Tools

### With UML Diagrams
Export model to Mermaid for visualization:
```bash
mbse diagrams model.yaml
```

### With Test Runners
Parse test results and update model:
```bash
# Update TEST-XXX status field based on actual test results
```

### With CI/CD
Validate model in pipeline:
```bash
mbse validate model.yaml || exit 1
```

### With Git Hooks
Pre-commit validation:
```bash
#!/bin/bash
# .git/hooks/pre-commit
mbse validate model.yaml || exit 1
```

## Limitations

- **No GUI yet** (CLI only, for now)
- **Export formats** JSON/HTML implemented, SysML WIP
- **Auto-diagram generation** not yet fully implemented
- **Real-time collaboration** not supported (use git for versioning)

## Next Steps

1. **Create first model** for your project
2. **Define requirements** clearly with acceptance criteria
3. **Map to architecture** via `traces_to` and `realizes`
4. **Track tests** that verify requirements
5. **Review gaps** with `mbse trace` and `mbse coverage`
6. **Export reports** with `mbse export`

## Schema Reference

Full schema with all fields:
```bash
cat ~/.openclaw/workspace/skills/mbse/schema.yaml
```

## Help

```bash
mbse help
```

---

**Start with a simple model and grow over time. MBSE is about precision and traceability, not perfection.** 🔧

Real-world examples:
- `~/.openclaw/workspace/reillydesignstudio/model.yaml`
- `~/.openclaw/workspace/momotaro-ios/model.yaml`
