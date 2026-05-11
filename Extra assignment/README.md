# PDF PII redaction (`redact.py`)

## Prompt

Write a Python script that:

1. Opens a PDF using PyMuPDF
2. Extracts text
3. Uses Microsoft Presidio to detect PII
4. Redacts the detected text in the PDF
5. Saves a new redacted PDF

Keep it simple and runnable.

## What it does

This script processes a PDF end-to-end:

1. **Opens the PDF** with [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`).
2. **Extracts text** from each page as plain text.
3. **Detects PII** with [Microsoft Presidio](https://microsoft.github.io/presidio/) (`AnalyzerEngine`), using the English analyzer on each page’s text.
4. **Redacts matches** in the PDF: for each unique detected substring, it finds all occurrences on that page with `search_for`, draws black redaction annotations, then applies redactions so the underlying content is removed (not just hidden).
5. **Saves a new file** at the path you pass as the second argument. The original PDF is not modified.

**Usage:**

```bash
python redact.py <input.pdf> <output_redacted.pdf>
```

