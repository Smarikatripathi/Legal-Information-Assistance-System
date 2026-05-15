from pypdf import PdfReader
import re


def extract_pdf_text(file_path: str) -> str:
    """
    Extract raw text from PDF
    """
    reader = PdfReader(file_path)

    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"

    return text


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()