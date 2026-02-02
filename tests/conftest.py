"""Shared fixtures for pdf-organizer tests."""

import pytest


@pytest.fixture()
def tax_text():
    return (
        "Internal Revenue Service\n"
        "Form 1040 - U.S. Individual Income Tax Return\n"
        "Tax Year 2023\n"
        "Adjusted Gross Income: $75,000\n"
        "Date: 04/15/2024\n"
    )


@pytest.fixture()
def bank_text():
    return (
        "Chase Bank\n"
        "Monthly Account Summary\n"
        "Statement Period: January 1, 2024 - January 31, 2024\n"
        "Beginning Balance: $5,230.00\n"
        "Total Deposits: $3,200.00\n"
        "Total Withdrawals: $2,100.00\n"
        "Ending Balance: $6,330.00\n"
    )


@pytest.fixture()
def insurance_text():
    return (
        "Aetna Insurance Company\n"
        "Policy Number: HLT-12345\n"
        "Coverage Effective: 01/01/2024\n"
        "Premium: $450.00/month\n"
        "Deductible: $1,500\n"
        "Insured: John Doe\n"
    )


@pytest.fixture()
def invoice_text():
    return (
        "Acme Corporation\n"
        "Invoice #INV-2024-0042\n"
        "Bill To: Jane Smith\n"
        "Date: 2024-03-15\n"
        "Amount Due: $1,250.00\n"
        "Payment Due: April 15, 2024\n"
    )


@pytest.fixture()
def unknown_text():
    return "Some random text with no identifiable patterns."
