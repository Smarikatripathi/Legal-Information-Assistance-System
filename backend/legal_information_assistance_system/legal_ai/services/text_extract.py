import os
from PyPDF2 import PdfReader
#from legal_ai.services.legal_parser import NepalLegalParser
from legal_information_assistance_system.legal_ai.services.legal_parser import NepalLegalParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PDF_FOLDER = os.path.join(BASE_DIR, "data", "pdfs")


def extract_text():

    all_data = []

    print("PDF Folder:", PDF_FOLDER)

    for file in os.listdir(PDF_FOLDER):

        if file.endswith(".pdf"):

            path = os.path.join(PDF_FOLDER, file)

            print(f"Reading: {file}")

            reader = PdfReader(path)

            for page_num, page in enumerate(reader.pages):

                text = page.extract_text()

                if text:

                    text = " ".join(text.split())

                    all_data.append({
                        "text": text,
                        "source": file,
                        "page": page_num + 1
                    })

    return all_data


# =========================
# RUN TEST PROPERLY
# =========================
if __name__ == "__main__":

    # STEP 1: Extract
    documents = extract_text()

    print("\nTOTAL PAGES:", len(documents))

    # STEP 2: Parse
    parser = NepalLegalParser()
    chunks = parser.parse(documents)

    print("\nTOTAL CHUNKS:", len(chunks))

    # STEP 3: Sample
    print("\n================ SAMPLE ================\n")
    print(chunks[0])

    # STEP 4: Preview
    for chunk in chunks[:3]:

        print("\n-------------------")
        print("TITLE:", chunk["title"])
        print("SOURCE:", chunk["source"])
        print("PAGES:", chunk["pages"])
        print("TEXT:", chunk["content"][:200])