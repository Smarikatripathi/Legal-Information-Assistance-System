import re
import unicodedata

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

# Fix spaced Devanagari characters: "ने प ल" -> "नेपाल"
SPACED_DEVANAGARI_PATTERN = re.compile(r'([\u0900-\u097F])\s([\u0900-\u097F])')


def normalize_nepali_unicode(text: str) -> str:
    """Normalize Devanagari Unicode to NFC form for consistent embeddings."""
    return unicodedata.normalize('NFC', text)


def normalize_nepali_punctuation(text: str) -> str:
    """Standardize Nepali punctuation marks while preserving sentence boundaries."""
    # Keep danda for sentence splitting but normalize for consistency
    # Don't replace danda with period - it's needed for Nepali sentence detection
    return text


def fix_spaced_devanagari(text: str) -> str:
    """Fix spaced Devanagari characters common in PDF extraction."""
    return SPACED_DEVANAGARI_PATTERN.sub(r'\1\2', text)


def clean_text(text: str) -> str:
    """
    Normalize extracted PDF text while preserving legal structure markers.
    Enhanced with Nepali-specific normalization.
    """
    if not text:
        return ""

    # Normalize Unicode first
    cleaned = normalize_nepali_unicode(text)
    cleaned = cleaned.replace("\u00A0", " ").strip()

    # Fix spaced Devanagari characters
    cleaned = fix_spaced_devanagari(cleaned)

    for pattern in ARTIFACT_PATTERNS:
        cleaned = pattern.sub("", cleaned)

    # Rejoin hyphenated words split across lines (both English and Nepali)
    cleaned = re.sub(r"([A-Za-z\u0900-\u097F])-\n([A-Za-z\u0900-\u097F])", r"\1\2", cleaned)

    for pattern, replacement in WHITESPACE_RULES:
        cleaned = pattern.sub(replacement, cleaned)

    # Preserve legal line breaks before Part/Chapter/Section/Article/Rule/Subrule headers
    header_break = re.compile(
        r"(?<!\n)\s+(?=(?:Part|Chapter|Section|Article|Clause|Rule|नियम|उपनियम|अनुच्छेद|अनुसूची|भाग|धारा|परिच्छेद|दफा)\s*[\d०-९A-Za-z]+)",
        re.I,
    )
    cleaned = header_break.sub("\n\n", cleaned)

    cleaned = re.sub(r"\n{2,}", "\n\n", cleaned)
    return cleaned.strip()
