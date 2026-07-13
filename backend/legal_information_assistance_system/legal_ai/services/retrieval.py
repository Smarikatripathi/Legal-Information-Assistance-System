from typing import Any, Dict, List, Optional

from django.conf import settings

from legal_information_assistance_system.legal_ai.models import EmbeddingConfig, LegalChunk
from legal_information_assistance_system.legal_ai.services.embedding import create_query_embedding, get_embedding_model
from legal_information_assistance_system.legal_ai.services.hybrid_retrieval import MIN_SCORE, filter_by_threshold, hybrid_score
from legal_information_assistance_system.legal_ai.services.reranker import rerank_results
from legal_information_assistance_system.legal_ai.storage.vector_db import FAISSService

RETRIEVAL_CANDIDATES = getattr(settings, "RAG_RETRIEVAL_CANDIDATES", 15)
FINAL_TOP_K = getattr(settings, "RAG_FINAL_TOP_K", 5)

_vector_store: FAISSService | None = None


def get_vector_store() -> FAISSService:
    global _vector_store
    if _vector_store is None:
        _vector_store = FAISSService()
    return _vector_store


def _build_faiss_metadata(chunk: LegalChunk, embedding_id: int) -> Dict[str, Any]:
    meta = chunk.to_metadata()
    meta["embedding_id"] = embedding_id
    return meta


def rebuild_faiss_index() -> bool:
    """Rebuild FAISS index once from all LegalChunk rows."""
    chunks = list(LegalChunk.objects.select_related("doc").order_by("id"))
    store = get_vector_store()

    if not chunks:
        store.clear()
        return False

    model = get_embedding_model()
    texts = [c.text for c in chunks]
    embeddings = model.embed_passages(texts)

    metadata = [_build_faiss_metadata(chunk, idx) for idx, chunk in enumerate(chunks)]
    store.build_index(embeddings, metadata, model_name=model.model_name)

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
    """Ensure FAISS matches the database."""
    db_count = LegalChunk.objects.count()
    store = get_vector_store()
    store.load()
    faiss_count = store.count()

    if db_count == 0 and faiss_count > 0:
        store.clear()
        return

    if db_count > 0 and (faiss_count == 0 or faiss_count != db_count):
        rebuild_faiss_index()


def search(
    query: str,
    top_k: int = FINAL_TOP_K,
    *,
    min_score: float | None = None,
) -> List[Dict[str, Any]]:
    """Hybrid FAISS search with similarity threshold."""
    if not query or not query.strip():
        return []

    sync_vector_store()
    store = get_vector_store()
    store.load()

    if not store.has_embeddings():
        return []

    query_vector = create_query_embedding(query).reshape(1, -1)
    distances, indices = store.search(query_vector, RETRIEVAL_CANDIDATES)

    candidates: List[Dict[str, Any]] = []
    for dense_score, idx in zip(distances[0].tolist(), indices[0].tolist()):
        if idx < 0 or idx >= len(store.metadata):
            continue
        entry = dict(store.metadata[idx])
        text = entry.get("text", "")
        combined = hybrid_score(float(dense_score), query, text, entry)
        entry["dense_score"] = float(dense_score)
        entry["score"] = combined
        candidates.append(entry)

    candidates.sort(key=lambda x: x["score"], reverse=True)
    reranked = rerank_results(query, candidates, top_k=RETRIEVAL_CANDIDATES)

    threshold = min_score if min_score is not None else MIN_SCORE
    return filter_by_threshold(reranked, min_score=threshold)[:top_k]


# Backward-compatible aliases
rebuild_index_from_chunks = rebuild_faiss_index
