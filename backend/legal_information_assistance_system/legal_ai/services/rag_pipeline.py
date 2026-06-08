import time
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.db import transaction

from legal_ai.models import EmbeddingConfig, LegalChunk, LegalDocument
from legal_ai.services.embedding import create_query_embedding, get_embedding_model
from legal_ai.services.hybrid_retrieval import MIN_SCORE, filter_by_threshold, hybrid_score
from legal_ai.services.llm import llm
from legal_ai.services.pdf_loader import extract_pdf_text
from legal_ai.services.reranker import rerank_results
from legal_ai.services.smart_chunking import SmartLegalChunker
from legal_ai.services.text_cleaning import clean_text
from legal_ai.storage.vector_db import FAISSService

RETRIEVAL_CANDIDATES = getattr(settings, "RAG_RETRIEVAL_CANDIDATES", 20)
FINAL_TOP_K = getattr(settings, "RAG_FINAL_TOP_K", 5)

chunker = SmartLegalChunker()
vector_store = FAISSService()


def _update_pipeline_step(document: LegalDocument, step: str, value: bool = True) -> None:
    steps = dict(document.pipeline_steps or {})
    steps[step] = value
    document.pipeline_steps = steps
    document.save(update_fields=["pipeline_steps"])


def _build_faiss_metadata(chunk: LegalChunk, embedding_id: int) -> Dict[str, Any]:
    meta = chunk.to_metadata()
    meta["embedding_id"] = embedding_id
    return meta


def rebuild_index_from_chunks() -> bool:
    """Rebuild FAISS index entirely from LegalChunk rows (DB is source of truth)."""
    chunks = list(LegalChunk.objects.select_related("doc").order_by("id"))
    if not chunks:
        vector_store.clear()
        return False

    model = get_embedding_model()
    texts = [c.text for c in chunks]
    embeddings = model.embed_passages(texts)

    metadata = [_build_faiss_metadata(chunk, idx) for idx, chunk in enumerate(chunks)]
    vector_store.build_index(embeddings, metadata, model_name=model.model_name)

    # Sync embedding_id on chunks
    for idx, chunk in enumerate(chunks):
        chunk.embedding_id = idx
    LegalChunk.objects.bulk_update(chunks, ["embedding_id"])

    EmbeddingConfig.objects.filter(is_active=True).update(is_active=False)
    EmbeddingConfig.objects.create(
        model_name=model.model_name,
        dimension=model.dimension,
        is_active=True,
    )
    return True


def sync_vector_store() -> None:
    """Ensure FAISS matches DB. Clears stale index if DB is empty."""
    db_count = LegalChunk.objects.count()
    vector_store.load()
    faiss_count = vector_store.count()

    if db_count == 0 and faiss_count > 0:
        vector_store.clear()
        return

    if db_count > 0 and (faiss_count == 0 or faiss_count != db_count):
        rebuild_index_from_chunks()


def process_pdf(document_id: int) -> Dict[str, Any]:
    document = LegalDocument.objects.get(id=document_id)
    document.processing_status = "extracting"
    document.processing_error = ""
    document.save(update_fields=["processing_status", "processing_error"])
    _update_pipeline_step(document, "pdf_uploaded")

    try:
        raw_text, page_count = extract_pdf_text(document.file.path)
        document.extracted_text = raw_text
        document.page_count = page_count
        document.processing_status = "cleaning"
        document.save(update_fields=["extracted_text", "page_count", "processing_status"])
        _update_pipeline_step(document, "text_extracted")

        cleaned = clean_text(raw_text)
        document.cleaned_text = cleaned
        document.processing_status = "chunking"
        document.save(update_fields=["cleaned_text", "processing_status"])
        _update_pipeline_step(document, "text_cleaned")

        chunks_data = chunker.chunk(cleaned, document_name=document.title)
        if not chunks_data:
            raise ValueError("No valid legal sections found in PDF.")

        document.processing_status = "embedding"
        document.save(update_fields=["processing_status"])

        with transaction.atomic():
            LegalChunk.objects.filter(doc=document).delete()
            chunk_objects: List[LegalChunk] = []
            for data in chunks_data:
                chunk_objects.append(
                    LegalChunk(
                        doc=document,
                        text=data["text"],
                        title=data.get("title", ""),
                        part=data.get("part", ""),
                        chapter=data.get("chapter", ""),
                        section=data.get("section", ""),
                        article=data.get("article", ""),
                        clause=data.get("clause", ""),
                        dhara=data.get("dhara", ""),
                        metadata=data.get("metadata", {}),
                        chunk_index=data.get("chunk_index", 0),
                    )
                )
            LegalChunk.objects.bulk_create(chunk_objects)

        _update_pipeline_step(document, "chunks_created")
        _update_pipeline_step(document, "metadata_generated")

        document.processing_status = "indexing"
        document.save(update_fields=["processing_status"])

        rebuild_index_from_chunks()

        _update_pipeline_step(document, "embeddings_generated")
        _update_pipeline_step(document, "stored_in_faiss")

        chunk_count = LegalChunk.objects.filter(doc=document).count()
        document.chunk_count = chunk_count
        document.processing_status = "completed"
        document.save(update_fields=["chunk_count", "processing_status"])

        return {"status": "success", "chunk_count": chunk_count, "page_count": page_count}

    except Exception as exc:
        document.processing_status = "failed"
        document.processing_error = str(exc)
        document.save(update_fields=["processing_status", "processing_error"])
        return {"status": "failed", "message": str(exc)}


