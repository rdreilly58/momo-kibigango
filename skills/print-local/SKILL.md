---
name: print-local
description: Print files to local Brother printers (Brother_MFC_L2700DW_series, Brother_HL_L2350DW_series). Use when printing documents, PDFs, or files to either printer, or when listing available printers. Supports specifying printer, number of copies, and print options.
---

# Print Local

Print files to your local Brother printers.

**Available printers:**
- `Brother_MFC_L2700DW_series` (default)
- `Brother_HL_L2350DW_series`

## Quick Examples

```bash
# Print to default printer
bash {baseDir}/scripts/print.sh document.pdf

# Print to specific printer
bash {baseDir}/scripts/print.sh -p Brother_HL_L2350DW_series report.pdf

# Print multiple copies
bash {baseDir}/scripts/print.sh -c 3 form.pdf

# List available printers
bash {baseDir}/scripts/print.sh --list
```

## Options

- `-p PRINTER` — Printer name (default: Brother_MFC_L2700DW_series)
- `-c COPIES` — Number of copies (default: 1)
- `-o OPTION` — lp print option (can be repeated, e.g. `-o media=A4`)
- `-l, --list` — Show available printers
- `-h, --help` — Show help

## Common Print Options

```bash
# Landscape
bash {baseDir}/scripts/print.sh -o landscape document.pdf

# Duplex (2-sided)
bash {baseDir}/scripts/print.sh -o sides=two-sided-long-edge document.pdf
```

See `man lp` for full option list.
