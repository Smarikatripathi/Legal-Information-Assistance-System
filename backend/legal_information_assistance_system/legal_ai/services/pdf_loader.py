from pypdf import PdfReader
from pathlib import Path
import re


PDF_FOLDER = r"C:\Users\ACER\OneDrive\Desktop\Legal Information System\backend\media\legal_docs"


def extract_pdf_text(file_path: str) -> str:
    """
    Extract text from a single PDF
    """

    reader = PdfReader(file_path)

    full_text = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            full_text.append(text)

    return "\n".join(full_text)


def clean_text(text: str) -> str:

    # remove weird spacing between letters
    text = re.sub(r"(?<=[A-Za-z])\s(?=[A-Za-z])", "", text)

    # fix multiple spaces
    text = re.sub(r"\s+", " ", text)

    # fix broken line spacing
    text = re.sub(r"\n{2,}", "\n\n", text)

    return text.strip()


def load_all_pdfs():
    """
    Load all PDFs from folder
    """

    pdf_path = Path(PDF_FOLDER)

    all_documents = []

    for pdf_file in pdf_path.glob("*.pdf"):

        print(f"Processing: {pdf_file.name}")

        raw_text = extract_pdf_text(str(pdf_file))

        cleaned_text = clean_text(raw_text)

        document_data = {
            "file_name": pdf_file.name,
            "raw": raw_text,
            "content": cleaned_text,
        }

        all_documents.append(document_data)

    return all_documents

# RUN TEST
if __name__ == "__main__":
    documents = load_all_pdfs()

    print(f"\nTOTAL PDFs LOADED: {len(documents)}")

    for doc in documents:
        print("\n" + "=" * 70)
        print("FILE:", doc["file_name"])
        print("=" * 70)

        raw = doc["raw"]
        cleaned = doc["content"]

        print("\nRAW LENGTH:", len(raw))
        print("CLEANED LENGTH:", len(cleaned))

        print("\n--- RAW SAMPLE ---\n")
        print(raw[:800])

        print("\n--- CLEANED SAMPLE ---\n")
        print(cleaned[:800])