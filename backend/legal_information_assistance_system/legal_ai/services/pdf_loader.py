from pathlib import Path
from typing import List

from pypdf import PdfReader
from pypdf.errors import PdfReadError



def extract_pdf_text(file_path: str) -> str:
    """
    Extract text safely from PDF.
    Handles empty pages and None returns.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    try:
        reader = PdfReader(str(path))
    except PdfReadError as exc:
        raise ValueError(f"Unable to parse PDF document: {exc}") from exc

    pages_text: List[str] = []

    for page_number, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text()
        except Exception:
            continue

        if not page_text:
            continue

        normalized = page_text.strip()
        if normalized:
            pages_text.append(normalized)

    return "\n\n".join(pages_text)


