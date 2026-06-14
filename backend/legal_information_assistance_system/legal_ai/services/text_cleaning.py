import re

WHITESPACE_RULES = [
    (re.compile(r"\r\n?"), "\n"),
    (re.compile(r"[ \t]+"), " "),
    (re.compile(r"\n{3,}"), "\n\n"),
    (re.compile(r"\s+([,.;:])"), r"\1"),
]

# Standalone page numbers and PDF artifacts
ARTIFACT_PATTERNS = [
    re.compile(r"^\s*\d{1,4}\s*$", re.M),
    re.compile(r"\f"),  # form feed
    re.compile(r"-\s*\n\s*", re.M),  # hyphenated line breaks
    re.compile(r"([a-z])-\s+([a-z])", re.I),  # broken words
]

# Fix spaced letters from PDF extraction: "t o" -> "to" (conservative)
BROKEN_WORD_PATTERN = re.compile(r"\b([a-z])\s([a-z])\b", re.I)


def clean_text(text: str) -> str:
    """
    Normalize extracted PDF text while preserving legal structure markers.
    """
    if not text:
        return ""

    cleaned = text.replace("\u00A0", " ").strip()

    for pattern in ARTIFACT_PATTERNS:
        cleaned = pattern.sub("", cleaned)

    # Rejoin hyphenated words split across lines
    cleaned = re.sub(r"([A-Za-z\u0900-\u097F])-\n([A-Za-z\u0900-\u097F])", r"\1\2", cleaned)

    for pattern, replacement in WHITESPACE_RULES:
        cleaned = pattern.sub(replacement, cleaned)

    # Preserve legal line breaks before Part/Chapter/Section/Article headers
    header_break = re.compile(
        r"(?<!\n)\s+(?=(?:Part|Chapter|Section|Article|Clause|भाग|धारा|परिच्छेद|दफा)\s*[\d०-९]+)",
        re.I,
    )
    cleaned = header_break.sub("\n\n", cleaned)

    cleaned = re.sub(r"\n{2,}", "\n\n", cleaned)
    return cleaned.strip()
