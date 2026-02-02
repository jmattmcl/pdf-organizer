"""PDF text extraction using pdfplumber."""

import logging
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)


def extract_text(pdf_path: Path) -> str:
    """Open a PDF and concatenate text from all pages.

    Returns empty string on extraction failure.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return "\n".join(pages)
    except Exception as exc:
        logger.warning("Failed to extract text from %s: %s", pdf_path, exc)
        return ""
