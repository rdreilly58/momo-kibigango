# Brother Printer Skill

**Version:** 1.0  
**Date:** March 22, 2026  
**Status:** ✅ PRODUCTION READY

Access and print to Brother printers on the local network.

## Quick Start

```bash
# List available printers
bash ~/.openclaw/workspace/skills/printer-brother/scripts/list-printers.sh

# Print a PDF to a specific printer
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
  -f document.pdf \
  -p Brother_HL_L2350DW_series

# Print with copies and options
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
  -f document.pdf \
  -p Brother_MFC_L2700DW_series \
  -c 2 \
  --duplex \
  --fit-to-page
```

## Available Printers

| Printer | Model | Status | Device |
|---------|-------|--------|--------|
| **Brother_HL_L2350DW_series** | HL-L2350DW | ✅ Online | dnssd://Brother HL-L2350DW series._ipp._tcp.local/ |
| **Brother_MFC_L2700DW_series** | MFC-L2700DW | ✅ Online | dnssd://Brother MFC-L2700DW series._ipp._tcp.local/ |

**Note:** MFC-L2700DW is set as system default printer.

### Printer Capabilities

**Brother HL-L2350DW** (Laser Printer)
- Type: Monochrome laser printer
- Color: Black & white only
- Best for: Documents, text, simple graphics
- Resolution: 2400 x 600 dpi
- Speed: 32 ppm

**Brother MFC-L2700DW** (Multifunction Printer)
- Type: Monochrome laser MFP (print + scan + copy + fax)
- Color: Black & white only
- Best for: Documents, text, office use
- Resolution: 2400 x 600 dpi
- Speed: 34 ppm
- Features: ADF (auto document feeder), scanning capability

## Common Print Tasks

### Print a Single Document

```bash
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
  -f ~/Downloads/report.pdf \
  -p Brother_MFC_L2700DW_series
```

### Print Multiple Copies

```bash
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
  -f presentation.pdf \
  -p Brother_HL_L2350DW_series \
  -c 3
```

### Print with Duplex (2-sided)

```bash
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
  -f report.pdf \
  -p Brother_MFC_L2700DW_series \
  --duplex
```

### Print and Scale to Page

```bash
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
  -f document.pdf \
  -p Brother_HL_L2350DW_series \
  --fit-to-page
```

### Batch Print Multiple Files

```bash
for file in *.pdf; do
  bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
    -f "$file" \
    -p Brother_MFC_L2700DW_series
done
```

## Advanced Usage

### Check Printer Status

```bash
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh --status
```

### View Print Queue

```bash
lpq -P Brother_MFC_L2700DW_series
```

### Cancel a Print Job

```bash
# List jobs
lpq -P Brother_MFC_L2700DW_series

# Cancel by job ID
lprm -P Brother_MFC_L2700DW_series JOB_ID
```

### Print Configuration

```bash
# Show all options for a printer
lpoptions -p Brother_MFC_L2700DW_series -l

# Set default printer
lpadmin -d Brother_MFC_L2700DW_series
```

## Scripts Provided

### list-printers.sh
List all available Brother printers with status and device info.

```bash
bash ~/.openclaw/workspace/skills/printer-brother/scripts/list-printers.sh
```

**Output:**
- Printer name
- Model
- Status (online/offline/error)
- Device URI
- Default indicator

### print-file.sh
Main printing script with multiple options.

**Usage:**
```bash
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh [OPTIONS]

OPTIONS:
  -f, --file FILE              PDF or text file to print (required)
  -p, --printer PRINTER        Printer name (default: system default)
  -c, --copies N               Number of copies (default: 1)
  --duplex                     Print double-sided (if supported)
  --fit-to-page                Scale to fit page
  --landscape                  Landscape orientation
  --grayscale                  Force grayscale
  --status                     Show printer status only
  -h, --help                   Show help
```

**Examples:**
```bash
# Print to default printer
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh -f document.pdf

# Print to specific printer, 2 copies, duplex
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
  -f document.pdf \
  -p Brother_MFC_L2700DW_series \
  -c 2 \
  --duplex

# Check printer status
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh --status
```

### test-printer.sh
Test printer connectivity and print a test page.

