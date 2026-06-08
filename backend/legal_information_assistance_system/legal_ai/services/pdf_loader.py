import re
from collections import Counter
from pathlib import Path
from typing import List, Tuple

from pypdf import PdfReader
from pypdf.errors import PdfReadError

PAGE_NUMBER_PATTERN = re.compile(r"^\s*\d{1,4}\s*$")
WATERMARK_PATTERNS = [
    re.compile(r"draft", re.I),
    re.compile(r"confidential", re.I),
    re.compile(r"do not distribute", re.I),
]


def _normalize_page_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _detect_repeated_lines(pages: List[str], min_ratio: float = 0.6) -> set[str]:
    """Find header/footer lines repeated across most pages."""
    if len(pages) < 3:
        return set()

    threshold = max(2, int(len(pages) * min_ratio))
    first_lines: Counter[str] = Counter()
    last_lines: Counter[str] = Counter()

    for page in pages:
        lines = [line.strip() for line in page.splitlines() if line.strip()]
        if not lines:
            continue
        first_lines[lines[0]] += 1
        if len(lines) > 1:
            last_lines[lines[-1]] += 1

    repeated = set()
    for line, count in first_lines.items():
        if count >= threshold and len(line) < 120:
            repeated.add(line)
    for line, count in last_lines.items():
        if count >= threshold and len(line) < 120:
            repeated.add(line)
    return repeated


def _clean_page(page_text: str, repeated_lines: set[str]) -> str:
    lines = page_text.splitlines()
    cleaned_lines: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue
        if stripped in repeated_lines:
            continue
        if PAGE_NUMBER_PATTERN.match(stripped):
            continue
        if any(pattern.search(stripped) for pattern in WATERMARK_PATTERNS):
            continue
        cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)


def extract_pdf_text(file_path: str) -> Tuple[str, int]:
    """
    Extract text from PDF with header/footer/page-number removal.
    Returns (text, page_count).
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    try:
        reader = PdfReader(str(path))
    except PdfReadError as exc:
        raise ValueError(f"Unable to parse PDF document: {exc}") from exc

    raw_pages: List[str] = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""
        normalized = page_text.strip()
        if normalized:
            raw_pages.append(normalized)

    repeated_lines = _detect_repeated_lines(raw_pages)
    cleaned_pages = [_clean_page(page, repeated_lines) for page in raw_pages]
    cleaned_pages = [page for page in cleaned_pages if page.strip()]

    return "\n\n".join(cleaned_pages), len(reader.pages)
