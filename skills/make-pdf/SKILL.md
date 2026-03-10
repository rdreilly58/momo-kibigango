---
name: make-pdf
description: Convert text, Markdown, and HTML files to PDF using pandoc. Use when creating PDFs from documents, exporting emails or notes as PDF, or converting formatted text to portable PDF documents.
---

# Make PDF

Convert text, Markdown, and HTML to PDF using pandoc.

## Quick Examples

```bash
# Markdown to PDF
bash {baseDir}/scripts/topdf.sh document.md -o output.pdf

# Text file with title
bash {baseDir}/scripts/topdf.sh -t "My Document" notes.txt -o notes.pdf

# HTML to PDF
bash {baseDir}/scripts/topdf.sh webpage.html -o webpage.pdf

# From stdin (pipe text)
cat email.txt | bash {baseDir}/scripts/topdf.sh --stdin -o email.pdf
```

## Options

- `-o FILE` (required) — Output PDF filename
- `-f FORMAT` — Input format: `txt`, `md`, `markdown`, `html` (auto-detected if omitted)
- `-t TITLE` — Document title (shows in PDF metadata)
- `--author NAME` — Author name
- `--subject TEXT` — Subject text
- `-s STYLE.css` — CSS stylesheet (HTML only)
- `--stdin` — Read from standard input instead of file

## Examples

```bash
# Convert markdown with metadata
bash {baseDir}/scripts/topdf.sh \
  interview.md \
  -o interview.pdf \
  -t "Interview Prep" \
  --author "Robert Reilly"

# Text email to PDF
cat email.txt | bash {baseDir}/scripts/topdf.sh --stdin -o email.pdf

# HTML with custom styling
bash {baseDir}/scripts/topdf.sh \
  -f html page.html \
  -s custom.css \
  -o styled.pdf
```

## Notes

- Requires `pandoc` (installed via Homebrew)
- Format auto-detection works for `.md`, `.markdown`, `.html`, `.htm`
- Plain text files default to `txt` format
- Metadata (title, author, subject) is embedded in PDF properties