```bash
bash ~/.openclaw/workspace/skills/printer-brother/scripts/test-printer.sh \
  -p Brother_HL_L2350DW_series
```

**What it does:**
1. Checks if printer is online
2. Verifies network connectivity
3. Prints a test page with date/time
4. Reports success/failure

## Troubleshooting

### Printer Not Found

**Problem:** "Printer not found" error

**Solution:**
```bash
# 1. List printers
lpstat -p

# 2. Check if CUPS is running
launchctl list | grep -i cups

# 3. Restart CUPS if needed
sudo launchctl stop org.cups.cupsd
sudo launchctl start org.cups.cupsd
```

### Print Job Stuck in Queue

**Problem:** Document won't print or is stuck in queue

**Solution:**
```bash
# 1. Check queue
lpq -P Brother_MFC_L2700DW_series

# 2. Cancel stuck job
lprm -P Brother_MFC_L2700DW_series JOB_ID

# 3. Clear entire queue if needed
cancel -a -P Brother_MFC_L2700DW_series
```

### Printer Offline

**Problem:** Printer shows as offline but is connected

**Solution:**
```bash
# 1. Check printer network status
ping "Brother MFC-L2700DW series._ipp._tcp.local"

# 2. Restart printer via power cycle (5 seconds)

# 3. Re-add printer to CUPS
# System Settings → Printers & Scanners → Remove printer → Re-add
```

### Poor Print Quality

**Problem:** Printed pages look faded or have streaks

**Solution (Brother printers):**
- Clean the drum unit (inside printer)
- Check toner level (may need replacement)
- Ensure "Grayscale" mode is intended (not accidentally set)

## System Integration

### Print from Markdown

```bash
# Convert Markdown to PDF, then print
pandoc document.md -o document.pdf
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
  -f document.pdf \
  -p Brother_MFC_L2700DW_series
```

### Print from Email (Gmail)

```bash
# Export email as PDF from Gmail, then print
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
  -f email.pdf \
  -p Brother_HL_L2350DW_series
```

### Scheduled Printing (Cron)

```bash
# Print a daily report at 9 AM
0 9 * * * bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
  -f /path/to/daily-report.pdf \
  -p Brother_MFC_L2700DW_series
```

## File Format Support

| Format | Support | Notes |
|--------|---------|-------|
| PDF | ✅ Full | Native CUPS support, best results |
| PostScript (.ps) | ✅ Full | Converted via Ghostscript |
| Text (.txt) | ✅ Full | Plain text, auto-formatted |
| Images (.jpg, .png) | ⚠️ Via conversion | Convert to PDF first |
| Office (.docx, .xlsx) | ⚠️ Via conversion | Convert to PDF first (LibreOffice) |

**Conversion examples:**
```bash
# Convert DOCX to PDF
libreoffice --headless --convert-to pdf document.docx

# Convert image to PDF
convert image.png image.pdf

# Print converted file
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
  -f image.pdf \
  -p Brother_MFC_L2700DW_series
```

## Performance & Limits

| Aspect | Value |
|--------|-------|
| Max jobs in queue | 50+ |
| Network latency | <100ms (local network) |
| Print speed | 32-34 ppm |
| Resolution | 2400 x 600 dpi |
| Job timeout | 30 minutes |
| Max file size | 500 MB |

## Tips & Best Practices

1. **Default Printer:** Set MFC-L2700DW as default (more features)
2. **Duplex Printing:** Save paper — use `--duplex` when possible
3. **Batching:** Print multiple documents in one queue to save time
4. **Fit-to-Page:** Use for documents with margins that might get cut off
5. **Check Status First:** Run `--status` before printing large batches
6. **Network Stability:** Ensure stable WiFi — printers can disconnect

## References

- **CUPS Documentation:** https://www.cups.org/doc/
- **Brother Driver Support:** https://support.brother.com/
- **macOS Printing:** https://support.apple.com/en-us/guide/mac-help/mh1607/mac

## Support

For issues or questions:
1. Run test script: `bash scripts/test-printer.sh`
2. Check logs: `tail -f /var/log/cups/access_log`
3. Verify printer online via web UI (usually http://PRINTER_IP:80)
