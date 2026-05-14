import re

class TextPreprocessor:

    def clean(self, text):
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def chunk_text(self, text, chunk_size=500, overlap=50):
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap

        return chunks