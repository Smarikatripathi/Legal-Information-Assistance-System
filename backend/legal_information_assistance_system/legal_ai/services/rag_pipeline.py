import numpy as np
import faiss

from legal_ai.models import LegalChunk, LegalDocument

from .pdf_loader import extract_pdf_text, clean_text
from .smart_chunking import smart_chunk
from .embedding import create_embedding
from legal_ai.storage.vector_db import save_index, load_index


def process_pdf(doc_id, file_path):

    raw_text = extract_pdf_text(file_path)

    cleaned = clean_text(raw_text)

    chunks = smart_chunk(cleaned)

    embeddings = create_embedding(chunks)

    dimension = embeddings.shape[1]

    try:
        index, stored_chunks = load_index()

    except:
        index = faiss.IndexFlatL2(dimension)
        stored_chunks = []

    doc = LegalDocument.objects.get(id=doc_id)

    for i, chunk_text in enumerate(chunks):

        chunk = LegalChunk.objects.create(
            doc=doc,
            text=chunk_text,
        )

        stored_chunks.append({
            "db_id": chunk.id,
            "text": chunk_text,
        })

    index.add(np.array(embeddings).astype("float32"))

    save_index(index, stored_chunks)


def search(query, top_k=5):

    index, stored_chunks = load_index()

    query_embedding = create_embedding([query])

    D, I = index.search(
        np.array(query_embedding).astype("float32"),
        top_k
    )

    results = []

    for idx in I[0]:

        if idx < len(stored_chunks):

            db_id = stored_chunks[idx]["db_id"]

            chunk = LegalChunk.objects.get(id=db_id)

            results.append(chunk)

    return results
