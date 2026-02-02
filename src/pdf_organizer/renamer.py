"""File renaming logic, collision handling, and CSV logging."""

import csv
import logging
import re
from pathlib import Path

from pdf_organizer.classifier import classify
from pdf_organizer.extractor import extract_text

logger = logging.getLogger(__name__)


def _sanitize(name: str) -> str:
    """Remove special characters and replace spaces with underscores."""
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name


def build_new_name(classification: dict[str, str], original: Path) -> str:
    """Build a new filename from classification results.

    Format: {Type}_{Institution}_{Date}.pdf
    Segments with empty values are omitted.
    """
    parts: list[str] = [classification["doc_type"]]

    institution = classification.get("institution", "")
    if institution:
        parts.append(_sanitize(institution))

    date = classification.get("date", "")
    if date:
        parts.append(date)

    if len(parts) == 1 and parts[0] == "Unknown":
        # Nothing useful detected — keep the original name.
        return original.name

    return "_".join(parts) + ".pdf"


def _resolve_collision(target: Path) -> Path:
    """Append _2, _3, … until the path is unique."""
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    parent = target.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def rename_files(
    folder: Path,
    dry_run: bool = False,
) -> list[dict[str, str]]:
    """Scan *folder* for PDFs, classify each, and rename (or preview).

    Returns a list of result dicts suitable for CSV logging.
    """
    results: list[dict[str, str]] = []
    pdf_files = sorted(folder.glob("*.pdf"))

    for pdf_path in pdf_files:
        text = extract_text(pdf_path)
        info = classify(text)
        new_name = build_new_name(info, pdf_path)

        status = "renamed"
        if new_name == pdf_path.name:
            status = "skipped"
        else:
            target = _resolve_collision(folder / new_name)
            new_name = target.name
            if not dry_run:
                try:
                    pdf_path.rename(target)
                except OSError as exc:
                    logger.error("Failed to rename %s: %s", pdf_path.name, exc)
                    status = "error"

        results.append({
            "original_name": pdf_path.name,
            "new_name": new_name,
            "doc_type": info["doc_type"],
            "institution": info["institution"],
            "date": info["date"],
            "status": status,
        })

    return results


def write_csv_log(results: list[dict[str, str]], output_path: Path) -> None:
    """Write rename results to a CSV file."""
    fieldnames = ["original_name", "new_name", "doc_type", "institution", "date"]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
