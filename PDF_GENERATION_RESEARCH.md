# PDF Generation - Research & Recommendations

**Date:** March 21, 2026  
**Context:** Failed PDF generation attempts in OpenClaw environment  
**Goal:** Establish best practices and tooling strategy

---

## Problem Statement

Recent attempts to generate PDFs in OpenClaw hit several issues:

1. **Pandoc + pdflatex**: pdflatex not installed, required manual installation
2. **wkhtmltopdf**: Not available, requires heavy dependencies
3. **Reportlab**: Python package management blocked by system constraints
4. **enscript**: Not found in system
5. **MacTeX BasiCTeX**: Installation requires sudo + password (no TTY available)

**Root Cause:** Over-reliance on heavyweight PDF engines without fallback chains

---

## Tools Evaluated

### 1. **mdPDFinator** ⭐ RECOMMENDED
**GitHub:** https://github.com/yjpictures/mdPDFinator

**Strengths:**
- Single binary, cross-platform (macOS, Linux, Windows)
- Fast, lightweight, <10MB download
- Uses WeasyPrint (CSS-to-PDF) internally
- No TeX/LaTeX dependencies required
- Supports custom CSS styling
- Easy installation: `brew install weasyprint` + download binary

**Weaknesses:**
- Requires WeasyPrint on system (but simple: `brew install weasyprint`)
- Single command: no advanced programmatic API

**Installation (macOS):**
```bash
brew install weasyprint
wget https://github.com/yjpictures/mdPDFinator/releases/latest
chmod +x mdPDFinator
./mdPDFinator input.md -o output.pdf
```

**Best For:** Markdown → PDF conversions (documents, reports, game instructions)

---

### 2. **Pandoc** (Existing)
**Status:** Already in system, works for MD→PDF

**Issue:** Requires one of:
- pdflatex (MacTeX - heavyweight, 3GB+)
- wkhtmltopdf (browser rendering - missing deps)
- groff (basic, limited styling)

**Recommendation:** Use for intermediate formats only (MD→HTML→PDF), not direct PDF

---

### 3. **Reportlab** (Python Library)
**Pros:**
- Pure Python, good for programmatic PDF generation
- Rich formatting support
- Successfully tested in venv environment

**Cons:**
- Requires Python venv setup (extra overhead)
- Slower than compiled tools
- Overkill for simple documents

**Best For:** Complex programmatic PDF generation (invoices, charts, multi-page docs)

---

### 4. **WeasyPrint** (Underlying Engine)
**Direct use:** HTML/CSS → PDF

```bash
brew install weasyprint
weasyprint input.html output.pdf
```

**Pros:**
- Modern CSS support
- Fast rendering
- Single dependency
- Works great with HTML

**Cons:**
- Lower-level API (not CLI-friendly for simple cases)
- Better used as mdPDFinator's engine

---

## Current Skills in OpenClaw

### make-pdf Skill
**Location:** `~/.openclaw/workspace/skills/make-pdf/`  
**Status:** Already installed

**Currently supports:**
- Uses Pandoc (requires dependencies)
- Wraps via `topdf.sh` script
- Supports TXT, MD, HTML, with metadata

**Issue:** Depends on Pandoc PDF engine chain (fragile)

---

## Recommendations

### Tier 1: Use mdPDFinator (PRIMARY)
**When:** Markdown → PDF conversions (most common use case)

```bash
# Simple
mdPDFinator game_instructions.md -o output.pdf

# With styling
mdPDFinator game_instructions.md -o output.pdf -s custom.css

# Install (one-time)
brew install weasyprint
# Download binary from releases
```

**Why:**
- Lightweight, zero config
- Fast (< 2 seconds per document)
- Reliable (no complex dependencies)
- Cross-platform

---

### Tier 2: Use WeasyPrint (SECONDARY)
**When:** HTML → PDF (styled web content)

```bash
# Simple HTML to PDF
weasyprint input.html output.pdf

# Install (one-time)
brew install weasyprint
```

**Why:**
- Modern CSS support
- Good for styled HTML
- Single dependency

---

### Tier 3: Use Reportlab (FALLBACK)
**When:** Complex programmatic generation (charts, tables, custom layouts)

**Setup:**
```bash
python3 -m venv /tmp/pdf_env
source /tmp/pdf_env/bin/activate
pip install reportlab
```

**Why:**
- Full Python control
- Can generate from code
- No external dependencies for content generation

---

