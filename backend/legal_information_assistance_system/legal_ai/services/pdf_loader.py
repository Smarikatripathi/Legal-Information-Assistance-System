from pypdf import PdfReader
from typing import List


def extract_pdf_text(file_path: str) -> str:
    """
    Extract text safely from PDF.
    Handles empty pages and None returns.
    """
    reader = PdfReader(file_path)

    pages_text: List[str] = []

    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text()
            if text and text.strip():
                pages_text.append(text)
        except Exception:
            # skip corrupted pages safely
            continue

    return "\n".join(pages_text)