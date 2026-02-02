"""Tests for the classifier module."""

from pdf_organizer.classifier import classify


class TestDocTypeDetection:
    def test_tax_return(self, tax_text):
        result = classify(tax_text)
        assert result["doc_type"] == "Tax_Return"

    def test_bank_statement(self, bank_text):
        result = classify(bank_text)
        assert result["doc_type"] == "Bank_Statement"

    def test_insurance(self, insurance_text):
        result = classify(insurance_text)
        assert result["doc_type"] == "Insurance"

    def test_invoice(self, invoice_text):
        result = classify(invoice_text)
        assert result["doc_type"] == "Invoice"

    def test_receipt(self):
        text = "Receipt\nThank you for your purchase\nTransaction #12345\nPaid: $29.99"
        result = classify(text)
        assert result["doc_type"] == "Receipt"

    def test_medical(self):
        text = "Patient: John Doe\nDiagnosis: Routine checkup\nPrescription: None"
        result = classify(text)
        assert result["doc_type"] == "Medical"

    def test_contract(self):
        text = "Agreement between the parties\nTerms and Conditions\nHereby agreed upon"
        result = classify(text)
        assert result["doc_type"] == "Contract"

    def test_unknown(self, unknown_text):
        result = classify(unknown_text)
        assert result["doc_type"] == "Unknown"


class TestInstitutionDetection:
    def test_known_institution_chase(self, bank_text):
        result = classify(bank_text)
        assert result["institution"] == "Chase"

    def test_known_institution_irs(self, tax_text):
        result = classify(tax_text)
        # "Internal Revenue Service" header appears first, but IRS is also known.
        # The first ~500 chars are scanned for known names.
        assert result["institution"] in ("IRS", "Internal Revenue Service")

    def test_known_institution_aetna(self, insurance_text):
        result = classify(insurance_text)
        assert result["institution"] == "Aetna"

    def test_heuristic_institution(self, invoice_text):
        result = classify(invoice_text)
        assert result["institution"] == "Acme Corporation"

    def test_no_institution(self, unknown_text):
        result = classify(unknown_text)
        assert result["institution"] == ""


class TestDateExtraction:
    def test_mm_dd_yyyy(self, tax_text):
        result = classify(tax_text)
        assert result["date"] == "2024-04-15"

    def test_month_dd_yyyy(self, bank_text):
        result = classify(bank_text)
        # Most recent date: January 31, 2024
        assert result["date"] == "2024-01-31"

    def test_yyyy_mm_dd(self, invoice_text):
        result = classify(invoice_text)
        # Most recent: April 15, 2024
        assert result["date"] == "2024-04-15"

    def test_no_date(self, unknown_text):
        result = classify(unknown_text)
        assert result["date"] == ""

    def test_picks_most_recent(self):
        text = "Date: 01/01/2020\nUpdated: 06/15/2023\nFiled: 12/31/2022"
        result = classify(text)
        assert result["date"] == "2023-06-15"
