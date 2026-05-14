import fitz

def load_pdf(pdf_path):
    return fitz.open(pdf_path)