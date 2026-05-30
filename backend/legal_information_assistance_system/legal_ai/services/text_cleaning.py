import re

WHITESPACE_RULES = [
    (re.compile(r"\r\n?"), "\n"),
    (re.compile(r"[ \t]+"), " "),
    (re.compile(r"\n{3,}"), "\n\n"),
    (re.compile(r"\s+([,.;:])"), r"\1"),
    (re.compile(r"([^\n])\n([^\n])"), r"\1 \2"),
]


def clean_text(text: str) -> str:
    """
    Normalize extracted PDF text while preserving legal boundaries.
    """
    if text is None:
        return ""

    cleaned = text.replace("\u00A0", " ").strip()

    for pattern, replacement in WHITESPACE_RULES:
        cleaned = pattern.sub(replacement, cleaned)

    cleaned = re.sub(r"\n{2,}", "\n\n", cleaned)
    return cleaned.strip()
