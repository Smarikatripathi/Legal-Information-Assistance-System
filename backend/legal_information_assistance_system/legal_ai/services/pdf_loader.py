import os
from langchain_community.document_loaders import PyPDFLoader


# Current file directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# PDFs folder path
PDF_FOLDER = os.path.join(BASE_DIR, "data", "pdfs")


def load_pdfs():

    documents = []

    print("PDF Folder:", PDF_FOLDER)

    for file_name in os.listdir(PDF_FOLDER):

        if file_name.endswith(".pdf"):

            file_path = os.path.join(PDF_FOLDER, file_name)

            print(f"Loading: {file_name}")

            loader = PyPDFLoader(file_path)

            docs = loader.load()

            documents.extend(docs)

    return documents


documents = load_pdfs()

print(f"\nTotal Pages Loaded: {len(documents)}")