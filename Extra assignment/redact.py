import argparse
from typing import Iterable, Set

import fitz  # PyMuPDF
from presidio_analyzer import AnalyzerEngine


def unique_detected_texts(source_text: str, results: Iterable) -> Set[str]:
    """Collect unique non-empty detected PII substrings using start/end offsets."""
    values = set()
    for result in results:
        value = source_text[result.start : result.end].strip()
        if value:
            values.add(value)
    return values


def redact_pdf(input_pdf: str, output_pdf: str) -> None:
    analyzer = AnalyzerEngine()
    doc = fitz.open(input_pdf)

    for page_index in range(len(doc)):
        page = doc[page_index]
        page_text = page.get_text("text")

        if not page_text.strip():
            continue

        detections = analyzer.analyze(text=page_text, language="en", return_decision_process=False)
        pii_values = unique_detected_texts(page_text, detections)

        for pii_text in pii_values:
            # Find all occurrences of detected text on this page and mark for redaction.
            for rect in page.search_for(pii_text):
                page.add_redact_annot(rect, fill=(0, 0, 0))

        page.apply_redactions()

    doc.save(output_pdf)
    doc.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect and redact PII in a PDF using Presidio + PyMuPDF.")
    parser.add_argument("input_pdf", help="Path to source PDF")
    parser.add_argument("output_pdf", help="Path to write redacted PDF")
    args = parser.parse_args()

    redact_pdf(args.input_pdf, args.output_pdf)
    print(f"Redacted PDF saved to: {args.output_pdf}")


if __name__ == "__main__":
    main()
