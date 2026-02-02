"""Tests for the renamer module."""

import csv
from pathlib import Path

from pdf_organizer.renamer import build_new_name, write_csv_log, _sanitize


class TestSanitize:
    def test_spaces_to_underscores(self):
        assert _sanitize("Bank of America") == "Bank_of_America"

    def test_special_chars_removed(self):
        assert _sanitize("AT&T") == "ATT"

    def test_already_clean(self):
        assert _sanitize("Chase") == "Chase"


class TestBuildNewName:
    def test_full_classification(self):
        info = {"doc_type": "Bank_Statement", "institution": "Chase", "date": "2024-01-31"}
        name = build_new_name(info, Path("old.pdf"))
        assert name == "Bank_Statement_Chase_2024-01-31.pdf"

    def test_no_institution(self):
        info = {"doc_type": "Invoice", "institution": "", "date": "2024-03-15"}
        name = build_new_name(info, Path("old.pdf"))
        assert name == "Invoice_2024-03-15.pdf"

    def test_no_date(self):
        info = {"doc_type": "Insurance", "institution": "Aetna", "date": ""}
        name = build_new_name(info, Path("old.pdf"))
        assert name == "Insurance_Aetna.pdf"

    def test_no_institution_no_date(self):
        info = {"doc_type": "Medical", "institution": "", "date": ""}
        name = build_new_name(info, Path("old.pdf"))
        assert name == "Medical.pdf"

    def test_unknown_keeps_original(self):
        info = {"doc_type": "Unknown", "institution": "", "date": ""}
        name = build_new_name(info, Path("mystery.pdf"))
        assert name == "mystery.pdf"

    def test_unknown_with_date_renames(self):
        info = {"doc_type": "Unknown", "institution": "", "date": "2024-01-01"}
        name = build_new_name(info, Path("mystery.pdf"))
        assert name == "Unknown_2024-01-01.pdf"

    def test_institution_sanitized(self):
        info = {"doc_type": "Invoice", "institution": "AT&T", "date": ""}
        name = build_new_name(info, Path("old.pdf"))
        assert name == "Invoice_ATT.pdf"


class TestWriteCsvLog:
    def test_writes_correct_csv(self, tmp_path):
        results = [
            {
                "original_name": "old.pdf",
                "new_name": "Bank_Statement_Chase_2024-01-31.pdf",
                "doc_type": "Bank_Statement",
                "institution": "Chase",
                "date": "2024-01-31",
                "status": "renamed",
            },
        ]
        csv_path = tmp_path / "log.csv"
        write_csv_log(results, csv_path)

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["original_name"] == "old.pdf"
        assert rows[0]["new_name"] == "Bank_Statement_Chase_2024-01-31.pdf"
        assert rows[0]["doc_type"] == "Bank_Statement"
        assert rows[0]["institution"] == "Chase"
        assert rows[0]["date"] == "2024-01-31"
        # status column is excluded from CSV
        assert "status" not in rows[0]

    def test_multiple_rows(self, tmp_path):
        results = [
            {
                "original_name": "a.pdf",
                "new_name": "Invoice_2024-01-01.pdf",
                "doc_type": "Invoice",
                "institution": "",
                "date": "2024-01-01",
                "status": "renamed",
            },
            {
                "original_name": "b.pdf",
                "new_name": "b.pdf",
                "doc_type": "Unknown",
                "institution": "",
                "date": "",
                "status": "skipped",
            },
        ]
        csv_path = tmp_path / "log.csv"
        write_csv_log(results, csv_path)

        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2


class TestCollisionHandling:
    def test_collision_appends_suffix(self, tmp_path):
        # Create a file that would collide.
        (tmp_path / "Bank_Statement_Chase_2024-01-31.pdf").touch()

        from pdf_organizer.renamer import _resolve_collision

        target = tmp_path / "Bank_Statement_Chase_2024-01-31.pdf"
        resolved = _resolve_collision(target)
        assert resolved.name == "Bank_Statement_Chase_2024-01-31_2.pdf"

    def test_multiple_collisions(self, tmp_path):
        (tmp_path / "Invoice_2024-01-01.pdf").touch()
        (tmp_path / "Invoice_2024-01-01_2.pdf").touch()

        from pdf_organizer.renamer import _resolve_collision

        target = tmp_path / "Invoice_2024-01-01.pdf"
        resolved = _resolve_collision(target)
        assert resolved.name == "Invoice_2024-01-01_3.pdf"
