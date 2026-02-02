"""Document type classification, institution detection, and date extraction."""

import re
from datetime import datetime


# Document type keywords in priority order.
DOC_TYPE_RULES: list[tuple[str, list[str]]] = [
    ("Tax_Return", [
        r"\b1040\b", r"\bW-2\b", r"\bW-4\b", r"tax\s+return",
        r"\bIRS\b", r"adjusted\s+gross",
    ]),
    ("Bank_Statement", [
        r"\bstatement\b", r"account\s+summary", r"\bbalance\b",
        r"\bdeposits\b", r"\bwithdrawals\b",
    ]),
    ("Insurance", [
        r"\bpolicy\b", r"\bpremium\b", r"\bcoverage\b",
        r"\bdeductible\b", r"\binsured\b",
    ]),
    ("Invoice", [
        r"\binvoice\b", r"bill\s+to", r"amount\s+due", r"payment\s+due",
    ]),
    ("Receipt", [
        r"\breceipt\b", r"\bpaid\b", r"\btransaction\b",
        r"thank\s+you\s+for\s+your\s+purchase",
    ]),
    ("Medical", [
        r"\bpatient\b", r"\bdiagnosis\b", r"\bprescription\b",
        r"\bmedical\b", r"\bhealth\b",
    ]),
    ("Contract", [
        r"\bagreement\b", r"terms\s+and\s+conditions", r"\bhereby\b",
        r"\bparties\b",
    ]),
]

# Known institution names (case-insensitive matching).
KNOWN_INSTITUTIONS: list[str] = [
    "Chase", "Bank of America", "Wells Fargo", "Citibank", "Capital One",
    "US Bank", "PNC Bank", "TD Bank", "IRS",
    "Aetna", "Blue Cross", "Blue Shield", "UnitedHealthcare", "Cigna", "Humana",
    "State Farm", "Allstate", "Geico", "Progressive", "Liberty Mutual",
    "Amazon", "Walmart", "Target", "Costco", "Best Buy",
    "AT&T", "Verizon", "T-Mobile", "Comcast", "Xfinity",
    "Kaiser Permanente", "CVS", "Walgreens",
]

# Month names for date parsing.
_MONTHS = (
    "january|february|march|april|may|june|"
    "july|august|september|october|november|december"
)

# Date regex patterns, each with named groups y/m/d.
_DATE_PATTERNS: list[re.Pattern[str]] = [
    # MM/DD/YYYY or MM-DD-YYYY
    re.compile(
        r"\b(?P<m>\d{1,2})[/\-](?P<d>\d{1,2})[/\-](?P<y>\d{4})\b"
    ),
    # Month DD, YYYY
    re.compile(
        r"\b(?P<month>" + _MONTHS + r")\s+(?P<d>\d{1,2}),?\s+(?P<y>\d{4})\b",
        re.IGNORECASE,
    ),
    # YYYY-MM-DD
    re.compile(
        r"\b(?P<y>\d{4})-(?P<m>\d{1,2})-(?P<d>\d{1,2})\b"
    ),
]

_MONTH_MAP: dict[str, int] = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


def _detect_doc_type(text: str) -> str:
    text_lower = text.lower()
    for doc_type, patterns in DOC_TYPE_RULES:
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return doc_type
    return "Unknown"


def _detect_institution(text: str) -> str:
    # Search the first ~500 characters for known names.
    header = text[:500]
    for name in KNOWN_INSTITUTIONS:
        if re.search(re.escape(name), header, re.IGNORECASE):
            return name

    # Heuristic: first capitalized multi-word phrase that looks like a company.
    # Use [^\S\n]+ to avoid matching across line boundaries.
    match = re.search(r"\b([A-Z][a-z]+(?:[^\S\n]+[A-Z][a-z]+)+)\b", header)
    if match:
        return match.group(1)

    return ""


def _extract_date(text: str) -> str:
    """Extract the most recent date found in *text*, returned as YYYY-MM-DD."""
    dates: list[datetime] = []
    for pattern in _DATE_PATTERNS:
        for m in pattern.finditer(text):
            try:
                groups = m.groupdict()
                if "month" in groups:
                    month = _MONTH_MAP[groups["month"].lower()]
                    day = int(groups["d"])
                    year = int(groups["y"])
                else:
                    month = int(groups["m"])
                    day = int(groups["d"])
                    year = int(groups["y"])
                dates.append(datetime(year, month, day))
            except (ValueError, KeyError):
                continue

    if not dates:
        return ""
    most_recent = max(dates)
    return most_recent.strftime("%Y-%m-%d")


def classify(text: str) -> dict[str, str]:
    """Classify document text and return doc_type, institution, and date."""
    return {
        "doc_type": _detect_doc_type(text),
        "institution": _detect_institution(text),
        "date": _extract_date(text),
    }