### Tier 4: Avoid (DON'T USE)
❌ **pdflatex/MacTeX** - Too heavyweight, requires sudo
❌ **wkhtmltopdf** - Missing dependencies, browser-based
❌ **Direct Pandoc PDF** - Fragile dependency chain
❌ **Online services** - Data privacy, network latency

---

## Implementation Strategy

### Step 1: Install mdPDFinator (NOW)
```bash
# One-time setup
brew install weasyprint

# Download mdPDFinator
curl -L https://github.com/yjpictures/mdPDFinator/releases/download/v0.1.x/mdPDFinator-macos -o /usr/local/bin/mdPDFinator
chmod +x /usr/local/bin/mdPDFinator

# Verify
mdPDFinator --help
```

### Step 2: Create OpenClaw Skill `pdf-pro` (OPTIONAL)
**Goal:** Unified PDF generation interface across all methods

**Structure:**
```
~/.openclaw/workspace/skills/pdf-pro/
├── SKILL.md                    # Documentation
├── scripts/
│   ├── md-to-pdf.sh           # mdPDFinator wrapper
│   ├── html-to-pdf.sh         # WeasyPrint wrapper
│   └── code-to-pdf.py         # Reportlab wrapper
└── styles/
    └── default.css            # Default CSS styling
```

**Usage (after setup):**
```bash
# Markdown
bash pdf-pro/scripts/md-to-pdf.sh input.md -o output.pdf

# HTML
bash pdf-pro/scripts/html-to-pdf.sh input.html -o output.pdf

# Programmatic
python3 pdf-pro/scripts/code-to-pdf.py --data game_data --template game.py -o output.pdf
```

---

## Comparison Table

| Tool | Speed | Size | Setup | Styling | Use Case |
|------|-------|------|-------|---------|----------|
| **mdPDFinator** | ⚡⚡⚡ Fast | <10MB | Brew | CSS | MD→PDF ✅ |
| **WeasyPrint** | ⚡⚡⚡ Fast | Small | Brew | CSS++ | HTML→PDF |
| **Reportlab** | ⚡⚡ Medium | Medium | Venv+pip | Python API | Programmatic |
| **Pandoc** | ⚡⚡ Medium | Med | Brew | Limited | Fallback only |
| **MacTeX** | ⚡ Slow | 3GB+ | Sudo | LaTeX | ❌ Avoid |

---

## For Your Game Instructions

**Recommended approach:**

```bash
# Convert game instructions from text → markdown → PDF
cat /tmp/GAME_INSTRUCTIONS.txt > /tmp/game_instructions.md

# Generate PDF
mdPDFinator /tmp/game_instructions.md -o /tmp/MOMOTARO_ROBLOX_RPG_INSTRUCTIONS.pdf

# Or with styling
mdPDFinator /tmp/game_instructions.md -o /tmp/MOMOTARO_ROBLOX_RPG_INSTRUCTIONS.pdf -s ~/.openclaw/workspace/styles/game.css
```

**Custom CSS example:**
```css
/* ~/.openclaw/workspace/styles/game.css */
body {
  font-family: 'Segoe UI', sans-serif;
  line-height: 1.6;
  color: #333;
}

h1 {
  color: #ff6b6b;
  border-bottom: 3px solid #ff6b6b;
  padding-bottom: 10px;
}

h2 {
  color: #ff6b6b;
  margin-top: 20px;
  border-left: 4px solid #ff6b6b;
  padding-left: 10px;
}

code {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
}
```

---

## Action Items

### Immediate (Today)
- [ ] Install mdPDFinator + WeasyPrint
- [ ] Test with game instructions
- [ ] Verify PDF quality/formatting

### Short-term (This week)
- [ ] Create pdf-pro skill (optional, but recommended)
- [ ] Update make-pdf skill to support multiple backends
- [ ] Document in TOOLS.md

### Long-term (Optional)
- [ ] Monitor new tools (evolving landscape)
- [ ] Add batch PDF generation
- [ ] Create template library

---

## References

- **mdPDFinator:** https://github.com/yjpictures/mdPDFinator
- **WeasyPrint:** https://weasyprint.org/
- **Reportlab:** https://www.reportlab.com/
- **Pandoc:** https://pandoc.org/
- **Clawhub Skills:** https://clawhub.com

---

**Recommendation Summary:**

🥇 **PRIMARY:** mdPDFinator (simple, fast, reliable)  
🥈 **SECONDARY:** WeasyPrint (styled HTML)  
🥉 **FALLBACK:** Reportlab (programmatic)  

**Next Step:** Bob reviews and decides on implementation path (Tier 1 only vs. full pdf-pro skill)
