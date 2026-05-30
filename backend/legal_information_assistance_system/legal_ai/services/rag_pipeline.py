from typing import Any, Dict, List

from legal_ai.models import LegalDocument, LegalChunk
from legal_ai.services.embedding import create_query_embedding, embedding_model
from legal_ai.services.llm import llm
from legal_ai.services.pdf_loader import extract_pdf_text
from legal_ai.services.smart_chunking import SmartLegalChunker
from legal_ai.services.text_cleaning import clean_text
from legal_ai.storage.vector_db import FaissVectorStore


chunker = SmartLegalChunker()
vector_store = FaissVectorStore()


def _build_metadata_from_chunk(chunk: LegalChunk) -> Dict[str, Any]:
    return {
        "doc_id": chunk.doc.id,
        "document_title": chunk.doc.title,
        "document_type": chunk.doc.document_type,
        "file_name": chunk.doc.file.name,
        "text": chunk.text,
        "part": chunk.part,
        "chapter": chunk.chapter,
        "section": chunk.section,
        "dhara": chunk.dhara,
    }


def rebuild_index_from_chunks() -> bool:
    """Rebuild the FAISS index from existing stored LegalChunk rows."""
    chunks = list(LegalChunk.objects.select_related("doc").all())
    if not chunks:
        return False

    texts = [chunk.text for chunk in chunks]
    embeddings = embedding_model.embed_batch(texts)

    vector_store.reset(embeddings.shape[1])

    metadata = [_build_metadata_from_chunk(chunk) for chunk in chunks]
    vector_store.add(embeddings, metadata)

    return True


# =========================
# PROCESS PDF → STORE DATA
# =========================
def process_pdf(document_id: int) -> Dict[str, Any]:
    document = LegalDocument.objects.get(id=document_id)

    raw_text = extract_pdf_text(document.file.path)
    cleaned_text = clean_text(raw_text)
    chunks = chunker.chunk(cleaned_text)

    if not chunks:
        return {"status": "failed", "message": "No valid text found in PDF."}

    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedding_model.embed_batch(texts)

    vector_store.load(dimension=embeddings.shape[1])

    for i, chunk in enumerate(chunks):
        # ✅ 1. SAVE IN DATABASE (IMPORTANT FIX)
        LegalChunk.objects.create(
            doc=document,
            text=chunk["text"],
            part=chunk.get("part"),
            chapter=chunk.get("chapter"),
            section=chunk.get("section"),
            dhara=chunk.get("dhara"),
        )

    # ✅ 2. STORE IN FAISS
    metadata = []
    for chunk in chunks:
        metadata.append({
            "doc_id": document_id,
            "document_title": document.title,
            "document_type": document.document_type,
            "file_name": document.file.name,
            **chunk,
        })

    vector_store.add(embeddings, metadata)

    return {
        "status": "success",
        "chunk_count": len(chunks),
    }


# =========================
# SEARCH FUNCTION
# =========================
def search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    if not query or not query.strip():
        return []

    vector_store.load()

    if not vector_store.has_embeddings():
        # If the store is missing but chunks exist, rebuild the index from DB.
        if rebuild_index_from_chunks():
            vector_store.load()
        else:
            return []

    query_vector = create_query_embedding(query).reshape(1, -1)

    distances, indices = vector_store.search(query_vector, top_k)

    results: List[Dict[str, Any]] = []

    for score, idx in zip(
        distances[0].tolist(),
        indices[0].tolist()
    ):
        if idx < 0 or idx >= len(vector_store.metadata):
            continue

        entry = dict(vector_store.metadata[idx])
        entry["score"] = float(score)
        results.append(entry)

    return results


# =========================
# ANSWER GENERATION
# =========================
def answer_query(query: str, top_k: int = 5) -> Dict[str, Any]:
    hits = search(query, top_k)

    if not hits:
        has_docs = LegalDocument.objects.exists()
        has_chunks = LegalChunk.objects.exists()

        if not has_docs:
            message = "No legal documents are available in the system. Please upload a PDF first."
        elif not has_chunks:
            message = (
                "Documents exist, but no chunks are indexed yet. "
                "Please upload and index the documents, or restart the ingestion process."
            )
        else:
            message = "No relevant legal documents found in the indexed content."

        return {
            "query": query,
            "answer": message,
            "sources": [],
        }

    context = "\n\n".join([
        f"Source: {hit.get('document_title')} ({hit.get('section_header', 'unknown')})\n{hit.get('text', '')}"
        for hit in hits
    ])

    answer = llm.generate(query, context)

    return {
        "query": query,
        "answer": answer,
        "sources": [
            {
                "document_id": hit.get("doc_id"),
                "document_title": hit.get("document_title"),
                "section": hit.get("section_header"),
                "score": hit.get("score"),
            }
            for hit in hits
        ],
    }