def search(query: str, top_k: int = FINAL_TOP_K, *, min_score: float | None = None) -> List[Dict[str, Any]]:
    if not query or not query.strip():
        return []

    sync_vector_store()
    vector_store.load()

    if not vector_store.has_embeddings():
        return []

    query_vector = create_query_embedding(query).reshape(1, -1)
    distances, indices = vector_store.search(query_vector, RETRIEVAL_CANDIDATES)

    candidates: List[Dict[str, Any]] = []
    for dense_score, idx in zip(distances[0].tolist(), indices[0].tolist()):
        if idx < 0 or idx >= len(vector_store.metadata):
            continue
        entry = dict(vector_store.metadata[idx])
        text = entry.get("text", "")
        combined = hybrid_score(float(dense_score), query, text, entry)
        entry["dense_score"] = float(dense_score)
        entry["score"] = combined
        candidates.append(entry)

    candidates.sort(key=lambda x: x["score"], reverse=True)
    reranked = rerank_results(query, candidates, top_k=RETRIEVAL_CANDIDATES)
    filtered = filter_by_threshold(reranked, min_score=min_score)
    return filtered[:top_k]


def _format_context(hits: List[Dict[str, Any]]) -> str:
    blocks = []
    for i, hit in enumerate(hits, 1):
        header_parts = [
            hit.get("document_name") or hit.get("document_title"),
            hit.get("part"),
            hit.get("chapter"),
            hit.get("section") and f"Section {hit['section']}",
            hit.get("article") and f"Article {hit['article']}",
            hit.get("title"),
        ]
        header = " | ".join(p for p in header_parts if p)
        blocks.append(f"[Source {i}] {header}\n{hit.get('text', '')}")
    return "\n\n".join(blocks)


def _format_sources(hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sources = []
    for hit in hits:
        sources.append({
            "document": hit.get("document_name") or hit.get("document_title", ""),
            "part": hit.get("part", ""),
            "chapter": hit.get("chapter", ""),
            "section": hit.get("section", "") or hit.get("dhara", ""),
            "article": hit.get("article", ""),
            "title": hit.get("title", ""),
            "score": round(hit.get("score", 0), 4),
        })
    return sources


def answer_query(
    query: str,
    top_k: int = FINAL_TOP_K,
    *,
    min_score: float | None = None,
) -> Dict[str, Any]:
    start = time.perf_counter()
    threshold = min_score if min_score is not None else MIN_SCORE

    hits = search(query, top_k=top_k, min_score=threshold)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    if not hits:
        has_docs = LegalDocument.objects.exists()
        has_chunks = LegalChunk.objects.count() > 0

        if not has_docs:
            message = "No legal documents are available. Please upload a PDF first."
        elif not has_chunks:
            message = "Documents exist but are not indexed yet. Re-upload or run rebuild_vector_index."
        else:
            message = "No sufficiently relevant legal provision was found in the available documents."

        return {
            "query": query,
            "answer": message,
            "sources": [],
            "confidence_score": 0.0,
            "response_time_ms": elapsed_ms,
        }

    confidence = round(sum(h["score"] for h in hits) / len(hits), 4)
    context = _format_context(hits)
    answer = llm.generate(query, context)

    return {
        "query": query,
        "answer": answer,
        "sources": _format_sources(hits),
        "confidence_score": confidence,
        "response_time_ms": elapsed_ms,
    }
