import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

from legal_ai.models import LegalChunk, LegalDocument
from .smart_chunking import smart_chunk
from .text_extract import clean_text
from .pdf_loader import load_pdf

# multilingual model
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

dimension = 384
index = faiss.IndexFlatL2(dimension)


def embed(text):
    return model.encode(text).astype("float32")


def process_pdf(doc_id, file_path):
    """
    FULL ingestion pipeline
    """

    raw_text = load_pdf(file_path)
    clean = clean_text(raw_text)

    doc = LegalDocument.objects.get(id=doc_id)

    chunks = smart_chunk(clean, doc.title)

    vectors = []

    for i, c in enumerate(chunks):
        vector = embed(c["text"])
        vectors.append(vector)

        # store chunk in DB
        chunk_obj = LegalChunk.objects.create(
            doc=doc,
            text=c["text"]
        )

        chunk_obj.embedding_id = index.ntotal + i
        chunk_obj.save()

    if vectors:
        index.add(np.array(vectors))

def search(query, top_k=5):
    q_vec = embed(query).reshape(1, -1)

    distances, indices = index.search(q_vec, top_k)

    results = []

    for i in indices[0]:
        chunk = LegalChunk.objects.filter(embedding_id=i).first()
        if chunk:
            results.append(chunk)

    return results
