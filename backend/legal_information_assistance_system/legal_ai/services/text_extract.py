from .pdf_loader import load_pdf

def extract_pdf_text(pdf_path):
    text = ""

    document = load_pdf(pdf_path)

    for page in document:
        text += page.get_text("text") + "\n"

    return text