# Brother Printer Skill

**Status:** ✅ Production Ready  
**Date:** March 22, 2026  
**Printers Found:** 2

## Printers on Network

| Name | Model | Type | Status |
|------|-------|------|--------|
| **Brother_HL_L2350DW_series** | HL-L2350DW | Laser (B&W) | ✅ Online |
| **Brother_MFC_L2700DW_series** | MFC-L2700DW | MFP (B&W) | ✅ Online (Default) |

## Quick Start

### List Printers
```bash
bash scripts/list-printers.sh
```

### Print a Document
```bash
# To default printer
bash scripts/print-file.sh -f document.pdf

# To specific printer
bash scripts/print-file.sh -f document.pdf -p Brother_HL_L2350DW_series

# With options (2 copies, duplex, fit-to-page)
bash scripts/print-file.sh -f document.pdf -p Brother_MFC_L2700DW_series -c 2 --duplex --fit-to-page
```

### Test Printer
```bash
bash scripts/test-printer.sh -p Brother_MFC_L2700DW_series
```

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `list-printers.sh` | List available printers | `bash list-printers.sh` |
| `print-file.sh` | Print documents | `bash print-file.sh -f FILE -p PRINTER [OPTIONS]` |
| `test-printer.sh` | Test connectivity | `bash test-printer.sh -p PRINTER` |

## Print Options

```
-f, --file FILE         PDF or text file to print
-p, --printer PRINTER   Printer name (default: system default)
-c, --copies N          Number of copies (default: 1)
--duplex                Print double-sided
--fit-to-page           Scale to fit page
--landscape             Landscape orientation
--grayscale             Force grayscale
--status                Show printer status
```

## Common Tasks

### Print 3 copies with duplex
```bash
bash scripts/print-file.sh -f report.pdf -p Brother_MFC_L2700DW_series -c 3 --duplex
```

### Batch print all PDFs
```bash
for pdf in *.pdf; do
  bash scripts/print-file.sh -f "$pdf" -p Brother_MFC_L2700DW_series
done
```

### Convert and print Markdown
```bash
pandoc document.md -o document.pdf
bash scripts/print-file.sh -f document.pdf
```

### Print with fit-to-page
```bash
bash scripts/print-file.sh -f slides.pdf --fit-to-page
```

## Supported Formats

- ✅ PDF (native)
- ✅ PostScript (.ps)
- ✅ Text (.txt)
- ⚠️ Images (.jpg, .png) — convert to PDF first
- ⚠️ Office (.docx, .xlsx) — convert to PDF first

## Troubleshooting

### List printers
```bash
lpstat -p
```

### Check printer status
```bash
lpstat -p -l
```

### View print queue
```bash
lpq -P Brother_MFC_L2700DW_series
```

### Cancel print job
```bash
lprm -P Brother_MFC_L2700DW_series JOB_ID
```

### Restart CUPS
```bash
sudo launchctl stop org.cups.cupsd
sudo launchctl start org.cups.cupsd
```

## Documentation

See **SKILL.md** for:
- Detailed usage examples
- Advanced options
- Troubleshooting guide
- System integration examples
- Tips and best practices
