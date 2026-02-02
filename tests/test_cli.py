"""CLI integration tests using Click's CliRunner."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from pdf_organizer.cli import main


def _make_dummy_pdf(path: Path) -> None:
    """Create a minimal valid PDF file."""
    # Minimal PDF that pdfplumber can open (single blank page).
    content = (
        b"%PDF-1.0\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"trailer<</Size 4/Root 1 0 R>>\n"
        b"startxref\n190\n%%EOF"
    )
    path.write_bytes(content)


class TestCliDryRun:
    def test_dry_run_no_renames(self, tmp_path):
        _make_dummy_pdf(tmp_path / "test.pdf")

        runner = CliRunner()
        result = runner.invoke(main, [str(tmp_path), "--dry-run"])

        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        # File should still exist with original name.
        assert (tmp_path / "test.pdf").exists()

    def test_dry_run_shows_would_rename(self, tmp_path):
        _make_dummy_pdf(tmp_path / "report.pdf")

        # Mock extract_text to return classifiable text.
        with patch("pdf_organizer.renamer.extract_text") as mock_extract:
            mock_extract.return_value = (
                "Chase Bank\nAccount Summary\nBalance: $1000\n"
                "Date: 03/15/2024\n"
            )
            runner = CliRunner()
            result = runner.invoke(main, [str(tmp_path), "--dry-run"])

        assert result.exit_code == 0
        assert "WOULD RENAME" in result.output
        # Original file untouched.
        assert (tmp_path / "report.pdf").exists()


class TestCliNormalMode:
    def test_renames_and_creates_csv(self, tmp_path):
        _make_dummy_pdf(tmp_path / "doc.pdf")

        with patch("pdf_organizer.renamer.extract_text") as mock_extract:
            mock_extract.return_value = (
                "Aetna Insurance Company\n"
                "Policy Number: HLT-999\n"
                "Coverage Effective: 01/01/2024\n"
                "Premium: $300/month\n"
            )
            csv_path = tmp_path / "log.csv"
            runner = CliRunner()
            result = runner.invoke(
                main, [str(tmp_path), "--output-csv", str(csv_path)]
            )

        assert result.exit_code == 0
        assert "RENAME" in result.output
        assert csv_path.exists()
        # Original should be gone (renamed).
        assert not (tmp_path / "doc.pdf").exists()

    def test_summary_counts(self, tmp_path):
        _make_dummy_pdf(tmp_path / "a.pdf")
        _make_dummy_pdf(tmp_path / "b.pdf")

        with patch("pdf_organizer.renamer.extract_text") as mock_extract:
            # First file classifiable, second returns empty text -> Unknown
            mock_extract.side_effect = [
                "Invoice #001\nBill To: Someone\nAmount Due: $100\nDate: 05/01/2024\n",
                "",
            ]
            runner = CliRunner()
            result = runner.invoke(main, [str(tmp_path), "--dry-run"])

        assert result.exit_code == 0
        assert "1 renamed" in result.output
        assert "1 skipped" in result.output


class TestCliMissingFolder:
    def test_nonexistent_folder(self):
        runner = CliRunner()
        result = runner.invoke(main, ["/nonexistent/path/xyz"])
        assert result.exit_code != 0
