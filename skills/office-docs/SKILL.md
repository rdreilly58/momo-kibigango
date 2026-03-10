---
name: office-docs
description: Read and write Microsoft Word (.docx) and Excel (.xlsx) files. Use when creating/editing Word documents, reading/writing spreadsheets, extracting data from Office files, or generating reports.
---

# Office Documents

Read and write Word (.docx) and Excel (.xlsx) files.

## Word Documents (.docx)

```bash
# Read all text
python3 {baseDir}/scripts/word.py read document.docx

# Read as structured JSON (with paragraphs, tables, styles)
python3 {baseDir}/scripts/word.py read document.docx --json

# Create new document
python3 {baseDir}/scripts/word.py create "My Document" -o output.docx

# Append paragraph
python3 {baseDir}/scripts/word.py append document.docx "This is a new paragraph"

# Append heading
python3 {baseDir}/scripts/word.py append document.docx --heading 1 "Section Title"

# Add list item
python3 {baseDir}/scripts/word.py append document.docx --list "List item"
```

## Excel Spreadsheets (.xlsx)

```bash
# List all sheets
python3 {baseDir}/scripts/excel.py read workbook.xlsx

# Read sheet as table
python3 {baseDir}/scripts/excel.py read workbook.xlsx "Sheet1"

# Read as JSON
python3 {baseDir}/scripts/excel.py read workbook.xlsx "Sheet1" --json

# Create new workbook
python3 {baseDir}/scripts/excel.py create "MySheet" -o output.xlsx

# Create with headers
python3 {baseDir}/scripts/excel.py create "Data" -o data.xlsx -h "Name,Email,Phone"

# Append row
python3 {baseDir}/scripts/excel.py append workbook.xlsx "Sheet1" Name=Bob Email=bob@example.com Phone=555-1234
```

## Examples

```bash
# Extract text from Word document
python3 {baseDir}/scripts/word.py read ~/Documents/report.docx

# Create interview notes document
python3 {baseDir}/scripts/word.py create "Interview Notes" -o notes.docx
python3 {baseDir}/scripts/word.py append notes.docx --heading 1 "Candidate: Jane Doe"
python3 {baseDir}/scripts/word.py append notes.docx "Strong background in software engineering."
python3 {baseDir}/scripts/word.py append notes.docx --heading 2 "Strengths"
python3 {baseDir}/scripts/word.py append notes.docx --list "Excellent communication"
python3 {baseDir}/scripts/word.py append notes.docx --list "5+ years experience"

# Create expense tracker
python3 {baseDir}/scripts/excel.py create "Expenses" -o expenses.xlsx -h "Date,Category,Amount,Description"
python3 {baseDir}/scripts/excel.py append expenses.xlsx "Expenses" Date=2026-03-09 Category=Travel Amount=150 Description="Flight to NYC"

# Read all data from spreadsheet
python3 {baseDir}/scripts/excel.py read expenses.xlsx "Expenses"
```

## Notes

- Requires: `python-docx` (Word) and `openpyxl` (Excel) — already installed
- Word output preserves formatting, styles, and tables
- Excel supports multiple sheets and cell formatting
- JSON mode useful for programmatic processing
