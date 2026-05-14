from .pdf_loader import PDFLoader
from .preprocessing import TextPreprocessor


class RAGPipeline:

    def __init__(self):
        self.loader = PDFLoader()
        self.preprocessor = TextPreprocessor()

    def build_dataset(self):
        """Convert all PDFs into clean chunks"""

        pdfs = self.loader.load_all_pdfs()

        dataset = []

        for pdf in pdfs:
            file_name = pdf["file_name"]
            text = self.preprocessor.clean(pdf["text"])

            chunks = self.preprocessor.chunk_text(text)

            for i, chunk in enumerate(chunks):
                dataset.append({
                    "file": file_name,
                    "chunk_id": i,
                    "text": chunk
                })

        return dataset